from fastapi import APIRouter, status, Depends, HTTPException, Form, UploadFile, File, Response, Request
import os
from core.permissions import IsAuthenticated, IsAdmin
from apps.auth.serializers import (
    OtpVerificationRequest, 
    Signin_Request, 
    SigninResponse, 
    Forget_Request, 
    OtpVerificationResoponse, 
    ResetPasswordRequest,
    ChangePasswordRequest,
)
from core.config import settings

from core.db import get_db
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from core.models import User
from core.base_auths import (
    get_password_hash,
    otp_varification,
    authenticate_user,
    create_access_token,
    create_refresh_token,
    verify_password,
    get_user_by_id,
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
            if existing_user.image and image is not None:
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
            send_code_to_email.delay(email=existing_user.email) 
            return {
                "success":True,
                "message":"User creted successfull!"
            }
        
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


@auth_router.post('/email-varification/', status_code=status.HTTP_200_OK )
async def email_verification(vf_data:OtpVerificationRequest, db:AsyncSession=Depends(get_db)):

    user = await otp_varification(db=db, email=vf_data.email, otp=vf_data.otp )
    if user == None:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="user not found with this email !")
    if user == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong verification code !")
    
    if user:
        user.is_verified = True
        await db.commit()
        await db.refresh(user)
        return {
            "success":True,
            "message":"Verification Successsfull!"
        }
    else:
        pass




@auth_router.post('/signin/', status_code=status.HTTP_200_OK, response_model=SigninResponse)
async def user_signin(signin_data: Signin_Request, response: Response, db: AsyncSession = Depends(get_db)):

    user = await authenticate_user(db=db, email=signin_data.email, password=signin_data.password)
    
    if user is not None and user.is_verified:
        access_token = create_access_token(subject=str(user.id))
        refresh_token = create_refresh_token(subject=str(user.id))
        
        response.set_cookie(
            key="refresh_token",
            value=refresh_token,
            httponly=True,            
            samesite="strict",        
            secure=True,              
            max_age=60*60*24*settings.REFRESH_TOKEN_EXPIRE_DAYS
        )

        return {
            "success": True,
            "message": "Login Success!",
            "access_token": access_token,
            "user": user
        }
    
    elif user is not None and not user.is_verified:
        send_code_to_email.delay(email=user.email)
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Check your email and get verified first!")
    
    else:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Email or password is invalid!")


@auth_router.post('/forget-password/', status_code=status.HTTP_200_OK)
async def forget_password(forget_pass:Forget_Request):

    send_code_to_email.delay(email=forget_pass.email)
    return {
        "message":"An otp sent to your email. verify and reset your password"
    }



@auth_router.post('/otp-varification/', status_code=status.HTTP_200_OK, response_model=OtpVerificationResoponse)
async def otp_verification(vf_data:OtpVerificationRequest, db:AsyncSession=Depends(get_db)):
    user = await otp_varification(db=db, email=vf_data.email, otp=vf_data.otp )
    if user == None:
        raise HTTPException(status_code=status.HTTP_200_OK, detail="user not found with this email !")
    if user == False:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail="Wrong verification code !")
    
    if user:
        access_token = create_access_token(subject=str(user.id), expires_delta=timedelta(minutes=5))
        
        return{
            "success":True,
            "message":"reset your passwor before 5 munite!",
            "access_token":access_token,
            "user":user
        }
    else:
        pass



@auth_router.post('/reset_passsword/', status_code=status.HTTP_200_OK)
async def reset_password(
    reset_data: ResetPasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(IsAuthenticated),
    
    ):
    user = await get_user_by_id(db=db, id=request.state.user.id)
   
    user.password_hash = get_password_hash(reset_data.new_password)
    await db.commit()
    return {
        "success": True,
        "message": "Password reset successfully!",
    }

@auth_router.post("/chage_password/", status_code=status.HTTP_200_OK)
async def change_password(
    change_data: ChangePasswordRequest,
    request: Request,
    db: AsyncSession = Depends(get_db),
    _: None = Depends(IsAdmin),
):
    user = await get_user_by_id(db=db, id=request.state.user.id)

    is_valid_pass = verify_password(
        plain_password=change_data.old_password,
        hashed_password=user.password_hash,
    )

    if not is_valid_pass:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Wrong old password!",
        )

    user.password_hash = get_password_hash(change_data.new_password)

    await db.commit()

    return {
        "success": True,
        "message": "Password Change Successful",
    }

