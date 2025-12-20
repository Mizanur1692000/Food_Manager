"""
Recipe parser module
Handles Claude AI parsing, validation, ingredient mapping, and cost calculation
"""

import json
import re
from typing import Dict, List, Any, Tuple, Optional
from datetime import datetime
from uuid import uuid4

import pandas as pd
from rapidfuzz import process, fuzz
import anthropic

from models.recipe_schema import (
    RecipeSchema,
    IngredientSchema,
    validate_recipe_dict,
    create_ingredient_dict
)
from utils.unit_normalizer import (
    normalize_ingredient_text,
    normalize_unit,
    convert_to_oz
)

# Mapping thresholds
MAP_THRESH = {
    "auto": 90,
    "warn": 65  # Lowered to capture substring matches
}


def parse_recipe_with_claude(extracted_text: str, api_key: str, source_filename: str = "") -> Optional[Dict[str, Any]]:
    """
    Send extracted text to Claude to structure recipe

    Args:
        extracted_text: Raw text from file extraction
        api_key: Anthropic API key
        source_filename: Original filename for context

    Returns:
        Parsed recipe dict or None if failed
    """
    try:
        client = anthropic.Anthropic(api_key=api_key)

        system_prompt = """You are a professional recipe parser for restaurant operations.
Extract recipe information from the provided text and return ONLY valid JSON (no markdown, no code blocks).

Requirements:
- Extract recipe name, description, category
- Parse ALL ingredients with quantities and units
- Calculate or estimate yield_oz (total recipe yield in ounces)
- Calculate portion_oz (single serving size in ounces)
- Extract step-by-step instructions
- Identify allergens (gluten, dairy, eggs, soy, nuts, shellfish, fish, etc.)
- Use realistic restaurant-scale quantities

Return ONLY the JSON object, no other text."""

        user_prompt = f"""Parse this recipe and return structured JSON:

{extracted_text}

Return JSON in this exact schema:
{{
  "name": "Recipe Name",
  "description": "Brief description",
  "servings": 4,
  "prep_time": 30,
  "cook_time": 45,
  "category": "Main Course",
  "yield_oz": 64.0,
  "portion_oz": 16.0,
  "ingredients": [
    {{"raw_name": "2 cups flour", "quantity": 2.0, "uom": "cup"}},
    {{"raw_name": "1 lb chicken", "quantity": 1.0, "uom": "lb"}}
  ],
  "instructions": [
    "Step 1: ...",
    "Step 2: ..."
  ],
  "allergens": ["gluten", "dairy"]
}}

Important:
- Preserve exact quantities and units from the original recipe
- If yield_oz or portion_oz not specified, calculate from servings and typical portion sizes
- Split instructions into clear numbered steps
- Identify common allergens present in ingredients"""

        if source_filename:
            user_prompt = f"Source file: {source_filename}\n\n" + user_prompt

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=3000,
            system=system_prompt,
            messages=[{
                "role": "user",
                "content": user_prompt
            }],
            temperature=0.2
        )

        content = message.content[0].text.strip()

        # Clean markdown artifacts
        if content.startswith("```json"):
            content = content[7:]
        if content.startswith("```"):
            content = content[3:]
        if content.endswith("```"):
            content = content[:-3]
        content = content.strip()

        # Parse JSON
        recipe_data = json.loads(content)

        # Validate required fields
        required_fields = ["name", "ingredients"]
        for field in required_fields:
            if field not in recipe_data:
                raise ValueError(f"Missing required field: {field}")

        # Add defaults for missing fields
        if "servings" not in recipe_data:
            recipe_data["servings"] = 4
        if "prep_time" not in recipe_data:
            recipe_data["prep_time"] = 0
        if "cook_time" not in recipe_data:
            recipe_data["cook_time"] = 0
        if "category" not in recipe_data:
            recipe_data["category"] = "Other"
        if "instructions" not in recipe_data:
            recipe_data["instructions"] = []
        if "allergens" not in recipe_data:
            recipe_data["allergens"] = []
        if "description" not in recipe_data:
            recipe_data["description"] = ""

        # Estimate yield_oz and portion_oz if missing
        if "yield_oz" not in recipe_data or recipe_data["yield_oz"] is None:
            # Rough estimate: 8 oz per serving
            recipe_data["yield_oz"] = recipe_data["servings"] * 8.0
        if "portion_oz" not in recipe_data or recipe_data["portion_oz"] is None:
            recipe_data["portion_oz"] = recipe_data["yield_oz"] / recipe_data["servings"]

        return recipe_data

    except json.JSONDecodeError as e:
        print(f"JSON decode error: {e}")
        print(f"Raw content: {content[:500]}...")
        return None
    except Exception as e:
        print(f"Error parsing recipe with Claude: {e}")
        return None


def normalize_ingredients(ingredients: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Apply fraction/range/unit parsing to each ingredient

    Args:
        ingredients: List of ingredient dicts from Claude

    Returns:
        Normalized ingredient list
    """
    normalized = []

    for ing in ingredients:
        try:
            raw_name = ing.get("raw_name", "")
            quantity = float(ing.get("quantity", 1.0))
            uom = ing.get("uom", "each")

            # Normalize unit
            uom_normalized = normalize_unit(uom)

            # Convert to oz
            quantity_oz = convert_to_oz(quantity, uom_normalized)

            # Extract ingredient name (remove quantity/uom from raw_name if present)
            ingredient_name = raw_name
            # Simple pattern to remove leading quantity/unit (including decimals like .00 or 24.00)
            pattern = re.compile(r'^[\d\.\s\-–to/½¼¾⅓⅔⅛⅜⅝⅞]+\s*[a-zA-Z]*\s*', re.IGNORECASE)
            ingredient_name = pattern.sub('', ingredient_name).strip()

            if not ingredient_name:
                ingredient_name = raw_name

            normalized.append({
                "raw_name": raw_name,
                "ingredient_name": ingredient_name,
                "quantity": quantity,
                "uom": uom_normalized,
                "quantity_oz": round(quantity_oz, 3),
                "estimate": False  # Claude provides explicit quantities
            })
        except Exception as e:
            print(f"Error normalizing ingredient {ing}: {e}")
            # Add as-is with defaults
            normalized.append({
                "raw_name": ing.get("raw_name", "Unknown"),
                "ingredient_name": ing.get("raw_name", "Unknown"),
                "quantity": 1.0,
                "uom": "each",
                "quantity_oz": 8.0,
                "estimate": True
            })

    return normalized


def map_ingredient_to_product(ingredient_name: str, products_df: pd.DataFrame, score_cutoff: int = 50) -> Tuple[Optional[Dict], int]:
    """
    Enhanced fuzzy match ingredient to product database
    Uses exact match, fuzzy match, and substring fallback matching

    Returns:
        Tuple of (product_dict or None, match_score)
    """
    import sys

    if not ingredient_name or products_df.empty:
        return None, 0

    ingredient_lower = ingredient_name.lower().strip()
    product_names = products_df["Product Name"].astype(str).tolist()

    print(f"[MATCHING] Trying to match ingredient: '{ingredient_name}'", file=sys.stderr)
    print(f"[MATCHING] Total products in database: {len(product_names)}", file=sys.stderr)

    # 1. Try exact match (case-insensitive)
    for idx, product_name in enumerate(product_names):
        if product_name.lower() == ingredient_lower:
            product_row = products_df.iloc[idx]
            print(f"[MATCHING] ✅ Exact match found: '{product_name}' (score: 100)", file=sys.stderr)
            return product_row.to_dict(), 100

    # 2. Try fuzzy matching with rapidfuzz
    # First, try without cutoff to see best match score
    best_result = process.extractOne(
        ingredient_name,
        product_names,
        scorer=fuzz.WRatio,
        score_cutoff=0
    )

    if best_result:
        best_name, best_score, _ = best_result
        print(f"[MATCHING] Best fuzzy match: '{best_name}' (score: {best_score})", file=sys.stderr)

    result = process.extractOne(
        ingredient_name,
        product_names,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff
    )

    if result:
        matched_name, score, _ = result
        product_row = products_df[products_df["Product Name"] == matched_name].iloc[0]
        print(f"[MATCHING] ✅ Fuzzy match found: '{matched_name}' (score: {score})", file=sys.stderr)
        return product_row.to_dict(), int(score)

    # 3. Fallback: Try substring matching (ingredient name contained in product name)
    # e.g., "soy sauce" matches "Sauce Soy"
    for idx, product_name in enumerate(product_names):
        if ingredient_lower in product_name.lower():
            product_row = products_df.iloc[idx]
            # Calculate a score based on length ratio (longer match = better score)
            score = int(80 * len(ingredient_lower) / len(product_name))
            score = max(65, min(score, 95))  # Clamp between 65-95
            print(f"[MATCHING] ✅ Substring match (ing in prod): '{product_name}' (score: {score})", file=sys.stderr)
            return product_row.to_dict(), score

    # 4. Also try if product name contained in ingredient (e.g., "salt" matches "kosher salt")
    for idx, product_name in enumerate(product_names):
        product_lower = product_name.lower()
        if product_lower in ingredient_lower:
            product_row = products_df.iloc[idx]
            # Calculate score based on how much of the ingredient the product name covers
            score = int(75 * len(product_lower) / len(ingredient_lower))
            score = max(65, min(score, 90))  # Clamp between 65-90
            print(f"[MATCHING] ✅ Substring match (prod in ing): '{product_name}' (score: {score})", file=sys.stderr)
            return product_row.to_dict(), score

    # 5. Word-based matching: Find ALL candidates, then pick the best
    # Remove common cooking terms and punctuation
    stop_words = {'chopped', 'minced', 'diced', 'sliced', 'fresh', 'raw', 'cooked', 'dried', 'whole', 'ground', 'cut'}
    ingredient_words = set(w.strip(',').strip('()') for w in ingredient_lower.split() if len(w.strip(',').strip('()')) > 2) - stop_words

    candidates = []
    for idx, product_name in enumerate(product_names):
        product_words = set(w.strip(',').strip('()') for w in product_name.lower().split() if len(w) > 2) - stop_words
        # Check for common words
        common_words = ingredient_words & product_words
        significant_common = [w for w in common_words if len(w) >= 4]  # At least 4 chars

        if len(significant_common) >= 2:
            # Strong match: 2+ significant words
            coverage = len(significant_common) / len(ingredient_words) if ingredient_words else 0
            score = int(70 + (coverage * 20))  # 70-90 based on coverage
            candidates.append((product_name, score, idx, significant_common))
        elif len(significant_common) == 1 and len(significant_common[0]) >= 5:
            # Weaker match: 1 significant word (5+ chars)
            # But ONLY if it's a unique/specific word
            word = significant_common[0]
            # Prefer if the word appears in few products (more specific)
            word_count = sum(1 for pn in product_names if word in pn.lower())
            if word_count <= 5:  # Word appears in 5 or fewer products
                score = 67  # Low score for single-word matches
                candidates.append((product_name, score, idx, significant_common))

    # Pick the best candidate (highest score, most common words)
    if candidates:
        best_match = max(candidates, key=lambda x: (x[1], len(x[3])))  # Sort by score, then word count
        product_row = products_df.iloc[best_match[2]]
        print(f"[MATCHING] ✅ Word-based match: '{best_match[0]}' (common: {best_match[3]}, score: {best_match[1]})", file=sys.stderr)
        return product_row.to_dict(), best_match[1]

    print(f"[MATCHING] ❌ No match found for '{ingredient_name}'", file=sys.stderr)
    return None, 0


def map_ingredients_to_products(
    ingredients: List[Dict[str, Any]],
    products_df: pd.DataFrame,
    match_threshold: int = 65
) -> List[Dict[str, Any]]:
    """
    Map ingredients to products with tiered confidence badges

    Args:
        ingredients: Normalized ingredient list
        products_df: Product database
        match_threshold: Minimum score to consider (default 65)

    Returns:
        Ingredients with mapping info added
    """
    mapped_ingredients = []

    for ing in ingredients:
        ingredient_name = ing.get("ingredient_name", ing.get("raw_name", ""))

        # Try to map
        product_info, score = map_ingredient_to_product(ingredient_name, products_df, score_cutoff=match_threshold)

        if product_info and score >= MAP_THRESH["auto"]:
            # Auto-map (green)
            ing["mapped_name"] = product_info["Product Name"]
            ing["mapping_confidence"] = float(score)
            ing["confidence_badge"] = "green"
            ing["product_info"] = product_info
        elif product_info and score >= MAP_THRESH["warn"]:
            # Warn (yellow)
            ing["mapped_name"] = product_info["Product Name"]
            ing["mapping_confidence"] = float(score)
            ing["confidence_badge"] = "yellow"
            ing["product_info"] = product_info
        else:
            # Unmapped (red)
            ing["mapped_name"] = None
            ing["mapping_confidence"] = float(score) if score > 0 else 0.0
            ing["confidence_badge"] = "red"
            ing["product_info"] = None

        mapped_ingredients.append(ing)

    return mapped_ingredients


def calculate_recipe_costs(ingredients: List[Dict[str, Any]]) -> Tuple[List[Dict[str, Any]], float]:
    """
    Calculate costs for each ingredient and total recipe cost

    Args:
        ingredients: Mapped ingredients with product_info

    Returns:
        Tuple of (ingredients with costs, total_recipe_cost)
    """
    total_cost = 0.0

    for ing in ingredients:
        if ing.get("product_info"):
            product = ing["product_info"]

            # Get price per oz
            if "Cost per Oz" in product:
                price_per_oz = float(product["Cost per Oz"])
            elif "Current Price per Unit" in product:
                price_per_unit = float(product["Current Price per Unit"])
                unit = product.get("Unit", "each")
                # Convert to price per oz (rough estimate)
                if unit.lower() == "lb":
                    price_per_oz = price_per_unit / 16.0
                elif unit.lower() == "oz":
                    price_per_oz = price_per_unit
                else:
                    price_per_oz = price_per_unit / 8.0  # Rough estimate
            else:
                price_per_oz = 0.0

            # Calculate total cost
            quantity_oz = ing.get("quantity_oz", 0.0)
            ingredient_cost = price_per_oz * quantity_oz

            ing["price_per_oz"] = round(price_per_oz, 4)
            ing["total_cost"] = round(ingredient_cost, 2)

            total_cost += ingredient_cost
        else:
            # No product mapped
            ing["price_per_oz"] = 0.0
            ing["total_cost"] = 0.0

    return ingredients, round(total_cost, 2)


def validate_parsed_recipe(recipe_dict: Dict[str, Any]) -> Dict[str, Any]:
    """
    Validate recipe using Pydantic schema

    Returns:
        Dict with validation status, recipe, errors
    """
    # Prepare ingredients for validation
    ingredients_validated = []
    for ing in recipe_dict.get("ingredients", []):
        try:
            # Ensure required fields exist
            ing_dict = {
                "raw_name": ing.get("raw_name", "Unknown"),
                "quantity": float(ing.get("quantity", 1.0)),
                "uom": ing.get("uom", "each"),
                "mapped_name": ing.get("mapped_name"),
                "quantity_oz": ing.get("quantity_oz"),
                "price_per_oz": ing.get("price_per_oz"),
                "total_cost": ing.get("total_cost"),
                "mapping_confidence": ing.get("mapping_confidence"),
                "confidence_badge": ing.get("confidence_badge"),
                "estimate": ing.get("estimate", False)
            }
            ingredients_validated.append(ing_dict)
        except Exception as e:
            print(f"Error validating ingredient {ing}: {e}")

    recipe_dict["ingredients"] = ingredients_validated

    # Add recipe_id if missing
    if "recipe_id" not in recipe_dict:
        recipe_dict["recipe_id"] = str(uuid4())

    # Validate with Pydantic
    is_valid, validated_recipe, errors = validate_recipe_dict(recipe_dict)

    return {
        "valid": is_valid,
        "recipe": validated_recipe.model_dump() if validated_recipe else recipe_dict,
        "errors": errors
    }


def process_recipe_import(
    extracted_text: str,
    api_key: str,
    products_df: pd.DataFrame,
    source_metadata: Dict[str, Any],
    match_threshold: int = 65
) -> Dict[str, Any]:
    """
    Complete recipe import pipeline

    Args:
        extracted_text: Text from file extraction
        api_key: Anthropic API key
        products_df: Product database
        source_metadata: File source info (filename, type, pages, hash)
        match_threshold: Fuzzy match threshold (default 65)

    Returns:
        Dict with status, recipe, validation, mapping_stats
    """
    # Step 1: Parse with Claude
    parsed_recipe = parse_recipe_with_claude(
        extracted_text,
        api_key,
        source_filename=source_metadata.get("filename", "")
    )

    if not parsed_recipe:
        return {
            "status": "error",
            "error": "Failed to parse recipe with Claude AI",
            "recipe": None
        }

    # Step 2: Normalize ingredients
    normalized_ingredients = normalize_ingredients(parsed_recipe.get("ingredients", []))

    # Step 3: Map to products
    mapped_ingredients = map_ingredients_to_products(
        normalized_ingredients,
        products_df,
        match_threshold
    )

    # Step 4: Calculate costs
    costed_ingredients, total_cost = calculate_recipe_costs(mapped_ingredients)

    # Update recipe with processed ingredients
    parsed_recipe["ingredients"] = costed_ingredients
    parsed_recipe["total_cost"] = total_cost

    # Add source metadata
    parsed_recipe["source"] = source_metadata

    # Add audit info
    parsed_recipe["audit"] = {
        "created_by": "recipe_importer",
        "created_at": datetime.now().isoformat()
    }

    # Step 5: Validate
    validation_result = validate_parsed_recipe(parsed_recipe)

    # Calculate mapping statistics
    auto_mapped = sum(1 for ing in costed_ingredients if ing.get("confidence_badge") == "green")
    warn_mapped = sum(1 for ing in costed_ingredients if ing.get("confidence_badge") == "yellow")
    unmapped = sum(1 for ing in costed_ingredients if ing.get("confidence_badge") == "red")

    mapping_stats = {
        "total": len(costed_ingredients),
        "auto_mapped": auto_mapped,
        "warn_mapped": warn_mapped,
        "unmapped": unmapped,
        "match_rate": round((auto_mapped + warn_mapped) / len(costed_ingredients) * 100, 1) if costed_ingredients else 0
    }

    return {
        "status": "success",
        "recipe": validation_result["recipe"],
        "validation": {
            "valid": validation_result["valid"],
            "errors": validation_result["errors"]
        },
        "mapping_stats": mapping_stats
    }

