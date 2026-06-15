from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.db.dependencies import get_db
from app.schemas.user import UserCreate, UserLogin
from app.models.user import User
from app.core.security import (
    hash_password,
    verify_password
)

router = APIRouter()


@router.get("/health")
def health_check():
    return {"message": "Auth API working"}

@router.post("/register")
def register(
    user: UserCreate,
    db: Session = Depends(get_db)
):
    hashed_password = hash_password(
        user.password
    )

    new_user = User(
        full_name=user.full_name,
        email=user.email,
        password_hash=hashed_password,
        role="developer"
    )

    db.add(new_user)
    db.commit()

    return {
        "message": "User registered successfully"
    }

@router.post("/login")
def login(
    user: UserLogin,
    db: Session = Depends(get_db)
):
    existing_user = (
        db.query(User)
        .filter(User.email == user.email)
        .first()
    )

    if not existing_user:
        return {
            "message": "Invalid email or password"
        }

    if not verify_password(
        user.password,
        existing_user.password_hash
    ):
        return {
            "message": "Invalid email or password"
        }

    return {
        "message": "Login successful"
    }