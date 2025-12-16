
import aiosmtplib
from email.message import EmailMessage
from datetime import timedelta
from core.config import settings
import random
from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import Depends, HTTPException
from sqlalchemy import select
from models import User
from pydantic import BaseModel


class EmailVarification(BaseModel):
    email: str
    code: str


async def send_verification_code_email(to_email: str, db):
    code = random.randint(100000, 999999)
    verification_code = f"{code}"
    msg = EmailMessage()
    msg["From"] = settings.EMAIL_FROM
    msg["To"] = to_email
    msg["Subject"] = "Verify your email"
    msg.set_content(f"Your email varification code: {verification_code}")

    user = await db.execute(
        select(User).where(User.email == to_email)
    )
  
    
    users = user.scalar_one_or_none()
    if users is None:
        raise HTTPException(
            status_code=400,
            detail= "user not found with this email!"
        )

    users.otp = verification_code
    await db.commit()
    await db.refresh(users)

    await aiosmtplib.send(
        msg,
        hostname=settings.SMTP_HOST,
        port=settings.SMTP_PORT,
        username=settings.SMTP_USER,
        password=settings.SMTP_PASS,
        start_tls=True,
    )
    


