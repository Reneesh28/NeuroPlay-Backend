from services.video.cv.frame_sampler import sample_frames
from services.video.cv.motion_detector import compute_motion_features
from services.video.cv.brightness_detector import compute_brightness_features
from services.video.cv.edge_detector import compute_edge_features
from services.video.cv.entropy_detector import compute_entropy_features


def extract_segment_features(cap, fps, segment):
    frames = sample_frames(
        cap,
        fps,
        segment["start_time_ms"],
        segment["end_time_ms"],
        sample_rate=1
    )

    motion = compute_motion_features(frames)
    brightness = compute_brightness_features(frames)
    edge = compute_edge_features(frames)
    entropy = compute_entropy_features(frames)

    return {
        **motion,
        **brightness,
        **edge,
        **entropy
    }


def enrich_segment_with_features(cap, fps, segment):
    features = extract_segment_features(cap, fps, segment)

    segment["input_data"]["player_state"] = features
    segment["processing"]["feature_extraction"] = "completed"

    return segment