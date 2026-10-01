"""
Physics-based differential vector engine — AnthroFit OS
Computes cross-brand garment fit compatibility using fabric mechanics
and weighted anatomical sensitivity penalties.
"""

from typing import Tuple, List, Dict, Optional
from data.real_catalog import FABRIC_SPECS, ANCHOR_LIBRARY, PRODUCT_CATALOG

# ─────────────────────────────────────────────────────────────
# Anatomical sensitivity weights
# Higher = more perceptible to the wearer when off
# ─────────────────────────────────────────────────────────────
TOP_WEIGHTS = {
    "shoulder_width":  4.2,   # Any misalignment is instantly visible
    "chest_half":      2.8,   # Primary comfort zone
    "torso_length":    1.2,   # Secondary — less perceptible
    "sleeve_length":   1.6,   # Noticeable at cuff
    "neck_width":      0.9,   # Low-sensitivity zone
}

BOT_WEIGHTS = {
    "waist_half":         3.5,  # Primary comfort fit point
    "thigh_half":         2.8,  # Movement restriction (most complaint zone)
    "hip_half":           2.0,
    "front_rise":         2.2,  # Very perceptible when wrong
    "inseam":             1.4,
    "knee_half":          1.0,
    "leg_opening_half":   0.7,
}

# Comfort tolerance bands — differences within tolerance add no penalty
TOP_TOLERANCE  = {"shoulder_width":0.5, "chest_half":0.8, "torso_length":1.5, "sleeve_length":1.0, "neck_width":1.0}
BOT_TOLERANCE  = {"waist_half":0.5, "thigh_half":0.5, "hip_half":0.8, "front_rise":0.8, "inseam":1.2, "knee_half":0.8, "leg_opening_half":0.8}

# Preference offset profiles (in cm, applied to anchor reference before matching)
PREF_OFFSETS_TOP = {
    "fitted":         {"shoulder_width":-1.0, "chest_half":-1.5, "torso_length": 0.0, "sleeve_length":0.0, "neck_width":0.0},
    "true_to_anchor": {"shoulder_width": 0.0, "chest_half": 0.0, "torso_length": 0.0, "sleeve_length":0.0, "neck_width":0.0},
    "relaxed":        {"shoulder_width": 1.0, "chest_half": 2.0, "torso_length": 1.5, "sleeve_length":0.0, "neck_width":0.0},
}
PREF_OFFSETS_BOT = {
    "fitted":         {"waist_half":-0.8, "thigh_half":-1.0, "hip_half":-1.0, "front_rise":0.0, "inseam":0.0, "knee_half":-0.5, "leg_opening_half":-0.5},
    "true_to_anchor": {"waist_half": 0.0, "thigh_half": 0.0, "hip_half": 0.0, "front_rise":0.0, "inseam":0.0, "knee_half": 0.0, "leg_opening_half": 0.0},
    "relaxed":        {"waist_half": 1.0, "thigh_half": 1.5, "hip_half": 1.5, "front_rise":0.5, "inseam":0.0, "knee_half": 0.8, "leg_opening_half": 0.5},
}


def _effective_dim(raw_cm: float, fabric_key: str, dim_type: str = "width") -> float:
    """
    Apply fabric stretch + wash shrinkage to a raw pattern measurement.
    Returns the 'lived-in' dimension the wearer actually experiences.
    """
    fab = FABRIC_SPECS.get(fabric_key, FABRIC_SPECS["cotton_jersey_light"])
    stretch  = fab["stretch_pct"] / 100  # as decimal
    shrinkage = fab["shrink_pct"] / 100

    # Stretch correction: garment expands to body under wear pressure
    # Conservative factor — only partial stretch engaged in normal wear
    stretch_factor = 1 + stretch * 0.18

    # Post-wash shrinkage: longitudinal and cross-grain differ slightly
    if dim_type == "length":
        shrink_factor = 1 - shrinkage * 0.65
    else:
        shrink_factor = 1 - shrinkage * 0.80

    return raw_cm * stretch_factor * shrink_factor


def resolve_anchor(anchor_id: str, custom_dims: Optional[Dict] = None) -> Optional[dict]:
    """Look up anchor from library or use custom dimensions."""
    if anchor_id in ANCHOR_LIBRARY:
        return ANCHOR_LIBRARY[anchor_id]
    return None


def find_target_product(brand: str, name: str, category: str) -> Optional[str]:
    """
    Best-effort catalog match by brand+name fuzzy match.
    Returns product ID if found.
    """
    brand_l = brand.lower().strip()
    name_l  = name.lower().strip()
    for pid, prod in PRODUCT_CATALOG.items():
        if prod["category"] != category:
            continue
        if prod["brand"].lower() in brand_l or brand_l in prod["brand"].lower():
            # Name match: any 2 consecutive words from user name in catalog name
            words = [w for w in name_l.split() if len(w) > 3]
            hits = sum(1 for w in words if w in prod["name"].lower())
            if hits >= 1:
                return pid
    return None


def compute_top_match(
    anchor: dict,
    target_id: str,
    fit_preference: str = "true_to_anchor",
) -> dict:
    """
    Compare anchor top against each size of target top.
    Returns: recommended size, confidence, per-size scores, friction points.
    """
    product = PRODUCT_CATALOG[target_id]
    anchor_fab  = anchor["fabric_key"]
    target_fab  = product["fabric_key"]
    anchor_dims = anchor["dims"]
    pref_off    = PREF_OFFSETS_TOP.get(fit_preference, PREF_OFFSETS_TOP["true_to_anchor"])
    tol         = TOP_TOLERANCE

    # Effective anchor dimensions (what wearer experiences)
    eff_anchor = {
        k: _effective_dim(v, anchor_fab, "width" if k != "torso_length" else "length")
           + pref_off.get(k, 0)
        for k, v in anchor_dims.items()
    }

    scores = {}
    for size_tag, size_dims in product["sizes"].items():
        total_penalty = 0.0
        for dim_key, weight in TOP_WEIGHTS.items():
            if dim_key not in size_dims or dim_key not in eff_anchor:
                continue
            eff_target_dim = _effective_dim(
                size_dims[dim_key], target_fab,
                "length" if dim_key == "torso_length" else "width"
            )
            delta = eff_target_dim - eff_anchor[dim_key]
            # Apply comfort tolerance
            tol_band = tol.get(dim_key, 0.5)
            penalized_delta = max(0.0, abs(delta) - tol_band) * (1.0 if delta > 0 else 1.4)
            total_penalty += penalized_delta * weight
        scores[size_tag] = total_penalty

    best_size = min(scores, key=scores.get)
    best_penalty = scores[best_size]

    # Confidence: 99 - f(penalty). Penalty 0 → 99%, penalty 10 → ~78%, penalty 20 → ~60%
    confidence = max(55, round(99 - best_penalty * 2.1))

    # Return risk: inversely proportional to confidence
    return_risk = round(max(1.2, 35 - (confidence - 55) * 0.55), 1)

    # Friction points for best size
    best_dims = product["sizes"][best_size]
    friction = []
    for dim_key, weight in TOP_WEIGHTS.items():
        if dim_key not in best_dims or dim_key not in eff_anchor:
            continue
        eff_target = _effective_dim(best_dims[dim_key], target_fab,
                                     "length" if dim_key == "torso_length" else "width")
        raw_delta = eff_target - eff_anchor[dim_key]

        label_map = {
            "shoulder_width": "Shoulder Seam",
            "chest_half":     "Chest Circumference",
            "torso_length":   "Body Length",
            "sleeve_length":  "Sleeve Length",
            "neck_width":     "Neckline Width",
        }
        assess_map = _top_assessment(dim_key, raw_delta, fit_preference)
        delta_str = "Identical" if abs(raw_delta) < 0.3 else f"{raw_delta:+.1f} cm"
        note = _top_note(dim_key, raw_delta, anchor)

        friction.append({
            "zone": label_map.get(dim_key, dim_key),
            "delta": delta_str,
            "assessment": assess_map,
            "note": note,
        })

    return {
        "recommended_size": best_size,
        "fit_confidence_pct": confidence,
        "return_risk_pct": return_risk,
        "size_scores": {k: round(v, 2) for k, v in scores.items()},
        "friction_points": friction,
    }


def compute_bottom_match(
    anchor: dict,
    target_id: str,
    fit_preference: str = "true_to_anchor",
) -> dict:
    product    = PRODUCT_CATALOG[target_id]
    anchor_fab = anchor["fabric_key"]
    target_fab = product["fabric_key"]
    anchor_dims = anchor["dims"]
    pref_off   = PREF_OFFSETS_BOT.get(fit_preference, PREF_OFFSETS_BOT["true_to_anchor"])
    tol        = BOT_TOLERANCE

    eff_anchor = {
        k: _effective_dim(v, anchor_fab, "length" if k == "inseam" else "width")
           + pref_off.get(k, 0)
        for k, v in anchor_dims.items()
    }

    scores = {}
    for size_tag, size_dims in product["sizes"].items():
        penalty = 0.0
        for dim_key, weight in BOT_WEIGHTS.items():
            if dim_key not in size_dims or dim_key not in eff_anchor:
                continue
            eff_tgt = _effective_dim(size_dims[dim_key], target_fab,
                                      "length" if dim_key == "inseam" else "width")
            delta = eff_tgt - eff_anchor[dim_key]
            tol_band = tol.get(dim_key, 0.5)
            pen = max(0.0, abs(delta) - tol_band) * (1.0 if delta > 0 else 1.5)
            penalty += pen * weight
        scores[size_tag] = penalty

    best_size = min(scores, key=scores.get)
    best_penalty = scores[best_size]
    confidence   = max(55, round(99 - best_penalty * 2.3))
    return_risk  = round(max(1.2, 35 - (confidence - 55) * 0.55), 1)

    best_dims = product["sizes"][best_size]
    friction = []
    label_map = {
        "waist_half":       "Waistband",
        "hip_half":         "Hip Seat",
        "thigh_half":       "Thigh Sweep",
        "front_rise":       "Front Rise",
        "knee_half":        "Knee",
        "leg_opening_half": "Leg Opening",
        "inseam":           "Inseam Length",
    }
    for dim_key, weight in BOT_WEIGHTS.items():
        if dim_key not in best_dims or dim_key not in eff_anchor:
            continue
        eff_tgt = _effective_dim(best_dims[dim_key], target_fab,
                                  "length" if dim_key == "inseam" else "width")
        raw_delta = eff_tgt - eff_anchor[dim_key]
        delta_str = "Identical" if abs(raw_delta) < 0.3 else f"{raw_delta:+.1f} cm"
        friction.append({
            "zone": label_map.get(dim_key, dim_key),
            "delta": delta_str,
            "assessment": _bot_assessment(dim_key, raw_delta, fit_preference),
            "note": _bot_note(dim_key, raw_delta, anchor),
        })

    return {
        "recommended_size": best_size,
        "fit_confidence_pct": confidence,
        "return_risk_pct": return_risk,
        "size_scores": {k: round(v, 2) for k, v in scores.items()},
        "friction_points": friction,
    }


# ─────────────────────────────────────────────────────────────
# Assessment & Note generators
# ─────────────────────────────────────────────────────────────
def _top_assessment(dim: str, delta: float, pref: str) -> str:
    if abs(delta) < 0.3: return "Identical to anchor"
    if dim == "shoulder_width":
        if delta > 0: return "Wider drop" if abs(delta) < 2 else "Significantly wider"
        return "Narrower shoulder" if abs(delta) < 2 else "Significantly narrower"
    if dim == "chest_half":
        if delta > 0: return "Relaxed drape" if abs(delta) < 1.5 else "Notably roomier"
        return "Fitted" if abs(delta) < 1.5 else "Tighter fit"
    if dim == "torso_length":
        if delta > 0: return "Longer hem"
        return "Cropped hem"
    if dim == "sleeve_length":
        if delta > 0: return "Longer cuff" if abs(delta) < 2 else "Much longer"
        return "Shorter cuff"
    if delta > 0: return "Roomier" 
    return "Tighter"


def _top_note(dim: str, delta: float, anchor: dict) -> str:
    aname = f"{anchor['brand']} {anchor['size_tag']}"
    notes = {
        "shoulder_width": f"Seam aligns {'wider' if delta > 0 else 'closer to neck'} than your {aname}. Shoulder is the most visible fit indicator.",
        "chest_half":     f"Circumference differential of {abs(delta)*2:.1f} cm total. {'Extra ease across the pectorals.' if delta > 0 else 'Sits tighter across chest — may restrict arm swing.'}",
        "torso_length":   f"Hem will {'cover more of your waistband' if delta > 0 else 'sit shorter — may untuck with movement'} compared to your {aname}.",
        "sleeve_length":  f"{'Cuff will show more above wrist.' if delta > 0 else 'Cuff sits higher toward wrist.'} Reference: your {aname} sleeve.",
        "neck_width":     f"Neckline {'wider, more relaxed collar opening' if delta > 0 else 'narrower, closer neck feel'} than your {aname}.",
    }
    return notes.get(dim, f"Difference of {delta:+.1f} cm from your {aname}.")


def _bot_assessment(dim: str, delta: float, pref: str) -> str:
    if abs(delta) < 0.3: return "Identical"
    if dim == "waist_half":
        if delta > 0: return "Looser waist" if abs(delta) < 1 else "Notably roomier"
        return "Snugger waist" if abs(delta) < 1 else "Tight waistband"
    if dim == "thigh_half":
        if delta > 0: return "More room" if abs(delta) < 1.5 else "Much roomier"
        return "Tighter thigh" if abs(delta) < 1.5 else "Restrictive"
    if dim == "front_rise":
        if delta > 0: return "Higher rise"
        return "Lower rise"
    if delta > 0: return "Roomier"
    return "Tighter"


def _bot_note(dim: str, delta: float, anchor: dict) -> str:
    aname = f"{anchor['brand']} {anchor['size_tag']}"
    notes = {
        "waist_half":       f"Total waistband circumference {abs(delta*2):.1f} cm {'larger' if delta > 0 else 'smaller'} than your {aname}.",
        "hip_half":         f"Hip seat gives {'extra ease for seated comfort' if delta > 0 else 'a slimmer hip line'} versus your {aname}.",
        "thigh_half":       f"{'Full-thigh comfort for walking and sitting.' if delta > 0 else 'Slim thigh — may restrict stride at full extension.'} Reference: {aname}.",
        "front_rise":       f"{'Higher waist, garment sits above hip bone.' if delta > 0 else 'Lower rise, garment sits below hip bone.'} ",
        "inseam":           f"Leg length {'longer — may stack at ankle' if delta > 0 else 'shorter — may show above shoe'} compared to your {aname}.",
        "knee_half":        f"Knee sweep {'roomier — easier movement' if delta > 0 else 'trimmer — cleaner line'}.",
        "leg_opening_half": f"Trouser opening {'wider, breaks over shoe generously' if delta > 0 else 'narrower, clean break at ankle'}.",
    }
    return notes.get(dim, f"{delta:+.1f} cm from your {aname}.")
