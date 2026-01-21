# -*- coding: utf-8 -*-
import os
import json
from datetime import datetime

import streamlit as st
import pandas as pd
from rapidfuzz import process, fuzz
import anthropic
import requests

# Import existing recipe engine functions
from modules.recipe_engine import (
    save_recipe, load_recipes,
    format_currency, get_recipe_text
)
from modules.product_manager import load_products
from utils.dependency_checks import require_anthropic_key

# ---------- CONFIG ----------
# Note: st.set_page_config is called in ui_components/layout.py via app.py

# Claude API Key - will be set in main() function

# ---------- UNIT CONVERSION ----------
UNIT_CONVERSIONS = {
    "oz_to_lb": 16.0,
    "oz_to_gallon": 128.0,
    "oz_to_quart": 32.0,
    "oz_to_liter": 33.814,
    "oz_to_dozen": 1.0,  # For eggs, approximate
    "oz_to_bunch": 1.0,  # For herbs, approximate
    "oz_to_case": 1.0,   # Product-specific
    "oz_to_each": 1.0,   # Item-specific
}

def oz_to_unit(oz_amount: float, target_unit: str, product_info: dict = None) -> tuple[float, str]:
    """
    Convert ounces to the target unit used in the product database.
    Returns (converted_amount, unit)
    """
    target_unit = target_unit.lower().strip()

    if target_unit == "lb":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_lb"], 3), "lb"
    elif target_unit == "gallon":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_gallon"], 3), "gallon"
    elif target_unit == "quart":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_quart"], 3), "quart"
    elif target_unit == "liter":
        return round(oz_amount / UNIT_CONVERSIONS["oz_to_liter"], 3), "liter"
    elif target_unit in ["dozen", "doz"]:
        # For eggs: assume ~2 oz per egg, 12 eggs per dozen
        return round(oz_amount / 24.0, 2), "dozen"
    elif target_unit == "bunch":
        # For herbs: assume ~1 oz per bunch (rough estimate)
        return round(oz_amount, 2), "bunch"
    elif target_unit == "case":
        # Need product info for case conversions
        if product_info and "Pack Size" in product_info:
            pack_size = product_info["Pack Size"]
            # Parse pack size (e.g., "50 lb bag" -> 50 * 16 oz)
            if "lb" in str(pack_size):
                lbs = float(str(pack_size).split()[0])
                oz_per_case = lbs * 16
                return round(oz_amount / oz_per_case, 3), "case"
        return round(oz_amount / 16.0, 3), "lb"  # Fallback to lb
    elif target_unit == "each":
        # For individual items, keep as-is or convert
        return round(oz_amount, 2), "each"
    else:
        # Default: keep as oz
        return round(oz_amount, 2), "oz"

# ---------- FUZZY MATCHING ----------
@st.cache_data
def load_product_database() -> pd.DataFrame:
    """Load product database from active storage (PostgreSQL when configured)."""
    return load_products()

def map_ingredient_to_product(ingredient_name: str, products_df: pd.DataFrame, score_cutoff=75):
    """
    Fuzzy match ingredient name to Product Name in database.
    Uses exact match, fuzzy match, and substring fallback.
    Returns (product_row, match_score) or (None, 0)
    """
    if not ingredient_name or products_df.empty:
        return None, 0

    ingredient_lower = ingredient_name.lower().strip()
    product_names = products_df["Product Name"].astype(str).tolist()

    # Try exact match (case-insensitive)
    for idx, product_name in enumerate(product_names):
        if product_name.lower() == ingredient_lower:
            product_row = products_df.iloc[idx]
            return product_row.to_dict(), 100

    # Try fuzzy matching with rapidfuzz
    result = process.extractOne(
        ingredient_name,
        product_names,
        scorer=fuzz.WRatio,
        score_cutoff=score_cutoff
    )

    if result:
        matched_name, score, _ = result
        product_row = products_df[products_df["Product Name"] == matched_name].iloc[0]
        return product_row.to_dict(), int(score)

    # Fallback: Try substring matching (ingredient name contained in product name)
    for idx, product_name in enumerate(product_names):
        if ingredient_lower in product_name.lower():
            product_row = products_df.iloc[idx]
            # Calculate a score based on length ratio (longer match = better score)
            score = int(80 * len(ingredient_lower) / len(product_name))
            score = max(75, min(score, 95))  # Clamp between 75-95
            return product_row.to_dict(), score

    # Also try if product name contained in ingredient (e.g., "salt" in "kosher salt")
    for idx, product_name in enumerate(product_names):
        if product_name.lower() in ingredient_lower:
            product_row = products_df.iloc[idx]
            return product_row.to_dict(), 80

    return None, 0

# ---------- CLAUDE LLM ----------
def call_claude_for_recipe(prompt: str, api_key: str) -> dict:
    """
    Ask Claude to generate a recipe in JSON format with oz measurements.
    """
    if not api_key:
        return None

    client = anthropic.Anthropic(api_key=api_key)

    system = (
        "You are a professional culinary R&D assistant for a quick service restaurant. "
        "Return ONLY valid JSON (no prose, no markdown, no code blocks). "
        "Use ounces (oz) for ALL ingredient quantities. "
        "Provide realistic yields and portions. "
        "Keep ingredient names simple and generic (avoid brand names). "
        "Number all preparation steps clearly."
    )

    user = f"""Create a professional, scalable restaurant recipe for:

{prompt}

Return ONLY valid JSON in this exact schema:
{{
  "recipe_name": "string - the dish name",
  "description": "string - brief description of the dish",
  "servings": number - number of servings this recipe makes,
  "category": "string - recipe category (Main Course, Appetizer, Dessert, etc.)",
  "prep_time": number - preparation time in minutes,
  "cook_time": number - cooking time in minutes,
  "ingredients": [
    {{"ingredient_name": "string", "oz": number}}
  ],
  "instructions": "string - step-by-step cooking instructions with numbered steps"
}}

Important:
- Use ounces (oz) for all ingredient quantities
- Be precise with measurements
- Use generic ingredient names (e.g., "Chicken Breast" not "Tyson Chicken")
- Make servings realistic for restaurant operations
- Keep instructions concise but complete

Return ONLY the JSON object, no other text."""

    try:
        with st.spinner("Claude is generating your recipe..."):
            message = client.messages.create(
                model="claude-sonnet-4-20250514",
                max_tokens=2000,
                system=system,
                messages=[{"role": "user", "content": user}],
                temperature=0.3
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

        # Parse and validate JSON
        data = json.loads(content)
        required_keys = ["recipe_name", "ingredients", "instructions"]
        if not all(key in data for key in required_keys):
            raise ValueError(f"Missing required keys. Found: {list(data.keys())}")

        return data

    except json.JSONDecodeError as e:
        st.error(f"Claude didn't return valid JSON: {e}")
        with st.expander("See raw response"):
            st.code(content)
        return None
    except Exception as e:
        st.error(f"Error calling Claude API: {e}")
        return None

# ---------- RECIPE CONVERSION ----------
def convert_ai_recipe_to_app_format(ai_recipe: dict, products_df: pd.DataFrame,
                                     match_threshold: int = 75) -> dict:
    """
    Convert Claude's recipe format to the app's existing recipe schema.
    Maps ingredients to products and converts oz to appropriate units.
    """
    ingredients = []
    mapping_notes = []

    for ing in ai_recipe.get("ingredients", []):
        ing_name = ing.get("ingredient_name", "").strip()
        oz_amount = float(ing.get("oz", 0.0))

        if not ing_name or oz_amount <= 0:
            continue

        # Try to map to existing product
        product_info, match_score = map_ingredient_to_product(
            ing_name, products_df, score_cutoff=match_threshold
        )

        if product_info:
            product_name = product_info["Product Name"]
            product_unit = product_info["Unit"]

            # Convert oz to product's unit
            converted_qty, final_unit = oz_to_unit(oz_amount, product_unit, product_info)

            ingredients.append({
                "product_name": product_name,
                "quantity": converted_qty,
                "unit": final_unit
            })

            mapping_notes.append({
                "ai_name": ing_name,
                "matched_product": product_name,
                "score": match_score,
                "original_oz": oz_amount,
                "converted": f"{converted_qty} {final_unit}"
            })
        else:
            # No match found - add as unmapped
            mapping_notes.append({
                "ai_name": ing_name,
                "matched_product": "NO MATCH FOUND",
                "score": 0,
                "original_oz": oz_amount,
                "converted": "N/A"
            })

    # Build recipe in app's expected format
    recipe_data = {
        "name": ai_recipe.get("recipe_name", "Untitled Recipe").strip(),
        "description": ai_recipe.get("description", "").strip(),
        "servings": int(ai_recipe.get("servings", 4)),
        "prep_time": int(ai_recipe.get("prep_time", 0)),
        "cook_time": int(ai_recipe.get("cook_time", 0)),
        "category": ai_recipe.get("category", "Main Course").strip(),
        "instructions": ai_recipe.get("instructions", "").strip(),
        "ingredients": ingredients
    }

    return recipe_data, mapping_notes

# ---------- UI ----------
def main():
    st.title("AI Recipe Generator")
    st.caption("Powered by Claude • Generates recipes compatible with your product database")

    # Get API key using dependency guard
    anthropic_ok, anthropic_api_key, anthropic_msg = require_anthropic_key()
    if not anthropic_ok:
        st.error(f"⚠️ {anthropic_msg}")
        st.info("Add your API key to `.streamlit/secrets.toml` file:")
        st.code('ANTHROPIC_API_KEY = "sk-ant-your-key-here"')
        st.info("Get your API key at: https://console.anthropic.com/settings/keys")
        st.stop()
    else:
        st.success("✓ Claude API connected")

    # Load product database
    products_df = load_product_database()

    if products_df.empty:
        st.error("No products found in database. Please add products first on the Product Database page.")
        st.stop()

    st.info(f"{len(products_df)} products available in your database")

    with st.expander("View Product Database (first 20)", expanded=False):
        st.dataframe(
            products_df[["Product Name", "Category", "Unit", "Current Price per Unit", "Cost per Oz"]].head(20),
            width='stretch'
        )

    st.divider()

    # Recipe generation form
    st.subheader("Generate Recipe")

    col1, col2 = st.columns([3, 1])
    with col1:
        prompt = st.text_area(
            "Describe the recipe you want:",
            placeholder="Example: Japanese karaage (fried chicken) with crispy coating, soy-ginger marinade, served with lemon wedges and scallions. Make it for 8 servings with 5 oz portions.",
            height=120,
            help="Be specific about the dish, desired servings, portion sizes, and any special requirements."
        )

    with col2:
        st.write("**Matching Settings**")
        match_threshold = st.slider(
            "Match confidence %",
            min_value=50,
            max_value=95,
            value=75,
            step=5,
            help="Higher = stricter ingredient matching to your products"
        )
        use_backend = st.toggle("Use Backend API", value=True, help="Call FastAPI backend instead of direct SDK call")

    if st.button("Generate Recipe with AI", type="primary", width='stretch'):
        if not prompt.strip():
            st.warning("Please enter a recipe description.")
            st.stop()

        if use_backend:
            try:
                api_url = os.environ.get("FOOD_MANAGER_API_URL", "http://127.0.0.1:8000")
                resp = requests.post(
                    f"{api_url}/recipes/generate",
                    json={"prompt": prompt, "match_threshold": match_threshold},
                    timeout=120
                )
                if resp.status_code != 200:
                    st.error(f"API error: {resp.status_code} {resp.text}")
                    st.stop()
                data = resp.json()
                # Expect keys: generated_recipe, mapping_notes, ai_raw_recipe
                st.session_state["generated_recipe"] = data.get("generated_recipe")
                st.session_state["mapping_notes"] = data.get("mapping_notes", [])
                st.session_state["ai_raw_recipe"] = data.get("ai_raw_recipe")
                st.rerun()
            except Exception as e:
                st.error(f"Failed to call backend API: {e}")
                st.stop()
        else:
            # Direct SDK path
            ai_recipe = call_claude_for_recipe(prompt, anthropic_api_key)

            if not ai_recipe:
                st.stop()

            # Convert to app format
            recipe_data, mapping_notes = convert_ai_recipe_to_app_format(
                ai_recipe, products_df, match_threshold
            )

            # Store in session state
            st.session_state["generated_recipe"] = recipe_data
            st.session_state["mapping_notes"] = mapping_notes
            st.session_state["ai_raw_recipe"] = ai_recipe

            st.rerun()

    # Display generated recipe
    if "generated_recipe" in st.session_state:
        st.divider()
        st.success("Recipe generated successfully!")

        recipe = st.session_state["generated_recipe"]
        mapping_notes = st.session_state.get("mapping_notes", [])

        # Show ingredient mapping results
        st.subheader("Ingredient Mapping Results")

        mapped_count = sum(1 for note in mapping_notes if note["score"] > 0)
        unmapped_count = len(mapping_notes) - mapped_count

        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Mapped", mapped_count)
        with col2:
            st.metric("Unmapped", unmapped_count, delta_color="inverse")
        with col3:
            match_rate = (mapped_count / len(mapping_notes) * 100) if mapping_notes else 0
            st.metric("Match Rate", f"{match_rate:.0f}%")

        # Show mapping details
        if mapping_notes:
            with st.expander("View Mapping Details", expanded=(unmapped_count > 0)):
                mapping_df = pd.DataFrame(mapping_notes)
                st.dataframe(
                    mapping_df,
                    width='stretch',
                    column_config={
                        "ai_name": st.column_config.TextColumn("AI Ingredient Name", width="medium"),
                        "matched_product": st.column_config.TextColumn("Matched Product", width="medium"),
                        "score": st.column_config.NumberColumn("Match %", format="%d%%"),
                        "original_oz": st.column_config.NumberColumn("AI Amount (oz)", format="%.1f oz"),
                        "converted": st.column_config.TextColumn("Converted Amount", width="small")
                    }
                )

                if unmapped_count > 0:
                    st.warning("Some ingredients couldn't be mapped. You can manually edit them below or adjust the match threshold and regenerate.")

        st.divider()

        # Editable recipe form
        st.subheader("Review & Edit Recipe")

        col1, col2 = st.columns(2)
        with col1:
            recipe["name"] = st.text_input("Recipe Name", value=recipe["name"], key="edit_name")
            recipe["description"] = st.text_area("Description", value=recipe["description"], height=80, key="edit_desc")
            recipe["category"] = st.selectbox(
                "Category",
                ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                 "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"],
                index=0 if not recipe.get("category") else
                      ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                       "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"].index(recipe["category"])
                      if recipe["category"] in ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                                                  "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"] else 0,
                key="edit_category"
            )

        with col2:
            recipe["servings"] = st.number_input("Servings", min_value=1, value=recipe["servings"], key="edit_servings")
            recipe["prep_time"] = st.number_input("Prep Time (minutes)", min_value=0, value=recipe["prep_time"], key="edit_prep")
            recipe["cook_time"] = st.number_input("Cook Time (minutes)", min_value=0, value=recipe["cook_time"], key="edit_cook")

        # Editable ingredients
        st.write("**Ingredients**")
        st.caption("Edit quantities, units, or products as needed. Rows with valid products will be saved.")

        if recipe["ingredients"]:
            # Create editable dataframe
            ing_df = pd.DataFrame(recipe["ingredients"])

            edited_ing = st.data_editor(
                ing_df,
                num_rows="dynamic",
                width='stretch',
                column_config={
                    "product_name": st.column_config.SelectboxColumn(
                        "Product Name",
                        options=products_df["Product Name"].tolist(),
                        width="large",
                        required=True
                    ),
                    "quantity": st.column_config.NumberColumn(
                        "Quantity",
                        format="%.3f",
                        min_value=0.0,
                        width="small",
                        required=True
                    ),
                    "unit": st.column_config.SelectboxColumn(
                        "Unit",
                        options=["oz", "lb", "gallon", "quart", "liter", "case", "each", "dozen", "bunch"],
                        width="small",
                        required=True
                    )
                },
                key="ingredient_editor"
            )

            # Update recipe with edited ingredients
            recipe["ingredients"] = edited_ing.to_dict("records")
        else:
            st.warning("No ingredients were successfully mapped. Please add products manually or adjust the recipe prompt.")

        # Instructions
        st.write("**Cooking Instructions**")
        recipe["instructions"] = st.text_area(
            "Instructions",
            value=recipe["instructions"],
            height=150,
            key="edit_instructions",
            help="Step-by-step cooking instructions"
        )

        st.divider()

        # Action buttons
        col1, col2, col3 = st.columns([2, 2, 3])

        with col1:
            if st.button("Save Recipe", type="primary", width='stretch'):
                if not recipe["name"].strip():
                    st.error("Recipe name is required")
                    st.stop()

                if not recipe["ingredients"]:
                    st.error("Recipe must have at least one ingredient")
                    st.stop()

                # Filter out invalid ingredients
                valid_ingredients = [
                    ing for ing in recipe["ingredients"]
                    if ing.get("product_name") and ing.get("quantity", 0) > 0
                ]

                if not valid_ingredients:
                    st.error("No valid ingredients to save. Please add at least one ingredient with a product and quantity.")
                    st.stop()

                recipe["ingredients"] = valid_ingredients

                # Use existing save_recipe function
                success, message = save_recipe(recipe)

                if success:
                    st.success(f"{message}")
                    st.balloons()

                    # Clear session state
                    for key in ["generated_recipe", "mapping_notes", "ai_raw_recipe"]:
                        if key in st.session_state:
                            del st.session_state[key]

                    st.info("Recipe saved! View it on the Recipe Builder page.")

                    if st.button("Generate Another Recipe"):
                        st.rerun()
                else:
                    st.error(f"{message}")

        with col2:
            if st.button("Start Over", width='stretch'):
                for key in ["generated_recipe", "mapping_notes", "ai_raw_recipe"]:
                    if key in st.session_state:
                        del st.session_state[key]
                st.rerun()

        with col3:
            with st.expander("View AI Raw Output"):
                if "ai_raw_recipe" in st.session_state:
                    st.json(st.session_state["ai_raw_recipe"])

if __name__ == "__main__":
    main()
