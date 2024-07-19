# BookTrading/app/routers/users.py
from fastapi import APIRouter, Depends, HTTPException, Response
from fastapi.security import  OAuth2PasswordRequestForm
from sqlmodel import Session, select
from starlette.status import HTTP_401_UNAUTHORIZED

from application.dependencies import get_session
from application.models import User
from application.schemas import RegisterUser
from application.utils import create_access_token, hash_password


router = APIRouter()


@router.post("/login/")
async def login_user(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                     session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}


@router.post("/register/")
async def register_user(user: RegisterUser, session: Session = Depends(get_session)):
    db_user = session.exec(select(User).where(User.username == user.username)).first()
    if db_user:
        raise HTTPException(status_code=400, detail="Username already registered")
    hashed_password = hash_password(user.password)
    new_user = User(username=user.username, hashed_password=hashed_password)
    session.add(new_user)
    session.commit()
    return {"message": "User registered successfully"}


@router.post("/token")
def login_for_access_token(response: Response, form_data: OAuth2PasswordRequestForm = Depends(),
                           session: Session = Depends(get_session)):
    user = session.exec(select(User).where(User.username == form_data.username)).first()
    if not user or not user.verify_password(form_data.password):
        raise HTTPException(
            status_code=HTTP_401_UNAUTHORIZED,
            detail="Incorrect username or password",
            headers={"WWW-Authenticate": "Bearer"},
        )
    access_token = create_access_token(data={"sub": user.username})
    response.set_cookie(key="access_token", value=f"Bearer {access_token}", httponly=True)
    return {"access_token": access_token, "token_type": "bearer"}
