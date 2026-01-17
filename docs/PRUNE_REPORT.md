# Prune Report (Draft)

This report identifies files and modules that appear unnecessary for the current system where only the API endpoints `/recipes/generate` and `/allergens/analyze` are active. Deletion is potentially destructive; please confirm scope before we remove files.

## Safe Changes Already Made
- API: Feature toggles added in `config.ACTIVE_API_FEATURES` to keep only AI Recipe and Allergen endpoints active.
- API: Conditionals in `api_server.py` to disable Products, non-AI Recipes, and Inventory endpoints without deletion.
- Tests: `api_test_runner.py` updated to target only active endpoints.

## Candidates for Deletion (if API-only system)
- Scripts (Linux/macOS): `scripts/setup_tmux.sh`, `scripts/setup.sh`, `run_app.sh` (Windows environment not using these).
- Pages unrelated to AI/Allergens:
  - `pages/1_ProductDatabase.py`
  - `pages/2_RecipeBuilder.py`
  - `pages/3_VarianceCalculator.py`
  - `pages/4_SheetToShelfInventory.py`
  - `pages/5_InventorySummary.py`
  - `pages/public_allergen_report.py` (keep if public QR flows required)
- Modules not used by active API endpoints:
  - `modules/inventory_engine.py`
  - `modules/variance_engine.py`
  - `modules/summary_engine.py`
  - `modules/product_importer.py` (only used by Product DB & tests)
  - `modules/file_extractor.py` (used by recipe import UI)
  - `modules/recipe_parser.py` (used by recipe import UI)
- Tests targeting disabled features:
  - `tests/test_import_debug.py`
  - `tests/test_inventory.py`
  - `tests/test_products.py`
  - `tests/test_recipes.py`
  - `tests/test_variance.py`
  - `tests/modules/test_inventory_engine.py`
- Data files for disabled features (verify not referenced elsewhere):
  - `data/inventory.csv`, `data/inventory_counts.json`, `data/count_history.json`, `data/sales_data.csv`, `data/test_supplier_pricing*.csv`

## Keep (used by active features)
- `pages/6_AI_Recipe_Generator.py` (source of backend helpers)
- `pages/7_AllergenManagement.py` (may contain shared logic)
- `modules/product_manager.py` (used for ingredient mapping against product DB)
- `models/recipe_schema.py` and `utils/shared_functions.py`, `utils/dependency_checks.py`
- `data/product_data.csv`, `data/allergen_database.json`

## Recommendation
- Prefer moving backend helpers out of Streamlit pages into `modules/ai_recipe_service.py` to eliminate Streamlit warnings when used by the API.
- Confirm whether the Streamlit app (`app.py`) is still needed. If so, keep pages and UI components; otherwise, we can remove Streamlit-specific files.

Please confirm which environment you plan to keep (API-only vs Streamlit+API). After confirmation, I will apply the deletions above safely.
