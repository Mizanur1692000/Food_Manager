"""
Test script for Allergen Management feature
Run this to verify the implementation is working correctly
"""

import sys
import os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

def test_allergen_database():
    """Test allergen database loading"""
    print("\n=== Testing Allergen Database ===")
    try:
        from modules.allergen_engine import load_allergen_database
        db = load_allergen_database()

        assert 'ingredient_patterns' in db, "Missing ingredient_patterns"
        assert 'allergen_metadata' in db, "Missing allergen_metadata"

        patterns_count = sum(len(p) for p in db['ingredient_patterns'].values())
        metadata_count = len(db['allergen_metadata'])

        print(f"✅ Allergen database loaded successfully")
        print(f"   - {patterns_count} ingredient patterns")
        print(f"   - {metadata_count} allergen types")
        return True
    except Exception as e:
        print(f"❌ Allergen database test failed: {e}")
        return False


def test_database_detection():
    """Test database allergen detection"""
    print("\n=== Testing Database Detection ===")
    try:
        from modules.allergen_engine import detect_allergens_database

        # Test ingredients with known allergens
        test_ingredients = [
            {'product_name': 'Butter'},
            {'product_name': 'Eggs Large'},
            {'product_name': 'Flour All Purpose'}
        ]

        result = detect_allergens_database(test_ingredients, min_confidence=70)

        assert 'detected_allergens' in result, "Missing detected_allergens"
        assert 'allergen_details' in result, "Missing allergen_details"

        detected = result['detected_allergens']
        print(f"✅ Database detection working")
        print(f"   - Detected allergens: {', '.join(detected) if detected else 'None'}")
        return True
    except Exception as e:
        print(f"❌ Database detection test failed: {e}")
        return False


def test_recipe_id_migration():
    """Test recipe ID migration utility"""
    print("\n=== Testing Recipe ID Migration ===")
    try:
        from modules.recipe_engine import ensure_recipe_ids, load_recipes

        recipes = load_recipes()
        recipes_without_id = sum(1 for r in recipes.values() if 'recipe_id' not in r)

        if recipes_without_id > 0:
            print(f"   - Found {recipes_without_id} recipes without IDs")
            updated = ensure_recipe_ids()
            print(f"✅ Migration completed: {updated} recipes updated")
        else:
            print(f"✅ All {len(recipes)} recipes already have IDs")

        return True
    except Exception as e:
        print(f"❌ Recipe ID migration test failed: {e}")
        return False


def test_qr_code_generation():
    """Test QR code generation"""
    print("\n=== Testing QR Code Generation ===")
    try:
        from modules.allergen_engine import generate_qr_code
        from uuid import uuid4

        test_recipe_id = str(uuid4())
        test_recipe_name = "Test Recipe"

        file_path, img_bytes = generate_qr_code(
            test_recipe_id,
            test_recipe_name,
            "http://localhost:8501"
        )

        assert os.path.exists(file_path), f"QR code file not created: {file_path}"
        assert len(img_bytes) > 0, "QR code image bytes empty"

        print(f"✅ QR code generation working")
        print(f"   - File saved: {file_path}")
        print(f"   - Image size: {len(img_bytes)} bytes")

        # Cleanup test file
        if os.path.exists(file_path):
            os.remove(file_path)
            print(f"   - Test file cleaned up")

        return True
    except Exception as e:
        print(f"❌ QR code generation test failed: {e}")
        return False


def test_allergen_report_generation():
    """Test allergen report generation"""
    print("\n=== Testing Allergen Report Generation ===")
    try:
        from modules.allergen_engine import generate_allergen_report, combine_allergen_detections

        # Mock allergen data
        mock_allergen_data = {
            'allergens': ['milk', 'eggs'],
            'allergen_details': {
                'milk': {
                    'display_name': 'Milk/Dairy',
                    'confidence': 95,
                    'metadata': {'fda_top_9': True, 'icon': '🥛', 'description': 'Contains milk'},
                    'sources': ['database'],
                    'matched_ingredients': [{'ingredient': 'Butter'}]
                }
            },
            'detection_methods': ['database'],
            'total_detected': 1,
            'fda_top_9_count': 1
        }

        mock_ingredients = [{'product_name': 'Butter', 'quantity': 1, 'unit': 'lb'}]

        report = generate_allergen_report(
            "Test Recipe",
            mock_allergen_data,
            mock_ingredients
        )

        assert 'recipe_name' in report, "Missing recipe_name"
        assert 'fda_allergens' in report, "Missing fda_allergens"
        assert 'disclaimer' in report, "Missing disclaimer"

        print(f"✅ Allergen report generation working")
        print(f"   - Recipe: {report['recipe_name']}")
        print(f"   - Total allergens: {report['total_allergens']}")
        print(f"   - FDA Top 9: {report['fda_top_9_present']}")
        return True
    except Exception as e:
        print(f"❌ Allergen report generation test failed: {e}")
        return False


def test_recipe_schema():
    """Test recipe schema with allergen fields"""
    print("\n=== Testing Recipe Schema ===")
    try:
        from models.recipe_schema import RecipeSchema, AllergenMetadataSchema, IngredientSchema
        from pydantic import ValidationError

        # Test creating recipe with allergen data
        test_recipe = {
            'name': 'Test Recipe',
            'ingredients': [
                {
                    'raw_name': 'Test Ingredient',
                    'quantity': 1.0,
                    'uom': 'oz'
                }
            ],
            'allergens': ['milk', 'eggs'],
            'allergen_metadata': {
                'detection_methods': ['database'],
                'total_detected': 2,
                'fda_top_9_count': 2
            }
        }

        recipe = RecipeSchema(**test_recipe)

        assert recipe.allergens == ['milk', 'eggs'], "Allergens not preserved"
        assert recipe.recipe_id is not None, "Recipe ID not generated"

        print(f"✅ Recipe schema validation working")
        print(f"   - Recipe ID: {recipe.recipe_id[:8]}...")
        print(f"   - Allergens: {', '.join(recipe.allergens)}")
        return True
    except Exception as e:
        print(f"❌ Recipe schema test failed: {e}")
        return False


def test_files_exist():
    """Test that all required files exist"""
    print("\n=== Testing File Existence ===")

    required_files = [
        'modules/allergen_engine.py',
        'pages/7_AllergenManagement.py',
        'pages/public_allergen_report.py',
        'data/allergen_database.json',
        'utils/migrate_recipe_ids.py',
        'ALLERGEN_MANAGEMENT_GUIDE.md',
        'ALLERGEN_FEATURE_IMPLEMENTATION.md'
    ]

    all_exist = True
    for file_path in required_files:
        if os.path.exists(file_path):
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} - MISSING")
            all_exist = False

    return all_exist


def run_all_tests():
    """Run all tests"""
    print("=" * 60)
    print("ALLERGEN MANAGEMENT FEATURE - TEST SUITE")
    print("=" * 60)

    tests = [
        ('File Existence', test_files_exist),
        ('Allergen Database', test_allergen_database),
        ('Database Detection', test_database_detection),
        ('Recipe ID Migration', test_recipe_id_migration),
        ('Recipe Schema', test_recipe_schema),
        ('Allergen Report Generation', test_allergen_report_generation),
        ('QR Code Generation', test_qr_code_generation),
    ]

    results = []
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ {test_name} crashed: {e}")
            results.append((test_name, False))

    # Summary
    print("\n" + "=" * 60)
    print("TEST SUMMARY")
    print("=" * 60)

    passed = sum(1 for _, result in results if result)
    total = len(results)

    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")

    print(f"\nTotal: {passed}/{total} tests passed")

    if passed == total:
        print("\n🎉 All tests passed! Feature is ready to use.")
    else:
        print(f"\n⚠️ {total - passed} test(s) failed. Please review errors above.")

    return passed == total


if __name__ == "__main__":
    success = run_all_tests()
    sys.exit(0 if success else 1)

