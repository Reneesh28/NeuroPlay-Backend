from pathlib import Path


def scan_dataset(root_path: str):
    root = Path(root_path)

    if not root.exists():
        raise ValueError(f"Dataset path not found: {root_path}")

    dataset = []

    # Only scan ONE level (flat structure)
    for folder in root.iterdir():
        if not folder.is_dir():
            continue

        videos = list(folder.glob("*.mp4"))

        if not videos:
            continue

        dataset.append({
            "folder_name": folder.name,
            "folder_path": str(folder),
            "videos": [str(v) for v in videos]
        })

    return dataset