from pydantic import BaseModel, Field
from typing import Optional
from datetime import datetime


class ForecastRequest(BaseModel):
    pincode: str = Field(description="Target pincode for demand prediction")
    sku_id: Optional[str] = Field(None, description="Specific SKU to forecast, or all SKUs if None")
    forecast_hours: int = Field(default=24, ge=1, le=168, description="Hours to forecast ahead")
    include_weather: bool = Field(default=True, description="Include weather context signals")
    latitude: Optional[float] = Field(default=None, description="Lat for weather lookup")
    longitude: Optional[float] = Field(default=None, description="Lon for weather lookup")


class HourlyForecast(BaseModel):
    hour: str
    predicted_demand: float
    lower_bound: float
    upper_bound: float
    confidence: float


class SKUForecast(BaseModel):
    sku_id: str
    product_name: str
    category: str
    pincode: str
    hourly_forecasts: list[HourlyForecast]
    total_predicted_demand: float
    peak_hour: str
    peak_demand: float
    contextual_factors: dict[str, str]


class ForecastResponse(BaseModel):
    pincode: str
    forecast_generated_at: str
    forecast_horizon_hours: int
    weather_context: Optional[dict] = None
    sku_forecasts: list[SKUForecast]
    processing_time_ms: float


class DemandSignals(BaseModel):
    hour_of_day: int
    day_of_week: int
    is_weekend: bool
    temperature: Optional[float] = None
    weather_condition: Optional[str] = None
    local_event: Optional[str] = None
    historical_return_rate: float = 0.0
    trend_factor: float = 1.0
