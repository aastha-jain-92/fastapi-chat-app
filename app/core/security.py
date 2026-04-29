from jose import jwt
from datetime import datetime, timedelta
from passlib.context import CryptContext
from app.core.config import settings

ALGORITHM = "HS256"

pwd_context = CryptContext(schemes=["argon2"], deprecated="auto")
def hash_password(password: str):
    return pwd_context.hash(password)

def verify_password(plain_password, hashed_password):
    return pwd_context.verify(plain_password, hashed_password)

def create_access_token(data: dict):
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=60)
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.secret_key, algorithm=ALGORITHM)