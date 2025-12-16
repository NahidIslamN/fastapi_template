from fastapi import APIRouter, status, Depends, HTTPException, Form, UploadFile, File
import os
from apps.auth.serializers import (
    SignupRequest, 
    OtpVerificationRequest, 
    Signin_Request, 
    SigninResponse, 
    Forget_Request, 
    OtpVerificationResoponse, 
    ResetPasswordRequest,
    ChangePasswordRequest,
)

from db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from models import User
from core.base_auths import (
    get_current_user,
    get_password_hash,
    otp_varification,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_password
)


from apps.auth.tasks import send_code_to_email
from datetime import timedelta
auth_router = APIRouter(prefix='/api/auth', tags=['Authentication'])

from core.statics import UPLOAD_DIR, delete_user_image, generate_unique_hash
import random
import shutil
import os
import bcrypt

UPLOAD_DIR = UPLOAD_DIR + '/profiles'
os.makedirs(UPLOAD_DIR, exist_ok=True)


@auth_router.post("/signup")
async def signup(
    name: str = Form(...),
    email: str = Form(...),
    password: str = Form(...),
    image: UploadFile = File(None),
    db: AsyncSession = Depends(get_db)
):

    result = await db.execute(select(User).where(User.email == email))
    existing_user = result.scalar_one_or_none()

    if existing_user:
        if existing_user.is_verified == False:
            existing_user.name = name
            existing_user.password_hash = get_password_hash(password)
            if existing_user.image:
                await delete_user_image(existing_user.image)
            file_name = await generate_unique_hash(length=15)
            image_path = None
            if image:
                file_ext = os.path.splitext(image.filename)[1]
                image_path = os.path.join(UPLOAD_DIR, f"{file_name}{file_ext}")
                with open(image_path, "wb") as buffer:
                    shutil.copyfileobj(image.file, buffer)       
            existing_user.image = image_path
            await db.commit()
            await db.refresh(existing_user )
            # PROBLEM: send_code_to_email.delay() returns an AsyncResult object.
            # AsyncResult is NOT a coroutine and CANNOT be awaited.
            # Celery tasks are executed in a task queue, not as async functions.
            # When you call .delay(), the task is immediately queued and returns right away.
            # SOLUTION: Remove 'await' - just call .delay() and let Celery handle it asynchronously
            send_code_to_email.delay(email=existing_user.email)  # Fire and forget - task queued
            raise HTTPException(status_code=200, detail="User creted successfull!")
        raise HTTPException(status_code=400, detail="Email already registered")
    hashed_password = bcrypt.hashpw(password.encode(), bcrypt.gensalt()).decode()


    image_path = None
    if image:
        file_ext = os.path.splitext(image.filename)[1]
        image_path = os.path.join(UPLOAD_DIR, f"{await generate_unique_hash(length=15)}{file_ext}")
        with open(image_path, "wb") as buffer:
            shutil.copyfileobj(image.file, buffer)


    new_user = User(
        name=name,
        email=email,
        password_hash=hashed_password,
        image=image_path
    )


    send_code_to_email.delay(email=email)

    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return {
        "success":True,
        "message":"User creted successfull!"
    }
