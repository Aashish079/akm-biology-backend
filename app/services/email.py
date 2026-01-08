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

async def send_registration_received_email(email: EmailStr, name: str):
    body = f"""
    <h1>Registration Received</h1>
    <p>Dear {name},</p>
    <p>Thank you for registering with AKM SIR BIOLOGY.</p>
    <p>We have received your registration and payment proof. An admin will verify your details shortly.</p>
    <p>You will receive another email with your login credentials once approved.</p>
    """
    try:
        await send_email("Registration Received - AKM SIR BIOLOGY", [email], body)
    except Exception as e:
        print(f"FAILED TO SEND EMAIL: {e}")

async def send_rejection_email(email: EmailStr, reason: str = ""):
    body = f"""
    <h1>Registration Update</h1>
    <p>Your registration for AKM SIR BIOLOGY was not approved.</p>
    <p><b>Reason:</b> {reason or 'Verification failed'}</p>
    <p>Please contact support or try registering again with correct details.</p>
    """
    try:
        await send_email("Registration Update - Action Required", [email], body)
    except Exception as e:
        print(f"FAILED TO SEND EMAIL: {e}")
