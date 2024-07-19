FROM python:3.12-alpine

WORKDIR ./app

ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1

COPY . .

RUN pip install --upgrade pip

RUN pip install -r requirements.txt

CMD ["uvicorn", "--port", "8081", "--host", "0.0.0.0", "application.main:app"]