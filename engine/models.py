"""
AnthroFit OS - Core Domain Models & Schemas
"""
from typing import Dict, List, Optional, Literal, Any
from pydantic import BaseModel, Field

GarmentCategory = Literal["tops", "bottoms", "outerwear"]
FitPreference = Literal["true_to_anchor", "fitted", "relaxed"]

class FabricMechanics(BaseModel):
    composition: str = Field(..., description="e.g., 98% Cotton, 2% Elastane")
    elastane_pct: float = Field(default=0.0, description="Elastane or Spandex percentage")
    stretch_yield_pct: float = Field(default=0.0, description="Tensile stretch elongation under 200g load (%)")
    shrinkage_wash_pct: float = Field(default=1.5, description="Post-first-wash contraction coefficient (%)")
    weave_tension: Literal["rigid", "semi_rigid", "comfort_stretch", "high_recovery"] = "semi_rigid"
    drape_stiffness_g_cm: float = Field(default=18.0, description="Bending length/stiffness in g*cm")

class TopCadDimensions(BaseModel):
    chest_half_cm: float
    shoulder_width_cm: float
    sleeve_length_cm: float
    bicep_half_cm: float
    torso_length_cm: float
    neck_girth_cm: float
    waist_half_cm: float

class BottomCadDimensions(BaseModel):
    waist_half_cm: float
    hip_half_cm: float
    front_rise_cm: float
    back_rise_cm: float
    thigh_half_cm: float
    knee_half_cm: float
    inseam_cm: float
    leg_opening_half_cm: float

class GarmentSku(BaseModel):
    sku_id: str
    brand: str
    model_name: str
    colorway: str
    category: GarmentCategory
    label_size: str  # Traditional size tag (e.g., "M", "32x32")
    fabric: FabricMechanics
    top_dimensions: Optional[TopCadDimensions] = None
    bottom_dimensions: Optional[BottomCadDimensions] = None
    cut_classification: str = "Standard Drop"
    retail_price_usd: float = 65.0
    image_url: str = ""
    description: str = ""

class TactileFrictionPoint(BaseModel):
    zone: str  # e.g., "Shoulder Seam", "Chest Drape", "Waist Band", "Thigh Sweep"
    delta_cm: float
    status: Literal["identical", "looser", "tighter", "longer", "shorter"]
    severity: Literal["optimal", "subtle", "noticeable", "friction"]
    explanation: str

class FitMatchRequest(BaseModel):
    user_reference_sku_id: str
    target_catalog_item_id: str
    fit_preference: FitPreference = "true_to_anchor"

class FitMatchResponse(BaseModel):
    match_confidence_pct: int
    recommended_sku_id: str
    recommended_cut_label: str
    user_anchor_summary: str
    summary_verdict: str
    tactile_friction_points: List[TactileFrictionPoint]
    return_risk_pct: float
    baseline_return_risk_pct: float = 32.0
    fabric_stretch_delta_factor: float
    dimensional_variance_vector: Dict[str, float]
    silhouette_overlay: Dict[str, Any]
