"""
LLM Loader — Phase 7: Digital Twin Reasoning Layer

Provides a controlled, resilient interface to the LLM API.

RULES:
- Temperature is controlled per-call (default 0.4 for determinism).
- Retry logic handles transient API failures (max 3 attempts).
- Supports both raw string prompts (legacy) and chat message lists (Phase 7).
- All failures are logged with latency metrics.
"""

import os
import time
import logging
from dotenv import load_dotenv
from huggingface_hub import InferenceClient

load_dotenv()

logger = logging.getLogger(__name__)

HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    provider="auto",
    api_key=HF_API_KEY
)

# ==============================
# CONFIGURATION
# ==============================
DEFAULT_MODEL = "meta-llama/Meta-Llama-3-8B-Instruct"
DEFAULT_TEMPERATURE = 0.4
DEFAULT_MAX_TOKENS = 512
MAX_RETRIES = 3
RETRY_DELAY_SECONDS = 1.0


def call_llm(
    prompt,
    max_tokens: int = DEFAULT_MAX_TOKENS,
    temperature: float = DEFAULT_TEMPERATURE,
    model: str = DEFAULT_MODEL
) -> str:
    """
    Calls the LLM with retry logic and latency tracking.

    Args:
        prompt:       Either a string (legacy) or a list of message dicts (Phase 7).
                      If string: wrapped as [{"role": "user", "content": prompt}]
                      If list:   used directly as messages payload.
        max_tokens:   Maximum tokens for the response (default: 512).
        temperature:  Controls randomness (default: 0.4 for determinism).
        model:        HuggingFace model identifier.

    Returns:
        Stripped string response from the LLM, or None on complete failure.
    """
    # Normalize prompt to messages format
    if isinstance(prompt, str):
        messages = [{"role": "user", "content": prompt}]
    elif isinstance(prompt, list):
        messages = prompt
    else:
        logger.error(f"Invalid prompt type: {type(prompt)}")
        return None

    last_error = None

    for attempt in range(1, MAX_RETRIES + 1):
        start = time.time()

        try:
            response = client.chat.completions.create(
                model=model,
                messages=messages,
                max_tokens=max_tokens,
                temperature=temperature
            )

            latency_ms = int((time.time() - start) * 1000)
            output = response.choices[0].message.content

            if not output:
                logger.warning(
                    f"[LLM] Attempt {attempt}/{MAX_RETRIES} returned empty | "
                    f"Latency: {latency_ms}ms"
                )
                last_error = Exception("LLM returned empty response")
                continue

            logger.info(
                f"[LLM] SUCCESS | Attempt: {attempt} | "
                f"Latency: {latency_ms}ms | "
                f"Tokens: ~{len(output.split())}"
            )

            return output.strip()

        except Exception as e:
            latency_ms = int((time.time() - start) * 1000)
            last_error = e

            logger.warning(
                f"[LLM] Attempt {attempt}/{MAX_RETRIES} FAILED | "
                f"Latency: {latency_ms}ms | "
                f"Error: {str(e)}"
            )

            if attempt < MAX_RETRIES:
                time.sleep(RETRY_DELAY_SECONDS * attempt)  # linear backoff

    logger.error(
        f"[LLM] ALL {MAX_RETRIES} ATTEMPTS FAILED | "
        f"Last error: {str(last_error)}"
    )
    return None