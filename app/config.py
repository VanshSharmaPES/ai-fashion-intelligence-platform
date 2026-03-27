from pydantic_settings import BaseSettings
from functools import lru_cache
import os


class Settings(BaseSettings):
    open_meteo_base_url: str = "https://api.open-meteo.com/v1"
    clip_model_name: str = "openai/clip-vit-base-patch32"
    catalogue_size: int = 500
    num_warehouses: int = 10
    num_pincodes: int = 15
    forecast_hours: int = 24
    top_k_recommendations: int = 10

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"


@lru_cache()
def get_settings() -> Settings:
    return Settings()
