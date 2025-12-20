# 📁 Project Reorganization Plan

## Current Structure Issues
- 20+ documentation files in root directory
- Test files mixed with main files
- Setup scripts scattered in root
- Hard to find what you need

## Proposed Clean Structure

```
restaurant_inventory_app/
│
├── 📄 app.py                          # Main entry point
├── 📄 config.py                       # Configuration
├── 📄 requirements.txt                # Dependencies
├── 📄 Procfile                        # Deployment config
├── 📄 README.md                       # Main documentation
├── 📄 .gitignore                      # Git ignore rules
│
├── 📂 docs/                           # 📚 Documentation - User guides & technical docs
│   ├── 📂 guides/                     # 👤 User guides - How-to guides for features
│   │   ├── AI_RECIPE_GENERATOR_GUIDE.md      # AI recipe generation setup & usage
│   │   ├── ALLERGEN_MANAGEMENT_GUIDE.md      # Allergen detection features
│   │   ├── PRODUCT_IMPORT_GUIDE.md           # Import products from CSV
│   │   ├── RECIPE_IMPORT_GUIDE.md            # Import recipes from files
│   │   └── QUICKSTART_AI_RECIPE.md           # Quick start for AI features
│   │
│   ├── 📂 implementation/             # 🔧 Technical docs - Implementation details
│   │   ├── ALLERGEN_FEATURE_IMPLEMENTATION.md  # Allergen feature technical notes
│   │   ├── INTEGRATION_SUMMARY.md              # How features integrate
│   │   ├── PRODUCT_IMPORT_IMPLEMENTATION.md    # Product import technical details
│   │   └── RECIPE_IMPORT_IMPLEMENTATION.md     # Recipe import technical details
│   │
│   └── setup_api_key.md              # 🔑 API key setup instructions
│
├── 📂 scripts/                        # 🛠️ Setup & utility scripts
│   ├── setup.sh                       # Initial project setup (Linux/Mac)
│   ├── setup_tmux.sh                  # Terminal multiplexer setup
│   ├── start_with_api_key.bat        # Start app with API key (Windows)
│   └── test_streamlit.py             # Test Streamlit installation
│
├── 📂 pages/                          # 🖥️ UI pages (Streamlit) - Each file = one page
│   ├── 1_ProductDatabase.py          # Product catalog management
│   ├── 2_RecipeBuilder.py            # Create/edit recipes manually
│   ├── 3_VarianceCalculator.py       # Expected vs actual inventory
│   ├── 4_SheetToShelfInventory.py    # Physical inventory counting
│   ├── 5_InventorySummary.py         # Inventory reports & summaries
│   ├── 6_AI_Recipe_Generator.py      # AI-powered recipe creation
│   ├── 7_AllergenManagement.py       # Allergen detection & QR codes
│   └── public_allergen_report.py     # Public allergen reporting page
│
├── 📂 modules/                        # ⚙️ Business logic - Core functionality
│   ├── allergen_engine.py            # Allergen detection algorithms
│   ├── file_extractor.py             # Extract text from PDFs/docs/images
│   ├── inventory_engine.py           # Inventory counting & tracking
│   ├── product_importer.py           # Import products from CSV files
│   ├── product_manager.py            # Product database operations (CRUD)
│   ├── recipe_engine.py              # Recipe operations (save/load/calculate costs)
│   ├── recipe_parser.py              # Parse recipes from various formats
│   ├── summary_engine.py             # Generate inventory summaries
│   └── variance_engine.py            # Calculate inventory variances
│
├── 📂 ui_components/                  # 🎨 Reusable UI components
│   ├── forms.py                      # Form elements (inputs, selects)
│   ├── layout.py                     # Page layout templates
│   └── sidebar.py                    # Sidebar navigation component
│
├── 📂 utils/                          # 🔧 Helper functions - Shared utilities
│   ├── error_handler.py              # Error handling & logging
│   ├── import_logger.py              # Import activity logging
│   ├── shared_functions.py           # Common functions used everywhere
│   ├── unit_normalizer.py            # Unit conversion utilities
│   └── validator.py                  # Data validation functions
│
├── 📂 models/                         # 📋 Data models - Pydantic schemas
│   └── recipe_schema.py              # Recipe data structure definition
│
├── 📂 tests/                          # 🧪 Test suite - Automated tests
│   ├── test_ai_recipe_generator.py   # AI recipe generator tests
│   ├── test_allergen_feature.py      # Allergen feature tests
│   ├── test_app.py                   # Main app tests
│   ├── test_import_debug.py          # Import debugging tests
│   ├── test_inventory.py             # Inventory tests
│   ├── test_product_import.py        # Product import tests
│   ├── test_products.py              # Product management tests
│   ├── test_recipes.py               # Recipe tests
│   ├── test_sanity.py                # Basic sanity checks
│   └── test_variance.py              # Variance calculation tests
│
├── 📂 data/                           # 💾 Data storage - CSV & JSON files
│   ├── allergen_database.json        # Allergen information database
│   ├── count_history.json            # Inventory count history
│   ├── import_templates.json         # Saved import column mappings
│   ├── inventory.csv                 # Inventory data (if used)
│   ├── inventory_counts.json         # Current inventory counts
│   ├── product_data.csv              # Product catalog
│   ├── recipes.json                  # Recipe database
│   └── backups/                      # Automatic data backups
│
└── 📂 logs/                           # 📝 Application logs - Debug & error logs
```

## Files to Move

### Documentation → docs/
```
AI_RECIPE_GENERATOR_GUIDE.md      → docs/guides/
ALLERGEN_MANAGEMENT_GUIDE.md      → docs/guides/
PRODUCT_IMPORT_GUIDE.md           → docs/guides/
RECIPE_IMPORT_GUIDE.md            → docs/guides/
RECIPE_IMPORT_QUICKSTART.md       → docs/guides/
QUICKSTART_AI_RECIPE.md           → docs/guides/

ALLERGEN_FEATURE_IMPLEMENTATION.md → docs/implementation/
IMPLEMENTATION_COMPLETE.md         → docs/implementation/
INTEGRATION_SUMMARY.md             → docs/implementation/
PRODUCT_IMPORT_IMPLEMENTATION.md   → docs/implementation/
RECIPE_IMPORT_IMPLEMENTATION.md    → docs/implementation/

INSTALLATION_COMPLETE.txt          → docs/implementation/
TMUX_GUIDE.md                      → docs/guides/
setup_api_key.md                   → docs/
WHATS_NEW.md                       → docs/ (or delete if outdated)

README.md                          → Keep in root
```

### Scripts → scripts/
```
setup.sh                → scripts/
setup_tmux.sh          → scripts/
start_with_api_key.bat → scripts/
test_streamlit.py      → scripts/
test_import_debug.py   → tests/ (or scripts/)
```

## Benefits

✅ **Clean root directory** - Only essential files visible  
✅ **Organized docs** - Easy to find user guides vs technical docs  
✅ **Centralized scripts** - All setup/utility scripts in one place  
✅ **Better navigation** - Developers can find files faster  
✅ **Professional structure** - Follows Python project best practices

## Implementation Steps

1. Create new folder structure
2. Move files to appropriate locations
3. Update any file references in code
4. Update README.md to reflect new structure
5. Test that everything still works
6. Commit changes to git

## Notes

- GitHub workflows (`.github/`) stay in root
- Hidden files (`.gitignore`, `.venv/`) stay in root  
- Config files (`config.py`, `Procfile`) stay in root
- All existing functionality preserved
