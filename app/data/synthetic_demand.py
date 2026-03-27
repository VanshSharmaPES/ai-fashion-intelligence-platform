"""
Synthetic demand history generator.
Produces realistic hourly demand patterns per SKU per pincode
with seasonal, day-of-week, and event-driven variations.
"""

import random
import math
from datetime import datetime, timedelta
from typing import Optional

LOCAL_EVENTS = [
    None, None, None, None, None, None, None,  # mostly no event
    "College Fest", "Diwali Sale", "Weekend Market", "Cricket Match",
    "Music Festival", "Food Festival", "Flash Sale", "Republic Day Sale",
    "Valentine's Week", "Wedding Season", "End of Season Sale"
]


def _hourly_base_pattern(hour: int) -> float:
    """Realistic shopping demand curve peaking at lunch and evening."""
    if 0 <= hour < 6:
        return 0.1 + 0.05 * hour
    elif 6 <= hour < 9:
        return 0.4 + 0.15 * (hour - 6)
    elif 9 <= hour < 12:
        return 0.85 + 0.05 * (hour - 9)
    elif 12 <= hour < 14:
        return 1.0
    elif 14 <= hour < 17:
        return 0.8 + 0.02 * (hour - 14)
    elif 17 <= hour < 21:
        return 0.9 + 0.1 * min(hour - 17, 2)  # evening peak
    else:
        return max(0.3, 1.0 - 0.2 * (hour - 21))


def _day_of_week_factor(dow: int) -> float:
    """Weekend boost, mid-week dip."""
    factors = [0.85, 0.80, 0.75, 0.85, 0.95, 1.15, 1.20]
    return factors[dow]


def _season_factor(month: int, category: str) -> float:
    winter_cats = {"Ethnic", "Topwear"}
    summer_cats = {"Footwear", "Bottomwear", "Accessories"}

    if month in [11, 12, 1, 2]:
        return 1.3 if category in winter_cats else 0.85
    elif month in [4, 5, 6]:
        return 1.2 if category in summer_cats else 0.9
    elif month in [7, 8, 9]:
        return 0.7  # monsoon dip across the board
    return 1.0


def _event_boost(event: Optional[str]) -> float:
    if event is None:
        return 1.0
    high_impact = {"Diwali Sale", "Flash Sale", "End of Season Sale", "Wedding Season"}
    medium_impact = {"College Fest", "Valentine's Week", "Republic Day Sale"}
    if event in high_impact:
        return random.uniform(1.8, 2.5)
    elif event in medium_impact:
        return random.uniform(1.3, 1.7)
    return random.uniform(1.05, 1.25)


def generate_demand_history(products: list[dict], pincodes: list[str],
                             days: int = 14, seed: int = 42) -> list[dict]:
    """Generate historical hourly demand data for the past N days."""
    random.seed(seed)
    now = datetime.utcnow()
    history = []

    sample_size = min(50, len(products))
    sampled_products = random.sample(products, sample_size)

    for product in sampled_products:
        for pincode in pincodes:
            base_demand = random.uniform(2.0, 15.0)
            return_rate = round(random.uniform(0.05, 0.25), 2)

            for day_offset in range(days, 0, -1):
                dt = now - timedelta(days=day_offset)
                dow = dt.weekday()
                month = dt.month
                event = random.choice(LOCAL_EVENTS)

                for hour in range(24):
                    timestamp = dt.replace(hour=hour, minute=0, second=0, microsecond=0)

                    demand = base_demand
                    demand *= _hourly_base_pattern(hour)
                    demand *= _day_of_week_factor(dow)
                    demand *= _season_factor(month, product["category"])
                    demand *= _event_boost(event)

                    # Add noise
                    demand *= random.uniform(0.7, 1.3)
                    demand = max(0, round(demand))

                    history.append({
                        "sku_id": product["sku_id"],
                        "product_name": product["name"],
                        "category": product["category"],
                        "pincode": pincode,
                        "timestamp": timestamp.isoformat(),
                        "hour": hour,
                        "day_of_week": dow,
                        "is_weekend": dow >= 5,
                        "month": month,
                        "demand": demand,
                        "return_rate": return_rate,
                        "local_event": event,
                    })

    return history


def get_demand_for_sku_pincode(history: list[dict], sku_id: str,
                                pincode: str) -> list[dict]:
    return [r for r in history if r["sku_id"] == sku_id and r["pincode"] == pincode]
