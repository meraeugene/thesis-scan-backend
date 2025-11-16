# app/routers/password_reset.py
from fastapi import APIRouter, Form, Depends, HTTPException, status
from sqlalchemy.orm import Session
from datetime import datetime, timedelta
import jwt
import os
from app import crud, models
from app.database import SessionLocal
from app.utils.emailer import send_reset_email
# from dotenv import load_dotenv

router = APIRouter()

# load_dotenv()  # uncomment if local testing is needed

# Config: read from env
RESET_SECRET =  os.getenv("SECRET_KEY") 
if not RESET_SECRET:
    raise RuntimeError("RESET_SECRET (or SECRET_KEY) not set in environment")

RESET_EXPIRE_MINUTES = int(os.getenv("RESET_EXPIRE_MINUTES"))
FRONTEND_RESET_URL = os.getenv("FRONTEND_RESET_URL") 

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def create_reset_token(email: str):
    payload = {
        "email": email,
        "type": "password_reset",
        "exp": datetime.utcnow() + timedelta(minutes=RESET_EXPIRE_MINUTES),
        "iat": datetime.utcnow()
    }
    return jwt.encode(payload, RESET_SECRET, algorithm="HS256")

def verify_reset_token(token: str):
    try:
        data = jwt.decode(token, RESET_SECRET, algorithms=["HS256"])
        if data.get("type") != "password_reset":
            raise jwt.InvalidTokenError("Invalid token type")
        return data
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=400, detail="Reset token expired. Please request a new password reset.")
    except jwt.InvalidTokenError:
        raise HTTPException(status_code=400, detail="Invalid reset token")

@router.post("/forgot-password/")
def forgot_password(email: str = Form(...), db: Session = Depends(get_db)):
    """
    Request password reset: only send email if the email exists in Users table.
    Returns 404 if not found.
    """
    user = crud.get_user_by_email(db, email=email)

    #  If the email does NOT exist → return error
    if not user:
        raise HTTPException(
            status_code=404,
            detail="Email not found. Please make sure you entered a registered email."
        )

    #  Create token
    token = create_reset_token(user.email)

    #  Build reset link
    reset_link = f"{FRONTEND_RESET_URL}?token={token}"

    #  Send email
    send_reset_email(
        to_email=user.email,
        reset_link=reset_link,
        recipient_name=user.full_name if hasattr(user, "full_name") else None
    )

    return {"message": "Password reset link sent successfully."}

@router.post("/reset-password/")
def reset_password(
    token: str = Form(...),
    new_password: str = Form(...),
    db: Session = Depends(get_db)
):
    """
    Verify reset token and update user's password.
    Prevent setting the same password as the current one.
    """
    payload = verify_reset_token(token)
    email = payload.get("email")
    if not email:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid token payload"
        )

    user = crud.get_user_by_email(db, email=email)
    if not user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not found"
        )

    # Check if new password is the same as current
    if user.password == new_password:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="New password cannot be the same as the current password"
        )

    # Update password (use hashed password in production)
    crud.update_user_password(db, user, new_password)

    return {"message": "Password updated successfully"}
