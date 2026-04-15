def process_video(input_data):
    file_path = input_data.get("data", {}).get("file_path") \
        or input_data.get("data", {}).get("payload")

    return {
        "message": "Video processed successfully",
        "file_path": file_path
    }