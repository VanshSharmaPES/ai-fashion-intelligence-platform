# Zintoo — AI-Powered Hyper-Local Fashion Intelligence Platform

Backend system for a quick-commerce fashion platform delivering curated apparel within 60 minutes, featuring live Try-and-Buy with instant refunds.

## Architecture

The system consists of three interconnected AI modules exposed via a unified FastAPI backend:

### Module 1: Multimodal Recommendation Engine
- Uses **CLIP** (openai/clip-vit-base-patch32) for text and image embeddings
- Synthetic fashion catalogue of 500 products with rich descriptions
- Cosine similarity search with gender, category, and price filters
- Supports text-only, image-only, and weighted text+image (multimodal) queries

### Module 2: Hyper-Local Demand Forecasting
- Hourly SKU-level demand predictions per pincode
- Contextual signals: **Open-Meteo** weather API, day-of-week, hour patterns, seasonal trends, local events
- Statistical forecasting with confidence intervals
- 14-day synthetic historical demand data

### Module 3: Agentic Inventory Orchestration
- Autonomous monitoring of inventory levels across 10 micro-warehouses
- Interprets demand forecasts to preemptively reallocate stock
- Generates structured action logs with reasoning traces (TRANSFER, REORDER, ALERT)
- Nearest-warehouse routing for optimal transfer decisions
- SLA fulfilment tracking (60-minute delivery target)

## API Endpoints

| Module | Endpoint | Method | Description |
|--------|----------|--------|-------------|
| Recommendations | `/recommend/text` | POST | Text-based search |
| Recommendations | `/recommend/image` | POST | Image-based search |
| Recommendations | `/recommend/multimodal` | POST | Combined text + image |
| Recommendations | `/recommend/catalogue/stats` | GET | Catalogue statistics |
| Forecasting | `/forecast/` | POST | Generate demand forecast |
| Forecasting | `/forecast/pincodes` | GET | Available pincodes |
| Forecasting | `/forecast/skus/{pincode}` | GET | SKUs at a pincode |
| Forecasting | `/forecast/quick/{pincode}` | GET | Quick forecast (GET) |
| Inventory | `/inventory/orchestrate` | POST | Run orchestration agent |
| Inventory | `/inventory/orchestrate/pincode/{pincode}` | POST | Per-pincode orchestration |
| Inventory | `/inventory/warehouses` | GET | List warehouses |
| Inventory | `/inventory/warehouses/{id}` | GET | Warehouse snapshot |
| Inventory | `/inventory/sla-metrics` | GET | SLA metrics |
| Evaluation | `/evaluate/recommendations` | GET | Precision@K, NDCG |
| Evaluation | `/evaluate/forecast` | GET | MAPE, RMSE |
| Evaluation | `/evaluate/sla` | GET | SLA fulfilment rate |
| Evaluation | `/evaluate/full-report` | GET | Complete eval report |
| Pipeline | `/pipeline/simulate` | POST | End-to-end simulation |

## Setup

```bash
# Create virtual environment
python -m venv venv
venv\Scripts\activate   # Windows

# Install dependencies
pip install -r requirements.txt

# Copy env file
copy .env.example .env

# Run the server
python run.py
```

The API will be available at `http://localhost:8000` with interactive docs at `http://localhost:8000/docs`.

## Example Requests

### Text Recommendation
```bash
curl -X POST http://localhost:8000/recommend/text \
  -H "Content-Type: application/json" \
  -d '{"query_text": "casual kurta for a college fest", "top_k": 5}'
```

### Demand Forecast
```bash
curl -X POST http://localhost:8000/forecast/ \
  -H "Content-Type: application/json" \
  -d '{"pincode": "400053", "forecast_hours": 24, "include_weather": true}'
```

### Inventory Orchestration
```bash
curl -X POST http://localhost:8000/inventory/orchestrate \
  -H "Content-Type: application/json" \
  -d '{"pincode": "400053"}'
```

### End-to-End Pipeline
```bash
curl -X POST http://localhost:8000/pipeline/simulate \
  -H "Content-Type: application/json" \
  -d '{"customer_query": "casual kurta for college", "customer_pincode": "400053"}'
```

## Evaluation Metrics

- **Recommendation**: Precision@K, NDCG@K across benchmark queries
- **Forecasting**: MAPE (Mean Absolute Percentage Error), RMSE
- **SLA**: Fulfilment rate, average delivery time, stockout incidents

## Tech Stack

- **FastAPI** — High-performance async API framework
- **CLIP** (via HuggingFace Transformers) — Multimodal embeddings
- **NumPy / Pandas / scikit-learn** — Data processing and similarity computation
- **Open-Meteo API** — Real-time weather context
- **Pydantic** — Data validation and serialization

## Synthetic Data

All data is synthetically generated for demonstration:
- **500 fashion products** across 6 categories (Topwear, Bottomwear, Dress, Ethnic, Footwear, Accessories)
- **10 micro-warehouses** across 6 Indian cities (Mumbai, Delhi, Bangalore, Hyderabad, Chennai, Pune, Kolkata)
- **Historical demand** for 14 days with hourly granularity per SKU per pincode
