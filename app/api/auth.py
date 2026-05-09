from fastapi import (
    APIRouter,
    Depends,
    HTTPException,
    status
)

from fastapi.responses import JSONResponse

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from sqlalchemy.exc import IntegrityError

from app.db import models
from app.schemas.user import UserCreate, UserLogin
from app.db.deps import get_db

from app.core.security import (
    hash_password,
    verify_password,
    create_access_token
)

router = APIRouter()


@router.post("/register")
async def register(
    user: UserCreate,
    db: AsyncSession = Depends(get_db)
):

    # Check existing user
    result = await db.execute(
        select(models.User).where(
            models.User.username == user.username
        )
    )

    existing_user = result.scalar_one_or_none()

    if existing_user:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    # Create user
    db_user = models.User(
        username=user.username,
        password=hash_password(user.password)
    )

    db.add(db_user)

    try:
        await db.commit()

        await db.refresh(db_user)

    except IntegrityError:

        await db.rollback()

        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Username already exists"
        )

    return {
        "message": "User created successfully"
    }


@router.post("/login")
async def login(
    user: UserLogin,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(models.User).where(
            models.User.username == user.username
        )
    )

    db_user = result.scalar_one_or_none()

    if not db_user:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="User not registered"
        )

    if not verify_password(
        user.password,
        db_user.password
    ):
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid credentials"
        )

    token = create_access_token(
        {"sub": db_user.username}
    )

    response = JSONResponse(
        content={
            "message": "Login successful"
        }
    )

    response.set_cookie(
        key="token",
        value=token,
        httponly=True,
        secure=False,
        samesite="Lax",
        max_age=60 * 60 * 24,
        path="/"
    )

    return response