# BookTrading/app/routers/books.py

from fastapi import APIRouter, Depends, HTTPException, Query
from fastapi.security import OAuth2PasswordBearer
from sqlmodel import Session, select
from typing import List

from starlette.responses import JSONResponse
from starlette.status import HTTP_401_UNAUTHORIZED

from application.models import Book, BookRequest, User
from application.dependencies import get_session
from application.schemas import BookCreate, BookRequestCreate, BookRequestResponse
from application.utils import verify_access_token

router = APIRouter()

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="token")

def get_current_user_from_token(token: str = Depends(oauth2_scheme), session: Session = Depends(get_session)):
    credentials_exception = HTTPException(
        status_code=HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    return verify_access_token(token, credentials_exception, session)

@router.post("/books/", response_model=Book)
def create_book(book_data: BookCreate, user: User = Depends(get_current_user_from_token),
                session: Session = Depends(get_session)):
    book = Book(**book_data.dict(), owner_id=user.id)
    session.add(book)
    session.commit()
    return book

@router.get("/mybooks/")
def read_books_for_user(user: User = Depends(get_current_user_from_token), session: Session = Depends(get_session)):
    statement = select(Book).where(Book.owner_id == user.id)
    results = session.exec(statement).all()
    books = [{"id": book.id, "title": book.title, "author": book.author, "is_available": book.is_available,
              "owner": {"id": user.id, "username": user.username}} for book in results]
    return JSONResponse(content=books)

@router.patch("/books/{book_id}/availability", response_model=Book)
def update_book_availability(book_id: int, is_available: bool = Query(...),
                             user: User = Depends(get_current_user_from_token),
                             session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book or book.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Book not found or not authorized")

    book.is_available = is_available
    session.add(book)
    session.commit()
    session.refresh(book)
    return book

@router.get("/available/", response_model=List[Book])
def read_available_books(user: User = Depends(get_current_user_from_token), session: Session = Depends(get_session)):
    statement = select(Book).where(Book.is_available == True, Book.owner_id != user.id)
    results = session.exec(statement).all()
    return results

@router.delete("/books/{book_id}", response_model=dict)
def delete_book(book_id: int, user: User = Depends(get_current_user_from_token),
                session: Session = Depends(get_session)):
    book = session.get(Book, book_id)
    if not book or book.owner_id != user.id:
        raise HTTPException(status_code=404, detail="Book not found or not authorized")

    session.delete(book)
    session.commit()
    return {"message": "Book deleted successfully"}
