import math
from uuid import uuid4
from datetime import datetime


SEGMENT_DURATION_SEC = 5


def generate_segments(video_meta, context, user_id="system_user"):
    fps = round(video_meta["fps"])
    total_frames = video_meta["total_frames"]

    frames_per_segment = int(fps * SEGMENT_DURATION_SEC)
    total_segments = math.ceil(total_frames / frames_per_segment)

    session_id = str(uuid4())

    segments = []

    for i in range(total_segments):
        start_frame = i * frames_per_segment
        end_frame = min((i + 1) * frames_per_segment, total_frames)

        start_time_ms = int((start_frame / fps) * 1000)
        end_time_ms = int((end_frame / fps) * 1000)

        segment = {
            "user_id": user_id,
            "session_id": session_id,

            "domain": context["domain"],
            "game_id": context["game_id"],

            "sequence_number": i,

            "start_time_ms": start_time_ms,
            "end_time_ms": end_time_ms,

            "input_data": {
                "events": [],
                "player_state": {},
                "timestamp": start_time_ms
            },

            "processing": {
                "feature_extraction": "pending",
                "embedding": "pending"
            },

            "created_at": datetime.utcnow()
        }

        segments.append(segment)

    return segments