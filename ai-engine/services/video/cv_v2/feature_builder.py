import numpy as np
import cv2
from .frame_sampler import sample_frames


def safe(val):
    if val is None or np.isnan(val):
        return 0.0
    return float(val)


def compute_basic_features(frames):
    if len(frames) < 2:
        return [0.0] * 20

    motion_vals = []
    brightness_vals = []
    edge_vals = []
    entropy_vals = []

    prev_gray = None

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        # brightness
        brightness_vals.append(np.mean(gray))

        # edges
        edges = cv2.Canny(gray, 100, 200)
        edge_vals.append(np.mean(edges) / 255.0)

        # entropy
        hist = cv2.calcHist([gray], [0], None, [256], [0, 256])
        hist_norm = hist / hist.sum()
        entropy = -np.sum(hist_norm * np.log2(hist_norm + 1e-7))
        entropy_vals.append(entropy)

        # motion
        if prev_gray is not None:
            diff = cv2.absdiff(prev_gray, gray)
            motion_vals.append(np.mean(diff) / 255.0)

        prev_gray = gray

    # aggregate
    features = [
        safe(np.mean(motion_vals)),
        safe(np.std(motion_vals)),
        safe(np.max(motion_vals)),
        safe(len([m for m in motion_vals if m > 0.2]) / len(motion_vals)) if motion_vals else 0,

        safe(np.mean(brightness_vals)),
        safe(np.std(brightness_vals)),
        safe(np.max(brightness_vals)),
        safe(np.min(brightness_vals)),

        safe(np.mean(edge_vals)),
        safe(np.std(edge_vals)),
        safe(np.max(edge_vals)),
        safe(np.min(edge_vals)),

        safe(np.mean(entropy_vals)),
        safe(np.std(entropy_vals)),
        safe(np.max(entropy_vals)),
        safe(np.min(entropy_vals)),
    ]

    # pad to 20
    while len(features) < 20:
        features.append(0.0)

    return features[:20]


def extract_ml_input(cap, fps, start_ms, end_ms):
    frames = sample_frames(cap, fps, start_ms, end_ms)

    if not frames:
        return [0.0] * 20

    features = compute_basic_features(frames)

    return features