# tests/conftest.py
"""Shared test fixtures for all tests — layered design with tmp_path."""

from __future__ import annotations

import json
from pathlib import Path
from typing import Dict, Any

import pandas as pd
import pytest


# ============================================================================
# BASE FIXTURES — Core test data structures (pure, no I/O)
# ============================================================================

@pytest.fixture
def sample_product() -> Dict[str, Any]:
    """Single product dictionary — base data structure."""
    return {
        "Product Name": "Test Chicken",
        "SKU": "TEST-001",
        "Category": "Protein",
        "Current Price per Unit": 5.99,
        "Unit": "lb",
    }


@pytest.fixture
def sample_product_2() -> Dict[str, Any]:
    """Second sample product."""
    return {
        "Product Name": "Test Rice",
        "SKU": "TEST-002",
        "Category": "Grain",
        "Current Price per Unit": 2.50,
        "Unit": "lb",
    }


@pytest.fixture
def sample_product_3() -> Dict[str, Any]:
    """Third sample product."""
    return {
        "Product Name": "Test Salt",
        "SKU": "TEST-003",
        "Category": "Seasoning",
        "Current Price per Unit": 1.00,
        "Unit": "lb",
    }


@pytest.fixture
def sample_products_list(
    sample_product, sample_product_2, sample_product_3
) -> list[dict]:
    """List of products — built from individual product fixtures."""
    return [sample_product, sample_product_2, sample_product_3]


@pytest.fixture
def sample_products_df(sample_products_list) -> pd.DataFrame:
    """Products as DataFrame — built from product list."""
    return pd.DataFrame(sample_products_list)


@pytest.fixture
def sample_recipe() -> Dict[str, Any]:
    """Sample recipe (references by product name). 
    TIP: Consider switching to SKU for joins to avoid name collisions.
    """
    return {
        "name": "Test Recipe",
        "description": "A test recipe",
        "servings": 4,
        "prep_time": 30,
        "cook_time": 20,
        "category": "Main Course",
        "ingredients": [
            {"product_name": "Test Chicken", "quantity": 2, "unit": "lb"},
            {"product_name": "Test Rice", "quantity": 1, "unit": "lb"},
        ],
        "instructions": "Cook the chicken and rice together",
    }


# ============================================================================
# LAYER 2 — File fixtures (prefer built-in tmp_path for temp dirs)
# ============================================================================

@pytest.fixture
def mock_products_file(tmp_path: Path, sample_products_df: pd.DataFrame) -> Path:
    """Mock products CSV file — built from tmp_path + sample_products_df."""
    products_file = tmp_path / "product_data.csv"
    sample_products_df.to_csv(products_file, index=False)
    return products_file


@pytest.fixture
def mock_recipes_file(tmp_path: Path, sample_recipe: dict) -> Path:
    """Mock recipes JSON file — built from tmp_path + sample_recipe."""
    recipes_file = tmp_path / "recipes.json"
    recipes = {sample_recipe["name"]: sample_recipe}
    recipes_file.write_text(json.dumps(recipes, indent=2), encoding="utf-8")
    return recipes_file


@pytest.fixture
def mock_inventory_file(tmp_path: Path, sample_product, sample_product_2) -> Path:
    """Mock inventory counts JSON."""
    inv_file = tmp_path / "inventory_counts.json"
    inventory = {
        sample_product["Product Name"]: 5,
        sample_product_2["Product Name"]: 10,
    }
    inv_file.write_text(json.dumps(inventory, indent=2), encoding="utf-8")
    return inv_file


# ============================================================================
# LAYER 3 — Composite bundle for E2E/integration tests
# ============================================================================

@pytest.fixture
def mock_dataset_bundle(
    mock_products_file: Path,
    mock_recipes_file: Path,
    mock_inventory_file: Path,
) -> dict[str, Path]:
    """Returns a dict of file paths for products/recipes/inventory in one fixture."""
    return {
        "products_csv": mock_products_file,
        "recipes_json": mock_recipes_file,
        "inventory_json": mock_inventory_file,
    }
