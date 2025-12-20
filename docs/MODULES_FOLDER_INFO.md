# ⚙️ Modules Folder - What Each Module Does

## Overview

The `modules/` folder contains all the core business logic for the application. Each module handles a specific aspect of functionality.

## Module List

### 1. `allergen_engine.py` (592 lines)
**Purpose:** Allergen detection and management  
**What it does:**
- Detects allergens in recipes using database matching and AI
- Generates allergen reports for recipes
- Creates QR codes for public allergen reports
- Manages allergen database (FDA Top 9 + additional allergens)

**Key Functions:**
- `detect_allergens_database()` - Fuzzy match ingredients against allergen patterns
- `generate_allergen_report()` - Create formatted allergen report
- `create_qr_code()` - Generate QR code linking to allergen report
- `load_allergen_database()` - Load allergen patterns

**Used By:** Allergen Management page

---

### 2. `file_extractor.py` (592 lines)
**Purpose:** Extract text from various file formats  
**What it does:**
- Extracts text from DOCX, PDF, Excel, CSV files
- Handles images using Claude Vision API
- Routes PDF pages (text vs scanned/vision)
- Supports recipe imports from multiple formats

**Key Functions:**
- `extract_text_from_docx()` - Extract from Word documents
- `extract_text_from_pdf()` - Extract from PDFs
- `extract_text_from_image()` - Extract using Claude Vision
- `route_pdf_pages()` - Decide text vs vision extraction per page

**Used By:** Recipe Import feature

---

### 3. `inventory_engine.py` (580 lines)
**Purpose:** Inventory counting and tracking  
**What it does:**
- Manages physical inventory counts
- Tracks count history
- Handles location filtering
- Saves/loads count data

**Key Functions:**
- `create_new_count()` - Start new inventory count
- `save_count_progress()` - Auto-save count progress
- `complete_count()` - Move count to history
- `load_count_history()` - Retrieve past counts

**Used By:** Sheet-to-Shelf Inventory page, Inventory Summary

---

### 4. `product_importer.py` (521 lines)
**Purpose:** Import products from supplier CSV files  
**What it does:**
- Detects CSV format (SYSCO vs standard)
- Maps supplier columns to product fields
- Auto-maps using fuzzy matching
- Saves/loads mapping templates
- Validates and imports product data

**Key Functions:**
- `detect_csv_format()` - Identify SYSCO format
- `suggest_column_mappings()` - AI-powered column suggestions
- `detect_duplicates()` - Find existing products
- `process_import_batch()` - Import and validate products

**Used By:** Product Database → Import Products tab

---

### 5. `product_manager.py` (918 lines - LARGEST)
**Purpose:** Product database operations  
**What it does:**
- CRUD operations for products (Create, Read, Update, Delete)
- Price calculations and unit conversions
- Cost per ounce calculations
- Bulk price updates from suppliers
- Data validation

**Key Functions:**
- `load_products()` - Load product catalog
- `save_product()` - Add new product
- `update_product()` - Edit existing product
- `delete_product()` - Remove product
- `calculate_cost_per_oz()` - Calculate cost per ounce
- `bulk_update_prices()` - Update prices from supplier data

**Used By:** Product Database page, almost all features that use products

---

### 6. `recipe_engine.py` (349 lines)
**Purpose:** Recipe operations  
**What it does:**
- Load and save recipes
- Calculate recipe costs
- Match ingredients to products
- Provide recipe data for UI

**Key Functions:**
- `load_recipes()` - Load recipe database
- `save_recipe()` - Save new/updated recipe
- `calculate_recipe_cost()` - Calculate total recipe cost
- `delete_recipe()` - Remove recipe
- `find_product()` - Match ingredient to product

**Used By:** Recipe Builder, AI Recipe Generator, Variance Calculator

---

### 7. `recipe_parser.py` (557 lines)
**Purpose:** Parse recipes from various formats  
**What it does:**
- Parses extracted text into structured recipes
- Uses Claude AI for intelligent parsing
- Normalizes units and quantities
- Validates recipe structure

**Key Functions:**
- `parse_recipe_with_ai()` - Parse using Claude AI
- `normalize_units()` - Standardize unit formats
- `parse_fractions()` - Handle fractional quantities
- `validate_parsed_recipe()` - Ensure data quality

**Used By:** Recipe Import feature

---

### 8. `summary_engine.py` (313 lines)
**Purpose:** Generate inventory summaries and reports  
**What it does:**
- Calculates inventory summaries by location
- Generates variance reports
- Computes financial impacts
- Creates CSV exports

**Key Functions:**
- `generate_summary()` - Create location-based summaries
- `calculate_variances()` - Compute expected vs actual
- `generate_export()` - Create CSV exports
- `calculate_financial_impact()` - Calculate cost differences

**Used By:** Inventory Summary page

---

### 9. `variance_engine.py` (467 lines)
**Purpose:** Variance calculation and analysis  
**What it does:**
- Compares expected vs actual usage
- Calculates variance percentages
- Identifies discrepancies
- Provides variance analysis

**Key Functions:**
- `calculate_variances()` - Compute variance metrics
- `analyze_variance_trends()` - Trend analysis
- `generate_variance_report()` - Create detailed reports
- `get_variance_summary()` - High-level summary

**Used By:** Variance Calculator page

---

## Module Dependencies

```
product_manager.py (core)
    ↓
recipe_engine.py (uses products)
    ↓
summary_engine.py (uses recipes & products)
    ↓
variance_engine.py (uses summaries)
```

**Standalone modules:**
- `allergen_engine.py` - Uses recipes but independent
- `file_extractor.py` - Independent utility
- `recipe_parser.py` - Used by import feature
- `inventory_engine.py` - Independent
- `product_importer.py` - Uses product_manager

## File Sizes (Lines of Code)

| Module | Lines | Complexity |
|--------|-------|------------|
| product_manager.py | 918 | Very High |
| allergen_engine.py | 592 | High |
| file_extractor.py | 592 | High |
| inventory_engine.py | 580 | High |
| recipe_parser.py | 557 | High |
| variance_engine.py | 467 | Medium |
| recipe_engine.py | 349 | Medium |
| summary_engine.py | 313 | Medium |
| product_importer.py | 521 | High |

**Total:** ~4,890 lines of core business logic

## When To Use Each Module

### Working on...
- **Product features** → `product_manager.py`
- **Recipe features** → `recipe_engine.py`, `recipe_parser.py`
- **Inventory counting** → `inventory_engine.py`
- **Import functionality** → `product_importer.py`, `file_extractor.py`
- **Allergen detection** → `allergen_engine.py`
- **Calculations** → `variance_engine.py`, `summary_engine.py`

## Summary

The `modules/` folder is the **brain** of your application. It contains all the business logic that:
- Saves and loads data
- Performs calculations
- Validates input
- Processes imports
- Generates reports

**Tip:** When adding features, these modules are where the core logic lives. The UI pages just call functions from these modules.
