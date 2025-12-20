# tests/modules/test_recipe_engine.py
"""Tests for recipe_engine.py"""
import pytest
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.recipe_engine import (
    load_recipes,
    save_recipe,
    calculate_recipe_cost
)


def test_calculate_recipe_cost_basic(sample_products_df):
    """Test basic recipe cost calculation"""
    # Arrange
    ingredients = [
        {"product_name": "Chicken", "quantity": 2, "unit": "lb"},
        {"product_name": "Rice", "quantity": 1, "unit": "lb"}
    ]
    
    # Act
    total_cost, ingredient_costs = calculate_recipe_cost(ingredients, sample_products_df)
    
    # Assert
    assert total_cost > 0
    assert len(ingredient_costs) == 2
    # Chicken: 2 * 5.99 = 11.98
    # Rice: 1 * 2.50 = 2.50
    # Total: ~14.48
    assert abs(total_cost - 14.48) < 0.01


def test_calculate_recipe_cost_empty_ingredients(sample_products_df):
    """Test cost calculation with no ingredients"""
    ingredients = []
    
    total_cost, ingredient_costs = calculate_recipe_cost(ingredients, sample_products_df)
    
    assert total_cost == 0
    assert len(ingredient_costs) == 0


def test_calculate_recipe_cost_missing_product(sample_products_df):
    """Test cost calculation when product doesn't exist"""
    ingredients = [
        {"product_name": "NonExistent Product", "quantity": 1, "unit": "lb"}
    ]
    
    total_cost, ingredient_costs = calculate_recipe_cost(ingredients, sample_products_df)
    
    # Should handle missing products gracefully
    assert total_cost >= 0


def test_recipe_cost_structure(sample_products_df):
    """Test that recipe cost returns correct structure"""
    ingredients = [
        {"product_name": "Chicken", "quantity": 1, "unit": "lb"}
    ]
    
    total_cost, ingredient_costs = calculate_recipe_cost(ingredients, sample_products_df)
    
    assert isinstance(total_cost, (int, float))
    assert isinstance(ingredient_costs, list)
    assert len(ingredient_costs) > 0
