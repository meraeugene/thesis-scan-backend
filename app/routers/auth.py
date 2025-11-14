from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app import schemas, crud, database
from app.config import PROFILE_PICTURES_DIR
from datetime import datetime
import os
import jwt
from datetime import datetime, timedelta
from dotenv import load_dotenv

load_dotenv()  # loads .env into environment

def get_db():
    db = database.SessionLocal()
    try:
        yield db
    finally:
        db.close()
        
        
router = APIRouter()

SECRET_KEY = os.getenv("SECRET_KEY")
if not SECRET_KEY:
    raise ValueError("SECRET_KEY not found in environment variables!")

ALGORITHM = "HS256"

def create_token(data: dict):
    payload = data.copy()
    payload["exp"] = datetime.utcnow() + timedelta(hours=8)
    return jwt.encode(payload, SECRET_KEY, algorithm=ALGORITHM)

def verify_token(token: str):
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except:
        return None
    
# Librarian login endpoint
@router.post("/librarian/login/")
def librarian_login(username: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    librarian = crud.get_librarian(db, username=username)
    
    if not librarian or librarian.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="Invalid credentials.")
    
    # Create login token
    token = create_token({"user_id": librarian.id, "role": "librarian"})
    
    return {
        "token": token,
        "id": librarian.id,
    }

# Update librarian profile
@router.post("/librarian/update/", response_model=schemas.LibrarianOut)
async def update_librarian(
    username: str = Form(...),  # username required to identify user
    full_name: str = Form(None),
    email: str = Form(None),
    role: str = Form(None),
    contact: str = Form(None),
    password: str = Form(None),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    librarian = crud.get_librarian(db, username=username)
    print("Updating librarian:", username)
    if not librarian:
        raise HTTPException(status_code=404, detail="Librarian not found")

    # Update fields only if provided
    if full_name is not None:
        librarian.full_name = full_name
    if email is not None:
        librarian.email = email
    if role is not None:
        librarian.role = role
    if contact is not None:
        librarian.contact = contact
    if password:
        librarian.password = password

    # Handle profile picture
    if profile_picture:
        ext = os.path.splitext(profile_picture.filename)[1]
        timestamp = int(datetime.now().timestamp())
        filename = f"{username}_{timestamp}{ext}"

        # Ensure profile pictures directory exists
        os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)

        # Remove old profile pictures
        for old_file in os.listdir(PROFILE_PICTURES_DIR):
            if old_file.startswith(f"{username}_"):
                try:
                    os.remove(os.path.join(PROFILE_PICTURES_DIR, old_file))
                except Exception as e:
                    print(f"Warning: Could not remove old profile picture: {e}")

        # Save new profile picture
        save_path = os.path.join(PROFILE_PICTURES_DIR, filename)
        try:
            with open(save_path, "wb") as f:
                f.write(await profile_picture.read())
            librarian.profile_picture = f"/static/profilePicture/{filename}"
        except Exception as e:
            print(f"Error saving profile picture: {e}")
            raise HTTPException(status_code=500, detail="Failed to save profile picture")

    db.commit()
    db.refresh(librarian)
    return librarian

# Get librarian by ID
@router.get("/librarian/id/{librarian_id}", response_model=schemas.LibrarianOut)
def get_librarian_by_id(librarian_id: int, db: Session = Depends(get_db)):
    librarian = crud.get_librarian_by_id(db, librarian_id=librarian_id)
    if not librarian:
        raise HTTPException(status_code=404, detail="Librarian not found")
    return librarian

# Create librarian endpoint
@router.post("/librarian/", response_model=schemas.LibrarianOut)
def create_librarian(librarian: schemas.LibrarianCreate, db: Session = Depends(get_db)):
    db_librarian = crud.get_librarian(db, username=librarian.username)
    if db_librarian:
        raise HTTPException(status_code=400, detail="Username already registered")
    return crud.create_librarian(db, librarian)
