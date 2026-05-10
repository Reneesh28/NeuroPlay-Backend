"""
Simulation Step — Phase 8: Persistent Digital Twin

This is the core simulation pipeline step that:
1. Loads player profile (Phase 8 — Digital Twin Identity)
2. Builds structured reasoning context (Context Builder)
3. Generates mode-aware, identity-aware prompts (Prompt System)
4. Calls the LLM with retry logic (LLM Integration)
5. Parses and validates the output (Output Parser + Validator)
6. Applies confidence calibration (Confidence Control)
7. Triggers profile update (Phase 8 — Profile Evolution)
8. Returns a deterministic, bounded response

Execution Modes:
- FULL:     ML + Memory + LLM + Profile — max confidence 0.95
- PARTIAL:  Degraded memory / LLM conservative — max confidence 0.70
- FALLBACK: No LLM, static safe response — fixed confidence 0.50

RULES:
- NEVER crashes — always returns a valid response.
- ALWAYS returns a tuple: (response_dict, execution_mode).
- Confidence is ALWAYS bounded by mode.
- Profile loading failures do NOT crash the pipeline.
"""

import logging
import json

from app.core.execution_mode import ExecutionMode, detect_ml_failure
from app.models.llm_loader import call_llm
from app.prompting.templates import build_simulation_prompt
from app.utils.output_parser import parse_llm_output
from app.pipeline.validators.simulation_output import validate_simulation_output
from app.pipeline.context_builder import build_reasoning_context
from app.core.response_builder import build_response

logger = logging.getLogger(__name__)


# ==============================
# CONFIDENCE CALIBRATION
# ==============================
CONFIDENCE_CAPS = {
    ExecutionMode.FULL: 0.95,
    ExecutionMode.PARTIAL: 0.70,
    ExecutionMode.FALLBACK: 0.50
}


def calibrate_confidence(confidence, mode):
    """
    Applies mode-specific confidence caps.

    FULL:     max 0.95
    PARTIAL:  max 0.70
    FALLBACK: fixed 0.50
    """
    try:
        confidence = float(confidence)
    except (ValueError, TypeError):
        confidence = 0.5

    if mode == ExecutionMode.FALLBACK:
        return 0.5

    cap = CONFIDENCE_CAPS.get(mode, 0.5)
    return min(confidence, cap)


# ==============================
# STATIC RESPONSES
# ==============================
def fallback_response():
    """Pre-validated static response for FALLBACK mode."""
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Fallback action applied due to system uncertainty",
        "coaching_tip": "Play safe and gather information"
    }


def partial_response():
    """Pre-validated static response for PARTIAL mode when LLM also fails."""
    return {
        "predicted_action": "hold position",
        "confidence": 0.6,
        "reasoning": "System degraded, applying conservative strategy",
        "coaching_tip": "Focus on safety and positioning"
    }


# ==============================
# MAIN EXECUTION
# ==============================
def run(input_data: dict, context: dict, execution_mode: str) -> tuple:
    """
    Executes the simulation step.

    Flow:
    1. Input validation → fallback if invalid
    2. Pre-triggered fallback check
    3. Build reasoning context (Context Builder)
    4. Generate prompt (Prompt System)
    5. Call LLM (with retry)
    6. Parse output (multi-strategy)
    7. Validate structure (schema guard)
    8. Calibrate confidence (mode-specific cap)
    9. Return response

    Args:
        input_data:      Raw pipeline input (from loader / previous step output)
        context:         Execution context dict (user_id, session_id, domain, trace_id, etc.)
        execution_mode:  Current pipeline execution mode (FULL / PARTIAL / FALLBACK)

    Returns:
        Tuple of (response_dict, execution_mode_str)
    """
    trace_id = context.get("trace_id", "unknown")

    # ==============================
    # 🔥 HARD GUARD: invalid input
    # ==============================
    if not input_data or not isinstance(input_data, dict):
        logger.warning(f"[Trace:{trace_id}] Invalid input_data → fallback")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    # ==============================
    # PRE-TRIGGERED FALLBACK
    # ==============================
    if execution_mode == ExecutionMode.FALLBACK:
        logger.info(f"[Trace:{trace_id}] MODE: FALLBACK (pre-triggered)")
        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK

    try:
        # ==============================
        # STEP 1: LOAD PLAYER PROFILE (Phase 8)
        # ==============================
        profile_data = None
        trends_data = None
        coaching_tips = None

        try:
            profile_data, trends_data, coaching_tips = _load_phase8_context(
                context, input_data
            )
            if profile_data:
                logger.info(f"[Trace:{trace_id}] PROFILE LOADED | Style: {profile_data.get('preferred_style', 'N/A')}")
        except Exception as e:
            logger.warning(f"[Trace:{trace_id}] Phase 8 context load failed (non-fatal): {str(e)}")

        # ==============================
        # STEP 2: BUILD REASONING CONTEXT
        # ==============================
        memory_data = _extract_memory_data(input_data)

        reasoning_context = build_reasoning_context(
            input_data=input_data,
            context=context,
            memory_data=memory_data,
            profile_data=profile_data,
            trends_data=trends_data,
            coaching_tips=coaching_tips
        )

        logger.info(f"[Trace:{trace_id}] CONTEXT BUILT")

        # ==============================
        # STEP 2: GENERATE PROMPT
        # ==============================
        prompt = build_simulation_prompt(
            input_data=input_data,
            context=context,
            mode=execution_mode,
            reasoning_context=reasoning_context
        )

        logger.info(f"[Trace:{trace_id}] PROMPT GENERATED | Mode: {execution_mode}")

        # ==============================
        # STEP 3: LLM CALL
        # ==============================
        raw = call_llm(prompt, temperature=0.4)

        if not raw:
            raise Exception("LLM returned empty response after all retries")

        logger.info(f"[Trace:{trace_id}] LLM RESPONSE RECEIVED")

        # ==============================
        # STEP 4: PARSE OUTPUT
        # ==============================
        parsed = parse_llm_output(raw)

        if not parsed:
            raise Exception("Parsed output empty after all strategies")

        # ==============================
        # STEP 5: VALIDATE STRUCTURE
        # ==============================
        validated = validate_simulation_output(parsed)

        # ==============================
        # STEP 6: CONFIDENCE CALIBRATION
        # ==============================
        validated["confidence"] = calibrate_confidence(
            validated.get("confidence"), execution_mode
        )

        logger.info(
            f"[Trace:{trace_id}] MODE: {execution_mode} SUCCESS | "
            f"Action: {validated.get('predicted_action')} | "
            f"Confidence: {validated.get('confidence')}"
        )

        return build_response(validated, execution_mode), execution_mode

    except Exception as e:
        failure_mode = detect_ml_failure(e)

        logger.error(f"[Trace:{trace_id}] ERROR: {str(e)} -> Triggering {failure_mode}")

        if failure_mode == ExecutionMode.PARTIAL:
            resp = partial_response()
            resp["confidence"] = calibrate_confidence(resp["confidence"], ExecutionMode.PARTIAL)
            return build_response(resp, ExecutionMode.PARTIAL), ExecutionMode.PARTIAL

        return build_response(fallback_response(), ExecutionMode.FALLBACK), ExecutionMode.FALLBACK


# ==============================
# HELPERS
# ==============================
def _extract_memory_data(input_data: dict) -> dict:
    """
    Extracts memory retrieval data from the input_data payload.

    The simulation step receives the output of the memory_retrieval step
    as its input_data. This function normalizes the extraction.
    """
    if not isinstance(input_data, dict):
        return {"memory": [], "fallback": True}

    # 🔥 Check top-level first (direct output from memory_retrieval step)
    if "memory" in input_data:
        return input_data

    # Check nested formats (legacy or wrapped)
    raw = input_data.get("input_data") or input_data.get("data") or input_data

    if isinstance(raw, dict):
        # Wrapped data format
        data = raw.get("data", {})
        if isinstance(data, dict) and "memory" in data:
            return data
        
        # Or maybe it's just raw memory
        if "memory" in raw:
            return raw

    return {"memory": [], "fallback": True}


# ==============================
# PHASE 8 — PROFILE LOADING
# ==============================
def _load_phase8_context(context: dict, input_data: dict) -> tuple:
    """
    Loads Phase 8 profile-aware context:
    1. Player profile from MongoDB
    2. Behavioral trends from snapshots
    3. Coaching tips from profile + trends

    Returns:
        Tuple of (profile_data, trends_data, coaching_tips)
        All may be None if loading fails (non-fatal).
    """
    from app.database.mongo_client import db
    from app.models.profile_schema import profile_from_mongo
    from app.services.trend_engine import compute_trends
    from app.services.coaching_engine import generate_coaching

    user_id = context.get("user_id")
    domain = context.get("domain", "blackops")

    if not user_id:
        return None, None, None

    # 1. Load profile
    profile_doc = db.playerprofiles.find_one(
        {"user_id": user_id, "domain": domain}
    )

    profile_summary = profile_from_mongo(profile_doc)
    profile_data = profile_summary.model_dump() if profile_summary else None

    # 2. Load trends from snapshots
    trends_data = None
    try:
        snapshots = list(
            db.behaviorsnapshots.find(
                {"user_id": user_id, "domain": domain}
            ).sort("created_at", 1).limit(50)
        )

        if snapshots and len(snapshots) >= 3:
            snapshot_dicts = []
            for s in snapshots:
                snap = dict(s)
                # Convert Mongoose Map to dict if needed
                cd = snap.get("cluster_distribution", {})
                if hasattr(cd, "items"):
                    snap["cluster_distribution"] = dict(cd)
                snapshot_dicts.append(snap)

            trends_data = compute_trends(snapshot_dicts)
    except Exception as te:
        logger.warning(f"[Phase8] Trend loading failed: {str(te)}")

    # 3. Generate coaching tips
    coaching_tips = None
    try:
        if profile_data:
            coaching_tips = generate_coaching(
                profile=profile_data,
                trends=trends_data
            )
    except Exception as ce:
        logger.warning(f"[Phase8] Coaching generation failed: {str(ce)}")

    return profile_data, trends_data, coaching_tips