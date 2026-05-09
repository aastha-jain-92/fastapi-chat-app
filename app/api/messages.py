from fastapi import APIRouter, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, or_, and_

from app.db.deps import get_db
from app.db import models

router = APIRouter()


@router.get("/messages/{user1}/{user2}")
async def get_messages(
    user1: str,
    user2: str,
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(
        select(models.Message).where(
            or_(
                and_(
                    models.Message.sender == user1,
                    models.Message.receiver == user2
                ),
                and_(
                    models.Message.sender == user2,
                    models.Message.receiver == user1
                )
            )
        )
    )

    messages = result.scalars().all()

    return messages