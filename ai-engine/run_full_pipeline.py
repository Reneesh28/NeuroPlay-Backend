from services.video.dataset_scanner import scan_dataset
from services.video.game_resolver import resolve_game_context
from services.video.video_loader import load_video, release_video
from services.video.segment_generator import generate_segments
from services.video.cv.cv_pipeline import enrich_segment_with_features

from services.db.segment_repository import insert_segments_batch, BATCH_SIZE


# 🔧 UPDATE IF NEEDED
DATASET_PATH = r"C:\Users\Bloodblade\Desktop\PROJECTS\COD DATASET\processed_videos"


def run_pipeline():
    dataset = scan_dataset(DATASET_PATH)

    total_videos = 0
    total_segments = 0

    for item in dataset:
        print("\n" + "=" * 60)
        print(f"📁 Folder: {item['folder_name']}")

        try:
            context = resolve_game_context(item["folder_name"])
        except Exception as e:
            print("❌ Skipping folder:", e)
            continue

        # 🔥 PROCESS ALL VIDEOS
        for video_path in item["videos"]:
            print(f"\n🎥 Processing video: {video_path}")

            try:
                video = load_video(video_path)
            except Exception as e:
                print("❌ Failed to load video:", e)
                continue

            fps = round(video["fps"])

            segments = generate_segments(video, context)

            batch = []

            for i, segment in enumerate(segments):
                enriched = enrich_segment_with_features(
                    video["cap"],
                    fps,
                    segment
                )

                batch.append(enriched)

                # 🔥 BATCH INSERT
                if len(batch) >= BATCH_SIZE:
                    insert_segments_batch(batch)
                    total_segments += len(batch)

                    print(f"📦 Inserted batch of {len(batch)}")
                    batch.clear()

            # 🔥 INSERT REMAINING
            if batch:
                insert_segments_batch(batch)
                total_segments += len(batch)

                print(f"📦 Inserted final batch of {len(batch)}")

            # Release video resource
            release_video(video["cap"])

            total_videos += 1

            print(f"✅ Completed video | Total segments so far: {total_segments}")

    print("\n" + "=" * 60)
    print("🚀 PIPELINE COMPLETE")
    print(f"🎥 Total Videos: {total_videos}")
    print(f"📦 Total Segments Inserted: {total_segments}")
    print("=" * 60)


if __name__ == "__main__":
    run_pipeline()