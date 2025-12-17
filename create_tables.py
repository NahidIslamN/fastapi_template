
import asyncio
from core.db import engine, Base
import core.models as models 

async def init_models():
    async with engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

asyncio.run(init_models())
print("Tables created successfully!")

