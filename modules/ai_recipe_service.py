import json
from typing import Dict, List, Tuple

import pandas as pd
from rapidfuzz import process, fuzz
import anthropic


# --- Unit Conversion ---
UNIT_CONVERSIONS = {
    "oz_to_lb": 16.0,
    "oz_to_gallon": 128.0,
    "oz_to_quart": 32.0,
    "oz_to_liter": 33.814,
    "oz_to_dozen": 24.0,  # approx 2 oz per egg, 12 eggs
}


def oz_to_unit(oz_amount: float, target_unit: str, product_info: Dict | None = None) -> Tuple[float, str]:
    target_unit = (target_unit or "oz").lower().strip()
    if target_unit == "lb":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_lb"], 3), "lb"
    if target_unit == "gallon":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_gallon"], 3), "gallon"
    if target_unit == "quart":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_quart"], 3), "quart"
    if target_unit == "liter":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_liter"], 3), "liter"
    if target_unit in ["dozen", "doz"]:
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_dozen"], 2), "dozen"
    if target_unit == "bunch":
        return round(oz_amount, 2), "bunch"
    if target_unit == "case":
        # fallback: treat as lbs if pack size not known
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_lb"], 3), "lb"
    if target_unit == "each":
        return round(oz_amount, 2), "each"
    return round(oz_amount, 2), "oz"


def map_ingredient_to_product(ingredient_name: str, products_df: pd.DataFrame, score_cutoff: int = 75):
    if not ingredient_name or products_df is None or products_df.empty:
        return None, 0

    ingredient_lower = ingredient_name.lower().strip()
    product_names = products_df["Product Name"].astype(str).tolist()

    # Exact match
    for idx, product_name in enumerate(product_names):
        if product_name.lower() == ingredient_lower:
            return products_df.iloc[idx].to_dict(), 100

    # Fuzzy match
    result = process.extractOne(
        ingredient_name,
        product_names,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff,
    )
    if result:
        matched_name, score, _ = result
        product_row = products_df[products_df["Product Name"] == matched_name].iloc[0]
        return product_row.to_dict(), int(score)

    # Substring heuristics
    for idx, product_name in enumerate(product_names):
        if ingredient_lower in product_name.lower():
            score = max(75, min(int(80 * len(ingredient_lower) / max(1, len(product_name))), 95))
            return products_df.iloc[idx].to_dict(), score
    for idx, product_name in enumerate(product_names):
        if product_name.lower() in ingredient_lower:
            return products_df.iloc[idx].to_dict(), 80

    return None, 0


def call_claude_for_recipe(prompt: str, api_key: str) -> Dict:
    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)
    system = (
        "You are a professional culinary R&D assistant for a quick service restaurant. "
        "Return ONLY valid JSON (no prose, no markdown, no code blocks). "
        "Use ounces (oz) for ALL ingredient quantities. "
        "Provide realistic yields and portions. "
        "Keep ingredient names simple and generic. "
        "Number all preparation steps clearly."
    )
    user = f"""Create a professional, scalable restaurant recipe for:\n\n{prompt}\n\nReturn ONLY valid JSON in this exact schema:\n{{\n  \"recipe_name\": \"string\",\n  \"description\": \"string\",\n  \"servings\": number,\n  \"category\": \"string\",\n  \"prep_time\": number,\n  \"cook_time\": number,\n  \"ingredients\": [ {{\"ingredient_name\": \"string\", \"oz\": number}} ],\n  \"instructions\": \"string\"\n}}\n\nReturn ONLY the JSON object."""

    message = client.messages.create(
        model="claude-sonnet-4-20250514",
        max_tokens=2000,
        system=system,
        messages=[{"role": "user", "content": user}],
        temperature=0.3,
    )

    content = message.content[0].text.strip()
    if content.startswith("```json"):
        content = content[7:]
    if content.startswith("```"):
        content = content[3:]
    if content.endswith("```"):
        content = content[:-3]
    content = content.strip()

    data = json.loads(content)
    required_keys = ["recipe_name", "ingredients", "instructions"]
    if not all(k in data for k in required_keys):
        raise ValueError("Missing required keys in AI response")
    return data


def convert_ai_recipe_to_app_format(ai_recipe: Dict, products_df: pd.DataFrame, match_threshold: int = 75):
    ingredients: List[Dict] = []
    mapping_notes: List[Dict] = []

    for ing in ai_recipe.get("ingredients", []):
        ing_name = str(ing.get("ingredient_name", "")).strip()
        try:
            oz_amount = float(ing.get("oz", 0.0))
        except (ValueError, TypeError):
            oz_amount = 0.0
        if not ing_name or oz_amount <= 0:
            continue

        product_info, match_score = map_ingredient_to_product(ing_name, products_df, score_cutoff=match_threshold)
        if product_info:
            product_name = product_info["Product Name"]
            product_unit = product_info.get("Unit", "oz")
            converted_qty, final_unit = oz_to_unit(oz_amount, product_unit, product_info)
            ingredients.append({
                "product_name": product_name,
                "quantity": converted_qty,
                "unit": final_unit,
            })
            mapping_notes.append({
                "ai_name": ing_name,
                "matched_product": product_name,
                "score": match_score,
                "original_oz": oz_amount,
                "converted": f"{converted_qty} {final_unit}",
            })
        else:
            mapping_notes.append({
                "ai_name": ing_name,
                "matched_product": "NO MATCH FOUND",
                "score": 0,
                "original_oz": oz_amount,
                "converted": "N/A",
            })

    recipe_data = {
        "name": str(ai_recipe.get("recipe_name", "Untitled Recipe")).strip(),
        "description": str(ai_recipe.get("description", "")).strip(),
        "servings": int(ai_recipe.get("servings", 4) or 4),
        "prep_time": int(ai_recipe.get("prep_time", 0) or 0),
        "cook_time": int(ai_recipe.get("cook_time", 0) or 0),
        "category": str(ai_recipe.get("category", "Main Course")).strip(),
        "instructions": str(ai_recipe.get("instructions", "")).strip(),
        "ingredients": ingredients,
    }

    return recipe_data, mapping_notes
