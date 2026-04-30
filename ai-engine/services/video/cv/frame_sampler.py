import cv2

def sample_frames(cap, fps, start_time_ms, end_time_ms, sample_rate=1):
    """
    Sample frames from a video capture object between start and end time.

    Args:
        cap: OpenCV VideoCapture object
        fps: frames per second
        start_time_ms: segment start time
        end_time_ms: segment end time
        sample_rate: frames per second to sample (default = 1 FPS)

    Returns:
        List of frames (numpy arrays)
    """

    frames = []

    # Convert ms → frame index
    start_frame = int((start_time_ms / 1000) * fps)
    end_frame = int((end_time_ms / 1000) * fps)

    # Step size (frames to skip)
    step = int(fps / sample_rate)

    # Move pointer to start frame
    cap.set(cv2.CAP_PROP_POS_FRAMES, start_frame)

    current_frame = start_frame

    while current_frame < end_frame:
        ret, frame = cap.read()

        if not ret:
            break

        frames.append(frame)

        # Skip frames to maintain sampling rate
        current_frame += step
        cap.set(cv2.CAP_PROP_POS_FRAMES, current_frame)

    return frames