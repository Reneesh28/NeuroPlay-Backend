import cv2
import numpy as np


def compute_edge_features(frames):
    """
    Compute edge density (scene complexity) from frames
    """

    if not frames:
        return {
            "edge_density_avg": 0.0
        }

    densities = []

    for frame in frames:
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)

        edges = cv2.Canny(gray, threshold1=50, threshold2=150)

        edge_pixels = np.sum(edges > 0)
        total_pixels = edges.size

        density = edge_pixels / total_pixels
        densities.append(density)

    return {
        "edge_density_avg": float(np.mean(densities))
    }