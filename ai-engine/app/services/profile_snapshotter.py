"""
Profile Snapshotter — Phase 8: Persistent Digital Twin

Creates periodic behavior snapshots from the player profile.
These snapshots are used by the Trend Engine for longitudinal analysis.

Trigger Logic:
- Snapshot is created every SNAPSHOT_INTERVAL simulations (default: 25).
- Also supports manual snapshot triggering.

Storage Strategy:
- Snapshots are lightweight (~500 bytes each).
- MongoDB TTL index auto-expires snapshots after 90 days.
- Additionally bounded by MAX_SNAPSHOTS_PER_USER (manual cleanup).

RULES:
- NEVER crashes — snapshot failure is non-fatal.
- Idempotent — safe to call on every simulation.
- Only creates a snapshot when the interval is hit.
"""

import logging
from typing import Dict, Any, Optional
from datetime import datetime

logger = logging.getLogger(__name__)

# === CONFIGURATION ===
SNAPSHOT_INTERVAL = 25
MAX_SNAPSHOTS_PER_USER = 100


def should_snapshot(total_simulations: int) -> bool:
    """
    Determines if a snapshot should be created based on simulation count.
    Snapshot every SNAPSHOT_INTERVAL simulations.
    """
    if total_simulations <= 0:
        return False
    return total_simulations % SNAPSHOT_INTERVAL == 0


def create_snapshot(
    profile: Dict[str, Any],
    db=None
) -> Optional[Dict[str, Any]]:
    """
    Creates a behavior snapshot from the current profile state.

    Args:
        profile:  Current player profile dict (from MongoDB or service).
        db:       PyMongo database instance (optional, uses default if None).

    Returns:
        The created snapshot document, or None on failure.
    """
    try:
        user_id = profile.get("user_id")
        domain = profile.get("domain", "blackops")
        total_sims = int(profile.get("total_simulations", 0))

        if not user_id:
            logger.warning("[Snapshotter] Missing user_id — skipping")
            return None

        if not should_snapshot(total_sims):
            return None

        # Compute average confidence from history
        confidence_history = profile.get("confidence_history", [])
        avg_confidence = 0.5
        if confidence_history:
            values = []
            for entry in confidence_history:
                if isinstance(entry, dict):
                    values.append(float(entry.get("value", 0.5)))
                elif isinstance(entry, (int, float)):
                    values.append(float(entry))
            if values:
                avg_confidence = sum(values) / len(values)

        # Build snapshot
        cluster_dist = profile.get("cluster_distribution", {})
        if hasattr(cluster_dist, "items"):
            cluster_dist = dict(cluster_dist)

        # Count existing snapshots for this user
        if db is None:
            from app.database.mongo_client import db as default_db
            db = default_db

        existing_count = db.behaviorsnapshots.count_documents(
            {"user_id": user_id, "domain": domain}
        )

        snapshot = {
            "user_id": user_id,
            "domain": domain,
            "aggression_score": float(profile.get("aggression_score", 0.5)),
            "adaptability_score": float(profile.get("adaptability_score", 0.5)),
            "avg_confidence": round(avg_confidence, 4),
            "consistency_score": float(
                profile.get("reaction_profile", {}).get("consistency_score", 0.5)
            ),
            "cluster_distribution": cluster_dist,
            "preferred_style": profile.get("preferred_style", "unknown"),
            "simulation_count": total_sims,
            "profile_version": int(profile.get("version", 1)),
            "snapshot_number": existing_count + 1,
            "created_at": datetime.utcnow()
        }

        # Insert snapshot
        db.behaviorsnapshots.insert_one(snapshot)

        # Enforce max snapshots (delete oldest if over limit)
        if existing_count + 1 > MAX_SNAPSHOTS_PER_USER:
            _cleanup_old_snapshots(db, user_id, domain)

        logger.info(
            f"[Snapshotter] Snapshot #{existing_count + 1} created | "
            f"User: {user_id} | Sims: {total_sims} | "
            f"Aggression: {snapshot['aggression_score']:.3f}"
        )

        return snapshot

    except Exception as e:
        logger.error(f"[Snapshotter] Error: {str(e)}")
        return None


def _cleanup_old_snapshots(db, user_id: str, domain: str):
    """
    Removes oldest snapshots to enforce MAX_SNAPSHOTS_PER_USER.
    """
    try:
        # Find the oldest excess snapshots
        excess_count = db.behaviorsnapshots.count_documents(
            {"user_id": user_id, "domain": domain}
        ) - MAX_SNAPSHOTS_PER_USER

        if excess_count <= 0:
            return

        # Find IDs of oldest snapshots
        oldest = list(
            db.behaviorsnapshots.find(
                {"user_id": user_id, "domain": domain},
                {"_id": 1}
            ).sort("created_at", 1).limit(excess_count)
        )

        ids_to_delete = [doc["_id"] for doc in oldest]

        if ids_to_delete:
            db.behaviorsnapshots.delete_many({"_id": {"$in": ids_to_delete}})
            logger.info(
                f"[Snapshotter] Cleaned {len(ids_to_delete)} old snapshots for {user_id}"
            )

    except Exception as e:
        logger.warning(f"[Snapshotter] Cleanup failed: {str(e)}")
