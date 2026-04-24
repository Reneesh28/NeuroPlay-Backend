def process_video(input_ref: str, context: dict):
    domain = context.get("domain", "unknown")
    
    return {
        "output_ref": f"{input_ref}_video_out" if input_ref else "new_video_out",
        "message": f"Video processed successfully for domain {domain}"
    }