import cv2
import numpy as np


def compute_brightness_features(frames, flash_threshold=40):
    """
    Compute brightness average and flash count from frames
    """

    if not frames:
        return {
            "brightness_avg": 0.0,
            "flash_count": 0
        }

    brightness_values = []

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        brightness = np.mean(gray)
        brightness_values.append(brightness)

    brightness_avg = float(np.mean(brightness_values))

    # Detect flashes (sudden brightness jumps)
    flash_count = 0

    for i in range(1, len(brightness_values)):
        diff = abs(brightness_values[i] - brightness_values[i - 1])
        if diff > flash_threshold:
            flash_count += 1

    return {
        "brightness_avg": brightness_avg / 255.0,  # normalize
        "flash_count": flash_count
    }