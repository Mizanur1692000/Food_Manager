# 🔄 How It All Works - Restaurant Inventory App

## Overview

This document explains how all the pieces of your Restaurant Inventory App connect together. It follows the flow from user actions to data storage.

---

## 📱 The Big Picture

```
User Interaction (pages/)
    ↓
Business Logic (modules/)
    ↓
Data Storage (data/)
```

**Simple version:** Users interact with pages → pages call modules → modules save/load data.

---

## 🔄 Core Data Flow

### 1. **Creating a Recipe**

```
User opens Recipe Builder page
    ↓
pages/2_RecipeBuilder.py shows UI
    ↓
User fills out form (name, ingredients, etc.)
    ↓
User clicks "Save Recipe"
    ↓
pages/2_RecipeBuilder.py calls: modules/recipe_engine.py → save_recipe()
    ↓
modules/recipe_engine.py:
    - Calculates recipe cost
    - Adds recipe to data/recipes.json
    ↓
Success message shown to user
```

**Files involved:**
- `pages/2_RecipeBuilder.py` - UI
- `modules/recipe_engine.py` - Logic
- `data/recipes.json` - Storage

---

### 2. **Importing Products**

```
User goes to Product Database page
    ↓
User uploads CSV file
    ↓
pages/1_ProductDatabase.py receives file
    ↓
pages/1_ProductDatabase.py calls: modules/product_importer.py → import_products()
    ↓
modules/product_importer.py:
    - Parses CSV
    - Maps columns
    - Validates data
    - Saves to data/product_data.csv
    ↓
Success message with import statistics
```

**Files involved:**
- `pages/1_ProductDatabase.py` - UI
- `modules/product_importer.py` - Logic
- `data/product_data.csv` - Storage

---

### 3. **Inventory Counting**

```
User goes to "Sheet to Shelf Inventory" page
    ↓
User enters count for each product
    ↓
pages/4_SheetToShelfInventory.py collects counts
    ↓
pages/4_SheetToShelfInventory.py calls: modules/inventory_engine.py → save_count()
    ↓
modules/inventory_engine.py:
    - Saves to data/inventory_counts.json
    - Creates backup in data/backups/
    ↓
User proceeds to Variance Calculator
```

**Files involved:**
- `pages/4_SheetToShelfInventory.py` - UI
- `modules/inventory_engine.py` - Logic
- `data/inventory_counts.json` - Storage

---

### 4. **Calculating Variances**

```
User goes to Variance Calculator page
    ↓
User clicks "Calculate Variances"
    ↓
pages/3_VarianceCalculator.py calls: modules/variance_engine.py → calculate_variance()
    ↓
modules/variance_engine.py:
    - Loads expected inventory (from recipes)
    - Loads actual inventory (from count)
    - Compares them
    - Calculates differences
    ↓
Results displayed in table
```

**Files involved:**
- `pages/3_VarianceCalculator.py` - UI
- `modules/variance_engine.py` - Logic
- `data/inventory_counts.json` - Actual inventory
- `data/recipes.json` - Expected inventory (recipes)

---

## 📂 How Pages, Modules, and Data Connect

### Example: User Adds a Product

#### 1. **Page Layer** (`pages/1_ProductDatabase.py`)
```python
# User interface - collects input
product_name = st.text_input("Product Name")
price = st.number_input("Price")

# When user clicks save
if st.button("Add Product"):
    save_product({...})  # ← Calls module
```

#### 2. **Module Layer** (`modules/product_manager.py`)
```python
def save_product(product):
    # Load existing data
    df = pd.read_csv('data/product_data.csv')
    
    # Add new product
    df = df.append(product, ignore_index=True)
    
    # Save to file
    df.to_csv('data/product_data.csv', index=False)
```

#### 3. **Data Layer** (`data/product_data.csv`)
```csv
Product Name,Price,Category,Unit
Chicken Breast,5.99,Protein,lb
```

---

## 🔗 Key Connections

### Products → Recipes
- **Recipe Builder** (`pages/2_RecipeBuilder.py`) loads products from `data/product_data.csv`
- When you add an ingredient to a recipe, you select from existing products
- Recipe cost is calculated using product prices

**Connection:**
```
Recipes use products as ingredients
    ↓
Recipe cost = sum of (ingredient quantity × product price)
```

### Recipes → Inventory
- **Variance Calculator** (`pages/3_VarianceCalculator.py`) uses recipes to calculate expected inventory
- If you make 10 servings of a recipe, it expects 10× the ingredient quantities

**Connection:**
```
Expected inventory = Recipes × Servings made
Actual inventory = Count from physical inventory
Variance = Expected - Actual
```

### Import → Products
- **Product Import** (`pages/1_ProductDatabase.py`) parses CSV files
- Maps columns to standard format
- Saves to `data/product_data.csv`
- Products are immediately available in Recipe Builder

**Connection:**
```
Import CSV → Parse → Validate → Save to product_data.csv
    ↓
Now available in Recipe Builder dropdown
```

---

## 🎯 Common User Journeys

### Journey 1: "I want to track my recipe costs"

1. **Start:** Product Database page
   - Import products from your vendor's CSV
   - Products saved to `data/product_data.csv`

2. **Next:** Recipe Builder page
   - Create recipes using imported products
   - Cost automatically calculated
   - Saved to `data/recipes.json`

3. **Result:** Know exactly how much each recipe costs

---

### Journey 2: "I want to find inventory discrepancies"

1. **Start:** Sheet to Shelf Inventory page
   - Enter actual inventory counts
   - Saved to `data/inventory_counts.json`

2. **Next:** Variance Calculator page
   - Loads expected inventory from recipes
   - Compares with actual counts
   - Shows discrepancies

3. **Result:** See which products are over/under expected

---

### Journey 3: "I want to generate allergen reports"

1. **Start:** Allergen Management page
   - Recipe allergen data auto-detected
   - Generate QR codes for recipes
   - QR codes link to public allergen report

2. **Next:** Public Allergen Report page
   - Customer scans QR code
   - Sees full allergen information

3. **Result:** Customers can safely check allergens

---

## 🗂️ Data Files Explained

| File | Purpose | Used By |
|------|---------|---------|
| `data/product_data.csv` | Master product catalog | Recipe Builder, Product Database |
| `data/recipes.json` | Recipe database | Recipe Builder, Variance Calculator |
| `data/inventory_counts.json` | Current physical inventory | Variance Calculator, Inventory Summary |
| `data/count_history.json` | Historical inventory counts | Inventory Summary |
| `data/allergen_database.json` | Allergen patterns | Allergen Engine |
| `data/import_templates.json` | Saved column mappings | Product Importer |

---

## 🔄 The Cycle

```
1. Import products → data/product_data.csv
2. Create recipes → data/recipes.json
3. Count inventory → data/inventory_counts.json
4. Calculate variance → Compare expected vs actual
5. Generate reports → Summary of results
```

This cycle repeats every time you do inventory.

---

## 🎨 UI Components

Reusable components used across pages:

- **`ui_components/sidebar.py`** - Navigation menu (used on every page)
- **`ui_components/layout.py`** - Page layout templates
- **`ui_components/forms.py`** - Form input elements

**Example:**
```python
# Every page imports this
from ui_components.sidebar import setup_sidebar

def main():
    setup_sidebar()  # Shows navigation menu
    # ... rest of page ...
```

---

## 🛠️ Helper Utilities

`utils/` folder contains shared helper functions:

- **`utils/shared_functions.py`** - Load/save data, currency formatting
- **`utils/unit_normalizer.py`** - Convert "1 lb" to "16 oz"
- **`utils/validator.py`** - Validate user input
- **`utils/error_handler.py`** - Handle errors gracefully

Used by all modules.

---

## 🧪 Testing

`tests/` folder contains automated tests that verify everything works:

- `test_products.py` - Test product operations
- `test_recipes.py` - Test recipe operations
- `test_inventory.py` - Test inventory counting
- `test_variance.py` - Test variance calculations

Run with: `python -m pytest tests/`

---

## 🎯 Summary

**The Flow:**
1. **User** interacts with page
2. **Page** collects input and calls module
3. **Module** performs logic and saves data
4. **Data** stored in JSON/CSV files
5. **Results** displayed back to user

**Key Separation:**
- **`pages/`** = What user sees (UI)
- **`modules/`** = What app does (logic)
- **`data/`** = What app remembers (storage)

This separation makes the code:
- ✅ Easy to understand
- ✅ Easy to maintain
- ✅ Easy to test
- ✅ Easy to extend

---

## 📚 More Details

- **Folder structure:** See `REORGANIZATION_PLAN.md`
- **Module details:** See `docs/MODULES_FOLDER_INFO.md`
- **Data files:** See `docs/DATA_FILES_REFERENCE.md`
- **Folder differences:** See `docs/FOLDER_DIFFERENCES.md`
