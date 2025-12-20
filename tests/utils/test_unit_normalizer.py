# tests/utils/test_unit_normalizer.py
"""Tests for unit_normalizer.py"""
import pytest
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from utils.unit_normalizer import (
    parse_fractions,
    normalize_unit,
    parse_quantity,
    convert_to_ounces
)


def test_parse_fractions_unicode():
    """Test parsing Unicode fractions"""
    assert parse_fractions("½ cup") == "0.5 cup"
    assert parse_fractions("¼ lb") == "0.25 lb"
    assert parse_fractions("1 ½ tsp") == "1 0.5 tsp"


def test_parse_fractions_ascii():
    """Test parsing ASCII fractions"""
    assert parse_fractions("1/2 cup") == "0.5 cup"
    assert parse_fractions("3/4 lb") == "0.75 lb"


def test_normalize_unit_weights():
    """Test weight unit normalization"""
    assert normalize_unit("pound") == "lb"
    assert normalize_unit("POUND") == "lb"
    assert normalize_unit("lbs") == "lb"
    assert normalize_unit("lb.") == "lb"
    assert normalize_unit("ounce") == "oz"
    assert normalize_unit("ounces") == "oz"


def test_normalize_unit_volumes():
    """Test volume unit normalization"""
    assert normalize_unit("teaspoon") == "tsp"
    assert normalize_unit("tablespoon") == "tbsp"
    assert normalize_unit("cup") == "cup"
    assert normalize_unit("cups") == "cup"


def test_normalize_unit_case_insensitive():
    """Test that unit normalization is case insensitive"""
    assert normalize_unit("POUND") == normalize_unit("pound")
    assert normalize_unit("OUNCE") == normalize_unit("ounce")


def test_parse_quantity_simple():
    """Test parsing simple quantities"""
    result = parse_quantity("2 cups")
    assert result["quantity"] == 2.0
    assert result["unit"] == "cup"


def test_parse_quantity_with_fractions():
    """Test parsing quantities with fractions"""
    result = parse_quantity("1/2 cup")
    assert result["quantity"] == 0.5
    result = parse_quantity("1 1/2 cups")
    assert result["quantity"] == 1.5


def test_convert_to_ounces_pounds():
    """Test converting pounds to ounces"""
    result = convert_to_ounces(1, "lb")
    assert result == 16.0
    
    result = convert_to_ounces(2, "lb")
    assert result == 32.0


def test_convert_to_ounces_already_ounces():
    """Test when already in ounces"""
    result = convert_to_ounces(16, "oz")
    assert result == 16.0


def test_convert_to_ounces_mixed():
    """Test converting mixed units"""
    result_1 = convert_to_ounces(1, "lb")
    result_2 = convert_to_ounces(16, "oz")
    assert result_1 == result_2
