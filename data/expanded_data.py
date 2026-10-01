"""
AnthroFit OS - Expanded Benchmark Anchors & Comprehensive Retailer Target Catalog
"""
from typing import Dict, List
from engine.models import GarmentSku, FabricMechanics, TopCadDimensions, BottomCadDimensions

# Popular User Inventory Anchors across common brands
EXPANDED_USER_ANCHORS: List[Dict] = [
    # Tops
    {
        "id": "REF-UNIQLO-AIRISM-M",
        "category": "tops",
        "brand": "Uniqlo",
        "model_name": "AIRism Cotton Oversized Crew Neck T-Shirt",
        "tag_size": "M",
        "color": "Black",
        "stretch": "Slight mechanical give (8.5%)",
        "composition": "53% Cotton, 47% Polyester",
        "display_name": "Uniqlo AIRism Oversized Tee - Size M",
        "chest_half_cm": 58.5,
        "shoulder_cm": 53.0,
        "torso_cm": 72.0,
        "sleeve_cm": 26.5
    },
    {
        "id": "REF-UNIQLO-AIRISM-L",
        "category": "tops",
        "brand": "Uniqlo",
        "model_name": "AIRism Cotton Oversized Crew Neck T-Shirt",
        "tag_size": "L",
        "color": "White",
        "stretch": "Slight mechanical give (8.5%)",
        "composition": "53% Cotton, 47% Polyester",
        "display_name": "Uniqlo AIRism Oversized Tee - Size L",
        "chest_half_cm": 61.5,
        "shoulder_cm": 55.0,
        "torso_cm": 74.5,
        "sleeve_cm": 27.5
    },
    {
        "id": "REF-LULU-5YEAR-M",
        "category": "tops",
        "brand": "Lululemon",
        "model_name": "Fundamental T-Shirt",
        "tag_size": "M",
        "color": "Navy",
        "stretch": "High recovery stretch (26.0%)",
        "composition": "Pima Cotton, Lyocell, Elastane",
        "display_name": "Lululemon Fundamental Tee - Size M",
        "chest_half_cm": 52.0,
        "shoulder_cm": 46.5,
        "torso_cm": 71.0,
        "sleeve_cm": 22.0
    },
    {
        "id": "REF-ZARA-SLIM-M",
        "category": "tops",
        "brand": "Zara",
        "model_name": "Tailored Oxford Button-Down Shirt",
        "tag_size": "M (38-40)",
        "color": "Sky Blue",
        "stretch": "Rigid poplin (2.0%)",
        "composition": "100% Poplin Cotton",
        "display_name": "Zara Tailored Oxford Shirt - Size M",
        "chest_half_cm": 53.0,
        "shoulder_cm": 47.0,
        "torso_cm": 74.0,
        "sleeve_cm": 64.0
    },
    {
        "id": "REF-NIKE-CLUB-L",
        "category": "tops",
        "brand": "Nike",
        "model_name": "Club Fleece Pullover Hoodie",
        "tag_size": "L",
        "color": "Heather Grey",
        "stretch": "Medium fleece give (12.0%)",
        "composition": "80% Cotton, 20% Polyester",
        "display_name": "Nike Sportswear Club Fleece Hoodie - Size L",
        "chest_half_cm": 62.0,
        "shoulder_cm": 51.0,
        "torso_cm": 71.5,
        "sleeve_cm": 65.5
    },
    # Bottoms
    {
        "id": "REF-LEVIS-511-32",
        "category": "bottoms",
        "brand": "Levi's",
        "model_name": "511 Slim Fit Stretch Jeans",
        "tag_size": "32x32",
        "color": "Dark Stonewash",
        "stretch": "Subtle comfort give (6.0%)",
        "composition": "99% Cotton, 1% Elastane",
        "display_name": "Levi's 511 Slim Jeans - 32x32",
        "waist_half_cm": 42.5,
        "hip_half_cm": 52.0,
        "thigh_half_cm": 29.5,
        "inseam_cm": 81.0,
        "front_rise_cm": 26.0
    },
    {
        "id": "REF-LEVIS-501-32",
        "category": "bottoms",
        "brand": "Levi's",
        "model_name": "501 Original Fit Rigid Denim",
        "tag_size": "32x32",
        "color": "Raw Indigo",
        "stretch": "Zero stretch (1.5%)",
        "composition": "100% Cotton",
        "display_name": "Levi's 501 Original Straight - 32x32",
        "waist_half_cm": 42.0,
        "hip_half_cm": 53.5,
        "thigh_half_cm": 31.5,
        "inseam_cm": 81.0,
        "front_rise_cm": 29.0
    },
    {
        "id": "REF-LULU-ABC-32",
        "category": "bottoms",
        "brand": "Lululemon",
        "model_name": "ABC Pant Slim-Fit 32L",
        "tag_size": "32",
        "color": "Obsidian Grey",
        "stretch": "Four-way warp stretch (24.0%)",
        "composition": "100% Elastomultiester Warpstreme",
        "display_name": "Lululemon ABC Pant Slim 32L - Size 32",
        "waist_half_cm": 43.0,
        "hip_half_cm": 52.5,
        "thigh_half_cm": 30.0,
        "inseam_cm": 81.5,
        "front_rise_cm": 26.5
    }
]

# Target Items that user is shopping for
TARGET_SHOPPING_ITEMS: List[Dict] = [
    {
        "id": "TARGET-COS-BOXY-TEE",
        "category": "tops",
        "brand": "COS",
        "name": "Heavyweight Clean-Cut T-Shirt",
        "price": 49.00,
        "fabric": "100% Mercerized Organic Cotton (Structured 240 GSM, 3.0% stretch)",
        "desc": "A wardrobe cornerstone cut from substantial jersey cotton with precise double-topstitched hems.",
        "sizes_available": ["XS", "S", "M", "L", "XL"],
        "options": [
            {"size": "S", "chest": 54.0, "shoulder": 48.0, "torso": 70.0, "sleeve": 24.0},
            {"size": "M", "chest": 58.0, "shoulder": 52.5, "torso": 72.5, "sleeve": 26.0},
            {"size": "L", "chest": 62.0, "shoulder": 55.5, "torso": 75.0, "sleeve": 27.5},
            {"size": "XL", "chest": 66.0, "shoulder": 58.0, "torso": 77.0, "sleeve": 29.0}
        ]
    },
    {
        "id": "TARGET-ZARA-OVERCOAT",
        "category": "tops",
        "brand": "Zara Studio",
        "name": "Structured Double-Breasted Wool Coat",
        "price": 229.00,
        "fabric": "78% Manteco Wool, 22% Polyamide (Rigid Structured Drape, 0.5% stretch)",
        "desc": "Italian fabric coat featuring peak lapels, interior welt pockets, and a tailored shoulder silhouette.",
        "sizes_available": ["S (36)", "M (38-40)", "L (42-44)", "XL (46)"],
        "options": [
            {"size": "S (36)", "chest": 55.0, "shoulder": 47.0, "torso": 104.0, "sleeve": 64.0},
            {"size": "M (38-40)", "chest": 59.0, "shoulder": 50.0, "torso": 106.0, "sleeve": 65.5},
            {"size": "L (42-44)", "chest": 63.0, "shoulder": 52.5, "torso": 108.0, "sleeve": 67.0},
            {"size": "XL (46)", "chest": 67.0, "shoulder": 55.0, "torso": 110.0, "sleeve": 68.5}
        ]
    },
    {
        "id": "TARGET-ACNE-1996-DENIM",
        "category": "bottoms",
        "brand": "Acne Studios",
        "name": "1996 Straight Leg Rigid Jeans",
        "price": 360.00,
        "fabric": "100% Cotton Mid-Blue Vintage Denim (100% Rigid, 0% Elastane)",
        "desc": "High-rise vintage cut with straight leg profile crafted from rigid denim that shapes over time.",
        "sizes_available": ["30/32", "31/32", "32/32", "33/32", "34/32"],
        "options": [
            {"size": "30/32", "waist": 40.0, "thigh": 29.0, "inseam": 82.0, "rise": 28.0},
            {"size": "31/32", "waist": 41.5, "thigh": 30.0, "inseam": 82.5, "rise": 28.5},
            {"size": "32/32", "waist": 43.0, "thigh": 31.0, "inseam": 83.0, "rise": 29.0},
            {"size": "33/32", "waist": 44.5, "thigh": 32.2, "inseam": 83.5, "rise": 29.5},
            {"size": "34/32", "waist": 46.0, "thigh": 33.5, "inseam": 84.0, "rise": 30.0}
        ]
    }
]
