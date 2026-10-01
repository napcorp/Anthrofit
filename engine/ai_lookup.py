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
    # List of models to try in priority order (Gemini 3 Flash first)
    candidate_models = ["gemini-3.0-flash", "gemini-2.5-flash", "gemini-2.0-flash"]
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
    Returns {size_tag: {dim_key: value_in_half_cm, ...}, ...}
    """
    result = {}
    is_bottom = category == "bottoms"

    for size_tag, measurements in size_chart.items():
        if not isinstance(measurements, dict):
            continue
        dims = {}
        if is_bottom:
            if "waist_cm" in measurements and measurements["waist_cm"]:
                dims["waist_half"] = float(measurements["waist_cm"]) / 2.0
            if "hip_cm" in measurements and measurements["hip_cm"]:
                dims["hip_half"] = float(measurements["hip_cm"]) / 2.0
            if "thigh_cm" in measurements and measurements["thigh_cm"]:
                dims["thigh_half"] = float(measurements["thigh_cm"]) / 2.0
            if "inseam_cm" in measurements and measurements["inseam_cm"]:
                dims["inseam"] = float(measurements["inseam_cm"])
            if "rise_cm" in measurements and measurements["rise_cm"]:
                dims["front_rise"] = float(measurements["rise_cm"])
            if "knee_cm" in measurements and measurements["knee_cm"]:
                dims["knee_half"] = float(measurements["knee_cm"]) / 2.0
            if "leg_opening_cm" in measurements and measurements["leg_opening_cm"]:
                dims["leg_opening_half"] = float(measurements["leg_opening_cm"]) / 2.0
        else:
            if "chest_cm" in measurements and measurements["chest_cm"]:
                dims["chest_half"] = float(measurements["chest_cm"]) / 2.0
            if "shoulder_cm" in measurements and measurements["shoulder_cm"]:
                dims["shoulder_width"] = float(measurements["shoulder_cm"])
            if "length_cm" in measurements and measurements["length_cm"]:
                dims["torso_length"] = float(measurements["length_cm"])
            if "sleeve_cm" in measurements and measurements["sleeve_cm"]:
                dims["sleeve_length"] = float(measurements["sleeve_cm"])
            if "neck_cm" in measurements and measurements["neck_cm"]:
                dims["neck_width"] = float(measurements["neck_cm"])

        if dims:
            result[size_tag] = dims

    return result
