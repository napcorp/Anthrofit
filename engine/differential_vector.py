"""
AnthroFit OS - Differential Garment Vector Engine
Calculates the physical tolerance delta between benchmark user garments and target SKU cuts.
"""
from typing import Dict, List, Tuple
import math
from engine.models import (
    GarmentSku,
    FitPreference,
    TactileFrictionPoint,
    FitMatchResponse
)
from data.catalog_database import REFERENCE_ANCHORS, RETAILER_CATALOG_ITEMS

def calculate_top_differential(
    ref: GarmentSku,
    target: GarmentSku,
    pref: FitPreference
) -> Tuple[int, List[TactileFrictionPoint], Dict[str, float], float]:
    """
    Computes dimensional differential vector for Tops.
    Incorporates tensile yield and post-wash shrinkage.
    """
    r_dim = ref.top_dimensions
    t_dim = target.top_dimensions

    # Effective physical dimensions considering fabric stretch & shrinkage
    # Effective = raw_dimension * (1 + stretch_yield * 0.15) * (1 - shrinkage * 0.5)
    r_stretch_factor = (1.0 + (ref.fabric.stretch_yield_pct / 100.0) * 0.25) * (1.0 - (ref.fabric.shrinkage_wash_pct / 100.0) * 0.3)
    t_stretch_factor = (1.0 + (target.fabric.stretch_yield_pct / 100.0) * 0.25) * (1.0 - (target.fabric.shrinkage_wash_pct / 100.0) * 0.3)

    # Reference preference offset (cm adjustment)
    pref_offset_chest = 0.0
    pref_offset_shoulder = 0.0
    if pref == "fitted":
        pref_offset_chest = -2.5
        pref_offset_shoulder = -1.0
    elif pref == "relaxed":
        pref_offset_chest = 3.0
        pref_offset_shoulder = 1.5

    delta_chest = round((t_dim.chest_half_cm * t_stretch_factor) - (r_dim.chest_half_cm * r_stretch_factor) - pref_offset_chest, 1)
    delta_shoulder = round((t_dim.shoulder_width_cm * t_stretch_factor) - (r_dim.shoulder_width_cm * r_stretch_factor) - pref_offset_shoulder, 1)
    delta_sleeve = round(t_dim.sleeve_length_cm - r_dim.sleeve_length_cm, 1)
    delta_torso = round(t_dim.torso_length_cm - r_dim.torso_length_cm, 1)
    delta_bicep = round(t_dim.bicep_half_cm - r_dim.bicep_half_cm, 1)

    variance_vector = {
        "chest_half_delta_cm": delta_chest,
        "shoulder_width_delta_cm": delta_shoulder,
        "sleeve_length_delta_cm": delta_sleeve,
        "torso_length_delta_cm": delta_torso,
        "bicep_half_delta_cm": delta_bicep
    }

    friction_points: List[TactileFrictionPoint] = []

    # 1. Shoulder Seam
    if abs(delta_shoulder) <= 0.8:
        friction_points.append(TactileFrictionPoint(
            zone="Shoulder Seam",
            delta_cm=delta_shoulder,
            status="identical",
            severity="optimal",
            explanation=f"Near identical shoulder drop ({'+' if delta_shoulder >= 0 else ''}{delta_shoulder} cm). Seam rests identically to your benchmark."
        ))
    elif delta_shoulder < -0.8:
        severity = "friction" if delta_shoulder < -2.0 else "noticeable"
        friction_points.append(TactileFrictionPoint(
            zone="Shoulder Seam",
            delta_cm=delta_shoulder,
            status="tighter",
            severity=severity,
            explanation=f"{abs(delta_shoulder)} cm narrower shoulder line; sits higher on the acromion bone."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Shoulder Seam",
            delta_cm=delta_shoulder,
            status="looser",
            severity="optimal" if delta_shoulder < 2.0 else "noticeable",
            explanation=f"{delta_shoulder} cm relaxed drop shoulder drape."
        ))

    # 2. Chest Drape & Breathability
    if abs(delta_chest) <= 1.0:
        friction_points.append(TactileFrictionPoint(
            zone="Chest Drape",
            delta_cm=delta_chest,
            status="identical",
            severity="optimal",
            explanation=f"Chest circumference matches within {abs(delta_chest)} cm; comfortable respiration room."
        ))
    elif delta_chest < -1.0:
        severity = "friction" if delta_chest < -3.0 else "noticeable"
        friction_points.append(TactileFrictionPoint(
            zone="Chest Drape",
            delta_cm=delta_chest,
            status="tighter",
            severity=severity,
            explanation=f"{abs(delta_chest)} cm less ease across pectorals; tailored structured fit."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Chest Drape",
            delta_cm=delta_chest,
            status="looser",
            severity="optimal",
            explanation=f"+{delta_chest} cm generous drape room for relaxed air circulation."
        ))

    # 3. Torso Vertical Length
    if abs(delta_torso) <= 1.2:
        friction_points.append(TactileFrictionPoint(
            zone="Hem Line",
            delta_cm=delta_torso,
            status="identical",
            severity="optimal",
            explanation="Hem falls at the identical pelvic landmark as your reference."
        ))
    elif delta_torso > 1.2:
        friction_points.append(TactileFrictionPoint(
            zone="Hem Line",
            delta_cm=delta_torso,
            status="longer",
            severity="subtle",
            explanation=f"+{delta_torso} cm longer vertical drop; prevents ride-up when bending."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Hem Line",
            delta_cm=delta_torso,
            status="shorter",
            severity="subtle",
            explanation=f"{abs(delta_torso)} cm cropped silhouette."
        ))

    # Tactile penalty calculation
    # Weights: shoulder=3.0, chest=2.5, bicep=1.5, torso=1.0
    penalty = (
        abs(delta_shoulder) * 3.0 +
        abs(delta_chest) * 2.5 +
        abs(delta_bicep) * 1.5 +
        abs(delta_torso) * 1.0
    )

    # Elasticity bonus (if target or reference has give, penalty is forgiven slightly)
    stretch_bonus = min(target.fabric.stretch_yield_pct * 0.4, 8.0)
    final_score = max(55, min(99, int(100 - (penalty * 1.6) + stretch_bonus)))

    fabric_stretch_delta = round(target.fabric.stretch_yield_pct - ref.fabric.stretch_yield_pct, 1)
    return final_score, friction_points, variance_vector, fabric_stretch_delta


def calculate_bottom_differential(
    ref: GarmentSku,
    target: GarmentSku,
    pref: FitPreference
) -> Tuple[int, List[TactileFrictionPoint], Dict[str, float], float]:
    """
    Computes dimensional differential vector for Bottoms (Denim, Trousers).
    """
    r_dim = ref.bottom_dimensions
    t_dim = target.bottom_dimensions

    r_stretch_factor = (1.0 + (ref.fabric.stretch_yield_pct / 100.0) * 0.2)
    t_stretch_factor = (1.0 + (target.fabric.stretch_yield_pct / 100.0) * 0.2)

    pref_offset_waist = 0.0
    pref_offset_thigh = 0.0
    if pref == "fitted":
        pref_offset_waist = -1.2
        pref_offset_thigh = -1.0
    elif pref == "relaxed":
        pref_offset_waist = 1.5
        pref_offset_thigh = 1.5

    delta_waist = round((t_dim.waist_half_cm * t_stretch_factor) - (r_dim.waist_half_cm * r_stretch_factor) - pref_offset_waist, 1)
    delta_thigh = round(t_dim.thigh_half_cm - r_dim.thigh_half_cm - pref_offset_thigh, 1)
    delta_inseam = round(t_dim.inseam_cm - r_dim.inseam_cm, 1)
    delta_rise = round(t_dim.front_rise_cm - r_dim.front_rise_cm, 1)
    delta_opening = round(t_dim.leg_opening_half_cm - r_dim.leg_opening_half_cm, 1)

    variance_vector = {
        "waist_half_delta_cm": delta_waist,
        "thigh_half_delta_cm": delta_thigh,
        "front_rise_delta_cm": delta_rise,
        "inseam_delta_cm": delta_inseam,
        "leg_opening_delta_cm": delta_opening
    }

    friction_points: List[TactileFrictionPoint] = []

    # 1. True Waistband Tension
    if abs(delta_waist) <= 0.6:
        friction_points.append(TactileFrictionPoint(
            zone="Waistband Tension",
            delta_cm=delta_waist,
            status="identical",
            severity="optimal",
            explanation=f"Waistband circumference identical ({'+' if delta_waist >= 0 else ''}{delta_waist} cm). No belt required."
        ))
    elif delta_waist < -0.6:
        friction_points.append(TactileFrictionPoint(
            zone="Waistband Tension",
            delta_cm=delta_waist,
            status="tighter",
            severity="friction" if delta_waist < -1.8 else "noticeable",
            explanation=f"{abs(delta_waist)} cm snugger on iliac crest; structured hold."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Waistband Tension",
            delta_cm=delta_waist,
            status="looser",
            severity="subtle",
            explanation=f"+{delta_waist} cm comfortable waist ease."
        ))

    # 2. Thigh & Quadricep Sweep
    if abs(delta_thigh) <= 0.8:
        friction_points.append(TactileFrictionPoint(
            zone="Thigh Clearance",
            delta_cm=delta_thigh,
            status="identical",
            severity="optimal",
            explanation="Thigh sweep matches reference volume with natural freedom of motion."
        ))
    elif delta_thigh < -0.8:
        friction_points.append(TactileFrictionPoint(
            zone="Thigh Clearance",
            delta_cm=delta_thigh,
            status="tighter",
            severity="noticeable",
            explanation=f"{abs(delta_thigh)} cm closer taper along upper quad."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Thigh Clearance",
            delta_cm=delta_thigh,
            status="looser",
            severity="optimal",
            explanation=f"+{delta_thigh} cm clean drape room through quadriceps."
        ))

    # 3. Leg Inseam & Stacking
    if abs(delta_inseam) <= 1.0:
        friction_points.append(TactileFrictionPoint(
            zone="Inseam & Break",
            delta_cm=delta_inseam,
            status="identical",
            severity="optimal",
            explanation="Standard clean trouser break resting directly on shoe tongue."
        ))
    elif delta_inseam > 1.0:
        friction_points.append(TactileFrictionPoint(
            zone="Inseam & Break",
            delta_cm=delta_inseam,
            status="longer",
            severity="subtle",
            explanation=f"+{delta_inseam} cm added length for modern Japanese cuffing or stacking."
        ))
    else:
        friction_points.append(TactileFrictionPoint(
            zone="Inseam & Break",
            delta_cm=delta_inseam,
            status="shorter",
            severity="subtle",
            explanation=f"{abs(delta_inseam)} cm cropped ankle break."
        ))

    penalty = (
        abs(delta_waist) * 4.0 +
        abs(delta_thigh) * 2.8 +
        abs(delta_rise) * 2.0 +
        abs(delta_inseam) * 1.0
    )
    stretch_bonus = min(target.fabric.stretch_yield_pct * 0.3, 6.0)
    final_score = max(50, min(99, int(100 - (penalty * 1.7) + stretch_bonus)))

    fabric_stretch_delta = round(target.fabric.stretch_yield_pct - ref.fabric.stretch_yield_pct, 1)
    return final_score, friction_points, variance_vector, fabric_stretch_delta


def match_garments(
    ref_sku_id: str,
    target_catalog_id: str,
    preference: FitPreference = "true_to_anchor"
) -> FitMatchResponse:
    """
    Evaluates all available cuts of a target catalog item against the user's reference anchor.
    Selects the mathematically superior SKU cut and outputs tactile friction analysis.
    """
    ref_garment = REFERENCE_ANCHORS.get(ref_sku_id)
    if not ref_garment:
        # Default fallback to Uniqlo Airism M
        ref_garment = REFERENCE_ANCHORS["REF-UNIQLO-AIRISM-M"]

    # Locate target catalog item
    target_product = next((p for p in RETAILER_CATALOG_ITEMS if p["id"] == target_catalog_id), None)
    if not target_product:
        target_product = RETAILER_CATALOG_ITEMS[0]

    best_sku_id = None
    best_sku_obj = None
    best_score = -1
    best_friction_points = []
    best_variance_vector = {}
    best_fabric_delta = 0.0

    # Evaluate each SKU cut in the target product
    for cut_key, sku_obj in target_product["skus"].items():
        if target_product["category"] == "tops":
            score, f_points, v_vector, f_delta = calculate_top_differential(ref_garment, sku_obj, preference)
        else:
            score, f_points, v_vector, f_delta = calculate_bottom_differential(ref_garment, sku_obj, preference)

        if score > best_score:
            best_score = score
            best_sku_id = sku_obj.sku_id
            best_sku_obj = sku_obj
            best_friction_points = f_points
            best_variance_vector = v_vector
            best_fabric_delta = f_delta

    # Calculate predicted return risk based on fit score and friction points
    # Industry average is ~32%
    friction_count = sum(1 for fp in best_friction_points if fp.severity == "friction")
    noticeable_count = sum(1 for fp in best_friction_points if fp.severity == "noticeable")
    calculated_risk = round(max(1.8, (100 - best_score) * 0.28 + (friction_count * 5.0) + (noticeable_count * 1.5)), 1)

    anchor_summary = f"{ref_garment.brand} {ref_garment.model_name} (Tagged: {ref_garment.label_size})"
    verdict = f"Fits like your {ref_garment.brand} {ref_garment.model_name.split()[0]} (Fit Confidence: {best_score}%)"

    # SVG Silhouette Overlay Coordinates & Polygons
    silhouette_data = {
        "category": target_product["category"],
        "ref_label": f"{ref_garment.brand} {ref_garment.label_size}",
        "target_label": f"{best_sku_obj.brand} {best_sku_obj.label_size}",
        "variance_vector": best_variance_vector,
        "ref_fabric": ref_garment.fabric.dict(),
        "target_fabric": best_sku_obj.fabric.dict()
    }

    return FitMatchResponse(
        match_confidence_pct=best_score,
        recommended_sku_id=best_sku_id,
        recommended_cut_label=best_sku_obj.label_size,
        user_anchor_summary=anchor_summary,
        summary_verdict=verdict,
        tactile_friction_points=best_friction_points,
        return_risk_pct=calculated_risk,
        baseline_return_risk_pct=32.0,
        fabric_stretch_delta_factor=best_fabric_delta,
        dimensional_variance_vector=best_variance_vector,
        silhouette_overlay=silhouette_data
    )
