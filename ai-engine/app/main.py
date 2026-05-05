from fastapi import FastAPI
from app.api.routes import router
from app.database.mongo_client import client
from app.core.error_classifier import global_exception_handler

app = FastAPI()

app.add_exception_handler(Exception, global_exception_handler)

@app.on_event("startup")
def startup_event():
    print("🚀 FastAPI starting...")
    try:
        client.admin.command("ping")
        print("✅ MongoDB Connected")
    except Exception as e:
        print("❌ MongoDB Connection Failed:", e)

# 🔥 SINGLE PREFIX POINT
app.include_router(router, prefix="/ai")