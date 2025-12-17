from celery_app import celery_app
from core.email_utils import send_verification_code_email
from core.db import AsyncSessionLocal  # Import the session factory directly instead of get_db
import asyncio

@celery_app.task(bind=True)
def send_code_to_email(self, email: str):
    """
    Celery task to send verification code email.
    
    PROBLEM: get_db() is an async generator (yield), not an async context manager.
    Async generators don't support 'async with' protocol - they need to be iterated,
    not used with the 'async with' statement.
    
    SOLUTION: Use AsyncSessionLocal directly which is the sessionmaker.
    AsyncSessionLocal() creates a proper async context manager that works with 'async with'.
    """
    async def _send():
        # Create async session using sessionmaker (proper async context manager)
        async with AsyncSessionLocal() as db:
            await send_verification_code_email(to_email=email, db=db)

    # asyncio.run() runs the async function in a new event loop
    # This is needed because Celery is a synchronous task queue by default
    asyncio.run(_send())
