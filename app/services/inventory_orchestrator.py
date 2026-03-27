"""
Agentic Inventory Orchestration Service.
Autonomously monitors inventory levels, interprets demand forecasts,
and issues reallocation instructions across micro-warehouses.
"""

import time
import uuid
import random
from datetime import datetime
from typing import Optional

from app.data.synthetic_catalogue import generate_catalogue
from app.data.synthetic_warehouses import (
    generate_warehouses, generate_inventory, get_inventory_for_pincode,
    get_inventory_for_sku, get_low_stock_items, find_nearest_warehouses, ALL_PINCODES
)
from app.services.demand_forecaster import forecast_demand
from app.models.forecast import ForecastRequest
from app.models.inventory import (
    ReallocationAction, ActionType, OrchestrationRequest, OrchestrationResponse,
    InventorySnapshot, InventoryItem, WarehouseInfo, SLAMetrics
)

_warehouses = None
_inventory = None


def _get_warehouses():
    global _warehouses
    if _warehouses is None:
        _warehouses = generate_warehouses()
    return _warehouses


def _get_inventory():
    global _inventory
    if _inventory is None:
        products = generate_catalogue()
        warehouses = _get_warehouses()
        _inventory = generate_inventory(products, warehouses)
    return _inventory


def _estimate_transfer_time(source_wh: dict, dest_wh: dict) -> int:
    """Estimate transfer time in minutes based on distance."""
    dist = ((source_wh["latitude"] - dest_wh["latitude"]) ** 2 +
            (source_wh["longitude"] - dest_wh["longitude"]) ** 2) ** 0.5

    # same city (close pincodes)
    if dist < 0.1:
        return random.randint(15, 30)
    elif dist < 1.0:
        return random.randint(30, 60)
    else:
        return random.randint(60, 180)


def _assess_urgency(current_stock: int, predicted_demand: float,
                     reorder_threshold: int) -> str:
    if current_stock == 0:
        return "CRITICAL"
    elif current_stock <= reorder_threshold * 0.5:
        return "HIGH"
    elif current_stock <= reorder_threshold:
        return "MEDIUM"
    elif predicted_demand > current_stock * 0.8:
        return "MEDIUM"
    return "LOW"


def _calculate_transfer_quantity(current_stock: int, predicted_demand: float,
                                  max_capacity: int, source_available: int) -> int:
    """Determine how many units to transfer."""
    deficit = max(0, int(predicted_demand * 1.5) - current_stock)
    # don't exceed capacity
    space_available = max_capacity - current_stock
    # don't take more than source can spare
    safe_source = max(0, source_available - 5)  # keep at least 5 at source

    quantity = min(deficit, space_available, safe_source)
    return max(0, quantity)


async def _analyze_pincode(pincode: str, inventory: list[dict],
                            warehouses: list[dict],
                            dry_run: bool = False) -> tuple[list[ReallocationAction], list[dict]]:
    """Analyze a single pincode and generate reallocation actions."""
    actions = []
    sla_risks = []

    # get demand forecast for this pincode
    try:
        forecast_req = ForecastRequest(pincode=pincode, forecast_hours=12, include_weather=True)
        forecast = await forecast_demand(forecast_req)
    except Exception as e:
        print(f"[Orchestrator] Forecast failed for {pincode}: {e}")
        forecast = None

    pincode_inventory = get_inventory_for_pincode(inventory, pincode)
    local_warehouse = next((w for w in warehouses if w["pincode"] == pincode), None)
    nearby_warehouses = find_nearest_warehouses(warehouses, pincode)

    # build demand lookup from forecast
    demand_lookup = {}
    if forecast:
        for sku_forecast in forecast.sku_forecasts:
            demand_lookup[sku_forecast.sku_id] = sku_forecast.total_predicted_demand

    # check each item in pincode inventory
    for item in pincode_inventory:
        predicted = demand_lookup.get(item["sku_id"], 0)
        urgency = _assess_urgency(item["current_stock"], predicted, item["reorder_threshold"])

        if urgency in ("CRITICAL", "HIGH", "MEDIUM"):
            # try to find stock from nearby warehouses
            source_found = False
            for nearby_wh in nearby_warehouses:
                nearby_inv = [
                    inv for inv in inventory
                    if inv["warehouse_id"] == nearby_wh["warehouse_id"]
                    and inv["sku_id"] == item["sku_id"]
                ]
                if not nearby_inv:
                    continue

                source_item = nearby_inv[0]
                if source_item["current_stock"] <= source_item["reorder_threshold"]:
                    continue  # source is also low

                transfer_qty = _calculate_transfer_quantity(
                    item["current_stock"], predicted,
                    item["max_capacity"], source_item["current_stock"]
                )

                if transfer_qty > 0:
                    transfer_time = _estimate_transfer_time(nearby_wh, local_warehouse) if local_warehouse else 45

                    action = ReallocationAction(
                        action_id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                        action_type=ActionType.TRANSFER,
                        sku_id=item["sku_id"],
                        product_name=item["product_name"],
                        source_warehouse=nearby_wh["warehouse_id"],
                        destination_warehouse=local_warehouse["warehouse_id"] if local_warehouse else "UNKNOWN",
                        quantity=transfer_qty,
                        reason=(
                            f"Forecasted demand of {predicted:.0f} units in next 12h at {pincode}. "
                            f"Current stock: {item['current_stock']}, threshold: {item['reorder_threshold']}. "
                            f"Transferring {transfer_qty} units from {nearby_wh['warehouse_id']} "
                            f"({nearby_wh['name']}) to prevent stockout."
                        ),
                        urgency=urgency,
                        estimated_time_minutes=transfer_time,
                        forecasted_demand=round(predicted, 1),
                        current_stock_at_destination=item["current_stock"],
                        timestamp=datetime.utcnow().isoformat(),
                    )
                    actions.append(action)
                    source_found = True
                    break

            if not source_found and urgency in ("CRITICAL", "HIGH"):
                # issue a reorder alert
                reorder_action = ReallocationAction(
                    action_id=f"ACT-{uuid.uuid4().hex[:8].upper()}",
                    action_type=ActionType.REORDER,
                    sku_id=item["sku_id"],
                    product_name=item["product_name"],
                    source_warehouse=None,
                    destination_warehouse=local_warehouse["warehouse_id"] if local_warehouse else "UNKNOWN",
                    quantity=item["max_capacity"] - item["current_stock"],
                    reason=(
                        f"No nearby warehouse has sufficient stock for {item['sku_id']}. "
                        f"Current stock: {item['current_stock']}, predicted demand: {predicted:.0f}. "
                        f"Triggering external reorder to replenish warehouse."
                    ),
                    urgency=urgency,
                    estimated_time_minutes=random.randint(120, 360),
                    forecasted_demand=round(predicted, 1),
                    current_stock_at_destination=item["current_stock"],
                    timestamp=datetime.utcnow().isoformat(),
                )
                actions.append(reorder_action)

            if urgency == "CRITICAL":
                sla_risks.append({
                    "sku_id": item["sku_id"],
                    "product_name": item["product_name"],
                    "pincode": pincode,
                    "current_stock": item["current_stock"],
                    "predicted_demand_12h": round(predicted, 1),
                    "risk_level": "HIGH - potential SLA breach within 2 hours",
                })

    return actions, sla_risks


async def run_orchestration(request: OrchestrationRequest) -> OrchestrationResponse:
    start = time.time()
    run_id = f"RUN-{uuid.uuid4().hex[:8].upper()}"
    warehouses = _get_warehouses()
    inventory = _get_inventory()

    target_pincodes = [request.pincode] if request.pincode else ALL_PINCODES
    all_actions = []
    all_sla_risks = []

    for pincode in target_pincodes:
        actions, risks = await _analyze_pincode(pincode, inventory, warehouses, request.dry_run)
        all_actions.extend(actions)
        all_sla_risks.extend(risks)

    # generate summary
    transfers = sum(1 for a in all_actions if a.action_type == ActionType.TRANSFER)
    reorders = sum(1 for a in all_actions if a.action_type == ActionType.REORDER)
    critical = sum(1 for a in all_actions if a.urgency == "CRITICAL")

    summary = (
        f"Orchestration run {run_id} completed. "
        f"Evaluated {len(target_pincodes)} pincode(s). "
        f"Generated {len(all_actions)} actions: {transfers} transfers, {reorders} reorders. "
        f"{critical} critical urgency items. "
        f"{len(all_sla_risks)} SKUs at risk of SLA breach."
    )

    elapsed = (time.time() - start) * 1000

    return OrchestrationResponse(
        run_id=run_id,
        triggered_at=datetime.utcnow().isoformat(),
        pincodes_evaluated=target_pincodes,
        total_actions=len(all_actions),
        actions=all_actions,
        sla_risk_skus=all_sla_risks,
        summary=summary,
        processing_time_ms=round(elapsed, 2),
    )


def get_warehouse_list() -> list[WarehouseInfo]:
    warehouses = _get_warehouses()
    return [WarehouseInfo(**w) for w in warehouses]


def get_inventory_snapshot(warehouse_id: str) -> Optional[InventorySnapshot]:
    warehouses = _get_warehouses()
    inventory = _get_inventory()

    wh = next((w for w in warehouses if w["warehouse_id"] == warehouse_id), None)
    if not wh:
        return None

    wh_items = [item for item in inventory if item["warehouse_id"] == warehouse_id]
    low_stock = [item for item in wh_items if item["current_stock"] <= item["reorder_threshold"]]

    return InventorySnapshot(
        warehouse_id=wh["warehouse_id"],
        warehouse_name=wh["name"],
        pincode=wh["pincode"],
        total_skus=len(wh_items),
        total_stock=sum(item["current_stock"] for item in wh_items),
        low_stock_skus=len(low_stock),
        items=[InventoryItem(**item) for item in wh_items[:50]],  # limit response size
    )


def get_all_inventory_snapshots() -> list[InventorySnapshot]:
    warehouses = _get_warehouses()
    return [get_inventory_snapshot(w["warehouse_id"]) for w in warehouses]


def simulate_sla_metrics() -> SLAMetrics:
    """Simulate SLA fulfilment metrics across the system."""
    random.seed(42)
    total_orders = random.randint(800, 1500)
    fulfilled = int(total_orders * random.uniform(0.82, 0.95))
    stockouts = random.randint(5, 30)
    reallocations = random.randint(15, 60)

    return SLAMetrics(
        total_orders_simulated=total_orders,
        fulfilled_within_sla=fulfilled,
        sla_fulfilment_rate=round(fulfilled / total_orders, 4),
        avg_fulfilment_time_minutes=round(random.uniform(28, 48), 1),
        stockout_incidents=stockouts,
        reallocations_triggered=reallocations,
    )
