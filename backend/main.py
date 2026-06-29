from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.sessions import SessionMiddleware
import uvicorn
import models
from auth.router import router as auth_router
from topics.router import router as topic_router
from exceptions.handler import register_exception_handlers
from config import env

app = FastAPI()

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
app.include_router(topic_router)

def main():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=(env.ENV == "dev")
    )

if __name__ == "__main__":
    main()
