from services.ml.v2.inference_engine import InferenceEngine

class EngineManager:
    def __init__(self):
        self.engines = {}

    def get_engine(self, domain):
        if domain not in self.engines:
            print(f"🔄 Creating engine for {domain}")
            self.engines[domain] = InferenceEngine(domain)

        return self.engines[domain]

    def infer(self, domain, player_state, prev_state=None):
        engine = self.get_engine(domain)
        return engine.infer(player_state, prev_state)


# ==============================
# TEST
# ==============================
if __name__ == "__main__":
    manager = EngineManager()

    sample = {
        "motion_intensity": 0.06,
        "motion_variance": 0.002,
        "brightness_avg": 0.15,
        "flash_count": 0,
        "edge_density_avg": 0.01,
        "entropy_avg": 0.63
    }

    result = manager.infer("blackops", sample)

    print("\n🧠 RESULT:")
    print(result)