"""
Test script for Product Import feature
Run this to verify the implementation is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

import pandas as pd

# Set encoding for Windows console
if sys.platform == 'win32':
    import io
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')


def test_format_detection():
    """Test CSV format detection"""
    print("\n=== Testing Format Detection ===")
    try:
        from modules.product_importer import detect_csv_format

        # Test SYSCO format
        sysco_df = pd.DataFrame({
            0: ['H', 'F', 'P', 'P'],
            1: ['test', 'SUPC', '12345', '67890']
        })
        format_type = detect_csv_format(sysco_df)
        assert format_type == 'sysco', f"Expected 'sysco', got '{format_type}'"
        print("✅ SYSCO format detected correctly")

        # Test standard format
        standard_df = pd.DataFrame({
            'Product': ['Item1', 'Item2'],
            'Price': [10.0, 20.0]
        })
        format_type = detect_csv_format(standard_df)
        assert format_type == 'standard', f"Expected 'standard', got '{format_type}'"
        print("✅ Standard format detected correctly")

        return True
    except Exception as e:
        print(f"❌ Format detection test failed: {e}")
        return False


def test_column_mapping():
    """Test smart column mapping suggestions"""
    print("\n=== Testing Column Mapping ===")
    try:
        from modules.product_importer import suggest_column_mappings

        # Test with SYSCO-like columns
        sysco_columns = ['SUPC', 'Desc', 'Cat', 'Brand', 'Pack', 'Size', 'Unit', 'Case $']
        mappings = suggest_column_mappings(sysco_columns, threshold=60)

        assert 'Product Name' in mappings, "Product Name should be mapped"
        assert 'SKU' in mappings, "SKU should be mapped"
        assert 'Category' in mappings, "Category should be mapped"

        print(f"✅ Successfully suggested {len(mappings)} column mappings")
        print(f"   Mappings: {dict(list(mappings.items())[:3])}")

        return True
    except Exception as e:
        print(f"❌ Column mapping test failed: {e}")
        return False


def test_mapping_validation():
    """Test mapping validation"""
    print("\n=== Testing Mapping Validation ===")
    try:
        from modules.product_importer import validate_mappings

        # Test valid mappings
        valid_mappings = {
            'Product Name': 'Desc',
            'SKU': 'SUPC',
            'Category': 'Cat',
            'Unit': 'Unit',
            'Current Price per Unit': 'Price'
        }
        is_valid, errors = validate_mappings(valid_mappings)
        assert is_valid, "Valid mappings should pass validation"
        print("✅ Valid mappings passed")

        # Test invalid mappings (missing required field)
        invalid_mappings = {
            'Product Name': 'Desc',
            'SKU': 'SUPC'
            # Missing other required fields
        }
        is_valid, errors = validate_mappings(invalid_mappings)
        assert not is_valid, "Invalid mappings should fail validation"
        assert len(errors) > 0, "Errors should be reported"
        print(f"✅ Invalid mappings correctly failed ({len(errors)} errors)")

        return True
    except Exception as e:
        print(f"❌ Mapping validation test failed: {e}")
        return False


def test_template_management():
    """Test template save/load"""
    print("\n=== Testing Template Management ===")
    try:
        from modules.product_importer import save_mapping_template, load_mapping_template, list_templates

        # Save a test template
        test_template = {
            "name": "Test Supplier",
            "format_type": "sysco",
            "column_mappings": {
                "Product Name": "Desc",
                "SKU": "SUPC"
            },
            "price_field": "Case $",
            "defaults": {
                "Location": "Storage"
            }
        }

        success, message = save_mapping_template("TEST_TEMPLATE", test_template)
        assert success, f"Template save failed: {message}"
        print("✅ Template saved successfully")

        # Load the template
        loaded = load_mapping_template("TEST_TEMPLATE")
        assert loaded is not None, "Template should be loaded"
        assert loaded['name'] == "Test Supplier", "Template data should match"
        print("✅ Template loaded successfully")

        # List templates
        templates = list_templates()
        assert "TEST_TEMPLATE" in templates, "Template should be in list"
        print(f"✅ Template appears in list ({len(templates)} total)")

        return True
    except Exception as e:
        print(f"❌ Template management test failed: {e}")
        return False


def test_duplicate_detection():
    """Test duplicate product detection"""
    print("\n=== Testing Duplicate Detection ===")
    try:
        from modules.product_importer import detect_duplicates

        # Create test dataframes
        new_products = pd.DataFrame({
            'Product Name': ['New Product', 'Existing Product'],
            'SKU': ['NEW123', 'EXIST456'],
            'Category': ['Test', 'Test']
        })

        existing_products = pd.DataFrame({
            'Product Name': ['Existing Product'],
            'SKU': ['EXIST456'],
            'Category': ['Test']
        })

        result = detect_duplicates(new_products, existing_products)

        assert 'is_duplicate' in result.columns, "is_duplicate column should exist"
        assert result.iloc[1]['is_duplicate'] == True, "Second product should be marked as duplicate"
        assert result.iloc[0]['is_duplicate'] == False, "First product should not be duplicate"
        print("✅ Duplicate detection working correctly")

        return True
    except Exception as e:
        print(f"❌ Duplicate detection test failed: {e}")
        return False


def test_bulk_import_functions():
    """Test bulk import functions in product_manager"""
    print("\n=== Testing Bulk Import Functions ===")
    try:
        from modules.product_manager import find_product_by_sku, bulk_import_products

        # Note: This test requires actual product data
        # For now, just verify functions exist and are callable
        assert callable(find_product_by_sku), "find_product_by_sku should be callable"
        assert callable(bulk_import_products), "bulk_import_products should be callable"

        print("✅ Bulk import functions exist")
        print("   ⚠️  Note: Full integration tests require database access")

        return True
    except Exception as e:
        print(f"❌ Bulk import functions test failed: {e}")
        return False


def test_pack_size_combination():
    """Test combining pack, size, unit columns"""
    print("\n=== Testing Pack Size Combination ===")
    try:
        from modules.product_importer import combine_pack_size

        # Create test row
        test_row = pd.Series({
            'Pack': '4',
            'Size': '5LB',
            'Unit': 'LB'
        })

        result = combine_pack_size(test_row, 'Pack', 'Size', 'Unit')
        assert result == '4 5LB LB', f"Expected '4 5LB LB', got '{result}'"
        print(f"✅ Pack size combination: '{result}'")

        return True
    except Exception as e:
        print(f"❌ Pack size combination test failed: {e}")
        return False


def test_files_exist():
    """Test that all required files exist"""
    print("\n=== Testing File Existence ===")
    try:
        required_files = [
            'modules/product_importer.py',
            'data/import_templates.json',
            'pages/1_ProductDatabase.py'
        ]

        for file_path in required_files:
            assert os.path.exists(file_path), f"Required file missing: {file_path}"
            print(f"✅ {file_path}")

        return True
    except Exception as e:
        print(f"❌ File existence test failed: {e}")
        return False


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("Product Import Feature Test Suite")
    print("=" * 60)

    tests = [
        test_files_exist,
        test_format_detection,
        test_column_mapping,
        test_mapping_validation,
        test_template_management,
        test_duplicate_detection,
        test_pack_size_combination,
        test_bulk_import_functions
    ]

    passed = 0
    failed = 0

    for test in tests:
        try:
            if test():
                passed += 1
            else:
                failed += 1
        except Exception as e:
            print(f"❌ Test '{test.__name__}' crashed: {e}")
            failed += 1

    print("\n" + "=" * 60)
    print(f"Test Results: {passed} passed, {failed} failed")
    print("=" * 60)

    return failed == 0


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

