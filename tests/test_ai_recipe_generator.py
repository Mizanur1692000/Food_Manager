"""
Tests for AI Recipe Generator integration
"""
import pytest
import pandas as pd
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Import the module directly
import importlib.util
spec = importlib.util.spec_from_file_location("ai_gen", "pages/6_AI_Recipe_Generator.py")
ai_gen = importlib.util.module_from_spec(spec)
spec.loader.exec_module(ai_gen)


class TestUnitConversions:
    """Test oz to various unit conversions"""

    def test_oz_to_lb(self):
        """16 oz should equal 1 lb"""
        result, unit = ai_gen.oz_to_unit(16.0, "lb")
        assert result == 1.0
        assert unit == "lb"

    def test_oz_to_gallon(self):
        """128 oz should equal 1 gallon"""
        result, unit = ai_gen.oz_to_unit(128.0, "gallon")
        assert result == 1.0
        assert unit == "gallon"

    def test_oz_to_quart(self):
        """32 oz should equal 1 quart"""
        result, unit = ai_gen.oz_to_unit(32.0, "quart")
        assert result == 1.0
        assert unit == "quart"

    def test_oz_to_dozen(self):
        """24 oz should equal 1 dozen (assuming 2 oz per egg)"""
        result, unit = ai_gen.oz_to_unit(24.0, "dozen")
        assert result == 1.0
        assert unit == "dozen"

    def test_partial_lb(self):
        """8 oz should equal 0.5 lb"""
        result, unit = ai_gen.oz_to_unit(8.0, "lb")
        assert result == 0.5
        assert unit == "lb"


class TestIngredientMapping:
    """Test fuzzy ingredient matching"""

    @pytest.fixture
    def sample_products_df(self):
        """Create sample product dataframe"""
        return pd.DataFrame({
            "Product Name": ["Chicken Breast", "Olive Oil Extra Virgin", "Salt Kosher", "Black Pepper Ground"],
            "Unit": ["lb", "gallon", "lb", "lb"],
            "Cost per Oz": [0.278125, 0.13671875, 0.115625, 0.765625],
            "Current Price per Unit": [4.45, 17.50, 1.85, 12.25],
            "Category": ["Chicken", "Dry Goods", "Dry Goods", "Dry Goods"],
            "Pack Size": ["40 lb case", "1 gallon jug", "3 lb box", "1 lb container"]
        })

    def test_exact_match(self, sample_products_df):
        """Test exact ingredient name match"""
        product, score = ai_gen.map_ingredient_to_product("Chicken Breast", sample_products_df)
        assert product is not None
        assert product["Product Name"] == "Chicken Breast"
        assert score == 100

    def test_fuzzy_match(self, sample_products_df):
        """Test fuzzy matching with similar name"""
        product, score = ai_gen.map_ingredient_to_product("chicken breast", sample_products_df)
        assert product is not None
        assert product["Product Name"] == "Chicken Breast"
        assert score >= 75

    def test_partial_match(self, sample_products_df):
        """Test partial name matching"""
        product, score = ai_gen.map_ingredient_to_product("olive oil", sample_products_df)
        assert product is not None
        assert "Olive Oil" in product["Product Name"]
        assert score >= 75

    def test_no_match(self, sample_products_df):
        """Test when no match is found"""
        product, score = ai_gen.map_ingredient_to_product("unicorn meat", sample_products_df, score_cutoff=75)
        assert product is None
        assert score == 0

    def test_empty_input(self, sample_products_df):
        """Test with empty ingredient name"""
        product, score = ai_gen.map_ingredient_to_product("", sample_products_df)
        assert product is None
        assert score == 0


class TestRecipeConversion:
    """Test AI recipe format conversion to app format"""

    @pytest.fixture
    def sample_products_df(self):
        """Create sample product dataframe"""
        return pd.DataFrame({
            "Product Name": ["Chicken Breast", "Olive Oil Extra Virgin", "Salt Kosher"],
            "Unit": ["lb", "gallon", "lb"],
            "Cost per Oz": [0.278125, 0.13671875, 0.115625],
            "Current Price per Unit": [4.45, 17.50, 1.85],
            "Category": ["Chicken", "Dry Goods", "Dry Goods"],
            "Pack Size": ["40 lb case", "1 gallon jug", "3 lb box"]
        })

    @pytest.fixture
    def sample_ai_recipe(self):
        """Sample recipe from Claude in AI format"""
        return {
            "recipe_name": "Grilled Chicken",
            "description": "Simple grilled chicken",
            "servings": 4,
            "category": "Main Course",
            "prep_time": 10,
            "cook_time": 20,
            "ingredients": [
                {"ingredient_name": "chicken breast", "oz": 48.0},  # 3 lbs
                {"ingredient_name": "olive oil", "oz": 2.0},
                {"ingredient_name": "salt", "oz": 0.5}
            ],
            "instructions": "1. Season chicken\n2. Grill until done"
        }

    def test_recipe_conversion(self, sample_ai_recipe, sample_products_df):
        """Test full recipe conversion"""
        recipe, mapping_notes = ai_gen.convert_ai_recipe_to_app_format(
            sample_ai_recipe,
            sample_products_df,
            match_threshold=75
        )

        # Check basic recipe structure
        assert recipe["name"] == "Grilled Chicken"
        assert recipe["servings"] == 4
        assert recipe["category"] == "Main Course"
        assert len(recipe["ingredients"]) == 3

        # Check ingredient conversion
        chicken_ing = recipe["ingredients"][0]
        assert chicken_ing["product_name"] == "Chicken Breast"
        assert chicken_ing["unit"] == "lb"
        assert chicken_ing["quantity"] == 3.0  # 48 oz = 3 lbs

        # Check mapping notes
        assert len(mapping_notes) == 3
        assert all(note["score"] > 0 for note in mapping_notes)

    def test_unmapped_ingredient(self, sample_products_df):
        """Test handling of unmapped ingredients"""
        ai_recipe = {
            "recipe_name": "Test",
            "ingredients": [
                {"ingredient_name": "unicorn powder", "oz": 1.0}
            ],
            "instructions": "Mix",
            "servings": 1
        }

        recipe, mapping_notes = ai_gen.convert_ai_recipe_to_app_format(
            ai_recipe,
            sample_products_df,
            match_threshold=75
        )

        # Should have no ingredients (unmapped)
        assert len(recipe["ingredients"]) == 0

        # But should have mapping note
        assert len(mapping_notes) == 1
        assert mapping_notes[0]["score"] == 0
        assert "NO MATCH" in mapping_notes[0]["matched_product"]


if __name__ == "__main__":
    pytest.main([__file__, "-v"])

