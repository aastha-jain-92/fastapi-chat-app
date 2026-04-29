from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.db.deps import get_db
from app.db import models

router = APIRouter()

@router.get("/messages/{user1}/{user2}")
def get_messages(user1: str, user2: str, db: Session = Depends(get_db)):
    messages = db.query(models.Message).filter(
        ((models.Message.sender == user1) & (models.Message.receiver == user2)) |
        ((models.Message.sender == user2) & (models.Message.receiver == user1))
    ).all()

    return messages