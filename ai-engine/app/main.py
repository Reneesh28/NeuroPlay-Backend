from fastapi import FastAPI
from app.api.routes import router
from app.database.mongo_client import client  # import triggers connection

app = FastAPI()

@app.on_event("startup")
def startup_event():
    print("🚀 FastAPI starting...")
    try:
        # Force connection check
        client.admin.command("ping")
        print("✅ MongoDB Connected")
    except Exception as e:
        print("❌ MongoDB Connection Failed:", e)

app.include_router(router)