# app\schemas.py
from pydantic import BaseModel
from datetime import datetime


class UserCreate(BaseModel):
    username: str
    password: str


class BookCreate(BaseModel):
    title: str
    author: str


class RegisterUser(BaseModel):
    username: str
    password: str


class LoginUser(BaseModel):
    username: str
    password: str


class BookRequestCreate(BaseModel):
    book_id: int

class BookRequestResponse(BaseModel):
    id: int
    book_id: int
    requester_id: int
    request_date: datetime
    status: str