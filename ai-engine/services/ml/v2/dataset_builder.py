import os
import numpy as np
from tqdm import tqdm
from sklearn.preprocessing import MinMaxScaler
import joblib
from dotenv import load_dotenv
from pymongo import MongoClient

# ==============================
# ENV
# ==============================
load_dotenv()

MONGO_URI = os.getenv("MONGO_URI")
DB_NAME = os.getenv("DB_NAME")

# ==============================
# PATHS
# ==============================
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, "../../"))

DATA_DIR = os.path.join(ROOT_DIR, "data", "v2")
MODEL_DIR = os.path.join(ROOT_DIR, "models", "v2")

os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(MODEL_DIR, exist_ok=True)

# ==============================
# DB
# ==============================
client = MongoClient(MONGO_URI)
db = client[DB_NAME]
collection = db["segments"]

# ==============================
# FETCH SEGMENTS
# ==============================
def get_segments_by_domain():
    domains = collection.distinct("domain")
    grouped = {}

    for d in domains:
        segments = list(collection.find({
            "domain": d,
            "input_data": {"$exists": True}
        }).sort("sequence_number", 1))

        grouped[d] = segments

    return grouped


# ==============================
# FEATURE ENGINEERING (20D)
# ==============================
def build_feature_vector(seg, prev_seg=None):
    ps = seg.get("input_data", {}).get("player_state", {})

    motion = ps.get("motion_intensity", 0)
    variance = ps.get("motion_variance", 0)
    brightness = ps.get("brightness_avg", 0)
    flash = ps.get("flash_count", 0)
    edge = ps.get("edge_density_avg", 0)
    entropy = ps.get("entropy_avg", 0)

    features = [
        motion, variance, brightness, flash, edge, entropy,
        motion / (variance + 1e-5),
        1 / (variance + 1e-5),
        brightness * edge,
        entropy * motion,
        flash / 5.0,
        motion * brightness,
        edge * entropy,
        motion * entropy,
        motion ** 2,
        entropy ** 2,
    ]

    if prev_seg:
        prev_ps = prev_seg.get("input_data", {}).get("player_state", {})
        features.extend([
            motion - prev_ps.get("motion_intensity", 0),
            entropy - prev_ps.get("entropy_avg", 0)
        ])
    else:
        features.extend([0, 0])

    if len(features) < 20:
        features.extend([0] * (20 - len(features)))
    else:
        features = features[:20]

    return features


# ==============================
# MAIN BUILDER
# ==============================
def build_dataset():
    grouped = get_segments_by_domain()

    for domain, segments in grouped.items():
        print(f"\n🚀 Processing domain: {domain}")
        print(f"Segments: {len(segments)}")

        raw_features = []
        valid_segment_ids = []

        prev_seg = None

        for seg in tqdm(segments):
            try:
                features = build_feature_vector(seg, prev_seg)

                # Optional noise filtering
                if features[0] < 0.001 and features[5] < 0.1:
                    continue

                raw_features.append(features)
                valid_segment_ids.append(str(seg["_id"]))

                prev_seg = seg

            except Exception as e:
                print("⚠️ Skipping:", e)
                continue

        raw_features = np.array(raw_features)

        if len(raw_features) == 0:
            print("❌ No valid data")
            continue

        print("📊 Raw shape:", raw_features.shape)

        # ==============================
        # NORMALIZATION
        # ==============================
        scaler = MinMaxScaler()
        normalized = scaler.fit_transform(raw_features)

        # ==============================
        # SAVE
        # ==============================
        dataset_path = os.path.join(DATA_DIR, f"dataset_{domain}.npy")
        scaler_path = os.path.join(MODEL_DIR, f"scaler_{domain}.pkl")
        ids_path = os.path.join(DATA_DIR, f"segment_ids_{domain}.npy")

        np.save(dataset_path, normalized)
        joblib.dump(scaler, scaler_path)
        np.save(ids_path, np.array(valid_segment_ids))

        print(f"💾 Dataset → {dataset_path}")
        print(f"💾 Scaler → {scaler_path}")
        print(f"💾 Segment IDs → {ids_path}")


# ==============================
# RUN
# ==============================
if __name__ == "__main__":
    build_dataset()