import uvicorn
from fastapi import FastAPI, HTTPException, Body
from typing import List, Dict, Any
import pandas as pd
from pydantic import BaseModel
from typing import List, Optional

# Importing existing business logic
from modules import product_manager, recipe_engine, inventory_engine, variance_engine, allergen_engine
import importlib.util
import sys
from pathlib import Path

def import_page_module(page_name: str):
    """Dynamically imports a module from the 'pages' directory."""
    try:
        file_path = Path(__file__).parent / "pages" / f"{page_name}.py"
        spec = importlib.util.spec_from_file_location(page_name, file_path)
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            sys.modules[page_name] = module
            spec.loader.exec_module(module)
            return module
        else:
            raise ImportError(f"Could not create module spec for {page_name}")
    except Exception as e:
        print(f"Error importing page module {page_name}: {e}", file=sys.stderr)
        return None

# Lazy-loaded AI recipe generator module
recipe_generator = None
allergen_management = import_page_module("7_AllergenManagement")
from models.recipe_schema import RecipeSchema
from models.recipe_schema import validate_recipe_dict
from utils.shared_functions import load_json_file
from utils.dependency_checks import require_anthropic_key

from fastapi.responses import JSONResponse

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
    """Ensure the AI recipe generator page module is imported after SDK checks."""
    global recipe_generator
    if recipe_generator is not None:
        return recipe_generator
    # Try importing dynamically; this can fail if dependencies (e.g., anthropic) are missing
    mod = import_page_module("6_AI_Recipe_Generator")
    recipe_generator = mod
    return recipe_generator

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

# --- Pydantic Models for Request Bodies ---
class AIRecipeRequest(BaseModel):
    prompt: str
    ingredients: Optional[List[str]] = None
    match_threshold: Optional[int] = 75

class AllergenAnalysisPayload(BaseModel):
    recipe_text: str

# --- API Endpoints ---

# --- Product Endpoints ---
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

# --- Recipe Endpoints ---
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
    if not gen or not hasattr(gen, 'call_claude_for_recipe') or not hasattr(gen, 'convert_ai_recipe_to_app_format'):
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
    recipe_data, mapping_notes = gen.convert_ai_recipe_to_app_format(
        ai_recipe, products_df, match_threshold
    )

    # Validate to support review & edit flows in other frontends
    schema_dict = app_recipe_to_schema(recipe_data)
    ok, validated, errors = validate_recipe_dict(schema_dict)

    return {
        "generated_recipe": recipe_data,
        "mapping_notes": mapping_notes,
        "ai_raw_recipe": ai_recipe,
        "validation": {"valid": ok, "errors": errors}
    }

# Backward-compatibility alias (hidden from schema)
@app.post("/recipes/generate-ai", include_in_schema=False)
async def generate_recipe_ai_alias(payload: AIRecipeRequest):
    return await generate_recipe_unified(payload)

# --- Review & Edit Endpoints (Backend) ---
@app.post("/recipes/validate-app", tags=["Recipes"], summary="Validate an app-format recipe")
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

@app.post("/recipes/save-app", tags=["Recipes"], summary="Save an app-format recipe")
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
            raise HTTPException(status_code=400, detail=message)
        return {"status": "success", "message": message}
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# --- Allergen Endpoints ---
@app.post("/allergens/analyze", tags=["Allergens"], summary="Analyze ingredients for allergens")
async def analyze_allergens(ingredients: List[Dict[str, Any]] = Body(..., example=[
    {"product_name": "All-Purpose Flour", "quantity": 1, "unit": "cup"},
    {"product_name": "Milk", "quantity": 1, "unit": "cup"},
    {"product_name": "Large Eggs", "quantity": 2, "unit": "each"}
])) -> Dict[str, Any]:
    """
    Analyzes a list of ingredients to detect potential allergens using both
    the internal database and an AI-powered check.
    """
    if not ingredients:
        raise HTTPException(status_code=400, detail="Ingredient list cannot be empty.")

    # 1. Run database-driven detection (uses fuzzy/exact matching against patterns)
    db_results = allergen_engine.detect_allergens_database(ingredients)

    # 2. Run AI analysis (Claude via Anthropic)
    is_ok, api_key, message = require_anthropic_key()
    if not is_ok:
        raise HTTPException(status_code=400, detail=f"Cannot perform AI analysis: {message}")

    ai_results = allergen_engine.detect_allergens_ai(ingredients, api_key)

    # 3. Combine detections into a single summary
    combined_results = allergen_engine.combine_allergen_detections(
        db_results,
        ai_results,
        None
    )

    return {
        "database_analysis": db_results,
        "ai_analysis": ai_results,
        "combined_summary": combined_results
    }


# --- Inventory Endpoints ---
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
