from fastapi import APIRouter, Depends, HTTPException, status, Form, File, UploadFile
from sqlalchemy.orm import Session
from app import schemas, crud, database
from app.config import PROFILE_PICTURES_DIR
import os
from datetime import datetime, timedelta
import jwt
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

# User login endpoint
@router.post("/login/")
def login(student_id: str = Form(...), password: str = Form(...), db: Session = Depends(get_db)):
    user = crud.get_user(db, student_id=student_id)
    if not user or user.password != password:
        raise HTTPException(status_code=status.HTTP_401_UNAUTHORIZED, detail="These credentials do not match our records.")
    
    # Update last login time
    user.last_login = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
    db.commit()

     # Create login token
    token = create_token({"user_id": user.id, "student_id": user.student_id, "role": "user"})
    
    return {
        "token": token,
        "id": user.id,
    }


# Add bookmark
@router.post("/users/bookmarks/", response_model=schemas.BookmarkOut)
def add_bookmark(bookmark: schemas.BookmarkCreate, db: Session = Depends(get_db)):
    return crud.add_bookmark(db, bookmark)

# Delete bookmark
@router.delete("/users/bookmarks/{student_id}/{thesis_id}", status_code=204)
def delete_bookmark(student_id: str, thesis_id: int, db: Session = Depends(get_db)):
    bookmark = crud.get_bookmark(db, student_id=student_id, thesis_id=thesis_id)
    if not bookmark:
        raise HTTPException(status_code=404, detail="Bookmark not found")
    
    crud.delete_bookmark(db, bookmark)
    return

# Get bookmarks
@router.get("/users/bookmarks/{studentId}", response_model=list[schemas.BookmarkOut])
def get_bookmarks(studentId: str, db: Session = Depends(get_db)):
    return crud.get_bookmarks(db, studentId)

# Add search history
@router.post("/users/search-history/", response_model=schemas.SearchHistoryOut)
def add_search_history(history: schemas.SearchHistoryCreate, db: Session = Depends(get_db)):
    return crud.add_search_history(db, history)

# Get search history
@router.get("/users/search-history/{id}", response_model=list[schemas.SearchHistoryOut])
def get_search_history(id: str, db: Session = Depends(get_db)):
    return crud.get_search_history(db, id)

# List all users
@router.get("/users/list/", response_model=list[schemas.UserOut])
def list_users(db: Session = Depends(get_db)):
    return crud.get_users(db)

# Get student profile by ID
@router.get("/users/{id}", response_model=schemas.UserOut)
def get_user_profile(id: str, db: Session = Depends(get_db)):
    id = id.strip()  
    user = crud.get_user_by_id(db, id=id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    return user

# Update user profile
@router.post("/users/update/", response_model=schemas.UserOut)
async def update_user(
    student_id: str = Form(...),
    email: str = Form(...),
    password: str = Form(None),
    profile_picture: UploadFile = File(None),
    db: Session = Depends(get_db)
):
    user = crud.get_user(db, student_id=student_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    user.email = email
    if password:
        user.password = password
    if profile_picture:
        ext = os.path.splitext(profile_picture.filename)[1]
        timestamp = int(datetime.now().timestamp())
        filename = f"{student_id}_{timestamp}{ext}"
        
        # Ensure profile pictures directory exists
        os.makedirs(PROFILE_PICTURES_DIR, exist_ok=True)
        
        # Remove any old profile pictures for this student
        for old_file in os.listdir(PROFILE_PICTURES_DIR):
            if old_file.startswith(f"{student_id}_"):
                try:
                    os.remove(os.path.join(PROFILE_PICTURES_DIR, old_file))
                except Exception as e:
                    print(f"Warning: Could not remove old profile picture: {e}")
        
        # Save the new profile picture
        save_path = os.path.join(PROFILE_PICTURES_DIR, filename)
        print(f"Saving profile picture to: {save_path}")
        try:
            with open(save_path, "wb") as f:
                f.write(await profile_picture.read())
            print(f"Successfully saved profile picture to: {save_path}")
        except Exception as e:
            print(f"Error saving profile picture: {e}")
            raise HTTPException(status_code=500, detail="Failed to save profile picture")
            
        # Update user profile picture path in database
        user.profile_picture = f"/static/profilePicture/{filename}"
    db.commit()
    db.refresh(user)
    return user

# Create new user
@router.post("/users/", response_model=schemas.UserOut)
def create_user(user: schemas.UserCreate, db: Session = Depends(get_db)):
    db_user = crud.get_user(db, student_id=user.student_id)
    if db_user:
        raise HTTPException(status_code=400, detail="Student ID already registered")
    return crud.create_user(db, user)

# Delete user by ID
@router.delete("/users/{user_id}", status_code=204)
def delete_user(user_id: int, db: Session = Depends(get_db)):
    user = crud.get_user_by_id(db, id=user_id)
    if not user:
        raise HTTPException(status_code=404, detail="User not found")
    crud.delete_user(db, user)
    return
