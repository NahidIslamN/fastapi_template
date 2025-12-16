import os
import asyncio
import uuid
import base64


UPLOAD_DIR = "uploads"

async def delete_user_image(image_path: str):
    if image_path and os.path.exists(image_path):
        await asyncio.to_thread(os.remove, image_path)


async def generate_unique_hash(length=15):
    
    random_uuid = uuid.uuid4().bytes
    
    hash_code = base64.urlsafe_b64encode(random_uuid).decode('utf-8')
    
    return hash_code.replace("=", "")[:length]