"""
Multimodal Fashion Recommendation Engine.
Uses CLIP for text and image embeddings, performs cosine similarity
search against a synthetic fashion catalogue.
"""

import time
import numpy as np
from typing import Optional
from io import BytesIO

from app.config import get_settings
from app.data.synthetic_catalogue import generate_catalogue, get_catalogue_stats
from app.models.recommendation import (
    ProductCard, RecommendationRequest, RecommendationResponse, CatalogueStats
)

# lazy-loaded globals
_clip_model = None
_clip_processor = None
_catalogue_embeddings: Optional[np.ndarray] = None
_catalogue: Optional[list[dict]] = None


def _load_clip():
    global _clip_model, _clip_processor
    if _clip_model is not None:
        return

    from transformers import CLIPModel, CLIPProcessor
    settings = get_settings()
    model_name = settings.clip_model_name
    print(f"[Recommendation] Loading CLIP model: {model_name}")
    _clip_model = CLIPModel.from_pretrained(model_name)
    _clip_processor = CLIPProcessor.from_pretrained(model_name)
    print("[Recommendation] CLIP model loaded successfully.")


def _get_catalogue() -> list[dict]:
    global _catalogue
    if _catalogue is None:
        settings = get_settings()
        _catalogue = generate_catalogue(size=settings.catalogue_size)
    return _catalogue


def _compute_catalogue_embeddings() -> np.ndarray:
    global _catalogue_embeddings
    if _catalogue_embeddings is not None:
        return _catalogue_embeddings

    _load_clip()
    import torch
    catalogue = _get_catalogue()

    print(f"[Recommendation] Computing embeddings for {len(catalogue)} products...")
    texts = [p["clip_text"] for p in catalogue]

    batch_size = 32
    all_embeddings = []

    for i in range(0, len(texts), batch_size):
        batch = texts[i:i + batch_size]
        inputs = _clip_processor(text=batch, return_tensors="pt", padding=True, truncation=True, max_length=77)
        with torch.no_grad():
            text_features = _clip_model.get_text_features(**inputs)
        text_features = text_features / text_features.norm(dim=-1, keepdim=True)
        all_embeddings.append(text_features.cpu().numpy())

    _catalogue_embeddings = np.vstack(all_embeddings)
    print("[Recommendation] Catalogue embeddings computed.")
    return _catalogue_embeddings


def _embed_query_text(query: str) -> np.ndarray:
    _load_clip()
    import torch
    inputs = _clip_processor(text=[query], return_tensors="pt", padding=True, truncation=True, max_length=77)
    with torch.no_grad():
        features = _clip_model.get_text_features(**inputs)
    features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy()[0]


def _embed_query_image(image_bytes: bytes) -> np.ndarray:
    _load_clip()
    import torch
    from PIL import Image

    image = Image.open(BytesIO(image_bytes)).convert("RGB")
    inputs = _clip_processor(images=image, return_tensors="pt")
    with torch.no_grad():
        features = _clip_model.get_image_features(**inputs)
    features = features / features.norm(dim=-1, keepdim=True)
    return features.cpu().numpy()[0]


def _cosine_similarity(query_emb: np.ndarray, catalogue_embs: np.ndarray) -> np.ndarray:
    return np.dot(catalogue_embs, query_emb)


def _apply_filters(catalogue: list[dict], request: RecommendationRequest) -> list[int]:
    """Return indices of products that pass all filters."""
    valid = []
    for i, p in enumerate(catalogue):
        if request.gender_filter and p["gender"].lower() != request.gender_filter.lower():
            if p["gender"].lower() != "unisex":
                continue
        if request.category_filter and p["category"].lower() != request.category_filter.lower():
            continue
        if request.price_min and p["price"] < request.price_min:
            continue
        if request.price_max and p["price"] > request.price_max:
            continue
        valid.append(i)
    return valid


def recommend_by_text(request: RecommendationRequest) -> RecommendationResponse:
    start = time.time()
    catalogue = _get_catalogue()
    embeddings = _compute_catalogue_embeddings()

    query_emb = _embed_query_text(request.query_text)
    similarities = _cosine_similarity(query_emb, embeddings)

    valid_indices = _apply_filters(catalogue, request)
    if not valid_indices:
        valid_indices = list(range(len(catalogue)))

    filtered_sims = [(idx, similarities[idx]) for idx in valid_indices]
    filtered_sims.sort(key=lambda x: x[1], reverse=True)
    top_results = filtered_sims[:request.top_k]

    results = []
    for idx, score in top_results:
        p = catalogue[idx]
        results.append(ProductCard(
            product_id=p["product_id"],
            name=p["name"],
            category=p["category"],
            sub_category=p["sub_category"],
            description=p["description"],
            color=p["color"],
            gender=p["gender"],
            season=p["season"],
            price=p["price"],
            image_url=p["image_url"],
            similarity_score=round(float(score), 4),
        ))

    elapsed = (time.time() - start) * 1000
    return RecommendationResponse(
        query_text=request.query_text,
        image_provided=False,
        total_results=len(results),
        results=results,
        processing_time_ms=round(elapsed, 2),
    )


def recommend_by_image(image_bytes: bytes, top_k: int = 10,
                        gender_filter: str = None, category_filter: str = None,
                        price_min: float = None, price_max: float = None) -> RecommendationResponse:
    start = time.time()
    catalogue = _get_catalogue()
    embeddings = _compute_catalogue_embeddings()

    query_emb = _embed_query_image(image_bytes)
    similarities = _cosine_similarity(query_emb, embeddings)

    request = RecommendationRequest(
        top_k=top_k, gender_filter=gender_filter,
        category_filter=category_filter, price_min=price_min, price_max=price_max
    )
    valid_indices = _apply_filters(catalogue, request)
    if not valid_indices:
        valid_indices = list(range(len(catalogue)))

    filtered_sims = [(idx, similarities[idx]) for idx in valid_indices]
    filtered_sims.sort(key=lambda x: x[1], reverse=True)
    top_results = filtered_sims[:top_k]

    results = []
    for idx, score in top_results:
        p = catalogue[idx]
        results.append(ProductCard(
            product_id=p["product_id"],
            name=p["name"],
            category=p["category"],
            sub_category=p["sub_category"],
            description=p["description"],
            color=p["color"],
            gender=p["gender"],
            season=p["season"],
            price=p["price"],
            image_url=p["image_url"],
            similarity_score=round(float(score), 4),
        ))

    elapsed = (time.time() - start) * 1000
    return RecommendationResponse(
        query_text=None,
        image_provided=True,
        total_results=len(results),
        results=results,
        processing_time_ms=round(elapsed, 2),
    )


def recommend_multimodal(query_text: Optional[str], image_bytes: Optional[bytes],
                          top_k: int = 10, text_weight: float = 0.6,
                          **filters) -> RecommendationResponse:
    """Combine text and image embeddings with weighted fusion."""
    start = time.time()
    catalogue = _get_catalogue()
    embeddings = _compute_catalogue_embeddings()

    query_emb = np.zeros(embeddings.shape[1])
    has_text = query_text is not None and query_text.strip()
    has_image = image_bytes is not None

    if has_text and has_image:
        text_emb = _embed_query_text(query_text)
        image_emb = _embed_query_image(image_bytes)
        query_emb = text_weight * text_emb + (1 - text_weight) * image_emb
        query_emb = query_emb / np.linalg.norm(query_emb)
    elif has_text:
        query_emb = _embed_query_text(query_text)
    elif has_image:
        query_emb = _embed_query_image(image_bytes)
    else:
        # fallback: return random popular items
        import random
        random.seed(42)
        indices = random.sample(range(len(catalogue)), min(top_k, len(catalogue)))
        results = [
            ProductCard(
                product_id=catalogue[i]["product_id"], name=catalogue[i]["name"],
                category=catalogue[i]["category"], sub_category=catalogue[i]["sub_category"],
                description=catalogue[i]["description"], color=catalogue[i]["color"],
                gender=catalogue[i]["gender"], season=catalogue[i]["season"],
                price=catalogue[i]["price"], similarity_score=0.5,
            )
            for i in indices
        ]
        elapsed = (time.time() - start) * 1000
        return RecommendationResponse(
            query_text=query_text, image_provided=False, total_results=len(results),
            results=results, processing_time_ms=round(elapsed, 2),
        )

    similarities = _cosine_similarity(query_emb, embeddings)

    request = RecommendationRequest(top_k=top_k, **filters)
    valid_indices = _apply_filters(catalogue, request)
    if not valid_indices:
        valid_indices = list(range(len(catalogue)))

    filtered_sims = [(idx, similarities[idx]) for idx in valid_indices]
    filtered_sims.sort(key=lambda x: x[1], reverse=True)
    top_results = filtered_sims[:top_k]

    results = []
    for idx, score in top_results:
        p = catalogue[idx]
        results.append(ProductCard(
            product_id=p["product_id"], name=p["name"],
            category=p["category"], sub_category=p["sub_category"],
            description=p["description"], color=p["color"],
            gender=p["gender"], season=p["season"],
            price=p["price"], image_url=p["image_url"],
            similarity_score=round(float(score), 4),
        ))

    elapsed = (time.time() - start) * 1000
    return RecommendationResponse(
        query_text=query_text, image_provided=has_image, total_results=len(results),
        results=results, processing_time_ms=round(elapsed, 2),
    )


def get_stats() -> CatalogueStats:
    catalogue = _get_catalogue()
    stats = get_catalogue_stats(catalogue)
    return CatalogueStats(**stats)
