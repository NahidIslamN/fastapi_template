from pydantic import BaseModel




class SignupRequest(BaseModel):
    name:str
    email:str
    password:str


class OtpVerificationRequest(BaseModel):
    email:str
    otp:str


class Signin_Request(BaseModel):
    email:str
    password:str


class Forget_Request(BaseModel):
    email:str


class UserOut(BaseModel):
    id:int
    name:str
    email:str
    
class SigninResponse(BaseModel):
    success:bool
    message:str
    access_token:str
    user:UserOut

class OtpVerificationResoponse(BaseModel):
    success:bool
    message:str
    access_token:str
    user:UserOut

class ResetPasswordRequest(BaseModel):
    new_password: str



class ChangePasswordRequest(BaseModel):
    old_password:str
    new_password:str