# BookTrading/models.py
from sqlmodel import SQLModel, Field
from typing import Optional
from hashlib import sha256


class User(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    username: str
    hashed_password: str

    def verify_password(self, password):
        return self.hashed_password == sha256(password.encode()).hexdigest()
    ##def verify_password(self, password):
        ##return self.hashed_password == password

class Book(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    title: str
    author: str
    owner_id: int = Field(foreign_key="user.id")
    is_available: bool = True

    def set_availability(self, is_available: bool):
        self.is_available = is_available

from datetime import datetime
from sqlmodel import SQLModel, Field
from typing import Optional

class BookRequest(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    book_id: int = Field(foreign_key="book.id")
    requester_id: int = Field(foreign_key="user.id")
    request_date: datetime = Field(default_factory=datetime.utcnow)
    status: str = Field(default="pending")

    def approve(self):
        self.status = "approved"

    def reject(self):
        self.status = "rejected"