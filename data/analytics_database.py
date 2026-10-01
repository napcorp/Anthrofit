"""
AnthroFit OS - Enterprise Retailer Analytics & ESG Impact Metrics
Offline simulated financial and sustainability model demonstrating return reduction.
"""
from typing import Dict, Any, List

ENTERPRISE_ANALYTICS: Dict[str, Any] = {
    "brand_overview": {
        "client_name": "Atelier Nordic Group",
        "integration_status": "Active (SDK v2.4.1)",
        "monthly_orders_analyzed": 142850,
        "anthrofit_adoption_rate_pct": 84.6
    },
    "kpis": {
        "baseline_return_rate_pct": 31.4,
        "anthrofit_return_rate_pct": 3.8,
        "return_rate_reduction_pct": 87.9,
        "net_margin_saved_usd": 1482900.00,
        "textile_waste_diverted_kg": 18450.0,
        "co2e_averted_metric_tons": 268.4,
        "checkout_conversion_lift_pct": 19.4
    },
    "return_reasons_comparison": {
        "pre_anthrofit": [
            {"reason": "Fit too tight / narrow", "pct": 42.0},
            {"reason": "Fit too loose / long", "pct": 28.0},
            {"reason": "Unflattering silhouette / drape", "pct": 18.0},
            {"reason": "Fabric feel unexpected", "pct": 8.0},
            {"reason": "Defective / Other", "pct": 4.0}
        ],
        "post_anthrofit": [
            {"reason": "Zero fit returns (Eliminated by AnthroFit)", "pct": 88.0},
            {"reason": "Style remorse / changed mind", "pct": 7.2},
            {"reason": "Fabric touch & feel preference", "pct": 3.1},
            {"reason": "Shipping delay / transit damage", "pct": 1.7}
        ]
    },
    "sku_anomaly_radar": [
        {
            "sku_code": "SKU-AT-HTEE-01",
            "name": "Heavyweight Tee (Cut 01)",
            "variance_anomaly": "Armhole curve sits 1.4cm high vs nominal grade",
            "risk_mitigated": "Prevented 612 predicted returns via smart warning",
            "status": "Monitored"
        },
        {
            "sku_code": "SKU-AT-SEL-31",
            "name": "Kuroki Selvedge (Cut 31)",
            "variance_anomaly": "100% Rigid Weave zero-yield causes high hip compression",
            "risk_mitigated": "Auto-diverted 1,140 shoppers to Cut 32 based on anchor",
            "status": "Diverted"
        }
    ],
    "monthly_timeline": [
        {"month": "Apr", "orders": 112000, "returns_prevented": 30800, "savings_usd": 320000},
        {"month": "May", "orders": 124000, "returns_prevented": 34100, "savings_usd": 354000},
        {"month": "Jun", "orders": 131000, "returns_prevented": 36000, "savings_usd": 374000},
        {"month": "Jul", "orders": 142850, "returns_prevented": 39400, "savings_usd": 434900}
    ]
}
