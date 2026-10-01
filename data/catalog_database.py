"""
AnthroFit OS - Reference Wardrobe Database & Target Retailer CAD Patterns
Offline realistic dataset modeled after actual manufacturer flat-lay tech packs.
"""
from typing import Dict, List
from engine.models import GarmentSku, FabricMechanics, TopCadDimensions, BottomCadDimensions

# Popular User Wardrobe Anchors (Garments shoppers commonly own that fit great)
REFERENCE_ANCHORS: Dict[str, GarmentSku] = {
    # Uniqlo U Crew Neck Tee - Size M
    "REF-UNIQLO-AIRISM-M": GarmentSku(
        sku_id="REF-UNIQLO-AIRISM-M",
        brand="Uniqlo",
        model_name="Airism Cotton Oversized Crew",
        colorway="Matte Black",
        category="tops",
        label_size="M",
        fabric=FabricMechanics(
            composition="53% Cotton, 47% Polyester",
            elastane_pct=0.0,
            stretch_yield_pct=8.5,
            shrinkage_wash_pct=1.0,
            weave_tension="semi_rigid",
            drape_stiffness_g_cm=16.5
        ),
        top_dimensions=TopCadDimensions(
            chest_half_cm=58.5,
            shoulder_width_cm=53.0,
            sleeve_length_cm=26.5,
            bicep_half_cm=21.0,
            torso_length_cm=72.0,
            neck_girth_cm=42.0,
            waist_half_cm=58.0
        ),
        cut_classification="Boxy Dropped Shoulder",
        retail_price_usd=24.90,
        description="Benchmark heavyweight drop-shoulder oversized silhouette."
    ),

    # Uniqlo U Crew Neck Tee - Size L
    "REF-UNIQLO-AIRISM-L": GarmentSku(
        sku_id="REF-UNIQLO-AIRISM-L",
        brand="Uniqlo",
        model_name="Airism Cotton Oversized Crew",
        colorway="Heather Grey",
        category="tops",
        label_size="L",
        fabric=FabricMechanics(
            composition="53% Cotton, 47% Polyester",
            elastane_pct=0.0,
            stretch_yield_pct=8.5,
            shrinkage_wash_pct=1.0,
            weave_tension="semi_rigid",
            drape_stiffness_g_cm=16.5
        ),
        top_dimensions=TopCadDimensions(
            chest_half_cm=61.5,
            shoulder_width_cm=55.0,
            sleeve_length_cm=27.5,
            bicep_half_cm=22.5,
            torso_length_cm=74.5,
            neck_girth_cm=43.5,
            waist_half_cm=61.0
        ),
        cut_classification="Boxy Dropped Shoulder",
        retail_price_usd=24.90,
        description="Standard benchmark large boxy tee."
    ),

    # Lululemon 5-Year Basic Crew - Size M
    "REF-LULU-5YEAR-M": GarmentSku(
        sku_id="REF-LULU-5YEAR-M",
        brand="Lululemon",
        model_name="Fundamental Performance Tee",
        colorway="Heather Navy",
        category="tops",
        label_size="M",
        fabric=FabricMechanics(
            composition="40% Pima Cotton, 37% Lyocell, 13% Poly, 10% Elastane",
            elastane_pct=10.0,
            stretch_yield_pct=26.0,
            shrinkage_wash_pct=0.5,
            weave_tension="high_recovery",
            drape_stiffness_g_cm=11.2
        ),
        top_dimensions=TopCadDimensions(
            chest_half_cm=52.0,
            shoulder_width_cm=46.5,
            sleeve_length_cm=22.0,
            bicep_half_cm=18.0,
            torso_length_cm=71.0,
            neck_girth_cm=41.0,
            waist_half_cm=49.5
        ),
        cut_classification="Tailored Athletic",
        retail_price_usd=68.00,
        description="High stretch athletic recovery drape."
    ),

    # Levi's 511 Slim Jeans - 32x32
    "REF-LEVIS-511-32": GarmentSku(
        sku_id="REF-LEVIS-511-32",
        brand="Levi's",
        model_name="511 Slim Fit Denim",
        colorway="Indigo Stonewash",
        category="bottoms",
        label_size="32x32",
        fabric=FabricMechanics(
            composition="99% Cotton, 1% Elastane",
            elastane_pct=1.0,
            stretch_yield_pct=6.0,
            shrinkage_wash_pct=2.2,
            weave_tension="semi_rigid",
            drape_stiffness_g_cm=32.0
        ),
        bottom_dimensions=BottomCadDimensions(
            waist_half_cm=42.5,
            hip_half_cm=52.0,
            front_rise_cm=26.0,
            back_rise_cm=36.5,
            thigh_half_cm=29.5,
            knee_half_cm=20.5,
            inseam_cm=81.0,
            leg_opening_half_cm=18.0
        ),
        cut_classification="Slim Tapered",
        retail_price_usd=89.50,
        description="Classic slim cut denim with subtle comfort stretch."
    ),

    # Levi's 501 Original Straight - 32x32
    "REF-LEVIS-501-32": GarmentSku(
        sku_id="REF-LEVIS-501-32",
        brand="Levi's",
        model_name="501 Original Fit Rigid",
        colorway="Dark Raw Blue",
        category="bottoms",
        label_size="32x32",
        fabric=FabricMechanics(
            composition="100% Rigid BCI Cotton",
            elastane_pct=0.0,
            stretch_yield_pct=1.5,
            shrinkage_wash_pct=3.0,
            weave_tension="rigid",
            drape_stiffness_g_cm=42.0
        ),
        bottom_dimensions=BottomCadDimensions(
            waist_half_cm=42.0,
            hip_half_cm=53.5,
            front_rise_cm=29.0,
            back_rise_cm=38.5,
            thigh_half_cm=31.5,
            knee_half_cm=22.5,
            inseam_cm=81.0,
            leg_opening_half_cm=20.5
        ),
        cut_classification="Straight Classic",
        retail_price_usd=98.00,
        description="100% rigid vintage cut denim without synthetic give."
    )
}

# Retailer Target Catalog Products (e.g. Atelier Nordic / Aura Studio brand)
RETAILER_CATALOG_ITEMS = [
    {
        "id": "PROD-ATELIER-HEAVY-TEE",
        "title": "Minimalist 280GSM Heavyweight Tee",
        "brand": "ATELIER NORDIC",
        "category": "tops",
        "price_usd": 78.00,
        "colorway": "Chalk / Bone",
        "material_display": "100% Combed Compact Cotton (Zero Polyester)",
        "hero_image": "/static/img/heavy_tee.svg",
        "story": "Engineered with dense 280 GSM Japanese jersey knit. Square architectural shoulder line with micro-rib collar designed not to stretch.",
        "skus": {
            "CUT-1": GarmentSku(
                sku_id="SKU-AT-HTEE-01",
                brand="ATELIER NORDIC",
                model_name="280GSM Heavyweight Tee",
                colorway="Chalk Bone",
                category="tops",
                label_size="Cut 01 (Slim)",
                fabric=FabricMechanics(
                    composition="100% Organic Heavy Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=3.5,
                    shrinkage_wash_pct=1.8,
                    weave_tension="semi_rigid",
                    drape_stiffness_g_cm=24.0
                ),
                top_dimensions=TopCadDimensions(
                    chest_half_cm=53.5,
                    shoulder_width_cm=47.5,
                    sleeve_length_cm=23.0,
                    bicep_half_cm=19.0,
                    torso_length_cm=69.0,
                    neck_girth_cm=40.5,
                    waist_half_cm=52.5
                ),
                cut_classification="Structured Narrow Drop",
                retail_price_usd=78.00
            ),
            "CUT-2": GarmentSku(
                sku_id="SKU-AT-HTEE-02",
                brand="ATELIER NORDIC",
                model_name="280GSM Heavyweight Tee",
                colorway="Chalk Bone",
                category="tops",
                label_size="Cut 02 (True Boxy)",
                fabric=FabricMechanics(
                    composition="100% Organic Heavy Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=3.5,
                    shrinkage_wash_pct=1.8,
                    weave_tension="semi_rigid",
                    drape_stiffness_g_cm=24.0
                ),
                top_dimensions=TopCadDimensions(
                    chest_half_cm=59.0,
                    shoulder_width_cm=53.8,
                    sleeve_length_cm=26.2,
                    bicep_half_cm=21.4,
                    torso_length_cm=72.8,
                    neck_girth_cm=42.2,
                    waist_half_cm=58.5
                ),
                cut_classification="Architectural Box Drop",
                retail_price_usd=78.00
            ),
            "CUT-3": GarmentSku(
                sku_id="SKU-AT-HTEE-03",
                brand="ATELIER NORDIC",
                model_name="280GSM Heavyweight Tee",
                colorway="Chalk Bone",
                category="tops",
                label_size="Cut 03 (Drape Exaggerated)",
                fabric=FabricMechanics(
                    composition="100% Organic Heavy Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=3.5,
                    shrinkage_wash_pct=1.8,
                    weave_tension="semi_rigid",
                    drape_stiffness_g_cm=24.0
                ),
                top_dimensions=TopCadDimensions(
                    chest_half_cm=63.5,
                    shoulder_width_cm=56.5,
                    sleeve_length_cm=28.0,
                    bicep_half_cm=23.0,
                    torso_length_cm=75.5,
                    neck_girth_cm=44.0,
                    waist_half_cm=63.0
                ),
                cut_classification="Exaggerated Drape",
                retail_price_usd=78.00
            )
        }
    },
    {
        "id": "PROD-ATELIER-SELVEDGE-DENIM",
        "title": "Kuroki Mills 14oz Raw Selvedge Denim",
        "brand": "ATELIER NORDIC",
        "category": "bottoms",
        "price_usd": 195.00,
        "colorway": "Deep Indigo Raw",
        "material_display": "100% Kuroki Mills Ring-Spun Cotton, Red Selvedge ID",
        "hero_image": "/static/img/selvedge_denim.svg",
        "story": "Loomed in Okayama, Japan on vintage shuttle looms. Raw, unwashed denim designed to break in over months of wear.",
        "skus": {
            "CUT-SLIM-31": GarmentSku(
                sku_id="SKU-AT-SEL-31",
                brand="ATELIER NORDIC",
                model_name="Kuroki 14oz Selvedge",
                colorway="Raw Indigo",
                category="bottoms",
                label_size="Cut 31 (Fitted Waist)",
                fabric=FabricMechanics(
                    composition="100% Rigid Japanese Selvedge Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=1.2,
                    shrinkage_wash_pct=3.5,
                    weave_tension="rigid",
                    drape_stiffness_g_cm=48.0
                ),
                bottom_dimensions=BottomCadDimensions(
                    waist_half_cm=40.5,
                    hip_half_cm=50.5,
                    front_rise_cm=26.5,
                    back_rise_cm=37.0,
                    thigh_half_cm=28.5,
                    knee_half_cm=20.0,
                    inseam_cm=83.0,
                    leg_opening_half_cm=18.0
                ),
                cut_classification="Mid-Rise Tailored Leg",
                retail_price_usd=195.00
            ),
            "CUT-BALANCED-32": GarmentSku(
                sku_id="SKU-AT-SEL-32",
                brand="ATELIER NORDIC",
                model_name="Kuroki 14oz Selvedge",
                colorway="Raw Indigo",
                category="bottoms",
                label_size="Cut 32 (Natural Ease)",
                fabric=FabricMechanics(
                    composition="100% Rigid Japanese Selvedge Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=1.2,
                    shrinkage_wash_pct=3.5,
                    weave_tension="rigid",
                    drape_stiffness_g_cm=48.0
                ),
                bottom_dimensions=BottomCadDimensions(
                    waist_half_cm=42.8,
                    hip_half_cm=52.8,
                    front_rise_cm=27.5,
                    back_rise_cm=38.0,
                    thigh_half_cm=30.2,
                    knee_half_cm=21.0,
                    inseam_cm=83.5,
                    leg_opening_half_cm=18.8
                ),
                cut_classification="Mid-Rise Modern Straight",
                retail_price_usd=195.00
            ),
            "CUT-RELAXED-33": GarmentSku(
                sku_id="SKU-AT-SEL-33",
                brand="ATELIER NORDIC",
                model_name="Kuroki 14oz Selvedge",
                colorway="Raw Indigo",
                category="bottoms",
                label_size="Cut 33 (Wide Thigh Drop)",
                fabric=FabricMechanics(
                    composition="100% Rigid Japanese Selvedge Cotton",
                    elastane_pct=0.0,
                    stretch_yield_pct=1.2,
                    shrinkage_wash_pct=3.5,
                    weave_tension="rigid",
                    drape_stiffness_g_cm=48.0
                ),
                bottom_dimensions=BottomCadDimensions(
                    waist_half_cm=44.5,
                    hip_half_cm=55.0,
                    front_rise_cm=29.0,
                    back_rise_cm=39.5,
                    thigh_half_cm=32.2,
                    knee_half_cm=22.8,
                    inseam_cm=84.0,
                    leg_opening_half_cm=20.0
                ),
                cut_classification="High-Rise Wide Leg",
                retail_price_usd=195.00
            )
        }
    }
]
