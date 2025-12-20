# 📁 Folder Differences - modules/ vs pages/ vs ui_components/

## Quick Summary

| Folder | What It Contains | Purpose | Has UI? | Has Logic? |
|--------|-----------------|---------|---------|------------|
| **modules/** | Business logic | Core functionality | ❌ No | ✅ Yes |
| **pages/** | UI pages | User interface | ✅ Yes | ⚠️ Minimal |
| **ui_components/** | Reusable UI | Shared components | ✅ Yes | ❌ No |

---

## Detailed Comparison

### 1. `modules/` - The Brain (Backend Logic)

**Purpose:** Core business logic and data operations

**Contains:**
- Data loading/saving functions
- Calculations (costs, variances, etc.)
- Processing logic (parsing, mapping, validation)
- Database operations

**Code Example:**
```python
# modules/recipe_engine.py
def calculate_recipe_cost(recipe):
    """Calculate total recipe cost"""
    total = 0
    for ingredient in recipe['ingredients']:
        product = find_product(ingredient['product_name'])
        cost = ingredient['quantity'] * product['price']
        total += cost
    return total
```

**Characteristics:**
- ✅ Pure functions (no Streamlit calls)
- ✅ Reusable across multiple pages
- ✅ Can be imported anywhere
- ❌ No UI elements
- ❌ No `st.write()`, `st.button()`, etc.

**Files:** 9 modules (recipe_engine.py, product_manager.py, etc.)

---

### 2. `pages/` - The Face (User Interface)

**Purpose:** User-facing pages that users interact with

**Contains:**
- Streamlit UI code (`st.button()`, `st.text_input()`, etc.)
- Page-specific logic
- Calls functions from `modules/`

**Code Example:**
```python
# pages/2_RecipeBuilder.py
def main():
    # Load data using module function
    recipes = load_recipes()  # ← From modules/recipe_engine.py
    
    # Display UI
    st.header("Recipe Builder")
    
    # Call module function when user clicks button
    if st.button("Save Recipe"):
        save_recipe(recipe_data)  # ← From modules/recipe_engine.py
```

**Characteristics:**
- ✅ Contains Streamlit UI elements
- ✅ One file per page (shown in sidebar)
- ✅ Calls functions from `modules/`
- ✅ Page-specific, not reusable
- ⚠️ Minimal logic (most logic in modules)

**Files:** 8 pages (1_ProductDatabase.py, 2_RecipeBuilder.py, etc.)

---

### 3. `ui_components/` - Building Blocks

**Purpose:** Reusable UI components used across pages

**Contains:**
- Sidebar navigation
- Layout templates
- Form elements
- Shared UI code

**Code Example:**
```python
# ui_components/sidebar.py
def create_navigation_buttons(pages):
    """Create navigation buttons in sidebar"""
    for page in pages:
        if st.sidebar.button(page["display"]):
            return page["name"]
```

**Characteristics:**
- ✅ Contains Streamlit UI elements
- ✅ Reusable across multiple pages
- ✅ Imported by pages and app.py
- ❌ No business logic
- ❌ No data operations

**Files:** 3 files (sidebar.py, layout.py, forms.py)

---

## Visual Comparison

### Example: Saving a Recipe

#### 1. `modules/recipe_engine.py` (Logic)
```python
def save_recipe(recipe):
    """Save recipe to JSON file"""
    recipes = load_json_file("data/recipes.json")
    recipes[recipe['name']] = recipe
    save_json_file("data/recipes.json", recipes)
```

**What it does:**
- Loads JSON file
- Adds recipe
- Saves JSON file
- **No UI code**

#### 2. `pages/2_RecipeBuilder.py` (UI)
```python
def main():
    st.header("Recipe Builder")
    
    # Collect data from user
    recipe_name = st.text_input("Recipe Name")
    
    # When user clicks button, call module function
    if st.button("Save"):
        save_recipe(recipe_data)  # ← Uses modules/recipe_engine.py
        st.success("Recipe saved!")
```

**What it does:**
- Shows UI elements
- Collects user input
- Calls module function
- Shows success message

#### 3. `ui_components/sidebar.py` (Navigation)
```python
def setup_sidebar():
    """Create sidebar navigation"""
    st.sidebar.title("Navigation")
    
    if st.sidebar.button("Recipe Builder"):
        return "2_RecipeBuilder"
```

**What it does:**
- Creates navigation buttons
- Used on every page
- **No business logic**

---

## Data Flow

```
User clicks button (pages/)
    ↓
Calls function (modules/)
    ↓
Function processes data (modules/)
    ↓
Returns result (modules/)
    ↓
Displays result (pages/)
```

**Example:**
```
User clicks "Calculate Cost" button (pages/2_RecipeBuilder.py)
    ↓
Calls calculate_recipe_cost() (modules/recipe_engine.py)
    ↓
Function calculates (modules/recipe_engine.py)
    ↓
Returns $25.50 (modules/recipe_engine.py)
    ↓
Displays "Total Cost: $25.50" (pages/2_RecipeBuilder.py)
```

---

## When To Use Each Folder

### Put code in `modules/` when:
- ✅ Saving/loading data
- ✅ Performing calculations
- ✅ Processing data
- ✅ Validating input
- ❌ Creating UI elements
- ❌ Getting user input

### Put code in `pages/` when:
- ✅ Creating the page interface
- ✅ Collecting user input
- ✅ Displaying results
- ✅ Handling user clicks
- ❌ Complex calculations (use modules for that)
- ❌ Database operations (use modules for that)

### Put code in `ui_components/` when:
- ✅ Shared across multiple pages
- ✅ Common UI patterns
- ✅ Reusable components
- ❌ Page-specific logic
- ❌ Business logic

---

## Real Example from Your App

### Scenario: User wants to add a product

#### `pages/1_ProductDatabase.py` (UI Layer)
```python
def main():
    st.header("Product Database")
    
    # Collect input
    product_name = st.text_input("Product Name")
    price = st.number_input("Price")
    
    # When user clicks Save
    if st.button("Add Product"):
        # Call module function
        save_product({
            'name': product_name,
            'price': price
        })
```

#### `modules/product_manager.py` (Logic Layer)
```python
def save_product(product):
    """Save product to CSV"""
    df = pd.read_csv('data/product_data.csv')
    df = df.append(product, ignore_index=True)
    df.to_csv('data/product_data.csv', index=False)
```

#### `ui_components/sidebar.py` (Navigation)
```python
def setup_sidebar():
    """Navigation used on all pages"""
    st.sidebar.button("Product Database")
    st.sidebar.button("Recipe Builder")
```

---

## Summary Table

| Aspect | modules/ | pages/ | ui_components/ |
|--------|----------|--------|----------------|
| **Purpose** | Business logic | User interface | Reusable UI |
| **Has `st.` calls** | ❌ No | ✅ Yes | ✅ Yes |
| **Has functions** | ✅ Yes | ⚠️ Some | ⚠️ Some |
| **Reusable** | ✅ Yes | ❌ No | ✅ Yes |
| **Does calculations** | ✅ Yes | ❌ No | ❌ No |
| **Shows UI** | ❌ No | ✅ Yes | ✅ Yes |
| **File count** | 9 files | 8 files | 3 files |

---

## Analogy

Think of your app like a restaurant:

- **`modules/`** = Kitchen (cooks the food, business logic)
- **`pages/`** = Dining room (where customers sit, user interface)
- **`ui_components/`** = Furniture (tables, chairs used everywhere)

The pages (dining room) can't cook - they order from the kitchen (modules). The furniture (ui_components) is used in every dining room (page).

---

## Bottom Line

- **modules/** = **WHAT** the app does (logic)
- **pages/** = **HOW** users see it (interface)
- **ui_components/** = **SHARED** UI pieces (navigation, layout)

**The separation keeps your code:**
- ✅ Organized
- ✅ Maintainable
- ✅ Reusable
- ✅ Testable
