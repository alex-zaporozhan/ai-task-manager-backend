import os
from datetime import datetime, timedelta
from typing import Optional
from dotenv import load_dotenv
from jose import jwt
from passlib.context import CryptContext

load_dotenv()

# "Fail Fast" — если ключей нет, программа не должна даже пытаться работать.
try:
    SECRET_KEY = os.environ["JWT_SECRET_KEY"]
    ALGORITHM = os.environ["JWT_ALGORITHM"]
    ACCESS_TOKEN_EXPIRE_MINUTES = int(os.environ["ACCESS_TOKEN_EXPIRE_MINUTES"])
except KeyError as e:
    raise RuntimeError(f"CRITICAL SECURITY ERROR: Variable {e} is missing in .env file!")
except ValueError:
    raise RuntimeError("CRITICAL ERROR: ACCESS_TOKEN_EXPIRE_MINUTES must be an integer!")

pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto", bcrypt__ident="2b")

def verify_password(plain_password: str, hashed_password: str) -> bool:
    return pwd_context.verify(plain_password, hashed_password)

def get_password_hash(password: str) -> str:
    return pwd_context.hash(password)

def create_access_token(data: dict, expires_delta: Optional[timedelta] = None) -> str:
    to_encode = data.copy()
    expire = datetime.utcnow() + (expires_delta or timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES))
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)

def create_password_reset_token(email: str) -> str:
    expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode = {"sub": email, "type": "password_reset", "exp": expire}
    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)