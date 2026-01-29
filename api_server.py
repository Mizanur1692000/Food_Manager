import uvicorn
from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional

# Importing existing business logic
from modules import product_manager, allergen_engine
from modules import ai_recipe_service as ai_gen
from modules import recipe_engine
import importlib.util
import sys
from pathlib import Path

def import_page_module(page_name: str):
    # Deprecated: Streamlit pages removed in API-only mode
    return None

# Lazy-loaded AI recipe generator module
recipe_generator = None
from models.recipe_schema import RecipeSchema
from models.recipe_schema import validate_recipe_dict
from utils.shared_functions import load_json_file
from utils.dependency_checks import require_anthropic_key

from fastapi.responses import JSONResponse
from config import config

app = FastAPI(
    title="Food Manager API",
    description="RESTful API for the Food Manager application, providing access to products, recipes, and inventory management.",
    version="1.0.0",
)

# --- Exception Handlers ---
@app.exception_handler(Exception)
async def general_exception_handler(request, exc):
    # Use JSONResponse for proper error formatting
    return JSONResponse(
        status_code=500, 
        content={"detail": f"An internal server error occurred: {str(exc)}"}
    )

# --- Helper Functions ---
def load_recipe_generator_module():
    # Deprecated: using modules.ai_recipe_service directly
    return ai_gen

def app_recipe_to_schema(recipe: Dict[str, Any]) -> Dict[str, Any]:
    """Convert the app-format recipe dict into RecipeSchema-compatible dict."""
    # Instructions: split into steps if provided as a single string
    instr = recipe.get("instructions", "")
    if isinstance(instr, str):
        instructions = [s.strip() for s in instr.splitlines() if s.strip()]
    elif isinstance(instr, list):
        instructions = [str(s).strip() for s in instr if str(s).strip()]
    else:
        instructions = []

    # Ingredients: map to IngredientSchema fields
    ing_list = []
    for ing in recipe.get("ingredients", []):
        product_name = ing.get("product_name")
        quantity = float(ing.get("quantity", 0) or 0)
        unit = ing.get("unit", "")
        if not product_name or quantity <= 0 or not unit:
            continue
        ing_list.append({
            "raw_name": product_name,
            "mapped_name": product_name,
            "quantity": quantity,
            "uom": unit,
        })

    schema_dict = {
        "name": recipe.get("name", "Untitled Recipe"),
        "description": recipe.get("description", ""),
        "servings": int(recipe.get("servings", 4)),
        "prep_time": int(recipe.get("prep_time", 0)),
        "cook_time": int(recipe.get("cook_time", 0)),
        "category": recipe.get("category", "Other"),
        "ingredients": ing_list,
        "instructions": instructions,
        # Optional fields can be extended later
    }
    return schema_dict
def get_product_by_name(name: str):
    """Helper to find a product by its name."""
    df = product_manager.load_products()
    if df is None or df.empty:
        return None
    matches = df[df['Product Name'] == name]
    if matches.empty:
        return None
    return matches.iloc[0].to_dict()

# --- Feature Toggle Helper ---
def feature_enabled(name: str) -> bool:
    return name in getattr(config, "ACTIVE_API_FEATURES", set())

# --- Pydantic Models for Request Bodies ---
class AIRecipeRequest(BaseModel):
    prompt: str
    ingredients: Optional[List[str]] = None
    match_threshold: Optional[int] = 75

class AllergenAnalysisPayload(BaseModel):
    recipe_text: str

class AllergenAnalyzeRequest(BaseModel):
    ingredients: List[Dict[str, Any]]
    db_confidence: Optional[int] = 70
    manual_allergens: Optional[List[str]] = None
    recipe_name: Optional[str] = None

class AllergenAnalyzeRecipeRequest(BaseModel):
    recipe_name: str
    db_confidence: Optional[int] = 70
    manual_allergens: Optional[List[str]] = None
    save: Optional[bool] = False

class AllergenQRRequest(BaseModel):
    recipe_name: str
    base_url: str = "http://example.com"
    format: Optional[str] = "png"  # "png" or "svg"

class AllergenBatchAnalyzeRequest(BaseModel):
    recipe_names: List[str]
    detection_method: str  # "Database Only" | "AI Only" | "Both"
    db_confidence: Optional[int] = 70
    auto_save: Optional[bool] = True

# --- API Endpoints ---

# --- Product Endpoints ---
if feature_enabled("products"):
    @app.get("/products", tags=["Products"], summary="Get all products")
    async def get_products() -> List[Dict[str, Any]]:
        """
        Retrieves a list of all products from the product database.
        """
        try:
            df = product_manager.load_products()
            if df is None:
                return []
            return df.fillna("").to_dict('records')
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load products: {e}")

    @app.post("/products", tags=["Products"], status_code=201, summary="Add a new product")
    async def add_product(product: Dict[str, Any] = Body(..., example={
        "Product Name": "Organic Tomatoes",
        "Category": "Produce",
        "Supplier": "Farm Fresh Co.",
        "Unit": "lb",
        "Pack Size": "25 lb case",
        "Current Price per Unit": 2.50,
        "Cost per Oz": 0.156
    })) -> Dict[str, str]:
        """
        Adds a new product to the database.
        """
        try:
            # Basic validation
            required_fields = ["Product Name", "Category", "Unit", "Current Price per Unit"]
            if not all(field in product for field in required_fields):
                raise HTTPException(status_code=400, detail=f"Missing one of the required fields: {required_fields}")
                
            mapped = {
                'name': product.get('Product Name'),
                'sku': product.get('SKU', ''),
                'location': product.get('Location', 'Dry Goods Storage'),
                'category': product.get('Category', ''),
                'pack': product.get('Pack', product.get('Pack Size', '')),
                'size': product.get('Size', ''),
                'unit': product.get('Unit'),
                'cost': product.get('Current Price per Unit'),
            }
            success, message = product_manager.save_product(mapped)
            if not success:
                raise HTTPException(status_code=400, detail=message)
            return {"status": "success", "message": message}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- Recipe Endpoints (Non-AI) ---
if feature_enabled("recipes"):
    @app.get("/recipes", tags=["Recipes"], summary="Get all recipes")
    async def get_recipes() -> Dict[str, Any]:
        """
        Retrieves all recipes from the recipe database.
        """
        try:
            recipes = recipe_engine.load_recipes()
            return recipes
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load recipes: {e}")

    @app.post("/recipes", tags=["Recipes"], status_code=201, summary="Add a new recipe")
    async def add_recipe(recipe: RecipeSchema) -> Dict[str, str]:
        """
        Adds a new recipe to the database.
        
        The recipe payload must conform to the RecipeSchema model.
        """
        try:
            # Convert Pydantic model to dictionary for saving
            recipe_data = recipe.dict()
            success, message = recipe_engine.save_recipe(recipe_data)
            if not success:
                raise HTTPException(status_code=400, detail=message)
            return {"status": "success", "message": message}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

@app.post("/recipes/generate", tags=["AI"], summary="Generate a recipe via AI")
async def generate_recipe_unified(payload: AIRecipeRequest) -> Dict[str, Any]:
    """
    Unified AI recipe generation endpoint (backend mirrors Streamlit flow).
    - Request: { prompt: string, ingredients?: string[], match_threshold?: number }
    - Response: { generated_recipe, mapping_notes, ai_raw_recipe, validation }
    """
    # Build prompt (append ingredients text if provided)
    prompt = (payload.prompt or "").strip()
    if not prompt:
        raise HTTPException(status_code=400, detail="`prompt` is required.")
    if payload.ingredients:
        ing_text = ", ".join(payload.ingredients)
        prompt = f"{prompt}\n\nInclude ingredients: {ing_text}."

    # Check Anthropic key and SDK
    is_ok, api_key, message = require_anthropic_key()
    if not is_ok:
        raise HTTPException(status_code=400, detail=message)

    # Load AI module lazily and verify functions
    gen = load_recipe_generator_module()
    if not gen:
        raise HTTPException(status_code=501, detail="AI recipe generator functions not available.")

    # Call AI
    ai_recipe = gen.call_claude_for_recipe(prompt, api_key)
    if not ai_recipe:
        raise HTTPException(status_code=500, detail="Failed to generate recipe from AI.")

    # Load products for mapping
    products_df = product_manager.load_products()
    if products_df is None or products_df.empty:
        raise HTTPException(status_code=404, detail="No products found to map ingredients against.")

    # Convert to app format
    match_threshold = payload.match_threshold or 75
    recipe_data, mapping_notes = gen.convert_ai_recipe_to_app_format(ai_recipe, products_df, match_threshold)

    # Validate to support review & edit flows in other frontends
    schema_dict = app_recipe_to_schema(recipe_data)
    ok, validated, errors = validate_recipe_dict(schema_dict)

    mapped_count = sum(1 for note in mapping_notes if (note.get("score", 0) or 0) > 0)
    total_notes = len(mapping_notes)
    unmapped_count = max(0, total_notes - mapped_count)
    match_rate = round((mapped_count / total_notes * 100.0) if total_notes else 0.0, 2)

    return {
        "generated_recipe": recipe_data,
        "mapping_notes": mapping_notes,
        "mapping_summary": {
            "mapped": mapped_count,
            "unmapped": unmapped_count,
            "match_rate": match_rate
        },
        "ai_raw_recipe": ai_recipe,
        "validation": {"valid": ok, "errors": errors}
    }

# Backward-compatibility alias (hidden from schema)
@app.post("/recipes/generate-ai", include_in_schema=False)
async def generate_recipe_ai_alias(payload: AIRecipeRequest):
    return await generate_recipe_unified(payload)

# --- Review & Edit Endpoints (Backend, AI flows) ---
if feature_enabled("ai_recipe"):
    @app.post("/recipes/validate-app", tags=["AI"], summary="Validate an app-format recipe")
    async def validate_app_recipe(recipe: Dict[str, Any] = Body(..., example={
        "name": "Shrimp Tacos",
        "description": "Spicy and tangy tacos",
        "servings": 6,
        "prep_time": 20,
        "cook_time": 10,
        "category": "Main Course",
        "instructions": "1. Prep shrimp\n2. Cook\n3. Assemble",
        "ingredients": [
            {"product_name": "Shrimp", "quantity": 24, "unit": "oz"},
            {"product_name": "Cabbage", "quantity": 16, "unit": "oz"}
        ]
    })) -> Dict[str, Any]:
        """
        Accepts the app-format recipe payload and validates it against RecipeSchema.
        Returns validation status and normalized schema-compatible recipe.
        """
        schema_dict = app_recipe_to_schema(recipe)
        ok, validated, errors = validate_recipe_dict(schema_dict)
        return {
            "valid": ok,
            "errors": errors,
            "normalized_recipe": validated.dict() if ok and validated else schema_dict
        }

    @app.post("/recipes/save-app", tags=["AI"], summary="Save an app-format recipe")
    async def save_app_recipe(recipe: Dict[str, Any] = Body(..., example={
        "name": "Shrimp Tacos",
        "description": "Spicy and tangy tacos",
        "servings": 6,
        "prep_time": 20,
        "cook_time": 10,
        "category": "Main Course",
        "instructions": "1. Prep shrimp\n2. Cook\n3. Assemble",
        "ingredients": [
            {"product_name": "Shrimp", "quantity": 24, "unit": "oz"},
            {"product_name": "Cabbage", "quantity": 16, "unit": "oz"}
        ]
    })) -> Dict[str, Any]:
        """
        Saves the app-format recipe using the existing recipe_engine.save_recipe logic.
        Returns success status and message.
        """
        try:
            # recipe_engine.save_recipe expects app-format ingredients/product fields
            success, message = recipe_engine.save_recipe(recipe)
            if not success:
                # If duplicate, return 200 with a friendly "exists" status
                msg_text = str(message).lower()
                if "already exists" in msg_text:
                    return {"status": "exists", "message": message}
                # Otherwise treat as a client error
                raise HTTPException(status_code=400, detail=message)
            return {"status": "success", "message": message}
        except HTTPException:
            raise
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

# --- Allergen Endpoints ---
if feature_enabled("allergen"):
    @app.post("/allergens/analyze", tags=["Allergens"], summary="Analyze ingredients for allergens")
    async def analyze_allergens(payload: AllergenAnalyzeRequest) -> Dict[str, Any]:
        """
        Mirrors Streamlit's individual analysis flow:
        - Inputs: ingredients[], db_confidence (slider), manual_allergens (checkbox selections), recipe_name (optional)
        - Outputs: database_analysis, ai_analysis, combined_summary
        """
        ingredients = payload.ingredients or []
        if not ingredients:
            raise HTTPException(status_code=400, detail="Ingredient list cannot be empty.")

        db_conf = int(payload.db_confidence or 70)
        manual = payload.manual_allergens or None
        recipe_name = payload.recipe_name

        # 1. Database-driven detection with confidence threshold
        db_results = allergen_engine.detect_allergens_database(ingredients, min_confidence=db_conf)

        # 2. AI analysis (Claude via Anthropic)
        is_ok, api_key, message = require_anthropic_key()
        if not is_ok:
            raise HTTPException(status_code=400, detail=f"Cannot perform AI analysis: {message}")
        ai_results = allergen_engine.detect_allergens_ai(ingredients, api_key, recipe_name=recipe_name)

        # 3. Combine detections, including manual selections
        combined_results = allergen_engine.combine_allergen_detections(
            db_results,
            ai_results,
            manual
        )

        return {
            "database_analysis": db_results,
            "ai_analysis": ai_results,
            "combined_summary": combined_results
        }

    @app.post("/allergens/analyze-recipe", tags=["Allergens"], summary="Analyze a saved recipe for allergens")
    async def analyze_recipe_allergens(payload: AllergenAnalyzeRecipeRequest) -> Dict[str, Any]:
        recipe_name = str(payload.recipe_name or "").strip()
        db_confidence = int(payload.db_confidence or 70)
        manual = payload.manual_allergens or None
        do_save = bool(payload.save or False)
        if not recipe_name:
            raise HTTPException(status_code=400, detail="`recipe_name` is required.")

        recipes = recipe_engine.load_recipes()
        recipe = recipes.get(recipe_name)
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Recipe '{recipe_name}' not found.")

        ingredients = recipe.get("ingredients", [])

        db_results = allergen_engine.detect_allergens_database(ingredients, min_confidence=db_confidence)
        is_ok, api_key, message = require_anthropic_key()
        if not is_ok:
            raise HTTPException(status_code=400, detail=f"Cannot perform AI analysis: {message}")
        ai_results = allergen_engine.detect_allergens_ai(ingredients, api_key, recipe_name=recipe_name)
        combined = allergen_engine.combine_allergen_detections(db_results, ai_results, manual)

        report = allergen_engine.generate_allergen_report(recipe_name, combined, ingredients)

        if do_save:
            allergen_engine.save_allergen_data(recipe_name, combined)

        return {
            "database_analysis": db_results,
            "ai_analysis": ai_results,
            "combined_summary": combined,
            "report": report,
            "saved": do_save
        }

    @app.post("/allergens/generate-qr", tags=["Allergens"], summary="Generate allergen report QR code")
    async def generate_allergen_qr(payload: AllergenQRRequest) -> Dict[str, Any]:
        recipe_name = str(payload.recipe_name or "").strip()
        base_url = str(payload.base_url or "http://example.com").strip()
        fmt = (payload.format or "png").lower()
        if fmt not in ("png", "svg"):
            raise HTTPException(status_code=400, detail="`format` must be 'png' or 'svg'.")
        if not recipe_name:
            raise HTTPException(status_code=400, detail="`recipe_name` is required.")

        recipes = recipe_engine.load_recipes()
        recipe = recipes.get(recipe_name)
        if not recipe:
            raise HTTPException(status_code=404, detail=f"Recipe '{recipe_name}' not found.")
        recipe_id = recipe.get("recipe_id")
        if not recipe_id:
            # ensure recipe has id
            ok, msg = recipe_engine.update_recipe(recipe_name, {**recipe, "name": recipe_name})
            recipes = recipe_engine.load_recipes()
            recipe = recipes.get(recipe_name)
            recipe_id = recipe.get("recipe_id")

        if fmt == "png":
            file_path, img_bytes = allergen_engine.generate_qr_code(recipe_id, recipe_name, base_url)
            import base64
            b64 = base64.b64encode(img_bytes).decode("utf-8")
            return {"file_path": file_path, "image_base64": b64, "format": "png"}
        else:
            file_path, svg_string = allergen_engine.generate_qr_code_svg(recipe_id, recipe_name, base_url)
            return {"file_path": file_path, "svg": svg_string, "format": "svg"}

    @app.get("/allergens/recipe/{recipe_name}", tags=["Allergens"], summary="Get saved allergen data for a recipe")
    async def get_recipe_allergens(recipe_name: str) -> Dict[str, Any]:
        data = allergen_engine.get_recipe_allergens(recipe_name)
        if not data:
            raise HTTPException(status_code=404, detail="No allergen data found for recipe.")
        return data

    @app.post("/allergens/batch-analyze", tags=["Allergens"], summary="Batch analyze recipes for allergens")
    async def batch_analyze_allergens(payload: AllergenBatchAnalyzeRequest) -> Dict[str, Any]:
        """
        Mirrors Streamlit's batch analysis tab.
        - Inputs: recipe_names[], detection_method (Database Only | AI Only | Both), db_confidence, auto_save
        - Outputs: results[] table with counts and methods; saved flag if auto_save
        """
        recipe_names = payload.recipe_names or []
        method = (payload.detection_method or "Both").strip()
        db_conf = int(payload.db_confidence or 70)
        auto_save = bool(payload.auto_save or False)
        if not recipe_names:
            raise HTTPException(status_code=400, detail="`recipe_names` cannot be empty.")

        recipes = recipe_engine.load_recipes()
        is_ok, api_key, message = require_anthropic_key()
        ai_available = is_ok and bool(api_key)

        results = []
        for recipe_name in recipe_names:
            recipe = recipes.get(recipe_name)
            if not recipe:
                # Skip missing recipes but include an entry
                results.append({
                    "recipe": recipe_name,
                    "allergens": 0,
                    "fda_top_9": 0,
                    "methods": "missing"
                })
                continue

            ingredients = recipe.get("ingredients", [])
            db_result = None
            ai_result = None

            if method in ("Database Only", "Both"):
                db_result = allergen_engine.detect_allergens_database(ingredients, min_confidence=db_conf)
            if method in ("AI Only", "Both") and ai_available:
                ai_result = allergen_engine.detect_allergens_ai(ingredients, api_key, recipe_name=recipe_name)

            combined = allergen_engine.combine_allergen_detections(db_result, ai_result, None)
            if auto_save:
                allergen_engine.save_allergen_data(recipe_name, combined)

            results.append({
                "recipe": recipe_name,
                "allergens": len(combined.get('allergens', [])),
                "fda_top_9": combined.get('fda_top_9_count', 0),
                "methods": ', '.join(combined.get('detection_methods', []))
            })

        return {
            "results": results,
            "saved": auto_save
        }


# --- Inventory Endpoints ---
if feature_enabled("inventory"):
    @app.get("/inventory/counts", tags=["Inventory"], summary="Get all inventory count history")
    async def get_inventory_counts() -> List[Dict[str, Any]]:
        """
        Retrieves historical inventory count data.
        """
        try:
            # This function might not exist, let's use a direct file load as a fallback
            counts = load_json_file('data/inventory_counts.json')
            return counts
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Failed to load inventory counts: {e}")

    @app.post("/inventory/calculate_variance", tags=["Inventory"], summary="Calculate inventory variance")
    async def calculate_variance(
        start_date: str = Body(..., example="2025-12-01"),
        end_date: str = Body(..., example="2025-12-18")
    ) -> Dict[str, Any]:
        """
        Calculates inventory variance between two dates.
        Requires sales data and inventory counts to be present for the period.
        """
        try:
            # Load necessary data
            sales_data = pd.read_csv('data/sales_data.csv')
            recipes = recipe_engine.load_recipes()
            products = product_manager.load_products()
            
            # Run variance calculation
            variance_summary, _ = variance_engine.calculate_variance(
                start_date, end_date, sales_data, recipes, products
            )
            
            if variance_summary is None:
                raise HTTPException(status_code=404, detail="Could not calculate variance. Check if data is available for the selected date range.")

            return variance_summary.to_dict('records')
        except FileNotFoundError as e:
            raise HTTPException(status_code=404, detail=f"Data file not found: {e.filename}")
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"An error occurred during variance calculation: {e}")


if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
