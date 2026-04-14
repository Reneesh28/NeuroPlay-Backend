import os
from fastapi import FastAPI
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "port": os.getenv("PORT")
    }