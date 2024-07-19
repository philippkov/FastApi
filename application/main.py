# BookTrading/app/main.py

from sqlmodel import SQLModel
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from starlette.responses import FileResponse
import os

from application.dependencies import engine
from application.routers import users, books, book_requests

parent_dir_path = os.path.dirname(os.path.realpath(__file__))
app = FastAPI()

app.include_router(users.router)
app.include_router(books.router)
app.include_router(book_requests.router)

SQLModel.metadata.create_all(engine)

app.mount("/static", StaticFiles(directory="application/static"), name="static")

@app.get('/')
def index():
    return FileResponse(parent_dir_path + '/static/index.html')

@app.get('/login')
def login_page():
    return FileResponse(parent_dir_path + '/static/login.html')

@app.get('/register')
def register_page():
    return FileResponse(parent_dir_path + '/static/registration.html')

@app.get('/available')
def available_page():
    return FileResponse(parent_dir_path + '/static/available.html')

@app.get('/mybooks')
def mybooks_page():
    return FileResponse(parent_dir_path + '/static/mybooks.html')

@app.get('/myrequests')
def myrequests_page():
    return FileResponse(parent_dir_path + '/static/myrequests.html')

@app.get('/receivedrequests')
def received_requests_page():
    return FileResponse(parent_dir_path + '/static/receivedrequests.html')

#uvicorn application.main:app --reload
