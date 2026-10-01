"""
AnthroFit OS — Main Server v4.0
Real physics-based garment matching + Gemini AI product lookup
"""
import os
import asyncio
from typing import Dict, Any, List, Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from fastapi.responses import HTMLResponse
from pydantic import BaseModel

from data.real_catalog import ANCHOR_LIBRARY, PRODUCT_CATALOG, DOMAIN_BRAND_MAP
from engine.real_matcher import (
    compute_top_match, compute_bottom_match, find_target_product
)
from engine.ai_lookup import (
    lookup_product, set_api_key, convert_ai_sizes_to_dims, _get_key
)
from data.analytics_database import ENTERPRISE_ANALYTICS

BASE_DIR = os.path.dirname(os.path.abspath(__file__))

app = FastAPI(
    title="AnthroFit OS",
    description="Physics-based garment sizing intelligence platform with Gemini AI",
    version="4.0.0"
)

static_dir = os.path.join(BASE_DIR, "static")
if os.path.exists(static_dir):
    app.mount("/static", StaticFiles(directory=static_dir), name="static")

# ─────────────────────────────────────────────────────────────
# REQUEST SCHEMAS
# ─────────────────────────────────────────────────────────────
class QuestionnaireRequest(BaseModel):
    anchor_id: str
    product_brand: str
    product_name: str
    product_category: str
    product_sizes: List[str]
    product_url: Optional[str] = None
    fit_preference: str = "true_to_anchor"
    custom_anchor_dims: Optional[Dict[str, Any]] = None
    # AI-resolved dimensions for the target product
    ai_size_dims: Optional[Dict[str, Dict[str, float]]] = None

class AddAnchorRequest(BaseModel):
    brand: str
    model: str
    size: str
    category: str
    color: Optional[str] = ""
    fit: str = "perfect"

class ProductLookupRequest(BaseModel):
    query: str       # product name, brand + name, or description
    url: str = ""    # optional product URL

class ApiKeyRequest(BaseModel):
    key: str

# ─────────────────────────────────────────────────────────────
# IN-MEMORY USER SESSION
# ─────────────────────────────────────────────────────────────
session_anchors: Dict[str, dict] = {}

def _estimate_dims_from_size(size: str, category: str) -> dict:
    TOP_SIZE_MAP = {
        "XS": dict(chest_half=26.5, shoulder_width=46.0, sleeve_length=24.0, torso_length=69.0, neck_width=17.5),
        "S":  dict(chest_half=28.0, shoulder_width=49.0, sleeve_length=25.0, torso_length=71.0, neck_width=18.0),
        "M":  dict(chest_half=29.5, shoulder_width=52.0, sleeve_length=26.0, torso_length=73.0, neck_width=18.5),
        "L":  dict(chest_half=31.5, shoulder_width=55.0, sleeve_length=27.0, torso_length=75.0, neck_width=19.0),
        "XL": dict(chest_half=33.5, shoulder_width=58.0, sleeve_length=28.0, torso_length=77.0, neck_width=19.5),
        "XXL":dict(chest_half=35.5, shoulder_width=61.0, sleeve_length=29.0, torso_length=79.0, neck_width=20.0),
    }
    BOT_WAIST_MAP = {
        "28": dict(waist_half=19.0, hip_half=25.0, thigh_half=14.0, knee_half=10.0, leg_opening_half=8.5, inseam=81.0, front_rise=27.0),
        "29": dict(waist_half=19.5, hip_half=25.5, thigh_half=14.3, knee_half=10.2, leg_opening_half=8.7, inseam=81.0, front_rise=27.2),
        "30": dict(waist_half=20.2, hip_half=26.0, thigh_half=14.6, knee_half=10.4, leg_opening_half=8.9, inseam=81.0, front_rise=27.5),
        "31": dict(waist_half=20.8, hip_half=26.5, thigh_half=15.0, knee_half=10.7, leg_opening_half=9.1, inseam=81.5, front_rise=27.8),
        "32": dict(waist_half=21.5, hip_half=27.0, thigh_half=15.4, knee_half=11.0, leg_opening_half=9.3, inseam=81.5, front_rise=28.2),
        "33": dict(waist_half=22.2, hip_half=27.6, thigh_half=15.8, knee_half=11.4, leg_opening_half=9.6, inseam=82.0, front_rise=28.6),
        "34": dict(waist_half=22.8, hip_half=28.2, thigh_half=16.2, knee_half=11.7, leg_opening_half=9.9, inseam=82.0, front_rise=29.0),
        "36": dict(waist_half=24.0, hip_half=29.2, thigh_half=17.0, knee_half=12.3, leg_opening_half=10.4, inseam=82.5, front_rise=29.8),
    }
    if category == "bottoms":
        waist_num = size.split("\u00d7")[0].split("x")[0].strip()
        return BOT_WAIST_MAP.get(waist_num, BOT_WAIST_MAP["32"])
    else:
        size_key = size.strip().upper().split("/")[0]
        return TOP_SIZE_MAP.get(size_key, TOP_SIZE_MAP["M"])


def _build_session_anchor(req: AddAnchorRequest) -> dict:
    fabric_key_map = {
        "tops":      "cotton_jersey_heavy",
        "bottoms":   "denim_stretch",
        "outerwear": "wool_blend_woven",
        "knitwear":  "merino_knit",
    }
    dims = _estimate_dims_from_size(req.size, req.category)
    if req.fit == "slightly_tight":
        dims = {k: v * 0.975 for k, v in dims.items()}
    elif req.fit == "slightly_loose":
        dims = {k: v * 1.025 for k, v in dims.items()}

    return {
        "brand": req.brand,
        "model": req.model,
        "size_tag": req.size,
        "category": req.category,
        "fabric_key": fabric_key_map.get(req.category, "cotton_jersey_heavy"),
        "dims": dims,
        "_user_added": True,
        "_color": req.color,
    }


# ─────────────────────────────────────────────────────────────
# ROUTES
# ─────────────────────────────────────────────────────────────
@app.get("/", response_class=HTMLResponse)
async def serve_app():
    tmpl_path = os.path.join(BASE_DIR, "templates", "questionnaire.html")
    with open(tmpl_path, "r", encoding="utf-8") as f:
        return HTMLResponse(content=f.read())


@app.get("/api/status")
async def get_status():
    """Check if API key is configured."""
    has_key = _get_key() is not None
    return {"ai_enabled": has_key}


@app.post("/api/key")
async def set_key(req: ApiKeyRequest):
    """Set the Gemini API key at runtime."""
    set_api_key(req.key)
    return {"status": "ok"}


@app.post("/api/ai/lookup")
async def ai_product_lookup(req: ProductLookupRequest):
    """
    Use Gemini 3 Flash + Google Search to look up a product's sizing data.
    Returns structured product info with available sizes and measurements.
    """
    result = await lookup_product(req.query, req.url)

    if "error" in result:
        return result

    # Convert size chart to internal engine dimensions
    ai_dims = {}
    if "size_chart" in result and result["size_chart"]:
        category = result.get("category", "tops")
        ai_dims = convert_ai_sizes_to_dims(result["size_chart"], category)

    result["ai_dims"] = ai_dims
    return result


@app.get("/api/catalog/anchors")
async def list_anchors():
    result = []
    for aid, a in ANCHOR_LIBRARY.items():
        result.append({
            "id": aid,
            "brand": a["brand"],
            "model": a["model"],
            "size": a["size_tag"],
            "category": a["category"],
            "builtin": True,
        })
    for aid, a in session_anchors.items():
        result.append({
            "id": aid,
            "brand": a["brand"],
            "model": a["model"],
            "size": a["size_tag"],
            "category": a["category"],
            "builtin": False,
        })
    return result


@app.post("/api/catalog/anchors/add")
async def add_anchor(req: AddAnchorRequest):
    anchor_id = f"SESSION-{req.brand.upper()[:4]}-{req.size.upper()}-{len(session_anchors)}"
    session_anchors[anchor_id] = _build_session_anchor(req)
    return {
        "status": "added",
        "id": anchor_id,
        "brand": req.brand,
        "model": req.model,
        "size": req.size,
        "category": req.category,
    }


@app.post("/api/match")
async def resolve_match(req: QuestionnaireRequest):
    """
    Core matching endpoint.
    Now accepts AI-resolved dimensions for accurate cross-brand matching.
    """
    # 1. Resolve anchor
    anchor = None
    if req.anchor_id in ANCHOR_LIBRARY:
        anchor = ANCHOR_LIBRARY[req.anchor_id]
    elif req.anchor_id in session_anchors:
        anchor = session_anchors[req.anchor_id]
    else:
        raise HTTPException(status_code=404, detail=f"Anchor '{req.anchor_id}' not found.")

    # 2. If AI provided real measurements, use them directly
    if req.ai_size_dims and len(req.ai_size_dims) > 0:
        return _match_with_real_dims(anchor, req)

    # 3. Otherwise try static catalog
    cat = req.product_category if req.product_category in ("tops","bottoms","outerwear","knitwear") else "tops"
    match_cat = "bottoms" if cat == "bottoms" else "tops"
    target_id = find_target_product(req.product_brand, req.product_name, cat)

    if not target_id:
        return _synthetic_match(anchor, req)

    if match_cat == "bottoms":
        result = compute_bottom_match(anchor, target_id, req.fit_preference)
    else:
        result = compute_top_match(anchor, target_id, req.fit_preference)

    if req.product_sizes:
        available = set(s.strip() for s in req.product_sizes)
        if result["recommended_size"] not in available:
            scores = result.get("size_scores", {})
            available_scores = {k: v for k, v in scores.items() if k in available}
            if available_scores:
                result["recommended_size"] = min(available_scores, key=available_scores.get)

    prod = PRODUCT_CATALOG[target_id]
    result["target_product"] = f"{prod['brand']} -- {prod['name']}"
    result["anchor_used"]    = f"{anchor['brand']} {anchor['model']} ({anchor['size_tag']})"
    result["verdict_summary"] = (
        f"Order size <strong>{result['recommended_size']}</strong>. "
        f"Same drape as your {anchor['brand']} {anchor['size_tag']}."
    )
    return result


def _match_with_real_dims(anchor: dict, req: QuestionnaireRequest) -> dict:
    """
    Match using real AI-sourced measurements from the actual product sizing chart.
    This is the most accurate mode — uses manufacturer data.
    """
    from engine.real_matcher import (
        FABRIC_SPECS, TOP_WEIGHTS, BOT_WEIGHTS,
        TOP_TOLERANCE, BOT_TOLERANCE,
        PREF_OFFSETS_TOP, PREF_OFFSETS_BOT,
        _effective_dim, _top_assessment, _top_note,
        _bot_assessment, _bot_note,
    )

    cat = req.product_category
    is_bot = cat == "bottoms"
    fab_key = "cotton_jersey_heavy" if cat in ("tops","outerwear","knitwear") else "denim_stretch"
    pref = req.fit_preference
    weights = BOT_WEIGHTS if is_bot else TOP_WEIGHTS
    tol_map = BOT_TOLERANCE if is_bot else TOP_TOLERANCE
    pref_off = (PREF_OFFSETS_BOT if is_bot else PREF_OFFSETS_TOP).get(pref, {})

    # Build effective anchor dimensions with fabric physics
    eff_anchor = {
        k: _effective_dim(v, anchor["fabric_key"],
                           "length" if k in ("torso_length","inseam") else "width")
            + pref_off.get(k, 0)
        for k, v in anchor["dims"].items()
    }

    sizes_to_check = req.ai_size_dims

    scores = {}
    for size_tag, dims in sizes_to_check.items():
        penalty = 0.0
        for dk, w in weights.items():
            if dk not in dims or dk not in eff_anchor:
                continue
            eff_t = _effective_dim(dims[dk], fab_key,
                                   "length" if dk in ("torso_length","inseam") else "width")
            d = eff_t - eff_anchor[dk]
            tband = tol_map.get(dk, 0.5)
            penalty += max(0.0, abs(d) - tband) * (1.0 if d > 0 else 1.4) * w
        scores[size_tag] = penalty

    if not scores:
        return _synthetic_match(anchor, req)

    best_size    = min(scores, key=scores.get)
    best_penalty = scores[best_size]
    confidence   = max(62, round(99 - best_penalty * 2.1))
    return_risk  = round(max(1.5, 35 - (confidence - 55) * 0.55), 1)

    best_dims = sizes_to_check[best_size]
    friction  = []
    label_map = {
        "shoulder_width":"Shoulder Seam","chest_half":"Chest Circumference",
        "torso_length":"Body Length","sleeve_length":"Sleeve Length","neck_width":"Neckline",
        "waist_half":"Waistband","hip_half":"Hip Seat","thigh_half":"Thigh Sweep",
        "front_rise":"Front Rise","inseam":"Inseam Length","knee_half":"Knee","leg_opening_half":"Leg Opening",
    }
    for dk, w in weights.items():
        if dk not in best_dims or dk not in eff_anchor:
            continue
        eff_t = _effective_dim(best_dims[dk], fab_key,
                               "length" if dk in ("torso_length","inseam") else "width")
        rd = eff_t - eff_anchor[dk]
        delta_str = "Identical" if abs(rd) < 0.3 else f"{rd:+.1f} cm"
        asmt = _bot_assessment(dk, rd, pref) if is_bot else _top_assessment(dk, rd, pref)
        note = _bot_note(dk, rd, anchor)     if is_bot else _top_note(dk, rd, anchor)
        friction.append({"zone": label_map.get(dk, dk), "delta": delta_str,
                         "assessment": asmt, "note": note})

    return {
        "recommended_size": best_size,
        "fit_confidence_pct": confidence,
        "return_risk_pct": return_risk,
        "size_scores": {k: round(v,2) for k,v in scores.items()},
        "friction_points": friction,
        "target_product": f"{req.product_brand} -- {req.product_name}",
        "anchor_used": f"{anchor['brand']} {anchor['model']} ({anchor['size_tag']})",
        "verdict_summary": (
            f"Order size <strong>{best_size}</strong>. "
            f"Based on real manufacturer measurements matched against your {anchor['brand']} {anchor['size_tag']}."
        ),
        "ai_sourced": True,
    }


def _synthetic_match(anchor: dict, req: QuestionnaireRequest) -> dict:
    from engine.real_matcher import (
        FABRIC_SPECS, TOP_WEIGHTS, BOT_WEIGHTS,
        TOP_TOLERANCE, BOT_TOLERANCE,
        PREF_OFFSETS_TOP, PREF_OFFSETS_BOT,
        _effective_dim, _top_assessment, _top_note,
        _bot_assessment, _bot_note,
    )

    cat = req.product_category
    fab_key = "cotton_jersey_heavy" if cat in ("tops","outerwear","knitwear") else "denim_stretch"
    pref    = req.fit_preference

    top_size_patterns = {
        "XS": dict(chest_half=26.5, shoulder_width=46.0, sleeve_length=24.0, torso_length=69.0, neck_width=17.5),
        "S":  dict(chest_half=28.0, shoulder_width=49.0, sleeve_length=25.0, torso_length=71.0, neck_width=18.0),
        "M":  dict(chest_half=29.5, shoulder_width=52.0, sleeve_length=26.0, torso_length=73.0, neck_width=18.5),
        "L":  dict(chest_half=31.5, shoulder_width=55.0, sleeve_length=27.0, torso_length=75.0, neck_width=19.0),
        "XL": dict(chest_half=33.5, shoulder_width=58.0, sleeve_length=28.0, torso_length=77.0, neck_width=19.5),
        "XXL":dict(chest_half=35.5, shoulder_width=61.0, sleeve_length=29.0, torso_length=79.0, neck_width=20.0),
    }
    bot_size_patterns = {
        "28":  dict(waist_half=19.0, hip_half=25.0, thigh_half=14.0, knee_half=10.0, leg_opening_half=8.5, inseam=81.0, front_rise=27.0),
        "30":  dict(waist_half=20.2, hip_half=26.0, thigh_half=14.6, knee_half=10.4, leg_opening_half=8.9, inseam=81.0, front_rise=27.5),
        "32":  dict(waist_half=21.5, hip_half=27.0, thigh_half=15.4, knee_half=11.0, leg_opening_half=9.3, inseam=81.5, front_rise=28.2),
        "34":  dict(waist_half=22.8, hip_half=28.2, thigh_half=16.2, knee_half=11.7, leg_opening_half=9.9, inseam=82.0, front_rise=29.0),
    }

    is_bot = cat == "bottoms"
    weights  = BOT_WEIGHTS if is_bot else TOP_WEIGHTS
    tol_map  = BOT_TOLERANCE if is_bot else TOP_TOLERANCE
    pref_off = (PREF_OFFSETS_BOT if is_bot else PREF_OFFSETS_TOP).get(pref, {})
    patterns = bot_size_patterns if is_bot else top_size_patterns

    sizes_to_check = {}
    for sz in req.product_sizes:
        if sz in patterns:
            sizes_to_check[sz] = patterns[sz]
        else:
            sizes_to_check[sz] = patterns.get("M", patterns.get("32", next(iter(patterns.values()))))
    if not sizes_to_check:
        sizes_to_check = patterns

    eff_anchor = {
        k: _effective_dim(v, anchor["fabric_key"],
                           "length" if k in ("torso_length","inseam") else "width")
            + pref_off.get(k, 0)
        for k, v in anchor["dims"].items()
    }

    scores = {}
    for size_tag, dims in sizes_to_check.items():
        penalty = 0.0
        for dk, w in weights.items():
            if dk not in dims or dk not in eff_anchor: continue
            eff_t = _effective_dim(dims[dk], fab_key, "length" if dk in ("torso_length","inseam") else "width")
            d = eff_t - eff_anchor[dk]
            tband = tol_map.get(dk, 0.5)
            penalty += max(0.0, abs(d) - tband) * (1.0 if d > 0 else 1.4) * w
        scores[size_tag] = penalty

    best_size    = min(scores, key=scores.get)
    best_penalty = scores[best_size]
    confidence   = max(62, round(99 - best_penalty * 2.1))
    return_risk  = round(max(1.5, 35 - (confidence - 55) * 0.55), 1)

    best_dims = sizes_to_check[best_size]
    friction  = []
    label_map = {
        "shoulder_width":"Shoulder Seam","chest_half":"Chest Circumference",
        "torso_length":"Body Length","sleeve_length":"Sleeve Length","neck_width":"Neckline",
        "waist_half":"Waistband","hip_half":"Hip Seat","thigh_half":"Thigh Sweep",
        "front_rise":"Front Rise","inseam":"Inseam Length","knee_half":"Knee","leg_opening_half":"Leg Opening",
    }
    for dk, w in weights.items():
        if dk not in best_dims or dk not in eff_anchor: continue
        eff_t = _effective_dim(best_dims[dk], fab_key, "length" if dk in ("torso_length","inseam") else "width")
        rd = eff_t - eff_anchor[dk]
        delta_str = "Identical" if abs(rd) < 0.3 else f"{rd:+.1f} cm"
        asmt = _bot_assessment(dk, rd, pref) if is_bot else _top_assessment(dk, rd, pref)
        note = _bot_note(dk, rd, anchor)     if is_bot else _top_note(dk, rd, anchor)
        friction.append({"zone": label_map.get(dk, dk), "delta": delta_str, "assessment": asmt, "note": note})

    return {
        "recommended_size": best_size,
        "fit_confidence_pct": confidence,
        "return_risk_pct": return_risk,
        "size_scores": {k: round(v,2) for k,v in scores.items()},
        "friction_points": friction,
        "target_product": f"{req.product_brand} -- {req.product_name}",
        "anchor_used": f"{anchor['brand']} {anchor['model']} ({anchor['size_tag']})",
        "verdict_summary": (
            f"Order size <strong>{best_size}</strong>. "
            f"Same drape as your {anchor['brand']} {anchor['size_tag']}."
        ),
    }


@app.get("/api/analytics")
async def get_analytics():
    return ENTERPRISE_ANALYTICS


if __name__ == "__main__":
    print(">> ANTHROFIT OS v4.0 -- AI-Powered Sizing Engine")
    print(">> http://localhost:8000")
    import uvicorn
    uvicorn.run("main:app", host="127.0.0.1", port=8000, reload=False)
