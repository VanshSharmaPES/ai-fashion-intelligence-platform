"""
Recommendation API Router.
Endpoints for text-based, image-based, and multimodal product recommendations.
"""

from fastapi import APIRouter, UploadFile, File, Form, HTTPException, Query
from typing import Optional

from app.models.recommendation import (
    RecommendationRequest, RecommendationResponse, CatalogueStats
)
from app.services.recommendation_engine import (
    recommend_by_text, recommend_by_image, recommend_multimodal, get_stats
)

router = APIRouter(prefix="/recommend", tags=["Recommendations"])


@router.post("/text", response_model=RecommendationResponse,
             summary="Text-based product recommendations",
             description="Pass a natural language query and get ranked product suggestions.")
async def recommend_text(request: RecommendationRequest):
    if not request.query_text or not request.query_text.strip():
        raise HTTPException(status_code=400, detail="query_text is required for text-based recommendations")
    return recommend_by_text(request)


@router.post("/image", response_model=RecommendationResponse,
             summary="Image-based product recommendations",
             description="Upload an outfit image to find similar products in the catalogue.")
async def recommend_image(
    image: UploadFile = File(..., description="Outfit or fashion image"),
    top_k: int = Query(default=10, ge=1, le=50),
    gender_filter: Optional[str] = Query(default=None),
    category_filter: Optional[str] = Query(default=None),
    price_min: Optional[float] = Query(default=None),
    price_max: Optional[float] = Query(default=None),
):
    if not image.content_type or not image.content_type.startswith("image/"):
        raise HTTPException(status_code=400, detail="Uploaded file must be an image")

    image_bytes = await image.read()
    if len(image_bytes) == 0:
        raise HTTPException(status_code=400, detail="Empty image file")

    return recommend_by_image(
        image_bytes, top_k=top_k,
        gender_filter=gender_filter, category_filter=category_filter,
        price_min=price_min, price_max=price_max,
    )


@router.post("/multimodal", response_model=RecommendationResponse,
             summary="Multimodal recommendations (text + image)",
             description="Combine text query and image for weighted hybrid recommendations.")
async def recommend_multi(
    query_text: Optional[str] = Form(default=None),
    image: Optional[UploadFile] = File(default=None),
    top_k: int = Form(default=10),
    text_weight: float = Form(default=0.6, ge=0.0, le=1.0),
    gender_filter: Optional[str] = Form(default=None),
    category_filter: Optional[str] = Form(default=None),
    price_min: Optional[float] = Form(default=None),
    price_max: Optional[float] = Form(default=None),
):
    image_bytes = None
    if image:
        image_bytes = await image.read()

    filters = {}
    if gender_filter:
        filters["gender_filter"] = gender_filter
    if category_filter:
        filters["category_filter"] = category_filter
    if price_min is not None:
        filters["price_min"] = price_min
    if price_max is not None:
        filters["price_max"] = price_max

    return recommend_multimodal(
        query_text=query_text, image_bytes=image_bytes,
        top_k=top_k, text_weight=text_weight, **filters
    )


@router.get("/catalogue/stats", response_model=CatalogueStats,
            summary="Get catalogue statistics")
async def catalogue_stats():
    return get_stats()
