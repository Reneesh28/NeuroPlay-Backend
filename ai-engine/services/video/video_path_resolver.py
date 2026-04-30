import os

# 🔧 UPDATE THIS PATH
BASE_DATASET_PATH = r"C:\Users\Bloodblade\Desktop\PROJECTS\COD DATASET\processed_videos"


def resolve_video_path(domain: str, video_file: str) -> str:
    return os.path.join(BASE_DATASET_PATH, domain, video_file)