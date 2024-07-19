# C:/Users/Nik/Desktop/Папка/BookTrading/application/utils.py
import jwt
from datetime import datetime, timedelta
from jwt import PyJWTError
from sqlmodel import select
from application.models import User
from hashlib import sha256

SECRET_KEY = "12312dsgsgfdg"
ALGORITHM = "HS256"

def hash_password(password: str):
    return sha256(password.encode()).hexdigest()


def create_access_token(data: dict, expires_delta: timedelta = None):
    to_encode = data.copy()
    if expires_delta:
        expire = datetime.utcnow() + expires_delta
    else:
        expire = datetime.utcnow() + timedelta(minutes=15)
    to_encode.update({"exp": expire})
    encoded_jwt = jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)
    return encoded_jwt


def verify_access_token(token: str, credentials_exception, session):
    try:
        payload = jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
        username: str = payload.get("sub")
        if username is None:
            raise credentials_exception
        user = session.exec(select(User).where(User.username == username)).first()
        if user is None:
            raise credentials_exception
        return user
    except PyJWTError:
        raise credentials_exception
