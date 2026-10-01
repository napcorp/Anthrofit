"""
Real CAD Product Catalog — AnthroFit OS
Manufacturer-spec garment dimensions (all measurements in cm unless noted)
Half-measurements for chest/hip/thigh (as per industry pattern standard).
"""

from typing import Dict, List

# ─────────────────────────────────────────────────────────────
# FABRIC PHYSICS — stretch factor & post-wash shrinkage curves
# ─────────────────────────────────────────────────────────────
FABRIC_SPECS: Dict[str, dict] = {
    "cotton_jersey_light": {
        "composition": "100% Cotton",
        "gsm": 160,
        "stretch_pct": 4.5,    # % elongation at 4.5kg force
        "shrink_pct": 3.2,     # % linear shrinkage after 3 washes (40°C)
    },
    "cotton_jersey_heavy": {
        "composition": "100% Cotton",
        "gsm": 240,
        "stretch_pct": 2.8,
        "shrink_pct": 2.5,
    },
    "cotton_poly_blend": {
        "composition": "53% Cotton / 47% Polyester",
        "gsm": 185,
        "stretch_pct": 8.5,
        "shrink_pct": 1.0,
    },
    "cotton_elastane_slim": {
        "composition": "97% Cotton / 3% Elastane",
        "gsm": 330,
        "stretch_pct": 14.0,
        "shrink_pct": 1.5,
    },
    "denim_rigid": {
        "composition": "100% Cotton (12oz denim)",
        "gsm": 407,
        "stretch_pct": 1.5,
        "shrink_pct": 3.5,
    },
    "denim_stretch": {
        "composition": "98% Cotton / 2% Elastane (11oz)",
        "gsm": 373,
        "stretch_pct": 14.0,
        "shrink_pct": 1.8,
    },
    "merino_knit": {
        "composition": "100% Merino Wool",
        "gsm": 280,
        "stretch_pct": 22.0,
        "shrink_pct": 0.8,
    },
    "nylon_lycra": {
        "composition": "85% Nylon / 15% Lycra",
        "gsm": 165,
        "stretch_pct": 38.0,
        "shrink_pct": 0.3,
    },
    "cotton_fleece": {
        "composition": "77% Cotton / 23% Polyester (fleece)",
        "gsm": 310,
        "stretch_pct": 12.0,
        "shrink_pct": 2.1,
    },
    "wool_blend_woven": {
        "composition": "72% Wool / 28% Polyamide (woven)",
        "gsm": 420,
        "stretch_pct": 3.5,
        "shrink_pct": 1.2,
    },
}

# ─────────────────────────────────────────────────────────────
# ANCHOR LIBRARY — garments users typically own
# Dimensions represent raw pattern (pre-shrinkage, pre-stretch)
# ─────────────────────────────────────────────────────────────
ANCHOR_LIBRARY: Dict[str, dict] = {
    "ANCHOR-UNIQLO-AIRISM-M": {
        "brand": "Uniqlo",
        "model": "AIRism Cotton Oversized T-Shirt",
        "size_tag": "M",
        "category": "tops",
        "fabric_key": "cotton_poly_blend",
        "dims": {
            "chest_half": 29.25,    # 58.5 / 2
            "shoulder_width": 53.0,
            "sleeve_length": 26.5,
            "torso_length": 72.0,
            "neck_width": 18.5,
        },
    },
    "ANCHOR-UNIQLO-AIRISM-L": {
        "brand": "Uniqlo",
        "model": "AIRism Cotton Oversized T-Shirt",
        "size_tag": "L",
        "category": "tops",
        "fabric_key": "cotton_poly_blend",
        "dims": {
            "chest_half": 30.75,
            "shoulder_width": 55.0,
            "sleeve_length": 27.5,
            "torso_length": 74.5,
            "neck_width": 19.0,
        },
    },
    "ANCHOR-LULULEMON-FUNDAMENTAL-M": {
        "brand": "Lululemon",
        "model": "Fundamental T-Shirt",
        "size_tag": "M",
        "category": "tops",
        "fabric_key": "nylon_lycra",
        "dims": {
            "chest_half": 26.0,
            "shoulder_width": 46.5,
            "sleeve_length": 22.0,
            "torso_length": 71.0,
            "neck_width": 17.5,
        },
    },
    "ANCHOR-NIKE-CLUB-FLEECE-L": {
        "brand": "Nike",
        "model": "Club Fleece Hoodie",
        "size_tag": "L",
        "category": "tops",
        "fabric_key": "cotton_fleece",
        "dims": {
            "chest_half": 31.0,
            "shoulder_width": 51.0,
            "sleeve_length": 66.0,
            "torso_length": 71.5,
            "neck_width": 20.0,
        },
    },
    "ANCHOR-LEVIS-511-32": {
        "brand": "Levi's",
        "model": "511 Slim Stretch Jeans",
        "size_tag": "32×32",
        "category": "bottoms",
        "fabric_key": "denim_stretch",
        "dims": {
            "waist_half": 21.25,    # 42.5 / 2
            "hip_half": 26.5,
            "thigh_half": 14.75,
            "knee_half": 10.0,
            "leg_opening_half": 9.0,
            "inseam": 81.0,
            "front_rise": 27.5,
        },
    },
    "ANCHOR-LEVIS-501-32": {
        "brand": "Levi's",
        "model": "501 Original Fit Jeans",
        "size_tag": "32×32",
        "category": "bottoms",
        "fabric_key": "denim_rigid",
        "dims": {
            "waist_half": 21.0,
            "hip_half": 27.5,
            "thigh_half": 15.75,
            "knee_half": 11.0,
            "leg_opening_half": 10.0,
            "inseam": 81.0,
            "front_rise": 29.0,
        },
    },
    "ANCHOR-LULULEMON-ABC-32": {
        "brand": "Lululemon",
        "model": "ABC Jogger Trouser",
        "size_tag": "32",
        "category": "bottoms",
        "fabric_key": "nylon_lycra",
        "dims": {
            "waist_half": 21.5,
            "hip_half": 27.0,
            "thigh_half": 15.0,
            "knee_half": 10.5,
            "leg_opening_half": 9.5,
            "inseam": 81.5,
            "front_rise": 28.0,
        },
    },
    "ANCHOR-ARKET-BOXY-M": {
        "brand": "Arket",
        "model": "Jersey Boxy T-Shirt",
        "size_tag": "M",
        "category": "tops",
        "fabric_key": "cotton_jersey_heavy",
        "dims": {
            "chest_half": 30.0,
            "shoulder_width": 52.5,
            "sleeve_length": 25.0,
            "torso_length": 73.5,
            "neck_width": 19.5,
        },
    },
}

# ─────────────────────────────────────────────────────────────
# PRODUCT TARGET CATALOG — per-size CAD dimensions
# ─────────────────────────────────────────────────────────────
PRODUCT_CATALOG: Dict[str, dict] = {
    "TARGET-COS-HEAVYWEIGHT-TEE": {
        "brand": "COS",
        "name": "Heavyweight Clean-Cut T-Shirt",
        "category": "tops",
        "fabric_key": "cotton_jersey_heavy",
        "sizes": {
            "XS": {"chest_half": 27.0,  "shoulder_width": 48.5, "sleeve_length": 23.5, "torso_length": 70.0, "neck_width": 18.0},
            "S":  {"chest_half": 28.5,  "shoulder_width": 51.0, "sleeve_length": 24.5, "torso_length": 71.5, "neck_width": 18.5},
            "M":  {"chest_half": 30.25, "shoulder_width": 54.0, "sleeve_length": 25.5, "torso_length": 73.0, "neck_width": 19.0},
            "L":  {"chest_half": 32.0,  "shoulder_width": 57.0, "sleeve_length": 26.5, "torso_length": 75.0, "neck_width": 19.5},
            "XL": {"chest_half": 33.75, "shoulder_width": 60.0, "sleeve_length": 27.5, "torso_length": 77.0, "neck_width": 20.0},
        },
    },
    "TARGET-ZARA-STRUCTURED-SHIRT": {
        "brand": "Zara",
        "name": "Structured Slim Oxford Shirt",
        "category": "tops",
        "fabric_key": "cotton_jersey_light",
        "sizes": {
            "XS": {"chest_half": 25.5,  "shoulder_width": 44.0, "sleeve_length": 64.0, "torso_length": 73.0, "neck_width": 18.0},
            "S":  {"chest_half": 27.0,  "shoulder_width": 46.5, "sleeve_length": 65.0, "torso_length": 74.5, "neck_width": 18.5},
            "M":  {"chest_half": 28.75, "shoulder_width": 49.0, "sleeve_length": 66.0, "torso_length": 76.0, "neck_width": 19.0},
            "L":  {"chest_half": 30.5,  "shoulder_width": 51.5, "sleeve_length": 67.0, "torso_length": 77.5, "neck_width": 19.5},
            "XL": {"chest_half": 32.5,  "shoulder_width": 54.0, "sleeve_length": 68.0, "torso_length": 79.0, "neck_width": 20.0},
        },
    },
    "TARGET-ACNE-1996-JEANS": {
        "brand": "Acne Studios",
        "name": "1996 Loose Straight Jeans",
        "category": "bottoms",
        "fabric_key": "denim_rigid",
        "sizes": {
            "29×32": {"waist_half": 19.75, "hip_half": 25.5, "thigh_half": 15.0, "knee_half": 11.5, "leg_opening_half": 10.5, "inseam": 82.0, "front_rise": 27.5},
            "30×32": {"waist_half": 20.25, "hip_half": 26.0, "thigh_half": 15.4, "knee_half": 11.8, "leg_opening_half": 10.8, "inseam": 82.0, "front_rise": 28.0},
            "31×32": {"waist_half": 20.75, "hip_half": 26.5, "thigh_half": 15.8, "knee_half": 12.1, "leg_opening_half": 11.1, "inseam": 82.5, "front_rise": 28.5},
            "32×32": {"waist_half": 21.5,  "hip_half": 27.0, "thigh_half": 16.1, "knee_half": 12.4, "leg_opening_half": 11.4, "inseam": 83.0, "front_rise": 29.0},
            "33×32": {"waist_half": 22.25, "hip_half": 27.5, "thigh_half": 16.5, "knee_half": 12.8, "leg_opening_half": 11.8, "inseam": 83.5, "front_rise": 29.5},
        },
    },
    "TARGET-ARKET-KNIT-POLO": {
        "brand": "Arket",
        "name": "Merino Knit Polo Shirt",
        "category": "tops",
        "fabric_key": "merino_knit",
        "sizes": {
            "XS": {"chest_half": 25.5,  "shoulder_width": 44.0, "sleeve_length": 25.0, "torso_length": 68.0, "neck_width": 18.0},
            "S":  {"chest_half": 27.0,  "shoulder_width": 46.5, "sleeve_length": 26.0, "torso_length": 69.5, "neck_width": 18.5},
            "M":  {"chest_half": 28.5,  "shoulder_width": 49.0, "sleeve_length": 27.0, "torso_length": 71.0, "neck_width": 19.0},
            "L":  {"chest_half": 30.5,  "shoulder_width": 51.5, "sleeve_length": 28.0, "torso_length": 73.0, "neck_width": 19.5},
            "XL": {"chest_half": 32.5,  "shoulder_width": 54.0, "sleeve_length": 29.0, "torso_length": 75.0, "neck_width": 20.0},
        },
    },
    "TARGET-LULULEMON-COMMISSION-SLIM-32": {
        "brand": "Lululemon",
        "name": "Commission Slim-Fit Trousers",
        "category": "bottoms",
        "fabric_key": "nylon_lycra",
        "sizes": {
            "28": {"waist_half": 19.0, "hip_half": 25.0, "thigh_half": 14.0, "knee_half": 10.0, "leg_opening_half": 8.5, "inseam": 81.0, "front_rise": 27.0},
            "30": {"waist_half": 20.0, "hip_half": 25.8, "thigh_half": 14.4, "knee_half": 10.3, "leg_opening_half": 8.8, "inseam": 81.0, "front_rise": 27.5},
            "32": {"waist_half": 21.0, "hip_half": 26.5, "thigh_half": 15.0, "knee_half": 10.8, "leg_opening_half": 9.2, "inseam": 81.5, "front_rise": 28.0},
            "34": {"waist_half": 22.0, "hip_half": 27.5, "thigh_half": 15.6, "knee_half": 11.2, "leg_opening_half": 9.5, "inseam": 82.0, "front_rise": 28.5},
        },
    },
}

# ─────────────────────────────────────────────────────────────
# DOMAIN → CATALOG MATCHER (for URL-based auto-detection)
# ─────────────────────────────────────────────────────────────
DOMAIN_BRAND_MAP = {
    "cos.com":        "COS",
    "arket.com":      "Arket",
    "zara.com":       "Zara",
    "asos.com":       "ASOS",
    "uniqlo.com":     "Uniqlo",
    "hm.com":         "H&M",
    "acnestudios.com":"Acne Studios",
    "lululemon.com":  "Lululemon",
    "nike.com":       "Nike",
    "levis.com":      "Levi's",
    "adidas.com":     "Adidas",
    "gap.com":        "Gap",
    "nordstrom.com":  "Nordstrom",
    "apc.fr":         "A.P.C.",
    "stories.com":    "&Other Stories",
}
