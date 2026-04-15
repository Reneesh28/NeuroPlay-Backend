import time
from app.processors.video_processor import process_video
from app.processors.feature_processor import process_feature 
from app.processors.embedding_processor import process_embedding
from app.processors.clustering_processor import process_clustering
from app.processors.simulation_processor import process_simulation

def execute_step(req):
    start = time.time()

    if req.step == "video_processing":
        result = process_video(req.input)

    elif req.step == "feature_extraction":   # 🔥 FIX
        result = process_feature(req.input)
    
    elif req.step == "embedding_generation":
        result = process_embedding(req.input)

    elif req.step == "clustering":
        result = process_clustering(req.input)

    elif req.step == "simulation":
        result = process_simulation(req.input)

    else:
        raise Exception(f"Unknown step: {req.step}")

    execution_time = int((time.time() - start) * 1000)

    return {
        "success": True,
        "step": req.step,
        "data": result,
        "meta": {
            "execution_time": execution_time
        }
    }