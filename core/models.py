from core.db import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, DateTime,  Date, Time, Float
from sqlalchemy.orm import relationship
from datetime import datetime

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Enum
from datetime import datetime
import enum


class UserRole(enum.Enum):
    admin = "admin"
    cruise_sales = "user_01"
    booking_operator = "user_02"
    direct_sales = "user_3"




class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    first_name = Column(String(250))
    last_name = Column(String(250))
    name = Column(String(250), nullable=False)
    username = Column(String(250), unique=True)
    email = Column(String(250), nullable=False, unique=True)
    password_hash = Column(String(250), nullable=False)
    is_verified = Column(Boolean, default=False)
    is_admin = Column(Boolean, default=False)
    is_active = Column(Boolean, default=True)
    is_staff = Column(Boolean, default=False)
    user_role = Column(Enum(UserRole), nullable=True, default=UserRole.direct_sales)
    otp = Column(String(8))
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
