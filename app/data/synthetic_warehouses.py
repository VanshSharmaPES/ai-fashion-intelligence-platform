"""
Synthetic micro-warehouse and inventory data generator.
Creates mock warehouses across Indian metro pincodes with realistic stock levels.
"""

import random
import hashlib
from datetime import datetime, timedelta
from typing import Optional

WAREHOUSE_CONFIGS = [
    {"city": "Mumbai", "area": "Andheri", "pincode": "400053", "lat": 19.1136, "lon": 72.8697},
    {"city": "Mumbai", "area": "Bandra", "pincode": "400050", "lat": 19.0596, "lon": 72.8295},
    {"city": "Delhi", "area": "Connaught Place", "pincode": "110001", "lat": 28.6315, "lon": 77.2167},
    {"city": "Delhi", "area": "Lajpat Nagar", "pincode": "110024", "lat": 28.5700, "lon": 77.2373},
    {"city": "Bangalore", "area": "Koramangala", "pincode": "560034", "lat": 12.9352, "lon": 77.6245},
    {"city": "Bangalore", "area": "Indiranagar", "pincode": "560038", "lat": 12.9716, "lon": 77.6412},
    {"city": "Hyderabad", "area": "Hitech City", "pincode": "500081", "lat": 17.4435, "lon": 78.3772},
    {"city": "Chennai", "area": "T. Nagar", "pincode": "600017", "lat": 13.0418, "lon": 80.2341},
    {"city": "Pune", "area": "Koregaon Park", "pincode": "411001", "lat": 18.5362, "lon": 73.8939},
    {"city": "Kolkata", "area": "Park Street", "pincode": "700016", "lat": 22.5495, "lon": 88.3514},
]

ALL_PINCODES = [w["pincode"] for w in WAREHOUSE_CONFIGS]

_warehouse_cache: Optional[list[dict]] = None
_inventory_cache: Optional[list[dict]] = None


def generate_warehouses(seed: int = 42) -> list[dict]:
    global _warehouse_cache
    if _warehouse_cache is not None:
        return _warehouse_cache

    random.seed(seed)
    warehouses = []

    for i, config in enumerate(WAREHOUSE_CONFIGS):
        wh_id = f"W{i + 1:02d}"
        warehouses.append({
            "warehouse_id": wh_id,
            "name": f"{config['city']} - {config['area']}",
            "city": config["city"],
            "area": config["area"],
            "pincode": config["pincode"],
            "latitude": config["lat"],
            "longitude": config["lon"],
            "capacity": random.choice([500, 750, 1000, 1200, 1500]),
            "current_utilization": round(random.uniform(0.3, 0.9), 2),
        })

    _warehouse_cache = warehouses
    return warehouses


def generate_inventory(products: list[dict], warehouses: list[dict],
                       skus_per_warehouse: int = 80, seed: int = 42) -> list[dict]:
    global _inventory_cache
    if _inventory_cache is not None:
        return _inventory_cache

    random.seed(seed)
    inventory = []
    now = datetime.utcnow()

    for wh in warehouses:
        selected_products = random.sample(products, min(skus_per_warehouse, len(products)))

        for product in selected_products:
            max_cap = random.choice([20, 30, 50, 75, 100])
            reorder_thresh = max(3, int(max_cap * random.uniform(0.15, 0.30)))
            current = random.randint(0, max_cap)
            restocked_days_ago = random.randint(0, 14)

            inventory.append({
                "product_id": product["product_id"],
                "sku_id": product["sku_id"],
                "product_name": product["name"],
                "category": product["category"],
                "warehouse_id": wh["warehouse_id"],
                "pincode": wh["pincode"],
                "current_stock": current,
                "reorder_threshold": reorder_thresh,
                "max_capacity": max_cap,
                "last_restocked": (now - timedelta(days=restocked_days_ago)).isoformat(),
            })

    _inventory_cache = inventory
    return inventory


def get_inventory_for_warehouse(inventory: list[dict], warehouse_id: str) -> list[dict]:
    return [item for item in inventory if item["warehouse_id"] == warehouse_id]


def get_inventory_for_pincode(inventory: list[dict], pincode: str) -> list[dict]:
    return [item for item in inventory if item["pincode"] == pincode]


def get_inventory_for_sku(inventory: list[dict], sku_id: str) -> list[dict]:
    return [item for item in inventory if item["sku_id"] == sku_id]


def get_low_stock_items(inventory: list[dict]) -> list[dict]:
    return [item for item in inventory if item["current_stock"] <= item["reorder_threshold"]]


def find_nearest_warehouses(warehouses: list[dict], target_pincode: str,
                             max_results: int = 3) -> list[dict]:
    """Find warehouses nearest to a target pincode by simple lat/lon distance."""
    target_wh = next((w for w in warehouses if w["pincode"] == target_pincode), None)
    if not target_wh:
        return []

    def _distance(w):
        return ((w["latitude"] - target_wh["latitude"]) ** 2 +
                (w["longitude"] - target_wh["longitude"]) ** 2) ** 0.5

    others = [w for w in warehouses if w["pincode"] != target_pincode]
    others.sort(key=_distance)
    return others[:max_results]
