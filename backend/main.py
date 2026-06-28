from fastapi import FastAPI
import uvicorn
from config import env

app = FastAPI()

def main():
    uvicorn.run(
        app="main:app",
        host="0.0.0.0",
        port=8000,
        reload=(env.ENV == "dev")
    )

if __name__ == "__main__":
    main()
