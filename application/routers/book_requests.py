# BookTrading/app/routers/book_requests.py

from fastapi import APIRouter, Depends, HTTPException
from sqlmodel import Session, select
from typing import List
from datetime import datetime

from application.models import BookRequest, Book, User
from application.dependencies import get_session
from application.routers.books import get_current_user_from_token
from application.schemas import BookRequestCreate, BookRequestResponse
from application.utils import verify_access_token

router = APIRouter()


@router.post("/book_requests/", response_model=BookRequestResponse)
def create_book_request(request_data: BookRequestCreate, user: User = Depends(get_current_user_from_token),
                        session: Session = Depends(get_session)):
    book = session.get(Book, request_data.book_id)
    if not book or not book.is_available:
        raise HTTPException(status_code=404, detail="Book not available")

    book_request = BookRequest(
        book_id=request_data.book_id,
        requester_id=user.id
    )
    session.add(book_request)
    session.commit()
    session.refresh(book_request)
    return book_request


@router.get("/book_requests/", response_model=List[BookRequestResponse])
def read_book_requests(user: User = Depends(get_current_user_from_token), session: Session = Depends(get_session)):
    statement = select(BookRequest).where(BookRequest.requester_id == user.id)
    results = session.exec(statement).all()
    return results


@router.get("/book_requests/received/", response_model=List[BookRequestResponse])
def read_received_requests(user: User = Depends(get_current_user_from_token), session: Session = Depends(get_session)):
    statement = (
        select(BookRequest)
        .join(Book, BookRequest.book_id == Book.id)
        .where(Book.owner_id == user.id)
    )
    results = session.exec(statement).all()
    return results


@router.patch("/book_requests/{request_id}/approve", response_model=BookRequestResponse)
def approve_request(request_id: int, user: User = Depends(get_current_user_from_token),
                    session: Session = Depends(get_session)):
    book_request = session.get(BookRequest, request_id)
    if not book_request:
        raise HTTPException(status_code=404, detail="Request not found")

    book = session.get(Book, book_request.book_id)
    if book.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to approve this request")

    book_request.approve()
    book.owner_id = book_request.requester_id  # Изменяем владельца книги
    book.is_available = False  # Книга больше не доступна для обмена
    session.add(book)
    session.add(book_request)
    session.commit()
    session.refresh(book_request)
    return book_request


@router.patch("/book_requests/{request_id}/reject", response_model=BookRequestResponse)
def reject_request(request_id: int, user: User = Depends(get_current_user_from_token),
                   session: Session = Depends(get_session)):
    book_request = session.get(BookRequest, request_id)
    if not book_request:
        raise HTTPException(status_code=404, detail="Request not found")

    book = session.get(Book, book_request.book_id)
    if book.owner_id != user.id:
        raise HTTPException(status_code=403, detail="Not authorized to reject this request")

    book_request.reject()
    session.add(book_request)
    session.commit()
    session.refresh(book_request)
    return book_request
