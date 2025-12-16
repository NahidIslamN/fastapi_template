
from datetime import datetime, timedelta
from typing import Optional
import bcrypt
from datetime import timedelta

from jose import jwt, JWTError

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from core.config import settings
from models import User
from db import get_db


oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/auth/login")


def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against a hashed password."""
    return bcrypt.checkpw(plain_password.encode('utf-8'), hashed_password.encode('utf-8'))

def get_password_hash(password: str) -> str:
    """Hash a password using bcrypt."""
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')


from datetime import datetime, timedelta
from typing import Optional
from jose import jwt
from core.config import settings


def _create_token(subject: str, expires_delta: timedelta, token_type: str):
    expire = datetime.utcnow() + expires_delta

    to_encode = {
        "sub": subject,
        "exp": expire,
        "type": token_type  # access / refresh
    }

    return jwt.encode(
        to_encode,
        settings.JWT_SECRET,
        algorithm=settings.JWT_ALGORITHM
    )


def create_access_token(subject: str, expires_delta:timedelta = timedelta(days=30)):
    return _create_token(
        subject=subject,
        expires_delta=expires_delta,
        token_type="access"
    )


def create_refresh_token(subject: str, expires_delta:timedelta = timedelta(days=90)):
    return _create_token(
        subject=subject,
        expires_delta=expires_delta,
        token_type="refresh"
    )


async def get_user_by_email(db: AsyncSession, email: str):
    q = await db.execute(select(User).where(User.email == email))
    return q.scalars().first()

async def get_user_by_id(db:AsyncSession, id:int):
    q = await db.execute(select(User).where(User.id == id))
    return q.scalars().first()



async def authenticate_user(db: AsyncSession, email: str, password: str):
    user = await get_user_by_email(db, email)
    if not user or not verify_password(password, user.password_hash):
        return None
    return user


async def get_current_user(
    token: str = Depends(oauth2_scheme),
    db: AsyncSession = Depends(get_db)
):
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )

    try:
        payload = jwt.decode(
            token,
            settings.JWT_SECRET,
            algorithms=[settings.JWT_ALGORITHM]
        )

        sub = payload.get("sub")
        token_type = payload.get("type")

        if sub is None or token_type != "access":
            raise credentials_exception

        user_id = int(sub)

    except (JWTError, ValueError):
        raise credentials_exception

    user = await get_user_by_id(db=db, id=user_id)
    if not user:
        raise credentials_exception

    return user



async def otp_varification(db: AsyncSession, email: str, otp: str):
    user = await get_user_by_email(db, email)
    if not user:
        return None

    if user.otp == otp:
        user.otp = None
        await db.commit()
        await db.refresh(user)
        return user    
    else:
        return False