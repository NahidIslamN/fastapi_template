from db import Base
from sqlalchemy import Column, String, Integer, Boolean, ForeignKey, Table, DateTime, Text
from sqlalchemy.orm import relationship
from datetime import datetime




news_image_table = Table(
    "news_image_table",
    Base.metadata,
    Column("news_id", Integer, ForeignKey("news.id"), primary_key=True),
    Column("image_id", Integer, ForeignKey("news_images.id"), primary_key=True),
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(250), nullable=False)
    email = Column(String(250), nullable=False, unique=True)
    password_hash = Column(String(250), nullable=False)
    is_verified = Column(Boolean, default=False)
    otp = Column(String(8))
    image = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship("News", back_populates="user", cascade="all, delete-orphan")


class NewsImages(Base):
    __tablename__ = "news_images"

    id = Column(Integer, primary_key=True, index=True)
    news_image = Column(String, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)

    news = relationship(
        "News",
        secondary=news_image_table,
        back_populates="images"
    )


class News(Base):
    __tablename__ = "news"

    id = Column(Integer, primary_key=True, index=True)
    title = Column(String(250), nullable=False)
    description = Column(Text, nullable=True)
    user_id = Column(Integer, ForeignKey('users.id'), nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates='news')
    images = relationship(
        "NewsImages",
        secondary=news_image_table,
        back_populates="news",
        cascade="all, delete"
    )
