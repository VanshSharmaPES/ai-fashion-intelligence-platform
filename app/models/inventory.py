from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime
from enum import Enum


class ActionType(str, Enum):
    TRANSFER = "TRANSFER"
    REORDER = "REORDER"
    ALERT = "ALERT"
    NO_ACTION = "NO_ACTION"


class WarehouseInfo(BaseModel):
    warehouse_id: str
    name: str
    pincode: str
    latitude: float
    longitude: float
    capacity: int
    current_utilization: float


class InventoryItem(BaseModel):
    product_id: str
    sku_id: str
    warehouse_id: str
    pincode: str
    current_stock: int
    reorder_threshold: int
    max_capacity: int
    last_restocked: str


class ReallocationAction(BaseModel):
    action_id: str
    action_type: ActionType
    sku_id: str
    product_name: str
    source_warehouse: Optional[str] = None
    destination_warehouse: str
    quantity: int
    reason: str
    urgency: str = Field(description="LOW / MEDIUM / HIGH / CRITICAL")
    estimated_time_minutes: int
    forecasted_demand: Optional[float] = None
    current_stock_at_destination: Optional[int] = None
    timestamp: str


class OrchestrationRequest(BaseModel):
    pincode: Optional[str] = Field(None, description="Target pincode, or run for all")
    force_recheck: bool = Field(default=False, description="Force recheck even if recently evaluated")
    dry_run: bool = Field(default=False, description="Simulate without executing actions")


class OrchestrationResponse(BaseModel):
    run_id: str
    triggered_at: str
    pincodes_evaluated: list[str]
    total_actions: int
    actions: list[ReallocationAction]
    sla_risk_skus: list[dict]
    summary: str
    processing_time_ms: float


class InventorySnapshot(BaseModel):
    warehouse_id: str
    warehouse_name: str
    pincode: str
    total_skus: int
    total_stock: int
    low_stock_skus: int
    items: list[InventoryItem]


class SLAMetrics(BaseModel):
    total_orders_simulated: int
    fulfilled_within_sla: int
    sla_fulfilment_rate: float
    avg_fulfilment_time_minutes: float
    stockout_incidents: int
    reallocations_triggered: int
