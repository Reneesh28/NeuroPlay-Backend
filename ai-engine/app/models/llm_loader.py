from dotenv import load_dotenv
import os
from huggingface_hub import InferenceClient

load_dotenv()

HF_API_KEY = os.getenv("HF_API_KEY")

client = InferenceClient(
    provider="auto",
    api_key=HF_API_KEY
)


def call_llm(prompt: str, max_tokens: int = 200):
    try:
        response = client.chat.completions.create(
            model="meta-llama/Meta-Llama-3-8B-Instruct",
            messages=[{"role": "user", "content": prompt}],
            max_tokens=max_tokens,
            temperature=0.3  # 🔥 slightly more stable
        )

        output = response.choices[0].message.content

        if not output:
            return None

        return output.strip()

    except Exception as e:
        print("LLM ERROR:", str(e))
        return None