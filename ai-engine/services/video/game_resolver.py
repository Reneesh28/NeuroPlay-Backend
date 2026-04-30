GAME_DOMAIN_MAP = {
    "mw1": "modern_warfare",
    "mw2": "modern_warfare",
    "mw3": "modern_warfare",
    "bo1": "blackops",
    "bo2": "blackops",
    "bo3": "blackops",
    "bo4": "blackops",
    "bo6": "blackops",
    "bo7": "blackops",
    "coldwar": "blackops"
}


def extract_game_id(folder_name: str) -> str:
    name = folder_name.lower()

    # Modern Warfare
    if name.startswith("mw"):
        if name.startswith("mw1"):
            return "mw1"
        elif name.startswith("mw2"):
            return "mw2"
        elif name.startswith("mw3"):
            return "mw3"

    # Black Ops
    if name.startswith("blackops"):
        if "1" in name:
            return "bo1"
        elif "2" in name:
            return "bo2"
        elif "3" in name:
            return "bo3"
        elif "4" in name:
            return "bo4"
        elif "6" in name:
            return "bo6"
        elif "7" in name:
            return "bo7"

    # Cold War
    if "coldwar" in name:
        return "coldwar"

    raise ValueError(f"Unknown game_id for folder: {folder_name}")


def resolve_domain(game_id: str) -> str:
    if game_id not in GAME_DOMAIN_MAP:
        raise ValueError(f"Invalid game_id: {game_id}")

    return GAME_DOMAIN_MAP[game_id]


def resolve_game_context(folder_name: str):
    game_id = extract_game_id(folder_name)
    domain = resolve_domain(game_id)

    return {
        "game_id": game_id,
        "domain": domain
    }