# 🧪 Testing Guide

## Overview

This document explains how to run and write tests for the Restaurant Inventory App.

---

## Quick Start

### Run All Tests
```bash
python -m pytest tests/
```

### Run Specific Test Folder
```bash
# Test only modules
python -m pytest tests/modules/

# Test only utils
python -m pytest tests/utils/
```

### Run Specific Test File
```bash
python -m pytest tests/modules/test_recipe_engine.py
```

### Run Specific Test Function
```bash
python -m pytest tests/modules/test_recipe_engine.py::test_calculate_recipe_cost_basic
```

### Verbose Output
```bash
python -m pytest tests/ -v
```

### Show Print Statements
```bash
python -m pytest tests/ -s
```

### Stop on First Failure
```bash
python -m pytest tests/ -x
```

---

## Test Structure

```
tests/
├── conftest.py              # Shared fixtures
├── test_sanity.py           # Basic sanity checks
│
├── modules/                 # Tests for modules/
│   ├── test_recipe_engine.py
│   ├── test_inventory_engine.py
│   └── ...
│
└── utils/                   # Tests for utils/
    ├── test_unit_normalizer.py
    └── ...
```

**Why this structure?**
- Mirrors the source code structure
- Easy to find corresponding tests
- Scalable and organized

---

## Writing Tests

### Basic Test Structure

```python
def test_function_name():
    """Brief description of what the test does"""
    # Arrange: Set up test data
    data = {"key": "value"}
    
    # Act: Run the function
    result = function_to_test(data)
    
    # Assert: Check the result
    assert result == expected_value
```

### Using Fixtures

Fixtures are predefined test data from `conftest.py`:

```python
def test_with_fixture(sample_product):
    """Test using a fixture"""
    assert sample_product["Product Name"] == "Test Chicken"
    assert sample_product["Price"] == 5.99
```

**Available fixtures (layered design):**

**Base Fixtures (Layer 0):**
- `sample_product` - Single product dictionary
- `sample_product_2` - Second sample product
- `sample_product_3` - Third sample product

**Composite Fixtures (Layer 1):**
- `sample_products_list` - List of products (built from individual products)
- `sample_products_df` - Pandas dataframe (built from product list)
- `sample_recipe` - Sample recipe dictionary

**File Fixtures (Layer 2):**
- `mock_products_file` - Mock CSV file (built from pytest's tmp_path + products_df)
- `mock_recipes_file` - Mock JSON file (built from tmp_path + recipe)
- `mock_inventory_file` - Mock inventory file (built from tmp_path + products)

**Integration Bundle (Layer 3):**
- `mock_dataset_bundle` - Dict of all file paths for E2E tests

**Why Layered Design?**
- **Single source of truth** - Product structure defined once in `sample_product`
- **Easy refactoring** - Change product fields in one place, all tests update
- **No duplication** - File fixtures build on data fixtures
- **Stable tests** - If data model changes, update fixtures, not individual tests

**Example - Layered Fixture Benefits:**

```python
# If your product structure changes (e.g., add new field "Supplier"),
# you only update the base fixture:

@pytest.fixture
def sample_product():
    """Single product dictionary"""
    return {
        "Product Name": "Test Chicken",
        "SKU": "TEST-001",
        "Category": "Protein",
        "Current Price per Unit": 5.99,
        "Unit": "lb",
        "Supplier": "ABC Foods"  # ← New field added here
    }

# All downstream fixtures automatically get the new field:
# - sample_products_df (automatically includes "Supplier")
# - mock_products_file (automatically includes "Supplier")
# - All tests automatically get the new field
```

This means **one change** updates **all tests** - no need to hunt through dozens of test files!

### Testing Edge Cases

Always test:
- ✅ **Happy path** - Normal usage
- ✅ **Empty inputs** - What happens with empty data?
- ✅ **Missing data** - What if data doesn't exist?
- ✅ **Wrong data types** - What if you pass wrong type?
- ✅ **Edge values** - Zero, negative, very large numbers

Example:
```python
def test_calculate_cost_empty():
    """Test cost calculation with no ingredients"""
    ingredients = []
    result = calculate_cost(ingredients)
    assert result == 0

def test_calculate_cost_missing_product():
    """Test cost calculation when product doesn't exist"""
    ingredients = [{"product_name": "NonExistent", "quantity": 1}]
    result = calculate_cost(ingredients)
    # Should handle gracefully, not crash
    assert result >= 0
```

---

## Test Organization

### Unit Tests (`tests/modules/`)
Test individual functions in isolation.

**Example:** `tests/modules/test_recipe_engine.py`
- Test `calculate_recipe_cost()` function
- Test `load_recipes()` function
- Test `save_recipe()` function

### Integration Tests (`tests/`)
Test how multiple components work together.

**Example:** Test import process end-to-end:
```python
def test_import_products():
    # Import products from CSV
    result = import_products('test_data.csv')
    
    # Verify products were added
    products = load_products()
    assert len(products) > 0
    
    # Verify can use in recipe
    recipe = create_recipe(['Imported Product'])
    assert recipe is not None
```

---

## Common Testing Patterns

### 1. Testing Functions with No Return Value

```python
def test_save_function():
    """Test that save function works without errors"""
    try:
        save_data({"test": "data"})
        result = True
    except Exception:
        result = False
    
    assert result == True
```

### 2. Testing with Mock Data

```python
def test_with_mock_file(mock_products_file):
    """Test using mock file"""
    df = pd.read_csv(mock_products_file)
    assert len(df) > 0
```

### 3. Testing Exceptions

```python
def test_raises_exception():
    """Test that function raises correct exception"""
    with pytest.raises(ValueError):
        function_that_raises_error()
```

### 4. Testing Data Types

```python
def test_returns_correct_type():
    """Test that function returns correct data type"""
    result = calculate_cost(ingredients)
    assert isinstance(result, float)
```

---

## Running Tests in CI/CD

### GitHub Actions Example

```yaml
name: Tests
on: [push, pull_request]
jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v2
      - name: Set up Python
        uses: actions/setup-python@v2
        with:
          python-version: 3.11
      - name: Install dependencies
        run: pip install -r requirements.txt
      - name: Run tests
        run: pytest tests/ -v
```

---

## Test Coverage

### Generate Coverage Report

```bash
# Install coverage tool
pip install pytest-cov

# Run tests with coverage
python -m pytest tests/ --cov=modules --cov=utils --cov-report=html

# View HTML report
# Open htmlcov/index.html in browser
```

### What Should Be Tested?

**Priority 1 - Must Test:**
- ✅ Cost calculations
- ✅ Data validation
- ✅ Import/export functions
- ✅ Critical user flows

**Priority 2 - Should Test:**
- ✅ Utility functions
- ✅ Data parsing
- ✅ Format conversions

**Priority 3 - Nice to Test:**
- ✅ UI components
- ✅ Display formatting
- ✅ Error messages

---

## Troubleshooting

### Import Errors

**Problem:** `ModuleNotFoundError`

**Solution:** Add to test file:
```python
import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))
```

### Fixture Not Found

**Problem:** `fixture 'sample_product' not found`

**Solution:** Make sure `conftest.py` is in `tests/` folder

### Tests Pass Individually but Fail Together

**Problem:** Shared state between tests

**Solution:** Use fixtures that create fresh data for each test

---

## Best Practices

### ✅ DO:
- Write tests that are independent
- Use descriptive test names
- Test one thing per test
- Use fixtures for shared data
- Clean up after tests

### ❌ DON'T:
- Write tests that depend on each other
- Use test data from production
- Leave temporary files
- Test implementation details
- Write tests that are too slow

---

## Examples from This Project

### Example 1: Recipe Cost Calculation
```python
def test_calculate_recipe_cost_basic(sample_products_df):
    """Test basic recipe cost calculation"""
    ingredients = [
        {"product_name": "Chicken", "quantity": 2, "unit": "lb"},
        {"product_name": "Rice", "quantity": 1, "unit": "lb"}
    ]
    
    total_cost, ingredient_costs = calculate_recipe_cost(
        ingredients, 
        sample_products_df
    )
    
    assert total_cost > 0
    assert len(ingredient_costs) == 2
    assert abs(total_cost - 14.48) < 0.01
```

### Example 2: Unit Normalization
```python
def test_parse_fractions_unicode():
    """Test parsing Unicode fractions"""
    assert parse_fractions("½ cup") == "0.5 cup"
    assert parse_fractions("¼ lb") == "0.25 lb"
```

### Example 3: Edge Cases
```python
def test_calculate_recipe_cost_empty_ingredients(sample_products_df):
    """Test cost calculation with no ingredients"""
    ingredients = []
    
    total_cost, ingredient_costs = calculate_recipe_cost(
        ingredients, 
        sample_products_df
    )
    
    assert total_cost == 0
    assert len(ingredient_costs) == 0
```

---

## Resources

- [pytest documentation](https://docs.pytest.org/)
- [Python testing best practices](https://realpython.com/python-testing/)
- Test structure mirrors source: See `REORGANIZATION_PLAN.md`

---

## Summary

**The Three Steps:**
1. **Arrange** - Set up test data
2. **Act** - Run the function
3. **Assert** - Check the result

**Remember:**
- Test structure should mirror code structure
- Write tests for critical functions first
- Use fixtures to avoid repetition
- Test edge cases, not just happy paths
