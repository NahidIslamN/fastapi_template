
from pydantic import  EmailStr
from pydantic_settings import BaseSettings



REDIS_BROKER_URL = "redis://localhost:6379/0"
REDIS_BACKEND_URL = "redis://localhost:6379/1"



class Settings(BaseSettings):
    DATABASE_URL: str
    JWT_SECRET: str
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_DAYS: int = 1
    REFRESH_TOKEN_EXPIRE_DAYS:int = 30
    SMTP_HOST: str
    SMTP_PORT: int
    SMTP_USER: str
    SMTP_PASS: str
    EMAIL_FROM: EmailStr

    class Config:
        env_file = ".env"

settings = Settings()
