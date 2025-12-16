from fastapi import FastAPI
from apps.auth.views import auth_router
from fastapi.staticfiles import StaticFiles
import os
from core.statics import UPLOAD_DIR




app = FastAPI()


app.include_router(auth_router)


if not os.path.exists(UPLOAD_DIR):
    os.makedirs(UPLOAD_DIR, exist_ok=True)
app.mount("/uploads", StaticFiles(directory=UPLOAD_DIR), name="uploads")