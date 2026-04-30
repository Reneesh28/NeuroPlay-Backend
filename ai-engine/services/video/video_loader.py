import cv2


def load_video(video_path: str):
    cap = cv2.VideoCapture(video_path)

    if not cap.isOpened():
        raise ValueError(f"❌ Cannot open video: {video_path}")

    fps = cap.get(cv2.CAP_PROP_FPS)

    # fallback FPS
    if fps == 0 or fps is None:
        fps = 30

    total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
    duration_sec = total_frames / fps if fps else 0

    return {
        "cap": cap,
        "fps": fps,
        "total_frames": total_frames,
        "duration_sec": duration_sec
    }


def release_video(cap):
    if cap:
        cap.release()