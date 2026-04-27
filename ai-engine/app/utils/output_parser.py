import json


def parse_llm_output(text: str):

    if not text or "{" not in text:
        return fallback()

    try:
        return json.loads(text)

    except:
        try:
            start = text.find("{")
            end = text.rfind("}") + 1
            return json.loads(text[start:end])
        except:
            return fallback()


def fallback():
    return {
        "predicted_action": "hold position",
        "confidence": 0.5,
        "reasoning": "Parsing failed",
        "coaching_tip": "Play safe"
    }