from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker, declarative_base
from decouple import config

DATABASE_URL = config('DATABASE_URL') #"sqlite+aiosqlite:///./main_db.sqlite3"

# Async SQLite engine
engine = create_async_engine(
    DATABASE_URL,
    echo=True,                 # change to False in production
    future=True
)

# Async Session
AsyncSessionLocal = sessionmaker(
    bind=engine,
    class_=AsyncSession,
    expire_on_commit=False,
    autoflush=False
)

# Model Base
Base = declarative_base()

# FastAPI DB dependency
async def get_db():
    async with AsyncSessionLocal() as session:
        yield session


