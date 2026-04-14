import os
from fastapi import FastAPI
from pydantic import BaseModel
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()


# -------------------------
# Request Schema
# -------------------------
class ExecuteRequest(BaseModel):
    job_id: str
    step: str
    input_data: dict = {}


# -------------------------
# Health Check
# -------------------------
@app.get("/health")
def health():
    return {
        "status": "ok",
        "service": "ai-engine",
        "port": os.getenv("PORT")
    }


# -------------------------
# AI Execution Endpoint
# -------------------------
@app.post("/ai/execute")
async def execute_ai(req: ExecuteRequest):
    print(f"🧠 AI Executing Step: {req.step} for Job: {req.job_id}")

    # 🔥 Placeholder logic (replace later with real AI)
    return {
        "success": True,
        "step": req.step,
        "output": {
            "message": f"Processed {req.step}",
        }
    }