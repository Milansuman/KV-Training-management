import logging

from fastapi import FastAPI
from fastapi.concurrency import asynccontextmanager
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
from middleware import configure_middleware
import models
from auth.router import router as auth_router
from topics.router import router as topic_router
from sessions.router import router as session_router
from exceptions.handler import register_exception_handlers
from user.router import router as user_router
from config import env
from programs.router import router as programs_router
from training_materials.router import router as training_material_router
from storage.minio import create_bucket_if_not_exists

logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s %(levelname)s %(name)s %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S"
)

@asynccontextmanager
async def lifespan(app: FastAPI):
    create_bucket_if_not_exists()

    yield

app = FastAPI(lifespan=lifespan)

    
configure_middleware(app)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_headers="*",
    allow_methods="*"
)

app.add_middleware(
    SessionMiddleware,
    secret_key=env.JWT_SECRET
)

register_exception_handlers(app)
app.include_router(auth_router)
app.include_router(user_router)
app.include_router(topic_router)
app.include_router(session_router)
app.include_router(programs_router)
app.include_router(training_material_router)

def main():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=(env.ENV == "dev")
    )

if __name__ == "__main__":
    main()
