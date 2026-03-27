"""
Hyper-Local Demand Forecasting Service.
Uses historical demand patterns + contextual signals (weather, events, time)
to predict hourly SKU-level demand per pincode.
"""

import time
import random
import math
import numpy as np
from datetime import datetime, timedelta
from typing import Optional
from collections import defaultdict

from app.data.synthetic_catalogue import generate_catalogue
from app.data.synthetic_warehouses import generate_warehouses, ALL_PINCODES
from app.data.synthetic_demand import generate_demand_history, get_demand_for_sku_pincode
from app.services.weather_service import get_weather_for_pincode
from app.models.forecast import (
    ForecastRequest, ForecastResponse, SKUForecast, HourlyForecast
)

_history_cache = None
_products_cache = None


def _get_products():
    global _products_cache
    if _products_cache is None:
        _products_cache = generate_catalogue()
    return _products_cache


def _get_history():
    global _history_cache
    if _history_cache is None:
        products = _get_products()
        _history_cache = generate_demand_history(products, ALL_PINCODES, days=14)
    return _history_cache


def _compute_hourly_averages(records: list[dict]) -> dict[int, float]:
    """Compute average demand per hour-of-day from historical records."""
    hourly = defaultdict(list)
    for r in records:
        hourly[r["hour"]].append(r["demand"])
    return {h: np.mean(vals) for h, vals in hourly.items()}


def _compute_dow_factors(records: list[dict]) -> dict[int, float]:
    """Compute day-of-week adjustment factors."""
    dow_demand = defaultdict(list)
    for r in records:
        dow_demand[r["day_of_week"]].append(r["demand"])
    overall_avg = np.mean([r["demand"] for r in records]) if records else 1.0
    if overall_avg == 0:
        overall_avg = 1.0
    return {dow: np.mean(vals) / overall_avg for dow, vals in dow_demand.items()}


def _compute_return_rate(records: list[dict]) -> float:
    if not records:
        return 0.1
    return np.mean([r["return_rate"] for r in records])


def _weather_demand_modifier(weather_context: Optional[dict], hour_index: int) -> float:
    """Adjust demand based on weather conditions."""
    if not weather_context:
        return 1.0

    conditions = weather_context.get("hourly_conditions", [])
    precip_probs = weather_context.get("hourly_precipitation_prob", [])
    temps = weather_context.get("hourly_temperatures", [])

    condition = conditions[hour_index] if hour_index < len(conditions) else "Clear sky"
    precip = precip_probs[hour_index] if hour_index < len(precip_probs) else 0
    temp = temps[hour_index] if hour_index < len(temps) else 30

    modifier = 1.0

    # rain reduces outdoor shopping demand
    if "rain" in condition.lower() or "thunderstorm" in condition.lower():
        modifier *= 0.7
    elif "drizzle" in condition.lower():
        modifier *= 0.85

    # extreme heat reduces demand slightly
    if temp > 40:
        modifier *= 0.8
    elif temp < 10:
        modifier *= 0.85

    # high precipitation probability
    if precip > 70:
        modifier *= 0.8

    return modifier


def _trend_extrapolation(records: list[dict]) -> float:
    """Simple linear trend from recent vs older demand."""
    if len(records) < 48:
        return 1.0

    mid = len(records) // 2
    older = np.mean([r["demand"] for r in records[:mid]])
    recent = np.mean([r["demand"] for r in records[mid:]])

    if older == 0:
        return 1.0
    ratio = recent / older
    return max(0.5, min(2.0, ratio))


def _generate_forecast_for_sku(sku_records: list[dict], sku_id: str,
                                 product_name: str, category: str, pincode: str,
                                 forecast_hours: int,
                                 weather_context: Optional[dict]) -> SKUForecast:
    """Generate hourly forecast for a single SKU at a pincode."""
    now = datetime.utcnow()
    hourly_avgs = _compute_hourly_averages(sku_records)
    dow_factors = _compute_dow_factors(sku_records)
    trend = _trend_extrapolation(sku_records)
    return_rate = _compute_return_rate(sku_records)

    hourly_forecasts = []
    peak_demand = 0
    peak_hour = ""
    total_demand = 0

    for h in range(forecast_hours):
        future_time = now + timedelta(hours=h)
        hour_of_day = future_time.hour
        dow = future_time.weekday()

        base = hourly_avgs.get(hour_of_day, 2.0)
        dow_factor = dow_factors.get(dow, 1.0)
        weather_mod = _weather_demand_modifier(weather_context, h)

        predicted = base * dow_factor * trend * weather_mod
        predicted = max(0, predicted)

        # confidence interval based on historical variance
        hour_records = [r["demand"] for r in sku_records if r["hour"] == hour_of_day]
        std_dev = np.std(hour_records) if len(hour_records) > 1 else predicted * 0.3
        confidence = max(0.5, min(0.95, 1.0 - (std_dev / (predicted + 1e-6))))

        lower = max(0, predicted - 1.96 * std_dev)
        upper = predicted + 1.96 * std_dev

        hour_str = future_time.strftime("%Y-%m-%d %H:00")
        hourly_forecasts.append(HourlyForecast(
            hour=hour_str,
            predicted_demand=round(predicted, 2),
            lower_bound=round(lower, 2),
            upper_bound=round(upper, 2),
            confidence=round(confidence, 3),
        ))

        total_demand += predicted
        if predicted > peak_demand:
            peak_demand = predicted
            peak_hour = hour_str

    # contextual factors summary
    factors = {
        "trend_direction": "upward" if trend > 1.05 else ("downward" if trend < 0.95 else "stable"),
        "return_rate": f"{return_rate:.1%}",
        "data_points_used": str(len(sku_records)),
        "weather_impact": "included" if weather_context else "not available",
    }

    return SKUForecast(
        sku_id=sku_id,
        product_name=product_name,
        category=category,
        pincode=pincode,
        hourly_forecasts=hourly_forecasts,
        total_predicted_demand=round(total_demand, 2),
        peak_hour=peak_hour,
        peak_demand=round(peak_demand, 2),
        contextual_factors=factors,
    )


async def forecast_demand(request: ForecastRequest) -> ForecastResponse:
    start = time.time()
    history = _get_history()
    products = _get_products()

    # fetch weather context
    weather_context = None
    if request.include_weather:
        weather_context = await get_weather_for_pincode(request.pincode)

    # determine which SKUs to forecast
    if request.sku_id:
        target_skus = [request.sku_id]
    else:
        pincode_records = [r for r in history if r["pincode"] == request.pincode]
        target_skus = list(set(r["sku_id"] for r in pincode_records))[:10]  # limit for perf

    sku_forecasts = []
    for sku_id in target_skus:
        sku_records = get_demand_for_sku_pincode(history, sku_id, request.pincode)
        if not sku_records:
            continue

        product = next((p for p in products if p["sku_id"] == sku_id), None)
        if not product:
            continue

        forecast = _generate_forecast_for_sku(
            sku_records, sku_id, product["name"], product["category"],
            request.pincode, request.forecast_hours, weather_context
        )
        sku_forecasts.append(forecast)

    elapsed = (time.time() - start) * 1000

    weather_summary = None
    if weather_context and weather_context.get("current"):
        weather_summary = weather_context["current"]

    return ForecastResponse(
        pincode=request.pincode,
        forecast_generated_at=datetime.utcnow().isoformat(),
        forecast_horizon_hours=request.forecast_hours,
        weather_context=weather_summary,
        sku_forecasts=sku_forecasts,
        processing_time_ms=round(elapsed, 2),
    )


def get_available_pincodes() -> list[str]:
    return ALL_PINCODES


def get_available_skus(pincode: str) -> list[dict]:
    history = _get_history()
    pincode_records = [r for r in history if r["pincode"] == pincode]
    seen = {}
    for r in pincode_records:
        if r["sku_id"] not in seen:
            seen[r["sku_id"]] = {
                "sku_id": r["sku_id"],
                "product_name": r["product_name"],
                "category": r["category"],
            }
    return list(seen.values())
