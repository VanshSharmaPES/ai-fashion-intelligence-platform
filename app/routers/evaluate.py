"""
Evaluation API Router.
Endpoints for running evaluation metrics across all three modules.
"""

from fastapi import APIRouter
from app.evaluation.metrics import (
    evaluate_recommendations, evaluate_forecast,
    evaluate_sla, generate_full_report
)

router = APIRouter(prefix="/evaluate", tags=["Evaluation"])


@router.get("/recommendations", summary="Evaluate recommendation engine quality",
            description="Runs Precision@K and NDCG metrics across benchmark queries.")
async def eval_recommendations():
    return evaluate_recommendations()


@router.get("/forecast", summary="Evaluate demand forecast accuracy",
            description="Returns MAPE and RMSE metrics for forecasting model.")
async def eval_forecast():
    return evaluate_forecast()


@router.get("/sla", summary="Evaluate SLA fulfilment metrics",
            description="Returns simulated SLA performance metrics.")
async def eval_sla():
    return evaluate_sla()


@router.get("/full-report", summary="Generate complete evaluation report",
            description="Comprehensive report with metrics for all modules and design tradeoff analysis.")
async def full_report():
    return generate_full_report()
