# 📊 Data Files Reference

This document explains what each file in the `data/` directory is used for.

## Production Data Files

### `product_data.csv`
**Purpose:** Master product catalog  
**Contents:** All ingredients/products your restaurant uses  
**Key Fields:**
- Product Name, SKU, Location, Category
- Unit, Current Price per Unit
- Cost per Oz (calculated)
**Used By:** Recipe calculations, inventory tracking, product imports  
**Size:** ~57 products currently

---

### `recipes.json`
**Purpose:** Recipe database  
**Contents:** All recipes with ingredients, quantities, costs, instructions  
**Key Fields:**
- name, description, servings
- ingredients (product_name, quantity, unit)
- total_cost, ingredient_costs
- instructions, prep_time, cook_time
**Used By:** Recipe Builder, AI Recipe Generator, Variance Calculator  
**Size:** Multiple recipes (~511 lines currently)

---

### `inventory_counts.json`
**Purpose:** Active inventory count session  
**Contents:** Current physical inventory being counted  
**Key Fields:**
- count_name, status, location_filter
- items (product_name, expected_qty, actual_qty)
**Used By:** Sheet-to-Shelf Inventory page  
**Note:** This is the "working" count in progress

---

### `count_history.json`
**Purpose:** Historical inventory counts  
**Contents:** All completed inventory counts  
**Key Fields:** Same as inventory_counts.json but archived  
**Used By:** Inventory Summary page, variance analysis  
**Note:** Completed counts from past inventory sessions

---

### `allergen_database.json`
**Purpose:** Allergen detection patterns  
**Contents:** Ingredient keywords that indicate allergens  
**Key Fields:**
- ingredient_patterns (milk, eggs, nuts, etc.)
- allergen_metadata (display names, icons, severity)
**Used By:** Allergen Management page  
**Example:** Detects "milk" in "buttermilk", "cream", "cheese", etc.

---

### `import_templates.json`
**Purpose:** Saved column mapping templates  
**Contents:** Column mappings for product imports from suppliers  
**Key Fields:**
- Template name
- Column mappings (product_name → "Description", etc.)
**Used By:** Product import feature  
**Note:** Speeds up imports from recurring suppliers

---

## Test/Development Files

**Location:** `data/test/` folder

### Test Files
These test files are stored in `data/test/`:
- `inventory.csv` - Test/example inventory data
- `test_supplier_pricing.csv`
- `test_supplier_pricing_matching.csv`
- `test_supplier_pricing_partial.csv`
- `test_supplier_pricing_v2.csv`
- `test_supplier_pricing_alt.csv`
- `test_no_matches.csv`
- `test_updated_pricing.csv`
- `count_Engine Test Count_20250714_134702.csv` - Example inventory count export

**Purpose:** Testing the product import feature with various scenarios:
- Matching prices
- Partial matches
- No matches
- Updated pricing

**Note:** All test files are in `data/test/` to keep the main `data/` folder clean.

---

## Backups Folder

### `data/backups/`
**Purpose:** Automatic backups of data files  
**Contents:** Timestamped copies of JSON/CSV files  
**When Created:** When you save/update data  
**Note:** Safety net if data gets corrupted

---

## Other Files

### `Curated Restaurant Consulting Logo for Business Card.png`
**Purpose:** Company logo  
**Used By:** UI components (header, reports)  
**Size:** 457KB - high quality image

---

## Data Flow

```
product_data.csv (products)
    ↓
recipes.json (uses products in recipes)
    ↓
inventory_counts.json (counts products)
    ↓
count_history.json (archives completed counts)
    ↓
Variance calculations (compare expected vs actual)
```

---

## File Usage Summary

| File | Category | Read | Write | Critical |
|------|----------|------|-------|----------|
| product_data.csv | Production | ✅ | ✅ | ✅ |
| recipes.json | Production | ✅ | ✅ | ✅ |
| inventory_counts.json | Production | ✅ | ✅ | ✅ |
| count_history.json | Production | ✅ | ✅ | ✅ |
| allergen_database.json | Production | ✅ | No | No |
| import_templates.json | Production | ✅ | ✅ | No |
| test_*.csv | Test | No | No | No |
| logo.png | Media | ✅ | No | No |
| backups/ | Backup | ✅ | ✅ | No |

---

## Notes

- **Never delete** product_data.csv or recipes.json - these are your core data
- **Test files** can be safely deleted if needed
- **Backups folder** is auto-managed - don't manually edit
- **Allergen database** is read-only during normal operation
- **JSON files** are edited by the app, not manually
