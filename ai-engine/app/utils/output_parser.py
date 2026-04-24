import json


def parse_llm_output(text: str):
    """
    Extracts JSON safely from LLM response
    """

    try:
        # Direct parse (best case)
        return json.loads(text)

    except:
        try:
            # Extract JSON from messy output
            start = text.find("{")
            end = text.rfind("}") + 1

            json_str = text[start:end]

            return json.loads(json_str)

        except:
            # Final fallback
            return {
                "predicted_action": "hold position",
                "confidence": 0.5,
                "reasoning": "Failed to parse model output",
                "coaching_tip": "Stay alert and reposition"
            }