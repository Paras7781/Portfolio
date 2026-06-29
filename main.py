import os
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from pathlib import Path

from dotenv import load_dotenv
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import FileResponse
from pydantic import BaseModel, EmailStr
from sqlalchemy import create_engine, MetaData, Table, Column, Integer, String, Text, DateTime, insert, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.orm import sessionmaker
from datetime import datetime

load_dotenv()

app = FastAPI(title='Paras Portfolio API', version='1.0.0')

app.add_middleware(
    CORSMiddleware,
    allow_origins=['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

BASE_DIR = Path(__file__).resolve().parent

DATABASE_URL = os.getenv(
    'DATABASE_URL',
    f"sqlite:///{(BASE_DIR / 'portfolio.db').as_posix()}"
)

connect_args = {'check_same_thread': False} if DATABASE_URL.startswith('sqlite') else {}
engine = create_engine(DATABASE_URL, connect_args=connect_args, future=True)
metadata = MetaData()

messages_table = Table(
    'messages',
    metadata,
    Column('id', Integer, primary_key=True, autoincrement=True),
    Column('name', String(100), nullable=False),
    Column('email', String(320), nullable=False),
    Column('message', Text, nullable=False),
    Column('created_at', DateTime, nullable=False),
)

SessionLocal = sessionmaker(bind=engine, autoflush=False, future=True)
metadata.create_all(engine)


def send_contact_email(name: str, email: str, message: str) -> bool:
    smtp_host = os.getenv('SMTP_HOST')
    smtp_port = os.getenv('SMTP_PORT', '587')
    smtp_username = os.getenv('SMTP_USERNAME')
    smtp_password = os.getenv('SMTP_PASSWORD')
    smtp_from = os.getenv('SMTP_FROM', smtp_username)
    smtp_to = os.getenv('SMTP_TO', 'chouguleparas498@gmail.com')

    if not all([smtp_host, smtp_username, smtp_password, smtp_from]):
        return False

    msg = MIMEMultipart()
    msg['From'] = smtp_from
    msg['To'] = smtp_to
    msg['Subject'] = f'New portfolio contact from {name}'

    body = (
        f'Name: {name}\n'
        f'Email: {email}\n\n'
        f'Message:\n{message}'
    )
    msg.attach(MIMEText(body, 'plain'))

    try:
        with smtplib.SMTP(smtp_host, int(smtp_port)) as server:
            server.starttls()
            server.login(smtp_username, smtp_password)
            server.sendmail(smtp_from, [smtp_to], msg.as_string())
    except (smtplib.SMTPException, ValueError, OSError):
        return False

    return True


class ContactMessage(BaseModel):
    name: str
    email: EmailStr
    message: str


class StoredContactMessage(BaseModel):
    id: int
    name: str
    email: EmailStr
    message: str
    created_at: datetime


def save_contact_message(message: ContactMessage) -> int:
    record = {
        'name': message.name.strip(),
        'email': str(message.email),
        'message': message.message.strip(),
        'created_at': datetime.utcnow(),
    }
    with SessionLocal() as session:
        result = session.execute(insert(messages_table).values(**record))
        session.commit()
        return result.inserted_primary_key[0]


def get_contact_messages() -> list[StoredContactMessage]:
    with SessionLocal() as session:
        result = session.execute(
            select(
                messages_table.c.id,
                messages_table.c.name,
                messages_table.c.email,
                messages_table.c.message,
                messages_table.c.created_at,
            ).order_by(messages_table.c.created_at.desc())
        )
        return [StoredContactMessage(**row._mapping) for row in result]


@app.get('/api/health')
def health_check():
    return {'status': 'ok', 'message': 'FastAPI backend is running'}


@app.post('/api/contact')
def submit_contact(message: ContactMessage):
    if not message.name.strip() or not message.message.strip():
        raise HTTPException(status_code=400, detail='Name and message are required')

    try:
        message_id = save_contact_message(message)
    except SQLAlchemyError:
        raise HTTPException(status_code=500, detail='Failed to save contact message')

    email_sent = send_contact_email(message.name.strip(), str(message.email), message.message.strip())

    return {
        'success': True,
        'message_id': message_id,
        'message': 'Message received successfully' if email_sent else 'Message received locally. Configure SMTP to send email.',
        'recipient': 'chouguleparas498@gmail.com',
        'email_sent': email_sent,
    }


@app.get('/api/messages', response_model=list[StoredContactMessage])
def get_messages():
    return get_contact_messages()


@app.get('/')
def index():
    return FileResponse(BASE_DIR / 'index.html')


@app.get('/{full_path:path}')
def serve_static(full_path: str):
    file_path = BASE_DIR / full_path
    if file_path.exists() and file_path.is_file():
        return FileResponse(file_path)
    return FileResponse(BASE_DIR / 'index.html')
