"""
Zintoo Backend — AI-Powered Hyper-Local Fashion Intelligence Platform

Main FastAPI application that exposes three interconnected AI modules:
1. Multimodal Recommendation Engine (CLIP-based)
2. Hyper-Local Demand Forecasting
3. Agentic Inventory Orchestration
"""

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
from datetime import datetime

from app.routers import recommend, forecast, inventory, evaluate, pipeline
from app.config import get_settings


@asynccontextmanager
async def lifespan(app: FastAPI):
    # startup
    settings = get_settings()
    print("=" * 60)
    print("  ZINTOO Backend Starting Up")
    print(f"  Catalogue Size: {settings.catalogue_size}")
    print(f"  Warehouses: {settings.num_warehouses}")
    print(f"  CLIP Model: {settings.clip_model_name}")
    print("=" * 60)

    # pre-generate synthetic data
    from app.data.synthetic_catalogue import generate_catalogue
    from app.data.synthetic_warehouses import generate_warehouses, generate_inventory
    from app.data.synthetic_demand import generate_demand_history

    catalogue = generate_catalogue(size=settings.catalogue_size)
    warehouses = generate_warehouses()
    inv = generate_inventory(catalogue, warehouses)
    print(f"[Startup] Catalogue: {len(catalogue)} products")
    print(f"[Startup] Warehouses: {len(warehouses)}")
    print(f"[Startup] Inventory records: {len(inv)}")

    history = generate_demand_history(catalogue, [w["pincode"] for w in warehouses])
    print(f"[Startup] Demand history records: {len(history)}")
    print("[Startup] Data generation complete. CLIP model will load on first recommendation request.")
    print("=" * 60)

    yield

    # shutdown
    print("[Shutdown] Zintoo backend shutting down.")


app = FastAPI(
    title="Zintoo — AI Fashion Intelligence API",
    description=(
        "Backend for the Zintoo quick-commerce fashion platform.\n\n"
        "## Modules\n"
        "- **Recommendations** — Multimodal (text + image) fashion search using CLIP\n"
        "- **Demand Forecasting** — Hyper-local hourly SKU-level predictions with weather context\n"
        "- **Inventory Orchestration** — Agentic reallocation across micro-warehouses\n"
        "- **Pipeline** — End-to-end simulation of order flow\n"
        "- **Evaluation** — Precision@K, NDCG, MAPE, RMSE, SLA metrics\n"
    ),
    version="1.0.0",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# register routers
app.include_router(recommend.router)
app.include_router(forecast.router)
app.include_router(inventory.router)
app.include_router(evaluate.router)
app.include_router(pipeline.router)


@app.get("/", tags=["Health"])
async def root():
    return {
        "service": "Zintoo AI Fashion Intelligence Platform",
        "version": "1.0.0",
        "status": "running",
        "timestamp": datetime.utcnow().isoformat(),
        "modules": {
            "recommendation_engine": "/recommend",
            "demand_forecasting": "/forecast",
            "inventory_orchestration": "/inventory",
            "evaluation": "/evaluate",
            "pipeline": "/pipeline",
        },
        "docs": "/docs",
    }


@app.get("/health", tags=["Health"])
async def health():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}
