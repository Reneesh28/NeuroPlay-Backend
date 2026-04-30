import cv2
import numpy as np


def compute_entropy_features(frames):
    if not frames:
        return {
            "entropy_avg": 0.0
        }

    entropies = []

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        hist = cv2.calcHist([gray], [0], None, [256], [0, 256]).ravel()
        prob = hist / np.sum(hist)
        prob = prob[prob > 0]

        entropy = -np.sum(prob * np.log2(prob))
        entropies.append(entropy)

    return {
        "entropy_avg": float(np.mean(entropies) / 8.0)
    }