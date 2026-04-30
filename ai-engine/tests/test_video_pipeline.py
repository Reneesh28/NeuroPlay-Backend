from services.video.dataset_scanner import scan_dataset
from services.video.game_resolver import resolve_game_context
from services.video.video_loader import load_video, release_video
from services.video.segment_generator import generate_segments
from services.video.cv.cv_pipeline import enrich_segment_with_features


# 🔧 UPDATE THIS PATH IF NEEDED
DATASET_PATH = r"C:\Users\Bloodblade\Desktop\PROJECTS\COD DATASET\processed_videos"


def run_test_pipeline():
    dataset = scan_dataset(DATASET_PATH)

    total_videos = 0
    total_segments = 0

    for item in dataset:
        print("\n" + "=" * 60)
        print("📁 Folder:", item["folder_name"])

        try:
            context = resolve_game_context(item["folder_name"])
            print("🎮 Game Context:", context)
        except Exception as e:
            print("❌ Skipping folder due to error:", e)
            continue

        # 🔥 PROCESS ALL VIDEOS IN FOLDER
        for video_path in item["videos"]:
            print("\n🎥 Video:", video_path)

            try:
                video = load_video(video_path)
            except Exception as e:
                print("❌ Failed to load video:", e)
                continue

            fps = round(video["fps"])

            print(f"⚙️ FPS: {fps}")
            print(f"⏱ Duration: {video['duration_sec']:.2f} sec")

            # 🔥 SEGMENT GENERATION
            segments = generate_segments(video, context)
            print("📦 Total Segments:", len(segments))

            # 🔥 ENRICH ALL SEGMENTS
            for i, segment in enumerate(segments):
                enriched_segment = enrich_segment_with_features(
                    video["cap"],
                    fps,
                    segment
                )
                segments[i] = enriched_segment

            # ✅ DEBUG SAMPLE (ONLY PRINT FIRST)
            print("\n🧠 Sample Enriched Player State:")
            print(segments[0]["input_data"]["player_state"])

            # Debug preview
            print("\n🟢 First Segment:", segments[0])
            print("🔴 Last Segment:", segments[-1])

            total_videos += 1
            total_segments += len(segments)

            # Always release resource
            release_video(video["cap"])

    print("\n" + "=" * 60)
    print("✅ FINAL SUMMARY")
    print(f"🎥 Total Videos Processed: {total_videos}")
    print(f"📦 Total Segments Generated: {total_segments}")
    print("=" * 60)


if __name__ == "__main__":
    run_test_pipeline()