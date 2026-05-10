# Phase 8 — Persistent Digital Twin & Learning System
## Implementation Plan

---

## 🎯 Objective

Transform the NeuroPlay Engine from **"Context-aware Tactical Intelligence" (Phase 7)** into a **"Persistent Adaptive Digital Twin"** that:

- Remembers long-term player behavior
- Evolves player profiles with EMA-based score updates
- Detects behavioral trends via longitudinal snapshots
- Provides personalized, data-grounded coaching
- Maintains persistent tactical identity
- Adapts simulation reasoning over time

---

## 🏗️ Architecture Overview

```
┌──────────────────────────────────────────────────────────────┐
│                    Phase 8 — Data Flow                       │
│                                                              │
│  ┌─────────────┐    ┌──────────────┐    ┌───────────────┐    │
│  │  Simulation  │───▶│   Profile    │───▶│   Behavior    │    │
│  │   Output     │    │   Updater    │    │   Snapshot    │    │
│  └──────┬───────┘    └──────┬───────┘    └───────┬───────┘    │
│         │                   │                    │            │
│         │                   ▼                    ▼            │
│         │           ┌──────────────┐    ┌───────────────┐    │
│         │           │   Player     │    │    Trend      │    │
│         │           │   Profile    │    │    Engine     │    │
│         │           │  (MongoDB)   │    │              │    │
│         │           └──────┬───────┘    └───────┬───────┘    │
│         │                  │                    │            │
│         │                  ▼                    ▼            │
│         │           ┌──────────────┐    ┌───────────────┐    │
│         │           │   Pattern    │    │   Coaching    │    │
│         │           │  Extractor   │    │    Engine     │    │
│         │           └──────┬───────┘    └───────┬───────┘    │
│         │                  │                    │            │
│         │                  ▼                    ▼            │
│         │           ┌──────────────────────────────────┐    │
│         └──────────▶│     Context Builder (Phase 8)    │    │
│                     │  + Player Identity               │    │
│                     │  + Weighted Memory               │    │
│                     │  + Trends + Coaching             │    │
│                     └──────────────┬───────────────────┘    │
│                                    │                         │
│                                    ▼                         │
│                     ┌──────────────────────────────────┐    │
│                     │     LLM Simulation (Phase 7)     │    │
│                     │  "What would THIS player do?"    │    │
│                     └──────────────────────────────────┘    │
└──────────────────────────────────────────────────────────────┘
```

---

## 📂 Files Created

### Backend (Node.js)

| File | Purpose |
|------|---------|
| `backend/src/models/playerProfile.model.js` | Mongoose schema for persistent player profiles |
| `backend/src/models/behaviorSnapshot.model.js` | Periodic behavior snapshots with TTL index |
| `backend/src/models/patternInsight.model.js` | Extracted behavioral patterns per user |
| `backend/src/services/profile.service.js` | CRUD operations for player profiles |
| `backend/src/services/analytics.service.js` | Read-only analytics queries |
| `backend/src/utils/profile.constants.js` | Centralized constants (EMA alpha, bounds, intervals) |
| `backend/src/core/workers/processors/profile_update.processor.js` | Post-simulation profile update processor |

### AI Engine (Python)

| File | Purpose |
|------|---------|
| `ai-engine/app/models/profile_schema.py` | Pydantic schemas + MongoDB converter |
| `ai-engine/app/services/profile_updater.py` | EMA-based profile score computation |
| `ai-engine/app/services/trend_engine.py` | Linear regression trends + Shannon entropy |
| `ai-engine/app/services/memory_weighting.py` | Multi-factor memory ranking system |
| `ai-engine/app/services/pattern_extractor.py` | Frequency-based pattern discovery |
| `ai-engine/app/services/coaching_engine.py` | Template-based personalized coaching |
| `ai-engine/app/services/profile_snapshotter.py` | Periodic snapshot creation + cleanup |
| `ai-engine/app/prompting/coaching_templates.py` | Data-grounded coaching message templates |

### Files Modified

| File | Changes |
|------|---------|
| `ai-engine/app/pipeline/context_builder.py` | Added profile, trends, coaching injection + memory weighting |
| `ai-engine/app/pipeline/steps/simulation.py` | Added Phase 8 profile loading, identity-aware context |
| `ai-engine/app/prompting/templates.py` | Added player identity, trends, coaching sections to prompts |

---

## 🔑 Key Design Decisions

### 1. EMA-Based Score Evolution
- Uses Exponential Moving Average (α = 0.15) for smooth profile adaptation.
- Prevents oscillation from single-game anomalies.
- Bounded [0.0, 1.0] for all scores.

### 2. Bounded Storage Growth
- Behavior snapshots: MongoDB TTL index (90-day expiry) + max 100 per user.
- Confidence history: Rolling window of 100 entries.
- Coaching history refs: Rolling window of 50 entries.
- Pattern insights: One document per user+domain (overwrite, not append).

### 3. Non-Fatal Integration
- All Phase 8 systems are fail-safe — profile loading errors do NOT crash the pipeline.
- The simulation step degrades gracefully to Phase 7 behavior when profile data is unavailable.
- Every service function catches exceptions and returns safe defaults.

### 4. Multi-Factor Memory Weighting
- Combines 5 factors: FAISS distance (35%), recency (25%), confidence (20%), outcome (10%), cluster stability (10%).
- Filters low-quality memories below a composite threshold.
- Deterministic scoring — no randomness.

### 5. Data-Grounded Coaching
- Every coaching message uses real data from the profile/trends.
- Templates require concrete values (percentages, counts, scores).
- No hallucinated statistics — the LLM only sees what the system computed.

---

## ⚠️ Risks & Mitigation

| Risk | Mitigation |
|------|-----------|
| Unbounded DB growth | TTL indexes, bounded arrays, periodic cleanup |
| Profile staleness | EMA ensures continuous adaptation; snapshots track evolution |
| LLM hallucination in coaching | Templates enforce data-grounding; coaching is pre-computed |
| Pipeline crash from Phase 8 | All Phase 8 loading wrapped in try/catch; degrades to Phase 7 |
| Concurrent writes | MongoDB atomic $set/$inc; idempotent profile operations |
| Cold start (no profile) | getOrCreate pattern; safe defaults for all scores |

---

## ✅ Success Criteria

- [x] Persistent player profiles stored in MongoDB
- [x] Profile evolves after every simulation
- [x] Behavioral snapshots generated at intervals
- [x] Trend analytics computed from snapshots
- [x] Memory weighting beyond raw FAISS similarity
- [x] Long-term pattern extraction
- [x] Personalized, data-grounded coaching
- [x] Profile-aware simulation reasoning
- [x] Analytics queryable via service layer
- [x] No pipeline crashes from Phase 8 failures
- [x] Bounded storage growth guaranteed
