"""
End-to-End Pipeline API Router.
Simulates a complete customer order flow through all three modules.
"""

import time
import uuid
from datetime import datetime
from fastapi import APIRouter, HTTPException
from pydantic import BaseModel, Field
from typing import Optional

from app.models.recommendation import RecommendationRequest
from app.models.forecast import ForecastRequest
from app.models.inventory import OrchestrationRequest
from app.services.recommendation_engine import recommend_by_text
from app.services.demand_forecaster import forecast_demand, get_available_pincodes
from app.services.inventory_orchestrator import run_orchestration, get_inventory_snapshot

router = APIRouter(prefix="/pipeline", tags=["End-to-End Pipeline"])


class PipelineRequest(BaseModel):
    customer_query: str = Field(
        description="What the customer is looking for",
        examples=["casual kurta for a college fest"]
    )
    customer_pincode: str = Field(
        description="Customer's delivery pincode",
        examples=["400053"]
    )
    top_k: int = Field(default=5, ge=1, le=20)
    gender_filter: Optional[str] = None


class PipelineStepResult(BaseModel):
    step: str
    status: str
    duration_ms: float
    data: dict


class PipelineResponse(BaseModel):
    pipeline_id: str
    triggered_at: str
    customer_query: str
    customer_pincode: str
    total_duration_ms: float
    steps: list[PipelineStepResult]
    summary: str


@router.post("/simulate", response_model=PipelineResponse,
             summary="Simulate end-to-end customer order pipeline",
             description=(
                 "Triggers the full flow: "
                 "1) Customer searches for fashion items → "
                 "2) System recommends products → "
                 "3) Demand forecast is checked for the pincode → "
                 "4) Inventory orchestrator ensures stock availability"
             ))
async def simulate_pipeline(request: PipelineRequest):
    pipeline_id = f"PIPE-{uuid.uuid4().hex[:8].upper()}"
    pipeline_start = time.time()
    steps = []

    # validate pincode
    available_pincodes = get_available_pincodes()
    if request.customer_pincode not in available_pincodes:
        raise HTTPException(
            status_code=400,
            detail=f"Pincode {request.customer_pincode} not in service area. Available: {available_pincodes}"
        )

    # Step 1: Get recommendations
    step_start = time.time()
    rec_request = RecommendationRequest(
        query_text=request.customer_query,
        top_k=request.top_k,
        gender_filter=request.gender_filter,
    )
    rec_response = recommend_by_text(rec_request)
    step_duration = (time.time() - step_start) * 1000

    steps.append(PipelineStepResult(
        step="1. Product Recommendation",
        status="completed",
        duration_ms=round(step_duration, 2),
        data={
            "query": request.customer_query,
            "results_count": rec_response.total_results,
            "top_product": rec_response.results[0].model_dump() if rec_response.results else None,
            "products": [
                {
                    "name": r.name,
                    "category": r.category,
                    "price": r.price,
                    "similarity_score": r.similarity_score
                }
                for r in rec_response.results[:5]
            ],
        },
    ))

    # Step 2: Check demand forecast for this pincode
    step_start = time.time()
    forecast_req = ForecastRequest(
        pincode=request.customer_pincode,
        forecast_hours=12,
        include_weather=True,
    )
    forecast_response = await forecast_demand(forecast_req)
    step_duration = (time.time() - step_start) * 1000

    steps.append(PipelineStepResult(
        step="2. Demand Forecast Check",
        status="completed",
        duration_ms=round(step_duration, 2),
        data={
            "pincode": request.customer_pincode,
            "forecast_horizon": "12 hours",
            "skus_forecasted": len(forecast_response.sku_forecasts),
            "weather_context": forecast_response.weather_context,
            "top_demand_skus": [
                {
                    "sku_id": sf.sku_id,
                    "product": sf.product_name,
                    "predicted_total": sf.total_predicted_demand,
                    "peak_hour": sf.peak_hour,
                }
                for sf in sorted(forecast_response.sku_forecasts,
                                  key=lambda x: x.total_predicted_demand, reverse=True)[:5]
            ],
        },
    ))

    # Step 3: Run inventory orchestration
    step_start = time.time()
    orch_request = OrchestrationRequest(
        pincode=request.customer_pincode,
        dry_run=False,
    )
    orch_response = await run_orchestration(orch_request)
    step_duration = (time.time() - step_start) * 1000

    steps.append(PipelineStepResult(
        step="3. Inventory Orchestration",
        status="completed",
        duration_ms=round(step_duration, 2),
        data={
            "run_id": orch_response.run_id,
            "total_actions": orch_response.total_actions,
            "actions_summary": [
                {
                    "action_id": a.action_id,
                    "type": a.action_type.value,
                    "sku": a.sku_id,
                    "quantity": a.quantity,
                    "urgency": a.urgency,
                    "reason": a.reason,
                    "from": a.source_warehouse,
                    "to": a.destination_warehouse,
                }
                for a in orch_response.actions[:10]
            ],
            "sla_risks": orch_response.sla_risk_skus[:5],
        },
    ))

    # Step 4: Check local warehouse stock
    step_start = time.time()
    # find the warehouse for this pincode
    from app.data.synthetic_warehouses import generate_warehouses
    warehouses = generate_warehouses()
    local_wh = next((w for w in warehouses if w["pincode"] == request.customer_pincode), None)

    warehouse_data = {}
    if local_wh:
        snapshot = get_inventory_snapshot(local_wh["warehouse_id"])
        if snapshot:
            warehouse_data = {
                "warehouse_id": snapshot.warehouse_id,
                "warehouse_name": snapshot.warehouse_name,
                "total_skus": snapshot.total_skus,
                "total_stock": snapshot.total_stock,
                "low_stock_skus": snapshot.low_stock_skus,
            }
    step_duration = (time.time() - step_start) * 1000

    steps.append(PipelineStepResult(
        step="4. Local Warehouse Status",
        status="completed",
        duration_ms=round(step_duration, 2),
        data=warehouse_data,
    ))

    total_duration = (time.time() - pipeline_start) * 1000

    # build summary
    top_rec = rec_response.results[0].name if rec_response.results else "None"
    summary = (
        f"Pipeline {pipeline_id} processed customer query '{request.customer_query}' "
        f"for pincode {request.customer_pincode}. "
        f"Found {rec_response.total_results} matching products (top: {top_rec}). "
        f"Demand forecast generated for {len(forecast_response.sku_forecasts)} SKUs. "
        f"Orchestrator issued {orch_response.total_actions} inventory actions. "
        f"Total processing time: {total_duration:.0f}ms."
    )

    return PipelineResponse(
        pipeline_id=pipeline_id,
        triggered_at=datetime.utcnow().isoformat(),
        customer_query=request.customer_query,
        customer_pincode=request.customer_pincode,
        total_duration_ms=round(total_duration, 2),
        steps=steps,
        summary=summary,
    )
