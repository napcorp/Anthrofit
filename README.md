# AnthroFit OS — Comparative Garment CAD Tolerance & Matching Engine

A headless B2B SaaS platform that plugs into e-commerce checkouts via an API/SDK, completely replacing sizing dropdowns with a single-click dynamic verification engine.

## Overview
- **Zero Cameras or Body Scanners**: Completely non-invasive.
- **Reverse Garment Tolerance Algorithm**: Clothes you already own contain the exact answer to your body's volume and drape tolerances.
- **Physics-Based Cross-Brand Translation**: Compares 8-point CAD cutting vectors and fabric elasticity against target garments.
- **Gemini AI Product Intelligence**: Automatically retrieves real garment sizing charts directly from the web with Google Search grounding.

---

## Quickstart (Development & Production)

### 1. Prerequisites
- Python 3.10+
- Google Gemini API Key (optional for offline CAD mode, required for live web lookups)

### 2. Environment Configuration
Copy `.env.example` to `.env` and insert your credentials:
```bash
GEMINI_API_KEY=your_key_here
HOST=127.0.0.1
PORT=8000
```

### 3. Installation
```bash
pip install -r requirements.txt
```

### 4. Running the Server
```bash
# Local development:
python main.py

# Or run with batch script:
start_app.bat

# Production with Uvicorn (multi-worker):
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

---

## Web Applications & Routes

| Route | Description |
|---|---|
| `/` | **Sizing Verification App**: Step-by-step sizing questionnaire, wardrobe anchor selection, and real-time fit recommendations. |
| `/health` | **Health Probe**: Load balancer and container liveness check (`{"status": "healthy", ...}`). |

---

## API Endpoints

- `GET /health`: Service health check.
- `GET /api/status`: Check if AI intelligence is enabled.
- `POST /api/ai/lookup`: Query Google Gemini + Search grounding for official garment sizing charts.
- `POST /api/match`: Solve garment fit compatibility using anchor garment and target dimensions.
- `GET /api/catalog/anchors`: List reference wardrobe anchors.
- `POST /api/catalog/anchors/add`: Add custom wardrobe anchor to session.
- `GET /api/analytics`: Return reduction & sizing metrics.

