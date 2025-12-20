# Integrated Data Structure Design for Menu Engineering

## Overview
This structure is optimized for integration between restaurant_inventory_app and hospitality_ai_agent, specifically for Menu Engineering analysis.

## File Structure

### 1. products.json
**Purpose**: Master product/ingredient database with costs
**Format**: JSON (changed from CSV for better integration)

```json
{
  "product_id": {
    "product_id": "uuid",
    "name": "Product Name",
    "sku": "SKU",
    "category": "Produce|Meats|Seafood|Dairy|Dry Goods|Frozen",
    "unit": "lb|oz|gallon|each",
    "cost_per_unit": 0.00,
    "pack_size": "description",
    "supplier": "Supplier Name",
    "last_updated": "ISO datetime"
  }
}
```

### 2. recipes.json
**Purpose**: Recipe database with ingredient costs
**Enhanced for Menu Engineering**

```json
{
  "recipe_id": {
    "recipe_id": "uuid",
    "name": "Recipe Name",
    "description": "Description",
    "category": "Appetizer|Main Course|Dessert|Beverage|Side",
    "servings": 4,
    "prep_time": 15,
    "cook_time": 20,
    "ingredients": [
      {
        "product_id": "uuid",
        "product_name": "Name",
        "quantity": 1.0,
        "unit": "lb"
      }
    ],
    "ingredient_costs": [
      {
        "product_id": "uuid",
        "product_name": "Name",
        "quantity": 1.0,
        "unit": "lb",
        "cost": 5.00,
        "unit_cost": 5.00
      }
    ],
    "total_cost": 15.50,
    "cost_per_serving": 3.88,
    "instructions": "Step by step...",
    "allergens": [],
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime"
  }
}
```

### 3. menu_items.json (NEW)
**Purpose**: Menu representation with pricing
**Links recipes to actual menu items**

```json
{
  "menu_item_id": {
    "menu_item_id": "uuid",
    "recipe_id": "uuid",
    "menu_name": "Display name on menu",
    "category": "Appetizer|Main Course|Dessert|Beverage|Side",
    "menu_price": 18.99,
    "recipe_cost": 5.50,
    "food_cost_percent": 28.96,
    "contribution_margin": 13.49,
    "is_active": true,
    "featured": false,
    "menu_description": "Marketing description",
    "dietary_tags": ["Vegetarian", "Gluten-Free"],
    "created_at": "ISO datetime",
    "updated_at": "ISO datetime"
  }
}
```

### 4. sales_data.json (NEW)
**Purpose**: Sales history for Menu Engineering Matrix
**Critical for Stars/Plowhorses/Puzzles/Dogs categorization**

```json
{
  "sales_records": [
    {
      "sale_id": "uuid",
      "menu_item_id": "uuid",
      "date": "2025-10-01",
      "units_sold": 45,
      "revenue": 854.55,
      "period": "daily|weekly|monthly"
    }
  ],
  "summary": {
    "menu_item_id": {
      "menu_item_id": "uuid",
      "menu_name": "Item Name",
      "total_units_sold": 450,
      "total_revenue": 8545.50,
      "avg_daily_sales": 15,
      "period_start": "2025-10-01",
      "period_end": "2025-10-31"
    }
  }
}
```

## Menu Engineering Matrix Logic

### Calculations
- **Popularity**: units_sold vs average units sold
- **Profitability**: contribution_margin vs average contribution margin
- **Food Cost %**: (recipe_cost / menu_price) * 100

### Quadrants
1. **Stars**: High profit margin (>70%) + High sales volume (>avg)
2. **Plowhorses**: Low profit margin (<70%) + High sales volume (>avg)
3. **Puzzles**: High profit margin (>70%) + Low sales volume (<avg)
4. **Dogs**: Low profit margin (<70%) + Low sales volume (<avg)

## Test Data Distribution Plan

### 28 Menu Items Distribution:
- **Appetizers**: 6 items
  - 2 Stars
  - 1 Plowhorse
  - 2 Puzzles
  - 1 Dog

- **Main Courses**: 10 items
  - 3 Stars
  - 2 Plowhorses
  - 3 Puzzles
  - 2 Dogs

- **Sides**: 4 items
  - 1 Star
  - 1 Plowhorse
  - 1 Puzzle
  - 1 Dog

- **Desserts**: 4 items
  - 1 Star
  - 1 Plowhorse
  - 1 Puzzle
  - 1 Dog

- **Beverages**: 4 items
  - 1 Star
  - 1 Plowhorse
  - 1 Puzzle
  - 1 Dog

## Integration Points

### Shared Data Directory (Option B)
```
/shared_data/
  ├── products.json
  ├── recipes.json
  ├── menu_items.json
  └── sales_data.json
```

Both apps read from this directory:
- restaurant_inventory_app: Manages products, recipes, costs
- hospitality_ai_agent: Reads menu_items + sales_data for Menu Engineering

### API Endpoints (Future)
- GET /api/menu-items
- GET /api/sales-data
- GET /api/recipes/{id}
- GET /api/menu-engineering/analysis

## Benefits
1. No data duplication
2. Single source of truth
3. JSON format for easy parsing
4. Clear separation of concerns
5. Ready for Menu Engineering Matrix analysis
6. Extensible for future features
