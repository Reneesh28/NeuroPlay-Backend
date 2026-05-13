from typing import Tuple

# Spatial configuration for separate universes
DOMAIN_OFFSETS = {
    "blackops": (0, 0, 0),         # Center
    "modern_warfare": (200, 0, 0)  # Offset by 200 units on X axis
}

def get_domain_offset(domain: str) -> Tuple[float, float, float]:
    """Returns the (x, y, z) offset for a given domain's spatial universe."""
    domain = domain.lower().replace(" ", "")
    if "modern" in domain:
        domain = "modern_warfare"
    elif "black" in domain:
        domain = "blackops"
        
    return DOMAIN_OFFSETS.get(domain, (0, 0, 0))

def apply_spatial_offset(coordinates: list, domain: str) -> list:
    """Applies domain offset to a list of (x, y, z) coordinates."""
    offset = get_domain_offset(domain)
    return [(c[0] + offset[0], c[1] + offset[1], c[2] + offset[2]) for c in coordinates]
