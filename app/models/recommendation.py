from pydantic import BaseModel, Field
from typing import Optional
from enum import Enum


class ProductCategory(str, Enum):
    TOPWEAR = "Topwear"
    BOTTOMWEAR = "Bottomwear"
    DRESS = "Dress"
    ETHNIC = "Ethnic"
    FOOTWEAR = "Footwear"
    ACCESSORIES = "Accessories"
    INNERWEAR = "Innerwear"
    LOUNGEWEAR = "Loungewear"


class ProductCard(BaseModel):
    product_id: str
    name: str
    category: str
    sub_category: str
    description: str
    color: str
    gender: str
    season: str
    price: float
    image_url: Optional[str] = None
    similarity_score: float = Field(ge=0.0, le=1.0)


class RecommendationRequest(BaseModel):
    query_text: Optional[str] = Field(
        None,
        description="Natural language query like 'casual kurta for a college fest'",
        examples=["casual kurta for a college fest", "black formal shoes for office"]
    )
    top_k: int = Field(default=10, ge=1, le=50)
    gender_filter: Optional[str] = None
    category_filter: Optional[str] = None
    price_min: Optional[float] = None
    price_max: Optional[float] = None


class RecommendationResponse(BaseModel):
    query_text: Optional[str] = None
    image_provided: bool = False
    total_results: int
    results: list[ProductCard]
    processing_time_ms: float


class CatalogueStats(BaseModel):
    total_products: int
    categories: dict[str, int]
    gender_distribution: dict[str, int]
    price_range: dict[str, float]
