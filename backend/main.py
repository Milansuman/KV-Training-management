from fastapi import FastAPI
import uvicorn

from auth.router import router as auth_router
from exceptions.handler import register_exception_handlers
from config import env

app = FastAPI()
register_exception_handlers(app)
app.include_router(auth_router)

def main():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=(env.ENV == "dev")
    )

if __name__ == "__main__":
    main()
