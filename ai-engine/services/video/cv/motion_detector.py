import cv2
import numpy as np


def compute_motion_features(frames):
    """
    Compute motion intensity and variance from sampled frames
    """

    if len(frames) < 2:
        return {
            "motion_intensity": 0.0,
            "motion_variance": 0.0
        }

    diffs = []

    prev_gray = cv2.cvtColor(frames[0], cv2.COLOR_BGR2GRAY)

    for i in range(1, len(frames)):
        curr_gray = cv2.cvtColor(frames[i], cv2.COLOR_BGR2GRAY)

        diff = cv2.absdiff(prev_gray, curr_gray)

        # Normalize motion score
        motion_score = np.mean(diff) / 255.0
        diffs.append(motion_score)

        prev_gray = curr_gray

    motion_intensity = float(np.mean(diffs))
    motion_variance = float(np.var(diffs))

    return {
        "motion_intensity": motion_intensity,
        "motion_variance": motion_variance
    }