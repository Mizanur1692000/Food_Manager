"""
Allergen Detection and Management Engine

Provides functionality for:
- AI-powered allergen detection using Claude
- Database-driven allergen matching
- Allergen report generation
- QR code creation for public allergen reports
"""

import os
import json
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Any
from pathlib import Path
import io
import base64

import anthropic
from rapidfuzz import process, fuzz
import qrcode
from qrcode.image.styledpil import StyledPilImage
from qrcode.image.styles.moduledrawers import RoundedModuleDrawer
import segno

from config import config
from utils.shared_functions import load_json_file, save_json_file

# File paths
ALLERGEN_DB_FILE = str(config.ALLERGEN_DATABASE_FILE)
RECIPES_FILE = str(config.RECIPES_FILE)
QR_CODE_DIR = config.QR_CODE_DIR

# Ensure QR code directory exists
QR_CODE_DIR.mkdir(parents=True, exist_ok=True)

# FDA Top 9 Allergens
FDA_TOP_9 = [
    "milk", "eggs", "fish", "shellfish", "tree_nuts",
    "peanuts", "wheat", "soybeans", "sesame"
]

# Additional common allergens
ADDITIONAL_ALLERGENS = [
    "gluten", "corn", "sulfites", "nightshades",
    "mustard", "celery", "lupin"
]

ALL_ALLERGENS = FDA_TOP_9 + ADDITIONAL_ALLERGENS


def load_allergen_database() -> Dict[str, Any]:
    """Load allergen database from JSON file"""
    return load_json_file(ALLERGEN_DB_FILE)


def detect_allergens_database(ingredients: List[Dict[str, Any]],
                              min_confidence: int = 70) -> Dict[str, Any]:
    """
    Detect allergens by fuzzy matching ingredients against allergen database

    Args:
        ingredients: List of ingredient dictionaries with 'product_name' or 'raw_name'
        min_confidence: Minimum fuzzy match confidence (0-100)

    Returns:
        Dictionary with detected allergens and match details
    """
    allergen_db = load_allergen_database()
    ingredient_patterns = allergen_db.get("ingredient_patterns", {})
    allergen_metadata = allergen_db.get("allergen_metadata", {})

    detected = {}
    match_details = []

    for ingredient in ingredients:
        # Get ingredient name (support both product_name and raw_name)
        ing_name = ingredient.get('product_name') or ingredient.get('raw_name', '')
        if not ing_name:
            continue

        ing_name_lower = ing_name.lower().strip()

        # Check each allergen category
        for allergen, patterns in ingredient_patterns.items():
            # Exact substring match first
            if any(pattern in ing_name_lower for pattern in patterns):
                if allergen not in detected:
                    detected[allergen] = {
                        "allergen": allergen,
                        "display_name": allergen_metadata.get(allergen, {}).get("display_name", allergen),
                        "confidence": 100,
                        "detection_method": "database_exact",
                        "matched_ingredients": [],
                        "metadata": allergen_metadata.get(allergen, {})
                    }
                detected[allergen]["matched_ingredients"].append({
                    "ingredient": ing_name,
                    "match_type": "exact",
                    "confidence": 100
                })
                continue

            # Fuzzy match
            result = process.extractOne(
                ing_name_lower,
                patterns,
                scorer=fuzz.WRatio,
                score_cutoff=min_confidence
            )

            if result:
                matched_pattern, score, _ = result
                if allergen not in detected:
                    detected[allergen] = {
                        "allergen": allergen,
                        "display_name": allergen_metadata.get(allergen, {}).get("display_name", allergen),
                        "confidence": int(score),
                        "detection_method": "database_fuzzy",
                        "matched_ingredients": [],
                        "metadata": allergen_metadata.get(allergen, {})
                    }
                detected[allergen]["matched_ingredients"].append({
                    "ingredient": ing_name,
                    "match_type": "fuzzy",
                    "pattern": matched_pattern,
                    "confidence": int(score)
                })

    return {
        "detected_allergens": list(detected.keys()),
        "allergen_details": detected,
        "detection_method": "database",
        "timestamp": datetime.now().isoformat()
    }


def detect_allergens_ai(ingredients: List[Dict[str, Any]],
                       api_key: str,
                       recipe_name: str = "") -> Optional[Dict[str, Any]]:
    """
    Use Claude AI to detect potential allergens from ingredients

    Args:
        ingredients: List of ingredient dictionaries
        api_key: Anthropic API key
        recipe_name: Name of the recipe (for context)

    Returns:
        Dictionary with AI-detected allergens or None if error
    """
    if not api_key:
        return None

    # Format ingredients for prompt
    ingredient_list = []
    for ing in ingredients:
        name = ing.get('product_name') or ing.get('raw_name', '')
        qty = ing.get('quantity', '')
        unit = ing.get('unit') or ing.get('uom', '')
        if name:
            ingredient_list.append(f"- {name} ({qty} {unit})".strip())

    if not ingredient_list:
        return None

    ingredients_text = "\n".join(ingredient_list)

    system_prompt = """You are a food safety and allergen detection expert. Analyze recipe ingredients and identify potential allergens.

Focus on FDA's Major Food Allergens (Top 9):
1. Milk (dairy products)
2. Eggs
3. Fish (finned fish)
4. Shellfish (crustacean shellfish)
5. Tree nuts (almonds, walnuts, cashews, etc.)
6. Peanuts
7. Wheat
8. Soybeans (soy)
9. Sesame

Also consider these common allergens:
- Gluten (wheat, barley, rye)
- Corn
- Sulfites
- Nightshades (tomatoes, peppers, eggplant, potatoes)
- Mustard
- Celery
- Lupin

Return ONLY valid JSON (no markdown, no code blocks) in this exact format:
{
  "allergens": [
    {
      "allergen": "milk",
      "confidence": 95,
      "reason": "Contains butter and cheese",
      "ingredients": ["Butter", "Parmesan Cheese"]
    }
  ],
  "notes": "Brief summary of allergen concerns"
}"""

    user_prompt = f"""Analyze these recipe ingredients for allergens:

Recipe: {recipe_name or "Untitled"}

Ingredients:
{ingredients_text}

Identify all potential allergens present in these ingredients. Be thorough but accurate."""

    try:
        client = anthropic.Anthropic(api_key=api_key)

        message = client.messages.create(
            model="claude-sonnet-4-20250514",
            max_tokens=2000,
            system=system_prompt,
            messages=[{"role": "user", "content": user_prompt}],
            temperature=0.2  # Lower temperature for consistency
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
        data = json.loads(content)

        # Validate structure
        if "allergens" not in data:
            return None

        # Transform to standard format
        detected = {}
        allergen_db = load_allergen_database()
        allergen_metadata = allergen_db.get("allergen_metadata", {})

        for item in data.get("allergens", []):
            allergen_key = item.get("allergen", "").lower()
            if allergen_key:
                detected[allergen_key] = {
                    "allergen": allergen_key,
                    "display_name": allergen_metadata.get(allergen_key, {}).get("display_name", allergen_key),
                    "confidence": item.get("confidence", 80),
                    "detection_method": "ai",
                    "reason": item.get("reason", ""),
                    "matched_ingredients": [{"ingredient": ing} for ing in item.get("ingredients", [])],
                    "metadata": allergen_metadata.get(allergen_key, {})
                }

        return {
            "detected_allergens": list(detected.keys()),
            "allergen_details": detected,
            "detection_method": "ai",
            "notes": data.get("notes", ""),
            "timestamp": datetime.now().isoformat()
        }

    except json.JSONDecodeError as e:
        print(f"AI response parsing error: {e}")
        return None
    except Exception as e:
        print(f"AI allergen detection error: {e}")
        return None


def combine_allergen_detections(db_result: Optional[Dict[str, Any]],
                                ai_result: Optional[Dict[str, Any]],
                                manual_allergens: Optional[List[str]] = None) -> Dict[str, Any]:
    """
    Combine allergen detections from database, AI, and manual sources

    Args:
        db_result: Database detection result
        ai_result: AI detection result
        manual_allergens: List of manually tagged allergens

    Returns:
        Combined allergen detection with merged results
    """
    combined_allergens = {}
    allergen_db = load_allergen_database()
    allergen_metadata = allergen_db.get("allergen_metadata", {})

    # Add database detections
    if db_result and db_result.get("allergen_details"):
        for allergen, details in db_result["allergen_details"].items():
            combined_allergens[allergen] = {
                **details,
                "sources": ["database"]
            }

    # Add or merge AI detections
    if ai_result and ai_result.get("allergen_details"):
        for allergen, details in ai_result["allergen_details"].items():
            if allergen in combined_allergens:
                # Merge: increase confidence, add AI as source
                combined_allergens[allergen]["confidence"] = min(100,
                    int((combined_allergens[allergen]["confidence"] + details["confidence"]) / 1.5))
                combined_allergens[allergen]["sources"].append("ai")
                if details.get("reason"):
                    combined_allergens[allergen]["ai_reason"] = details["reason"]
            else:
                # New allergen from AI
                combined_allergens[allergen] = {
                    **details,
                    "sources": ["ai"]
                }

    # Add manual allergens
    if manual_allergens:
        for allergen in manual_allergens:
            allergen_lower = allergen.lower()
            if allergen_lower in combined_allergens:
                combined_allergens[allergen_lower]["sources"].append("manual")
                combined_allergens[allergen_lower]["confidence"] = 100  # Manual is always 100%
            else:
                # New manual allergen
                combined_allergens[allergen_lower] = {
                    "allergen": allergen_lower,
                    "display_name": allergen_metadata.get(allergen_lower, {}).get("display_name", allergen),
                    "confidence": 100,
                    "detection_method": "manual",
                    "sources": ["manual"],
                    "matched_ingredients": [],
                    "metadata": allergen_metadata.get(allergen_lower, {})
                }

    # Sort by confidence (highest first), then by FDA top 9 status
    sorted_allergens = sorted(
        combined_allergens.items(),
        key=lambda x: (
            x[1].get("metadata", {}).get("fda_top_9", False),
            x[1].get("confidence", 0)
        ),
        reverse=True
    )

    return {
        "allergens": [allergen for allergen, _ in sorted_allergens],
        "allergen_details": dict(sorted_allergens),
        "detection_methods": list(set(
            source for details in combined_allergens.values()
            for source in details.get("sources", [])
        )),
        "timestamp": datetime.now().isoformat(),
        "total_detected": len(combined_allergens),
        "fda_top_9_count": sum(1 for details in combined_allergens.values()
                               if details.get("metadata", {}).get("fda_top_9", False))
    }


def generate_allergen_report(recipe_name: str,
                            allergen_data: Dict[str, Any],
                            ingredients: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Generate a formatted allergen report for a recipe

    Args:
        recipe_name: Name of the recipe
        allergen_data: Combined allergen detection data
        ingredients: List of recipe ingredients

    Returns:
        Formatted report dictionary
    """
    allergen_details = allergen_data.get("allergen_details", {})

    # Categorize by FDA Top 9 vs Others
    fda_allergens = []
    other_allergens = []

    for allergen, details in allergen_details.items():
        allergen_info = {
            "name": details.get("display_name", allergen),
            "confidence": details.get("confidence", 0),
            "icon": details.get("metadata", {}).get("icon", "⚠️"),
            "description": details.get("metadata", {}).get("description", ""),
            "sources": details.get("sources", []),
            "matched_ingredients": [
                ing.get("ingredient", "")
                for ing in details.get("matched_ingredients", [])
            ]
        }

        if details.get("metadata", {}).get("fda_top_9", False):
            fda_allergens.append(allergen_info)
        else:
            other_allergens.append(allergen_info)

    report = {
        "recipe_name": recipe_name,
        "report_date": datetime.now().strftime("%B %d, %Y at %I:%M %p"),
        "total_allergens": allergen_data.get("total_detected", 0),
        "fda_top_9_present": len(fda_allergens),
        "fda_allergens": fda_allergens,
        "other_allergens": other_allergens,
        "all_ingredients": [
            ing.get('product_name') or ing.get('raw_name', '')
            for ing in ingredients
        ],
        "detection_methods": allergen_data.get("detection_methods", []),
        "disclaimer": "This allergen information is provided as a guide. Always verify with fresh ingredients and consult with guests about specific dietary needs. Cross-contamination may occur during preparation."
    }

    return report


def generate_qr_code(recipe_id: str,
                    recipe_name: str,
                    base_url: str = "http://localhost:8501") -> Tuple[str, bytes]:
    """
    Generate QR code linking to public allergen report

    Args:
        recipe_id: Unique recipe identifier
        recipe_name: Name of the recipe (for filename)
        base_url: Base URL of the Streamlit app

    Returns:
        Tuple of (file_path, image_bytes)
    """
    # Create URL for public allergen report
    url = f"{base_url}/public_allergen_report?recipe_id={recipe_id}"

    # Generate QR code using qrcode library (with styling)
    qr = qrcode.QRCode(
        version=1,
        error_correction=qrcode.constants.ERROR_CORRECT_H,  # 30% recovery
        box_size=10,
        border=4,
    )
    qr.add_data(url)
    qr.make(fit=True)

    # Create styled image
    img = qr.make_image(
        fill_color="black",
        back_color="white",
        image_factory=StyledPilImage,
        module_drawer=RoundedModuleDrawer()
    )

    # Save to bytes
    img_bytes = io.BytesIO()
    img.save(img_bytes, format='PNG')
    img_bytes.seek(0)

    # Save to file
    safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in recipe_name)
    safe_name = safe_name.replace(' ', '_')
    filename = f"allergen_qr_{safe_name}_{recipe_id[:8]}.png"
    file_path = QR_CODE_DIR / filename

    img.save(str(file_path))

    return str(file_path), img_bytes.getvalue()


def generate_qr_code_svg(recipe_id: str,
                        recipe_name: str,
                        base_url: str = "http://localhost:8501") -> Tuple[str, str]:
    """
    Generate SVG QR code (scalable) using segno

    Args:
        recipe_id: Unique recipe identifier
        recipe_name: Name of the recipe
        base_url: Base URL of the app

    Returns:
        Tuple of (file_path, svg_string)
    """
    url = f"{base_url}/public_allergen_report?recipe_id={recipe_id}"

    # Generate QR code
    qr = segno.make(url, error='h', micro=False)

    # Save to file
    safe_name = "".join(c if c.isalnum() or c in (' ', '_') else '_' for c in recipe_name)
    safe_name = safe_name.replace(' ', '_')
    filename = f"allergen_qr_{safe_name}_{recipe_id[:8]}.svg"
    file_path = QR_CODE_DIR / filename

    qr.save(str(file_path), scale=8, border=2)

    # Get SVG string
    svg_buffer = io.BytesIO()
    qr.save(svg_buffer, kind='svg', scale=8, border=2)
    svg_string = svg_buffer.getvalue().decode('utf-8')

    return str(file_path), svg_string


def save_allergen_data(recipe_name: str, allergen_data: Dict[str, Any]) -> bool:
    """
    Save allergen data to recipe in recipes.json

    Args:
        recipe_name: Name of the recipe
        allergen_data: Allergen detection data to save

    Returns:
        True if successful, False otherwise
    """
    try:
        recipes = load_json_file(RECIPES_FILE)

        if recipe_name not in recipes:
            print(f"Recipe '{recipe_name}' not found")
            return False

        # Update recipe with allergen data
        recipes[recipe_name]["allergens"] = allergen_data.get("allergens", [])
        recipes[recipe_name]["allergen_details"] = allergen_data.get("allergen_details", {})
        recipes[recipe_name]["allergen_metadata"] = {
            "detection_methods": allergen_data.get("detection_methods", []),
            "last_updated": datetime.now().isoformat(),
            "total_detected": allergen_data.get("total_detected", 0),
            "fda_top_9_count": allergen_data.get("fda_top_9_count", 0)
        }

        # Save back to file
        return save_json_file(recipes, RECIPES_FILE)

    except Exception as e:
        print(f"Error saving allergen data: {e}")
        return False


def get_recipe_allergens(recipe_name: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve allergen information for a recipe

    Args:
        recipe_name: Name of the recipe

    Returns:
        Allergen data dictionary or None if not found
    """
    try:
        recipes = load_json_file(RECIPES_FILE)

        if recipe_name not in recipes:
            return None

        recipe = recipes[recipe_name]

        return {
            "allergens": recipe.get("allergens", []),
            "allergen_details": recipe.get("allergen_details", {}),
            "allergen_metadata": recipe.get("allergen_metadata", {}),
            "recipe_name": recipe_name
        }

    except Exception as e:
        print(f"Error retrieving allergen data: {e}")
        return None


def get_recipe_by_id(recipe_id: str) -> Optional[Dict[str, Any]]:
    """
    Retrieve recipe by recipe_id

    Args:
        recipe_id: Recipe ID to search for

    Returns:
        Recipe dictionary or None if not found
    """
    try:
        recipes = load_json_file(RECIPES_FILE)

        for recipe_name, recipe_data in recipes.items():
            if recipe_data.get("recipe_id") == recipe_id:
                return {**recipe_data, "name": recipe_name}

        return None

    except Exception as e:
        print(f"Error retrieving recipe by ID: {e}")
        return None

