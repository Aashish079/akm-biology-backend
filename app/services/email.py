from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from app.core.config import settings
from pydantic import EmailStr
from typing import List

conf = ConnectionConfig(
    MAIL_USERNAME=settings.mail_username,
    MAIL_PASSWORD=settings.mail_password,
    MAIL_FROM=settings.mail_from,
    MAIL_PORT=settings.mail_port,
    MAIL_SERVER=settings.mail_server,
    MAIL_FROM_NAME=settings.mail_from_name,
    MAIL_STARTTLS=settings.mail_starttls,
    MAIL_SSL_TLS=settings.mail_ssl_tls,
    USE_CREDENTIALS=settings.use_credentials,
    VALIDATE_CERTS=settings.validate_certs
)

async def send_email(subject: str, recipients: List[EmailStr], body: str):
    message = MessageSchema(
        subject=subject,
        recipients=recipients,
        body=body,
        subtype=MessageType.html
    )
    
    fm = FastMail(conf)
    await fm.send_message(message)

async def send_welcome_email(email: EmailStr, password: str):
    body = f"""
    <h1>Welcome to AKM SIR BIOLOGY</h1>
    <p>Your account has been approved.</p>
    <p><b>Username:</b> {email}</p>
    <p><b>Temporary Password:</b> {password}</p>
    <p>Please login and change your password immediately.</p>
    """
    try:
        await send_email("Account Approved - Credentials", [email], body)
    except Exception as e:
        print(f"FAILED TO SEND EMAIL: {e}")
