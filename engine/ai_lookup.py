"""
AnthroFit OS — Gemini AI Product Intelligence Layer
Uses Google Gemini 3 Flash to look up real product sizing data from the web.
"""
import re
import json
import os
import asyncio
import traceback
from typing import Optional, Dict, Any
from google import genai
from google.genai import types

# ─────────────────────────────────────────────────────────────
# CLIENT INITIALIZATION & KEY DISCOVERY
# ─────────────────────────────────────────────────────────────
_client: Optional[genai.Client] = None
_api_key: Optional[str] = None

def _get_key() -> Optional[str]:
    global _api_key
    if _api_key:
        return _api_key
    # 1. Check environment variables
    key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
    if key and not key.startswith("your_"):
        _api_key = key
        return key
    # 2. Check .env file in project root and parent directories
    candidate_paths = [
        os.path.join(os.getcwd(), ".env"),
        os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), ".env"),
        os.path.join(os.path.dirname(os.path.abspath(__file__)), ".env"),
    ]
    for env_path in candidate_paths:
        if os.path.exists(env_path):
            try:
                with open(env_path, "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line.startswith("#") or not line:
                            continue
                        for prefix in ("GEMINI_API_KEY=", "GOOGLE_API_KEY=", "GEMINI_KEY="):
                            if line.startswith(prefix):
                                val = line.split("=", 1)[1].strip().strip('"').strip("'")
                                if val and not val.startswith("your_"):
                                    _api_key = val
                                    return _api_key
            except Exception:
                pass
    return None

def set_api_key(key: str):
    global _api_key, _client
    _api_key = key.strip()
    _client = None  # Force re-init

def _get_client() -> Optional[genai.Client]:
    global _client
    if _client:
        return _client
    key = _get_key()
    if not key:
        return None
    _client = genai.Client(api_key=key)
    return _client


# ─────────────────────────────────────────────────────────────
# CORE LOOKUP: Product Sizing via Gemini 3 Flash + Google Search
# ─────────────────────────────────────────────────────────────
SYSTEM_INSTRUCTION = """You are a garment product data extraction engine. 
When given a product name (and optionally a URL), you must:
1. Search for the exact product on the web
2. Find the product's official sizing chart / size guide
3. Extract structured sizing data

Return ONLY valid JSON with this exact schema — no markdown, no explanation, no backticks:

{
  "brand": "string",
  "name": "Full product name",
  "url": "Product page URL or empty string",
  "category": "tops|bottoms|outerwear|knitwear",
  "fabric_description": "Brief fabric/material description",
  "retail_price": "Price with currency symbol or empty string",
  "available_sizes": ["XS", "S", "M", "L", "XL"],
  "size_chart": {
    "S": {
      "chest_cm": 96,
      "shoulder_cm": 44,
      "length_cm": 70,
      "sleeve_cm": 24
    },
    "M": {
      "chest_cm": 100,
      "shoulder_cm": 46,
      "length_cm": 72,
      "sleeve_cm": 25
    }
  },
  "fit_notes": "Regular fit / Slim fit / Oversized etc."
}

Rules:
- For tops: include chest_cm, shoulder_cm, length_cm, sleeve_cm where available
- For bottoms: include waist_cm, hip_cm, thigh_cm, inseam_cm, rise_cm where available
- All measurements in centimetres (cm)
- If a measurement is not available, omit the key — do NOT guess or hallucinate measurements
- available_sizes must list ALL sizes the product comes in
- Return ONLY the JSON object, nothing else"""


def _clean_json_response(raw_text: str) -> dict:
    """Robustly extract and parse JSON object from model response."""
    text = raw_text.strip()
    # Strip markdown fences if present
    if "```" in text:
        match = re.search(r"```(?:json)?\s*([\s\S]*?)\s*```", text)
        if match:
            text = match.group(1).strip()
    # Find matching outermost braces
    brace_match = re.search(r"\{[\s\S]*\}", text)
    if brace_match:
        text = brace_match.group(0)
    return json.loads(text)


def _sync_gemini_call(client: genai.Client, prompt: str) -> str:
    """Execute Gemini call synchronously with model fallback."""
    env_model = os.environ.get("GEMINI_MODEL")
    candidate_models = [env_model] if env_model else ["gemini-2.5-flash", "gemini-3.8-flash"]
    last_err = None

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=prompt,
                config=types.GenerateContentConfig(
                    system_instruction=SYSTEM_INSTRUCTION,
                    temperature=0.1,
                    tools=[types.Tool(google_search=types.GoogleSearch())],
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            # If not a model-not-found error, don't keep failing with other models for auth errors
            if "api_key" in err_str or "unauthenticated" in err_str or "401" in err_str:
                raise e
            continue

    if last_err:
        raise last_err
    raise RuntimeError("No response received from Gemini.")


def _catalog_fallback_lookup(query: str) -> Optional[Dict[str, Any]]:
    """Check if query matches built-in CAD catalog as an offline/instant fallback."""
    from data.real_catalog import PRODUCT_CATALOG
    q = query.lower()
    for pid, p in PRODUCT_CATALOG.items():
        if p["brand"].lower() in q or any(word in q for word in p["name"].lower().split()):
            # Reconstruct sizing chart in cm for the preview
            size_chart = {}
            for sz, dims in p["sizes"].items():
                if p["category"] == "bottoms":
                    size_chart[sz] = {
                        "waist_cm": round(dims.get("waist_half", 0) * 2, 1),
                        "hip_cm": round(dims.get("hip_half", 0) * 2, 1),
                        "inseam_cm": round(dims.get("inseam", 0), 1),
                    }
                else:
                    size_chart[sz] = {
                        "chest_cm": round(dims.get("chest_half", 0) * 2, 1),
                        "shoulder_cm": round(dims.get("shoulder_width", 0), 1),
                        "length_cm": round(dims.get("torso_length", 0), 1),
                    }
            return {
                "brand": p["brand"],
                "name": p["name"],
                "url": "",
                "category": p["category"],
                "fabric_description": p.get("fabric_key", "cotton_jersey_heavy").replace("_", " ").title(),
                "retail_price": "Catalog Spec",
                "available_sizes": list(p["sizes"].keys()),
                "size_chart": size_chart,
                "fit_notes": "Verified manufacturer CAD dimensions",
                "_from_catalog": True,
            }
    return None


async def lookup_product(query: str, url: str = "") -> Dict[str, Any]:
    """
    Look up a product's sizing data using Gemini 3 Flash with Google Search grounding.
    Returns structured product data dict or {"error": "..."}.
    """
    client = _get_client()

    # If no API key configured yet, check if it matches local catalog
    if not client:
        fallback = _catalog_fallback_lookup(query)
        if fallback:
            return fallback
        return {
            "error": "No API key configured. Please add your key to .env or click the settings gear (⚙) to paste your Google AI Studio key."
        }

    prompt = f"Find the sizing chart and garment dimensions for: {query}"
    if url:
        prompt += f"\nProduct URL: {url}"

    try:
        raw_text = await asyncio.to_thread(_sync_gemini_call, client, prompt)
        data = _clean_json_response(raw_text)

        if "error" in data:
            # Fall back to catalog if available
            fb = _catalog_fallback_lookup(query)
            if fb: return fb
            return data

        return data

    except json.JSONDecodeError as e:
        fb = _catalog_fallback_lookup(query)
        if fb: return fb
        return {"error": f"Could not parse product data: {str(e)}"}
    except Exception as e:
        err_msg = str(e)
        if "API_KEY" in err_msg.upper() or "401" in err_msg or "403" in err_msg:
            return {"error": "Invalid API key. Please check your Google AI Studio API key in .env or settings."}
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            fb = _catalog_fallback_lookup(query)
            if fb: return fb
            return {"error": "API rate limit reached. Please wait a moment and try again."}
        fb = _catalog_fallback_lookup(query)
        if fb: return fb
        return {"error": f"AI search error: {err_msg}"}


def convert_ai_sizes_to_dims(size_chart: dict, category: str) -> dict:
    """
    Convert AI-returned size chart measurements to internal engine dimensions.
    Gracefully normalizes between full body circumference (e.g. 84cm waist)
    and flat garment measurement (e.g. 42cm waist).
    Returns {size_tag: {dim_key: value_in_cad_half_cm, ...}, ...}
    """
    result = {}
    is_bottom = category == "bottoms"

    for size_tag, measurements in size_chart.items():
        if not isinstance(measurements, dict):
            continue
        dims = {}
        if is_bottom:
            if "waist_cm" in measurements and measurements["waist_cm"]:
                w = float(measurements["waist_cm"])
                dims["waist_half"] = round(w / 4.0 if w > 52 else w / 2.0, 2)
            if "hip_cm" in measurements and measurements["hip_cm"]:
                h = float(measurements["hip_cm"])
                dims["hip_half"] = round(h / 4.0 if h > 65 else h / 2.0, 2)
            if "thigh_cm" in measurements and measurements["thigh_cm"]:
                t = float(measurements["thigh_cm"])
                dims["thigh_half"] = round(t / 4.0 if t > 36 else t / 2.0, 2)
            if "inseam_cm" in measurements and measurements["inseam_cm"]:
                dims["inseam"] = round(float(measurements["inseam_cm"]), 1)
            if "rise_cm" in measurements and measurements["rise_cm"]:
                dims["front_rise"] = round(float(measurements["rise_cm"]), 1)
            if "knee_cm" in measurements and measurements["knee_cm"]:
                k = float(measurements["knee_cm"])
                dims["knee_half"] = round(k / 4.0 if k > 24 else k / 2.0, 2)
            if "leg_opening_cm" in measurements and measurements["leg_opening_cm"]:
                lo = float(measurements["leg_opening_cm"])
                dims["leg_opening_half"] = round(lo / 4.0 if lo > 20 else lo / 2.0, 2)
        else:
            if "chest_cm" in measurements and measurements["chest_cm"]:
                c = float(measurements["chest_cm"])
                dims["chest_half"] = round(c / 4.0 if c > 68 else c / 2.0, 2)
            if "shoulder_cm" in measurements and measurements["shoulder_cm"]:
                dims["shoulder_width"] = round(float(measurements["shoulder_cm"]), 1)
            if "length_cm" in measurements and measurements["length_cm"]:
                dims["torso_length"] = round(float(measurements["length_cm"]), 1)
            if "sleeve_cm" in measurements and measurements["sleeve_cm"]:
                dims["sleeve_length"] = round(float(measurements["sleeve_cm"]), 1)
            if "neck_cm" in measurements and measurements["neck_cm"]:
                dims["neck_width"] = round(float(measurements["neck_cm"]), 1)

        if dims:
            result[size_tag] = dims

    return result


# ─────────────────────────────────────────────────────────────
# VISION IDENTIFICATION: Garment / Tag Image Recognition
# ─────────────────────────────────────────────────────────────
VISION_SYSTEM_INSTRUCTION = """You are an expert fashion patternmaker and computer vision engine for clothing.
You analyze images of garments (laid flat, hanging, worn, or e-commerce screenshots) OR photos of clothing tags / care labels.

Your job is to identify the clothing piece across ALL categories of clothing worldwide:
1. Tops: T-shirts, dress shirts, casual shirts, polo shirts, tank tops, henleys.
2. Bottoms: Trousers, dress slacks, chinos, jeans, denim pants, cargo pants, joggers, shorts.
3. Outerwear: Jackets, overshirts, coats, blazers, trench coats, bombers, parkas.
4. Knitwear: Sweaters, crewnecks, cardigans, pullovers, knit vests, hoodies.
5. South Asian & Draped Garments: Saris (sarees), lehengas, salwar kameez, kurtas, sherwanis, blouses, dupattas, anarkalis, churidars.

SPECIAL RULES FOR SARIS / SAREES:
- A sari is an unstitched draped fabric (typically 5-9 yards / 4.5-8.2 meters long, 1.1-1.2 meters wide).
- The SIZE-CRITICAL fitted component of a sari ensemble is the BLOUSE (choli). The blouse has measurable chest, shoulder, length, and sleeve dimensions.
- When you identify a sari, set category to "tops" and subcategory to "sari_blouse".
- For the size_chart, provide blouse measurements (chest_cm, shoulder_cm, length_cm, sleeve_cm).
- In fit_notes, include sari details: fabric type (silk, chiffon, georgette, cotton, banarasi, etc.), drape length in meters, border/pallu description.
- In fabric_description, describe the sari fabric itself (e.g. "Pure Kanjivaram Silk", "Banarasi Brocade", "Georgette with Zari Work").

SPECIAL RULES FOR KURTAS / KAMEEZ:
- Kurtas and kameez are category "tops", subcategory "kurta".
- Provide chest_cm, shoulder_cm, length_cm, sleeve_cm in size_chart.

SPECIAL RULES FOR LEHENGAS:
- A lehenga is a skirt, categorize as "bottoms", subcategory "lehenga".
- Provide waist_cm, hip_cm, length_cm (skirt length) in size_chart.

If the photo shows a clothing tag or care label:
- Read the brand name, size, material composition, cut/style name, RN number, or wash instructions.

Return ONLY a valid JSON object with this exact schema (no markdown, no backticks, no explanatory text):
{
  "brand": "Brand name (e.g. Levi's, COS, Zara, Uniqlo, Sabyasachi, FabIndia, Manyavar) or 'Standard Cut' if unknown",
  "name": "Specific model or descriptive title (e.g. 511 Slim Fit Jeans, Kanjivaram Silk Sari, Banarasi Brocade Saree, Anarkali Suit Set)",
  "category": "tops|bottoms|outerwear|knitwear",
  "subcategory": "jeans|trousers|chinos|pants|t-shirt|shirt|hoodie|jacket|sweater|shorts|sari_blouse|kurta|lehenga|sherwani",
  "color": "Detected color or wash (e.g. Indigo Dark Wash, Washed Black, Sand Beige, Royal Magenta with Gold Zari)",
  "fabric_description": "Material (e.g. 99% Cotton 1% Elastane Denim, Pure Kanjivaram Silk, Banarasi Brocade with Zari)",
  "retail_price": "Estimated retail price with symbol e.g. '$79' or '₹4,500' or ''",
  "available_sizes": ["28", "30", "32", "34", "36"] or ["XS", "S", "M", "L", "XL", "XXL"] or ["32", "34", "36", "38", "40", "42"],
  "detected_tag_size": "Size specifically seen on tag (e.g. '32', 'M', '31x32', '38') or null",
  "size_chart": {
    "size_tag": {
      // FOR BOTTOMS (pants/jeans/trousers/lehengas):
      // "waist_cm": 82, "hip_cm": 104, "thigh_cm": 60, "inseam_cm": 81, "rise_cm": 28
      // FOR TOPS / OUTERWEAR / KNITWEAR / SARI BLOUSES / KURTAS:
      // "chest_cm": 102, "shoulder_cm": 46, "length_cm": 72, "sleeve_cm": 65
    }
  },
  "fit_notes": "Concise silhouette summary (e.g. 'Slim straight cut with mid rise', 'Relaxed boxy drop-shoulder cut', 'Princess-cut sari blouse; 6.3m pure silk drape with contrast pallu')"
}

CRITICAL RULES:
- Trousers, pants, jeans, chinos, slacks, joggers, shorts, lehengas MUST be category 'bottoms'.
- Saris/sarees: category MUST be 'tops' (blouse is the fitted sizing component), subcategory 'sari_blouse'.
- Kurtas, kameez: category MUST be 'tops', subcategory 'kurta'.
- All measurements in size_chart must be in centimeters (cm).
- available_sizes must be an array of standard sizes for that garment type.
- Return ONLY the JSON object."""


def _synthesize_fallback_sizes(category: str, subcategory: str = "") -> tuple[list, dict]:
    """Provide realistic default size offerings and measurements when not detected."""
    sub = (subcategory or "").lower()
    if category == "bottoms" and not any(w in sub for w in ["jogger", "sweat"]):
        sizes = ["28", "29", "30", "31", "32", "33", "34", "36"]
        chart = {
            "28": {"waist_cm": 74.0, "hip_cm": 96.0, "thigh_cm": 56.0, "inseam_cm": 81.0, "rise_cm": 26.5},
            "29": {"waist_cm": 76.5, "hip_cm": 98.5, "thigh_cm": 57.5, "inseam_cm": 81.0, "rise_cm": 27.0},
            "30": {"waist_cm": 79.0, "hip_cm": 101.0, "thigh_cm": 59.0, "inseam_cm": 81.0, "rise_cm": 27.5},
            "31": {"waist_cm": 81.5, "hip_cm": 103.5, "thigh_cm": 60.5, "inseam_cm": 81.5, "rise_cm": 28.0},
            "32": {"waist_cm": 84.0, "hip_cm": 106.0, "thigh_cm": 62.0, "inseam_cm": 81.5, "rise_cm": 28.5},
            "33": {"waist_cm": 86.5, "hip_cm": 108.5, "thigh_cm": 63.5, "inseam_cm": 82.0, "rise_cm": 29.0},
            "34": {"waist_cm": 89.0, "hip_cm": 111.0, "thigh_cm": 65.0, "inseam_cm": 82.0, "rise_cm": 29.5},
            "36": {"waist_cm": 94.0, "hip_cm": 116.0, "thigh_cm": 68.0, "inseam_cm": 82.5, "rise_cm": 30.5},
        }
    else:
        sizes = ["XS", "S", "M", "L", "XL", "XXL"]
        chart = {
            "XS": {"chest_cm": 92.0, "shoulder_cm": 43.0, "length_cm": 68.0, "sleeve_cm": 23.0},
            "S":  {"chest_cm": 96.0, "shoulder_cm": 45.0, "length_cm": 70.0, "sleeve_cm": 24.0},
            "M":  {"chest_cm": 102.0, "shoulder_cm": 47.5, "length_cm": 72.0, "sleeve_cm": 25.0},
            "L":  {"chest_cm": 108.0, "shoulder_cm": 50.0, "length_cm": 74.0, "sleeve_cm": 26.0},
            "XL": {"chest_cm": 116.0, "shoulder_cm": 53.0, "length_cm": 76.0, "sleeve_cm": 27.0},
            "XXL":{"chest_cm": 124.0, "shoulder_cm": 56.0, "length_cm": 78.0, "sleeve_cm": 28.0},
        }
    return sizes, chart


def _sync_gemini_vision_call(client: genai.Client, image_bytes: bytes, mime_type: str) -> str:
    """Execute Gemini vision call synchronously."""
    env_model = os.environ.get("GEMINI_MODEL")
    candidate_models = [env_model] if env_model else ["gemini-2.5-flash", "gemini-3.8-flash"]
    last_err = None

    prompt = (
        "Identify this garment or clothing tag. Determine the brand, exact piece name, "
        "clothing category (tops, bottoms, outerwear, knitwear), and sizing chart. "
        "This includes ALL garment types worldwide: Western wear, saris/sarees, "
        "kurtas, lehengas, sherwanis, salwar kameez, and any ethnic or traditional clothing."
    )

    for model_name in candidate_models:
        try:
            response = client.models.generate_content(
                model=model_name,
                contents=[
                    prompt,
                    types.Part.from_bytes(data=image_bytes, mime_type=mime_type),
                ],
                config=types.GenerateContentConfig(
                    system_instruction=VISION_SYSTEM_INSTRUCTION,
                    temperature=0.1,
                )
            )
            if response and response.text:
                return response.text
        except Exception as e:
            last_err = e
            err_str = str(e).lower()
            if "api_key" in err_str or "unauthenticated" in err_str or "401" in err_str:
                raise e
            continue

    if last_err:
        raise last_err
    raise RuntimeError("No response received from Gemini Vision.")


async def identify_garment_from_image(image_bytes: bytes, mime_type: str = "image/jpeg") -> Dict[str, Any]:
    """
    Multimodal clothing analyzer: recognizes shirts, trousers, jeans, jackets,
    care tags, or brand labels from photo.
    """
    client = _get_client()
    if not client:
        return {
            "error": "No API key configured in .env for Gemini Vision."
        }

    try:
        raw_text = await asyncio.to_thread(_sync_gemini_vision_call, client, image_bytes, mime_type)
        data = _clean_json_response(raw_text)

        # Normalize and validate extracted fields
        brand = (data.get("brand") or "").strip() or "Standard Cut"
        name = (data.get("name") or "").strip() or "Garment"
        category = (data.get("category") or "").strip().lower()
        subcategory = (data.get("subcategory") or "").strip().lower()

        # Enforce all-rounder classification
        bottom_keywords = ["pant", "trouser", "jean", "chino", "short", "jogger", "slack", "bottom", "cargo", "lehenga"]
        outerwear_keywords = ["jacket", "coat", "blazer", "parka", "windbreaker", "overshirt", "bomber", "sherwani"]
        knitwear_keywords = ["sweater", "cardigan", "knit", "pullover"]
        # Saris, kurtas, blouses → tops (blouse is the fitted sizing component)
        tops_keywords = ["sari", "saree", "blouse", "choli", "kurta", "kameez", "anarkali", "kurti"]

        combined_text = f"{name} {subcategory} {category}".lower()
        if any(w in combined_text for w in tops_keywords):
            category = "tops"
            # Refine subcategory for sari detection
            if any(w in combined_text for w in ["sari", "saree", "choli"]):
                subcategory = subcategory or "sari_blouse"
            elif any(w in combined_text for w in ["kurta", "kameez", "kurti", "anarkali"]):
                subcategory = subcategory or "kurta"
        elif any(w in combined_text for w in bottom_keywords):
            category = "bottoms"
        elif any(w in combined_text for w in outerwear_keywords):
            category = "outerwear"
        elif any(w in combined_text for w in knitwear_keywords):
            category = "knitwear"
        elif category not in ("tops", "bottoms", "outerwear", "knitwear"):
            category = "tops"

        data["brand"] = brand
        data["name"] = name
        data["category"] = category
        data["subcategory"] = subcategory

        # Ensure available sizes
        avail_sizes = data.get("available_sizes")
        if not avail_sizes or not isinstance(avail_sizes, list) or len(avail_sizes) == 0:
            def_sizes, def_chart = _synthesize_fallback_sizes(category, subcategory)
            data["available_sizes"] = def_sizes
            if not data.get("size_chart"):
                data["size_chart"] = def_chart
        else:
            data["available_sizes"] = [str(s).strip() for s in avail_sizes]

        # Ensure size chart covers all available sizes
        size_chart = data.get("size_chart")
        _, def_chart = _synthesize_fallback_sizes(category, subcategory)

        clean_chart = {}
        if isinstance(size_chart, dict) and size_chart:
            if "size_tag" in size_chart and len(size_chart) == 1:
                # Model provided single template measurement; grade using standard CAD offsets
                template = size_chart["size_tag"]
                for sz in data["available_sizes"]:
                    if sz in def_chart:
                        clean_chart[sz] = def_chart[sz]
                    else:
                        clean_chart[sz] = template
            else:
                for sz in data["available_sizes"]:
                    if sz in size_chart and isinstance(size_chart[sz], dict):
                        clean_chart[sz] = size_chart[sz]
                    elif sz in def_chart:
                        clean_chart[sz] = def_chart[sz]

        if not clean_chart:
            clean_chart = def_chart
            data["available_sizes"] = list(def_chart.keys())

        data["size_chart"] = clean_chart

        # Compute internal dimensional mapping
        data["ai_dims"] = convert_ai_sizes_to_dims(data["size_chart"], category)

        return data

    except Exception as e:
        err_msg = str(e)
        if "API_KEY" in err_msg.upper() or "401" in err_msg or "403" in err_msg:
            return {"error": "Invalid API key in .env"}
        if "RESOURCE_EXHAUSTED" in err_msg or "429" in err_msg:
            return {"error": "API rate limit reached. Please wait a moment and try again."}
        return {"error": f"Vision analysis failed: {err_msg}"}
