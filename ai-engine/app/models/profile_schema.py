"""
Profile Schema — Phase 8: Persistent Digital Twin

Pydantic schemas for the player profile system.
Used by the AI Engine to validate profile data received from MongoDB
and to structure profile data for context injection.

RULES:
- All fields have safe defaults.
- Scores are bounded [0.0, 1.0].
- cluster_distribution is a dict (cluster_id str → count int).
- strengths/weaknesses are bounded lists of strings.
"""

from pydantic import BaseModel, Field
from typing import Dict, List, Optional
from datetime import datetime


class ReactionProfile(BaseModel):
    """Reaction timing and consistency metrics."""
    avg_response_time: float = Field(default=0.0, ge=0.0)
    consistency_score: float = Field(default=0.5, ge=0.0, le=1.0)
    under_pressure_score: float = Field(default=0.5, ge=0.0, le=1.0)


class PlayerProfile(BaseModel):
    """
    Full player profile schema.
    Mirrors the Mongoose model in the backend.
    """
    user_id: str
    domain: str = "blackops"

    # Tactical identity
    preferred_style: str = "unknown"
    aggression_score: float = Field(default=0.5, ge=0.0, le=1.0)
    adaptability_score: float = Field(default=0.5, ge=0.0, le=1.0)

    # Cluster distribution (cluster_id → frequency count)
    cluster_distribution: Dict[str, int] = Field(default_factory=dict)

    # Reaction profile
    reaction_profile: ReactionProfile = Field(default_factory=ReactionProfile)

    # Strengths / Weaknesses
    strengths: List[str] = Field(default_factory=list, max_length=20)
    weaknesses: List[str] = Field(default_factory=list, max_length=20)

    # Metadata
    version: int = 1
    total_simulations: int = 0
    last_simulation_at: Optional[datetime] = None


class ProfileSummary(BaseModel):
    """
    Lightweight profile summary for injection into LLM context.
    This is what the context_builder consumes.
    """
    user_id: str
    preferred_style: str = "unknown"
    aggression_score: float = Field(default=0.5, ge=0.0, le=1.0)
    adaptability_score: float = Field(default=0.5, ge=0.0, le=1.0)
    cluster_distribution: Dict[str, int] = Field(default_factory=dict)
    reaction_profile: ReactionProfile = Field(default_factory=ReactionProfile)
    strengths: List[str] = Field(default_factory=list)
    weaknesses: List[str] = Field(default_factory=list)
    total_simulations: int = 0
    version: int = 1


def profile_from_mongo(doc: dict) -> Optional[ProfileSummary]:
    """
    Converts a raw MongoDB document into a validated ProfileSummary.
    Returns None if doc is None or invalid.
    """
    if not doc or not isinstance(doc, dict):
        return None

    try:
        # Handle Mongoose Map type for cluster_distribution
        cluster_dist = doc.get("cluster_distribution", {})
        if hasattr(cluster_dist, "items"):
            cluster_dist = dict(cluster_dist)

        return ProfileSummary(
            user_id=doc.get("user_id", "unknown"),
            preferred_style=doc.get("preferred_style", "unknown"),
            aggression_score=float(doc.get("aggression_score", 0.5)),
            adaptability_score=float(doc.get("adaptability_score", 0.5)),
            cluster_distribution=cluster_dist,
            reaction_profile=ReactionProfile(
                avg_response_time=float(
                    doc.get("reaction_profile", {}).get("avg_response_time", 0.0)
                ),
                consistency_score=float(
                    doc.get("reaction_profile", {}).get("consistency_score", 0.5)
                ),
                under_pressure_score=float(
                    doc.get("reaction_profile", {}).get("under_pressure_score", 0.5)
                )
            ),
            strengths=doc.get("strengths", [])[:20],
            weaknesses=doc.get("weaknesses", [])[:20],
            total_simulations=int(doc.get("total_simulations", 0)),
            version=int(doc.get("version", 1))
        )
    except Exception:
        return None
