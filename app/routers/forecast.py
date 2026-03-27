"""
Demand Forecasting API Router.
Endpoints for hyper-local hourly SKU-level demand predictions.
"""

from fastapi import APIRouter, HTTPException, Query

from app.models.forecast import ForecastRequest, ForecastResponse
from app.services.demand_forecaster import (
    forecast_demand, get_available_pincodes, get_available_skus
)

router = APIRouter(prefix="/forecast", tags=["Demand Forecasting"])


@router.post("/", response_model=ForecastResponse,
             summary="Generate demand forecast",
             description="Predict hourly SKU-level demand for a specific pincode with weather context.")
async def create_forecast(request: ForecastRequest):
    available = get_available_pincodes()
    if request.pincode not in available:
        raise HTTPException(
            status_code=404,
            detail=f"Pincode {request.pincode} not found. Available: {available}"
        )
    return await forecast_demand(request)


@router.get("/pincodes", summary="List available pincodes for forecasting")
async def list_pincodes():
    return {"pincodes": get_available_pincodes()}


@router.get("/skus/{pincode}", summary="List available SKUs at a pincode")
async def list_skus(pincode: str):
    available_pincodes = get_available_pincodes()
    if pincode not in available_pincodes:
        raise HTTPException(status_code=404, detail=f"Pincode {pincode} not found")
    skus = get_available_skus(pincode)
    return {"pincode": pincode, "total_skus": len(skus), "skus": skus}


@router.get("/quick/{pincode}", response_model=ForecastResponse,
            summary="Quick forecast for a pincode (GET endpoint)")
async def quick_forecast(
    pincode: str,
    hours: int = Query(default=12, ge=1, le=72),
    include_weather: bool = Query(default=True),
):
    available = get_available_pincodes()
    if pincode not in available:
        raise HTTPException(status_code=404, detail=f"Pincode {pincode} not found")
    request = ForecastRequest(pincode=pincode, forecast_hours=hours, include_weather=include_weather)
    return await forecast_demand(request)
