from sqlalchemy import Column, Integer, String
from app.db.database import Base

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    username = Column(String, unique=True)
    password = Column(String) 

from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
from datetime import datetime

class Message(Base):
    __tablename__ = "messages"

    id = Column(Integer, primary_key=True, index=True)
    sender = Column(String, ForeignKey("users.username"))
    receiver = Column(String, ForeignKey("users.username"))
    content = Column(String)
    timestamp = Column(DateTime, default=datetime.utcnow)