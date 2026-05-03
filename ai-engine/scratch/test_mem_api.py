import requests

base_url = "http://localhost:8000"

context = {
    "user_id": "u1",
    "session_id": "s1",
    "domain": "blackops",
    "game_id": "g1",
    "trace_id": "t1",
    "feature_version": "v1",
    "pipeline_version": "v1"
}

req1 = {
    "job_id": "job1",
    "input_ref": "test_inline_1",
    "step": "embedding_generation",
    "input_type": "segment",
    "context": context
}

res1 = requests.post(f"{base_url}/ai/embedding-generation", json=req1)
out_ref = res1.json().get("output_ref")
print("Embedding out_ref:", out_ref)

if out_ref:
    req2 = {
        "job_id": "job2",
        "input_ref": out_ref,
        "step": "memory_retrieval",
        "input_type": "segment",
        "context": context
    }
    res2 = requests.post(f"{base_url}/ai/memory-retrieval", json=req2)
    print("Memory retrieval result:", res2.json())
