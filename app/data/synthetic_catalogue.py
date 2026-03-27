"""
Synthetic fashion product catalogue generator.
Produces ~500 realistic fashion products with categories, descriptions,
colors, seasons, prices, and pre-computed text for CLIP embedding.
"""

import random
import hashlib
from typing import Optional

CATEGORIES = {
    "Topwear": {
        "sub_categories": ["T-Shirt", "Casual Shirt", "Formal Shirt", "Polo", "Hoodie", "Sweatshirt", "Crop Top", "Tank Top", "Kurta", "Tunic"],
        "price_range": (399, 2999),
    },
    "Bottomwear": {
        "sub_categories": ["Jeans", "Trousers", "Chinos", "Shorts", "Leggings", "Palazzos", "Joggers", "Culottes"],
        "price_range": (499, 3499),
    },
    "Dress": {
        "sub_categories": ["Maxi Dress", "A-Line Dress", "Bodycon Dress", "Shift Dress", "Wrap Dress", "Shirt Dress", "Anarkali"],
        "price_range": (799, 4999),
    },
    "Ethnic": {
        "sub_categories": ["Kurta Set", "Saree", "Lehenga", "Sherwani", "Dhoti Set", "Ethnic Jacket", "Salwar Suit"],
        "price_range": (999, 7999),
    },
    "Footwear": {
        "sub_categories": ["Sneakers", "Loafers", "Sandals", "Heels", "Boots", "Flip Flops", "Formal Shoes", "Kolhapuri"],
        "price_range": (499, 4999),
    },
    "Accessories": {
        "sub_categories": ["Watch", "Sunglasses", "Bag", "Belt", "Scarf", "Jewellery", "Cap", "Wallet"],
        "price_range": (199, 2999),
    },
}

COLORS = [
    "Black", "White", "Navy Blue", "Grey", "Maroon", "Olive", "Beige",
    "Teal", "Coral", "Mustard", "Lavender", "Rust", "Sky Blue", "Pink",
    "Forest Green", "Charcoal", "Cream", "Burgundy", "Peach", "Indigo"
]

GENDERS = ["Men", "Women", "Unisex"]
SEASONS = ["Summer", "Winter", "Monsoon", "All-Season"]
MATERIALS = ["Cotton", "Polyester", "Linen", "Silk", "Denim", "Chiffon", "Georgette", "Rayon", "Wool", "Leather"]
OCCASIONS = ["Casual", "Formal", "Party", "Festive", "Sports", "Loungewear", "Office", "Date Night", "College", "Wedding"]
FITS = ["Regular Fit", "Slim Fit", "Relaxed Fit", "Oversized", "Tailored"]
PATTERNS = ["Solid", "Striped", "Checked", "Printed", "Floral", "Geometric", "Abstract", "Polka Dot", "Colour Block"]

STYLE_ADJECTIVES = [
    "trendy", "classic", "modern", "vintage", "minimalist", "bohemian",
    "chic", "edgy", "elegant", "sporty", "preppy", "grunge", "retro",
    "sophisticated", "casual", "luxe", "street-style", "traditional"
]

_catalogue_cache: Optional[list[dict]] = None


def _generate_product_id(index: int) -> str:
    seed = f"zintoo-product-{index}"
    return f"PROD-{hashlib.md5(seed.encode()).hexdigest()[:8].upper()}"


def _generate_sku(product_id: str) -> str:
    return f"SKU-{product_id.split('-')[1]}"


def _build_description(category: str, sub_cat: str, color: str, gender: str,
                        season: str, material: str, occasion: str, fit: str,
                        pattern: str) -> str:
    style = random.choice(STYLE_ADJECTIVES)
    templates = [
        f"A {style} {color.lower()} {sub_cat.lower()} made from premium {material.lower()}. "
        f"Perfect for {occasion.lower()} occasions, designed with a {fit.lower()} silhouette "
        f"and {pattern.lower()} pattern. Ideal for the {season.lower()} season.",

        f"{gender}'s {style} {sub_cat.lower()} in {color.lower()} with a {pattern.lower()} design. "
        f"Crafted from {material.lower()}, this {fit.lower()} piece is great for {occasion.lower()} wear. "
        f"Best suited for {season.lower()} wardrobe.",

        f"Elevate your {occasion.lower()} look with this {style} {color.lower()} {sub_cat.lower()}. "
        f"Features a {fit.lower()} cut in {material.lower()} fabric with a {pattern.lower()} finish. "
        f"Designed for {gender.lower()}, perfect for {season.lower()}.",
    ]
    return random.choice(templates)


def _build_clip_text(name: str, description: str, category: str, color: str,
                      gender: str, season: str, occasion: str) -> str:
    return (
        f"{name}. {description} "
        f"Category: {category}. Color: {color}. Gender: {gender}. "
        f"Season: {season}. Occasion: {occasion}."
    )


def generate_catalogue(size: int = 500, seed: int = 42) -> list[dict]:
    global _catalogue_cache
    if _catalogue_cache is not None and len(_catalogue_cache) == size:
        return _catalogue_cache

    random.seed(seed)
    products = []

    for i in range(size):
        category = random.choice(list(CATEGORIES.keys()))
        cat_info = CATEGORIES[category]
        sub_cat = random.choice(cat_info["sub_categories"])
        color = random.choice(COLORS)
        gender = random.choice(GENDERS)
        season = random.choice(SEASONS)
        material = random.choice(MATERIALS)
        occasion = random.choice(OCCASIONS)
        fit = random.choice(FITS)
        pattern = random.choice(PATTERNS)

        price_low, price_high = cat_info["price_range"]
        price = round(random.uniform(price_low, price_high), 0)

        product_id = _generate_product_id(i)
        sku_id = _generate_sku(product_id)
        name = f"{color} {pattern} {sub_cat} - {fit}"

        description = _build_description(
            category, sub_cat, color, gender, season, material, occasion, fit, pattern
        )
        clip_text = _build_clip_text(name, description, category, color, gender, season, occasion)

        products.append({
            "product_id": product_id,
            "sku_id": sku_id,
            "name": name,
            "category": category,
            "sub_category": sub_cat,
            "description": description,
            "color": color,
            "gender": gender,
            "season": season,
            "material": material,
            "occasion": occasion,
            "fit": fit,
            "pattern": pattern,
            "price": price,
            "image_url": None,
            "clip_text": clip_text,
        })

    _catalogue_cache = products
    return products


def get_catalogue_stats(products: list[dict]) -> dict:
    categories = {}
    genders = {}
    prices = []

    for p in products:
        categories[p["category"]] = categories.get(p["category"], 0) + 1
        genders[p["gender"]] = genders.get(p["gender"], 0) + 1
        prices.append(p["price"])

    return {
        "total_products": len(products),
        "categories": categories,
        "gender_distribution": genders,
        "price_range": {"min": min(prices), "max": max(prices), "avg": round(sum(prices) / len(prices), 2)},
    }
