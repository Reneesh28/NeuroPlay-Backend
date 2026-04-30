import cv2


def sample_frames(cap, fps, start_ms, end_ms, sample_rate=2):
    """
    Extract frames between start and end (ms)
    sample_rate = frames per second
    """
    frames = []

    start_frame = int((start_ms / 1000) * fps)
    end_frame = int((end_ms / 1000) * fps)

    step = max(1, int(fps / sample_rate))

    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    for i in range(start_frame, end_frame, step):
        ret, frame = cap.read()
        if not ret:
            break
        frames.append(frame)

    return frames