from fastapi import APIRouter, Depends,HTTPException,status
from sqlalchemy.orm import Session
from fastapi.responses import JSONResponse
from app.db import models
from app.schemas.user import UserCreate
from app.db.deps import get_db
from app.core.security import hash_password
from app.schemas.user import UserLogin
from sqlalchemy.exc import IntegrityError
from app.core.security import verify_password, create_access_token

router = APIRouter()

@router.post("/register")
def register(user: UserCreate, db: Session = Depends(get_db)):
    db_user = models.User(
        username=user.username,
        password=hash_password(user.password)
    )
    db.add(db_user)
    try:
        db.commit()
        db.refresh(db_user)

    except IntegrityError:
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    return {"message": "User created"} 

@router.post("/login")
def login(user: UserLogin, db: Session = Depends(get_db)):
    db_user = db.query(models.User).filter(
        models.User.username == user.username
    ).first()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered"
        )
        
    if not verify_password(user.password, db_user.password):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token({"sub": db_user.username})

    response = JSONResponse(
        content={
            "message": "Login successful"
        }
    )

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,      # True in production HTTPS
        samesite="Lax",
        max_age=60 * 60 * 24,
        path='/'
    )

    return response