from fastapi import Request, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.db import get_db
from core.models import User
import jwt
from decouple import config

SECRET_KEY = config("JWT_SECRET")
ALGORITHM = "HS256"


class AuthMiddleware:
    async def __call__(self, request: Request, call_next):
        request.state.user = None

        auth = request.headers.get("Authorization")
        if not auth or not auth.startswith("Bearer "):
            return await call_next(request)

        token = auth.replace("Bearer ", "").strip()

        try:
            payload = jwt.decode(
                token,
                SECRET_KEY,
                algorithms=[ALGORITHM],
            )

            user_id = payload.get("sub")
            if not user_id:
                return await call_next(request)

            async for db in get_db():
                result = await db.execute(
                    select(User).where(User.id == user_id)
                )
                user = result.scalar_one_or_none()

                if user and user.is_active:
                    request.state.user = user

        except jwt.ExpiredSignatureError:
            pass
        except jwt.InvalidTokenError:
            pass

        return await call_next(request)
