# app/dependencies.py
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from sqlmodel import Session
from .models import User
from sqlmodel import select
from fastapi import HTTPException, status, Depends
from sqlalchemy import create_engine

engine = create_engine("sqlite:///./book_exchange.db")
security = HTTPBasic()


def get_session():
    with Session(engine) as session:
        yield session