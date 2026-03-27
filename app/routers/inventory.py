"""
Inventory Orchestration API Router.
Endpoints for warehouse management, inventory monitoring, and autonomous reallocation.
"""

from fastapi import APIRouter, HTTPException, Query
from typing import Optional

from app.models.inventory import (
    OrchestrationRequest, OrchestrationResponse,
    InventorySnapshot, WarehouseInfo, SLAMetrics
)
from app.services.inventory_orchestrator import (
    run_orchestration, get_warehouse_list, get_inventory_snapshot,
    get_all_inventory_snapshots, simulate_sla_metrics
)

router = APIRouter(prefix="/inventory", tags=["Inventory Orchestration"])


@router.post("/orchestrate", response_model=OrchestrationResponse,
             summary="Run agentic inventory orchestration",
             description="Analyze demand forecasts and autonomously generate reallocation instructions.")
async def orchestrate(request: OrchestrationRequest):
    return await run_orchestration(request)


@router.post("/orchestrate/pincode/{pincode}", response_model=OrchestrationResponse,
             summary="Run orchestration for a specific pincode")
async def orchestrate_pincode(pincode: str, dry_run: bool = Query(default=False)):
    request = OrchestrationRequest(pincode=pincode, dry_run=dry_run)
    return await run_orchestration(request)


@router.get("/warehouses", response_model=list[WarehouseInfo],
            summary="List all micro-warehouses")
async def list_warehouses():
    return get_warehouse_list()


@router.get("/warehouses/{warehouse_id}", response_model=InventorySnapshot,
            summary="Get inventory snapshot for a warehouse")
async def warehouse_snapshot(warehouse_id: str):
    snapshot = get_inventory_snapshot(warehouse_id.upper())
    if not snapshot:
        raise HTTPException(status_code=404, detail=f"Warehouse {warehouse_id} not found")
    return snapshot


@router.get("/snapshots", summary="Get all warehouse inventory snapshots")
async def all_snapshots():
    snapshots = get_all_inventory_snapshots()
    return {
        "total_warehouses": len(snapshots),
        "snapshots": snapshots,
    }


@router.get("/sla-metrics", response_model=SLAMetrics,
            summary="Get SLA fulfilment metrics")
async def sla_metrics():
    return simulate_sla_metrics()
