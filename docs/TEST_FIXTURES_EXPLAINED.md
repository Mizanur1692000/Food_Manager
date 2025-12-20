# 🎯 Test Fixtures - Layered Design

## Overview

The test fixtures are designed using a **layered approach** where fixtures build on top of each other. This makes them maintainable, refactor-friendly, and DRY (Don't Repeat Yourself).

---

## The Layers

### Layer 0: Base Fixtures
**Single units of data (pure Python, no I/O)**

```python
@pytest.fixture
def sample_product() -> Dict[str, Any]:
    """Base product structure"""
    return {
        "Product Name": "Test Chicken",
        "SKU": "TEST-001",
        "Category": "Protein",
        "Current Price per Unit": 5.99,
        "Unit": "lb"
    }
```

**Purpose:** Define the structure of data **once**. This is your single source of truth.

---

### Layer 1: Composite Fixtures
**Built from base fixtures**

```python
@pytest.fixture
def sample_products_df(sample_product, sample_product_2, sample_product_3):
    """DataFrame built from individual products"""
    return pd.DataFrame([
        sample_product,
        sample_product_2,
        sample_product_3
    ])
```

**Purpose:** Combine base fixtures into more complex structures.

---

### Layer 2: File Fixtures
**Built from composite fixtures + pytest's built-in tmp_path**

```python
@pytest.fixture
def mock_products_file(tmp_path: Path, sample_products_df: pd.DataFrame) -> Path:
    """CSV file built from DataFrame"""
    products_file = tmp_path / "product_data.csv"
    sample_products_df.to_csv(products_file, index=False)
    return products_file
```

**Purpose:** Create actual files for testing file I/O operations.

**Benefits of using `tmp_path`:**
- ✅ Built into pytest (no custom cleanup needed)
- ✅ Automatic cleanup after tests
- ✅ Less code
- ✅ Standard pytest idiom

---

## The Dependency Chain

```
sample_product (Layer 0) → sample_products_list (Layer 1) → sample_products_df (Layer 1) → mock_products_file (Layer 2)
     ↓                                                                                              ↑
pytest's tmp_path (built-in) ──────────────────────────────────────────────────────────────────────┘
```

**Flow:**
1. Base fixtures define structure
2. Composite fixtures combine them
3. File fixtures use pytest's `tmp_path` and create actual files
4. Integration bundle provides all files together

---

## Benefits

### ✅ Single Source of Truth

**Before (Bad):**
```python
# Test 1
products = [{
    "Product Name": "Chicken",
    "Price": 5.99
}]

# Test 2  
products = [{
    "Product Name": "Chicken",
    "Price": 5.99
}]

# Test 3
# ... duplicated again
```

**After (Good):**
```python
# Define once
@pytest.fixture
def sample_product():
    return {"Product Name": "Chicken", "Price": 5.99}

# Use everywhere
def test_1(sample_product):
    # Uses sample_product

def test_2(sample_product):
    # Uses sample_product
```

---

### ✅ Easy Refactoring

**Scenario:** Add a new field "Supplier" to products

**Without layered design:**
- ❌ Update 20+ test files
- ❌ Search and replace everywhere
- ❌ Easy to miss tests
- ❌ Risk of inconsistency

**With layered design:**
- ✅ Update 1 fixture (sample_product)
- ✅ All tests automatically get the new field
- ✅ Impossible to miss tests
- ✅ Guaranteed consistency

```python
@pytest.fixture
def sample_product():
    return {
        "Product Name": "Chicken",
        "Price": 5.99,
        "Supplier": "ABC Foods"  # ← Add here, all tests get it
    }
```

---

### ✅ No Duplication

**File fixtures build on data fixtures:**

```python
# Layer 1: DataFrame (no duplication)
@pytest.fixture
def sample_products_df(sample_product, sample_product_2, sample_product_3):
    return pd.DataFrame([sample_product, sample_product_2, sample_product_3])

# Layer 2: File (no duplication)
@pytest.fixture  
def mock_products_file(temp_data_dir, sample_products_df):
    products_file = temp_data_dir / "products.csv"
    sample_products_df.to_csv(products_file, index=False)  # ← Reuses DataFrame
    return products_file
```

If the DataFrame structure changes, the file automatically reflects it.

---

### ✅ Stable Tests

**Problem:** Data model changes frequently

**Solution:** Update fixtures, not tests

```python
# Data model changes
# Old: {"Name": "Chicken"}
# New: {"Product Name": "Chicken", "Display Name": "Fresh Chicken"}

# Update base fixture
@pytest.fixture
def sample_product():
    return {
        "Product Name": "Chicken",
        "Display Name": "Fresh Chicken"  # ← New field
    }

# All tests continue to work
# No changes needed in individual tests
```

---

## Real-World Example

### Adding a new product field

**Step 1:** Update base fixture
```python
@pytest.fixture
def sample_product():
    return {
        "Product Name": "Test Chicken",
        "SKU": "TEST-001",
        "Category": "Protein",
        "Current Price per Unit": 5.99,
        "Unit": "lb",
        "Supplier": "ABC Foods",  # ← New field
        "Location": "Freezer A"    # ← New field
    }
```

**Step 2:** Done! ✨

**What automatically updates:**
- ✅ `sample_products_df` - DataFrame now has Supplier and Location columns
- ✅ `sample_products_list` - List items now have Supplier and Location
- ✅ `mock_products_file` - CSV file now has Supplier and Location columns
- ✅ All tests that use these fixtures now have the new fields

**Time saved:** 30+ minutes of search-and-replace across dozens of test files

---

## Fixture Hierarchy

```
BASE FIXTURES (Layer 0)
├── sample_product       # Product dict (typed)
├── sample_product_2     # Product dict (typed)
└── sample_product_3     # Product dict (typed)
    │
    ↓
COMPOSITE FIXTURES (Layer 1)
├── sample_products_list  # List of products (built from Layer 0)
├── sample_products_df    # DataFrame (built from list)
└── sample_recipe         # Recipe dict (typed)
    │
    ↓
FILE FIXTURES (Layer 2) [uses pytest's tmp_path]
├── mock_products_file    # CSV file (tmp_path + sample_products_df)
├── mock_recipes_file     # JSON file (tmp_path + sample_recipe)
└── mock_inventory_file   # JSON file (tmp_path + products)
    │
    ↓
INTEGRATION BUNDLE (Layer 3)
└── mock_dataset_bundle   # Dict with all file paths
```

---

## Best Practices

### ✅ DO:

1. **Define structure in base fixtures**
   ```python
   @pytest.fixture
   def sample_product():
       return {"name": "Chicken", "price": 5.99}
   ```

2. **Build composite fixtures from base**
   ```python
   @pytest.fixture
   def sample_products_df(sample_product, sample_product_2):
       return pd.DataFrame([sample_product, sample_product_2])
   ```

3. **Build file fixtures from composite**
   ```python
   @pytest.fixture
   def mock_file(temp_data_dir, sample_products_df):
       path = temp_data_dir / "products.csv"
       sample_products_df.to_csv(path)
       return path
   ```

### ❌ DON'T:

1. **Don't duplicate data**
   ```python
   # Bad - duplicates "Chicken" structure
   @pytest.fixture
   def mock_file(temp_data_dir):
       df = pd.DataFrame({"Product Name": ["Chicken"], "Price": [5.99]})
       df.to_csv(temp_data_dir / "products.csv")
       return temp_data_dir / "products.csv"
   ```

2. **Don't hardcode values in fixtures**
   ```python
   # Bad
   @pytest.fixture
   def sample_product():
       return {"name": "Hardcoded Chicken"}  # Not flexible
   
   # Good
   @pytest.fixture
   def sample_product():
       return {"Product Name": "Test Chicken"}  # Descriptive, reusable
   ```

3. **Don't skip layers**
   ```python
   # Bad - file fixture bypasses composite fixtures
   @pytest.fixture
   def mock_file(temp_data_dir):
       df = pd.DataFrame({"Name": "Chicken"})  # Duplicates structure
       df.to_csv(temp_data_dir / "file.csv")
   
   # Good - uses composite fixture
   @pytest.fixture
   def mock_file(temp_data_dir, sample_products_df):
       sample_products_df.to_csv(temp_data_dir / "file.csv")
   ```

---

## Key Improvements in This Implementation

### ✅ Type Hints
All fixtures are fully typed:
```python
def sample_product() -> Dict[str, Any]:
def sample_products_df(sample_products_list) -> pd.DataFrame:
def mock_products_file(tmp_path: Path, sample_products_df: pd.DataFrame) -> Path:
```

**Benefits:**
- Better IDE support and autocomplete
- Catches type errors early
- Self-documenting code
- Easier refactoring

### ✅ Pytest's Built-in `tmp_path`
Instead of manual temp directory management:
```python
# OLD (removed)
def temp_data_dir():
    temp_dir = tempfile.mkdtemp()
    yield Path(temp_dir)
    shutil.rmtree(temp_dir)

# NEW (uses pytest)
def mock_file(tmp_path: Path, data):
    file = tmp_path / "file.csv"
    data.to_csv(file)
    return file
```

**Benefits:**
- Automatic cleanup
- Less boilerplate
- Standard pytest pattern
- One less fixture to maintain

### ✅ Integration Bundle
New Layer 3 fixture for E2E tests:
```python
@pytest.fixture
def mock_dataset_bundle(mock_products_file, mock_recipes_file, mock_inventory_file):
    return {
        "products_csv": mock_products_file,
        "recipes_json": mock_recipes_file,
        "inventory_json": mock_inventory_file,
    }
```

**Usage:**
```python
def test_end_to_end_workflow(mock_dataset_bundle):
    # All files available in one fixture
    products = pd.read_csv(mock_dataset_bundle["products_csv"])
    recipes = json.loads(mock_dataset_bundle["recipes_json"].read_text())
    # ... test integration
```

### ✅ Better Composition
`sample_products_df` builds from `sample_products_list`:
```python
def sample_products_df(sample_products_list) -> pd.DataFrame:
    return pd.DataFrame(sample_products_list)
```

This creates a cleaner dependency chain with less repetition.

---

## Summary

**Layered fixtures = Maintainable tests**

- **Change once, update everywhere** - Update base fixtures, all tests get updates
- **Single source of truth** - Product structure defined once
- **No duplication** - File fixtures reuse data fixtures
- **Easy refactoring** - Data model changes are trivial
- **Stable tests** - Tests don't break when data model evolves
- **Fully typed** - Type hints throughout for better IDE support
- **Cleaner code** - Uses pytest's built-in `tmp_path`
- **Integration ready** - Bundle fixture for E2E tests

**Remember:** If you find yourself copying data structures across test files, create a fixture instead!

