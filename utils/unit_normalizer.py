"""
Unit normalization and conversion utilities
Handles fractions, ranges, unit standardization, and conversions
"""

import re
from typing import Dict, Tuple, Optional
from unidecode import unidecode

# Unicode fraction mappings
UNICODE_FRACTIONS = {
    "½": 0.5, "⅓": 0.33, "⅔": 0.67, "¼": 0.25, "¾": 0.75,
    "⅕": 0.2, "⅖": 0.4, "⅗": 0.6, "⅘": 0.8, "⅙": 0.17, "⅚": 0.83,
    "⅐": 0.14, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875
}

# ASCII fraction patterns
ASCII_FRACTION_PATTERN = re.compile(r'(\d+)\s*/\s*(\d+)')

# Quantity range patterns (e.g., "1-2", "1 to 2", "1–2")
RANGE_PATTERN = re.compile(r'(\d+\.?\d*)\s*[-–to]+\s*(\d+\.?\d*)', re.IGNORECASE)

# Unit normalization mappings
UNIT_MAPPINGS = {
    # Volume
    "teaspoon": "tsp", "teaspoons": "tsp", "t": "tsp",
    "tablespoon": "tbsp", "tablespoons": "tbsp", "T": "tbsp", "tbs": "tbsp",
    "fluid ounce": "fl oz", "fluid ounces": "fl oz", "floz": "fl oz",
    "ounce": "oz", "ounces": "oz", "oz.": "oz",
    "cup": "cup", "cups": "cup", "c": "cup",
    "pint": "pint", "pints": "pint", "pt": "pint",
    "quart": "quart", "quarts": "quart", "qt": "quart",
    "gallon": "gallon", "gallons": "gallon", "gal": "gallon",
    "milliliter": "ml", "milliliters": "ml", "millilitre": "ml", "millilitres": "ml",
    "liter": "liter", "liters": "liter", "litre": "liter", "litres": "liter", "l": "liter",

    # Weight
    "pound": "lb", "pounds": "lb", "lbs": "lb", "lb.": "lb",
    "gram": "g", "grams": "g", "g.": "g", "gr": "g",
    "kilogram": "kg", "kilograms": "kg", "kgs": "kg", "kg.": "kg",

    # Count
    "dozen": "dozen", "doz": "dozen",
    "each": "each", "ea": "each", "piece": "each", "pieces": "each",
    "bunch": "bunch", "bunches": "bunch",
    "case": "case", "cases": "case",
    "can": "can", "cans": "can",
    "jar": "jar", "jars": "jar",
    "bag": "bag", "bags": "bag",
    "box": "box", "boxes": "box",
    "package": "package", "packages": "package", "pkg": "package",
}

# Conversion factors to ounces (weight)
CONVERSION_TO_OZ = {
    "oz": 1.0,
    "lb": 16.0,
    "g": 0.035274,
    "kg": 35.274,

    # Volume conversions (approximate for water/milk density)
    "tsp": 0.17,
    "tbsp": 0.5,
    "fl oz": 1.0,
    "cup": 8.0,
    "pint": 16.0,
    "quart": 32.0,
    "gallon": 128.0,
    "ml": 0.033814,
    "liter": 33.814,

    # Count (rough estimates)
    "dozen": 24.0,  # e.g., eggs
    "each": 8.0,    # average item
    "bunch": 4.0,   # average bunch
    "case": 192.0,  # 12 lbs average
    "can": 14.5,    # standard can
    "jar": 16.0,    # standard jar
    "bag": 32.0,    # 2 lb average
    "box": 16.0,    # 1 lb average
    "package": 16.0,  # 1 lb average
}


def parse_fractions(text: str) -> str:
    """
    Convert Unicode and ASCII fractions to decimal

    Args:
        text: String potentially containing fractions

    Returns:
        String with fractions replaced by decimals
    """
    # First handle Unicode fractions
    for fraction, decimal in UNICODE_FRACTIONS.items():
        text = text.replace(fraction, str(decimal))

    # Handle ASCII fractions like "1/2", "3/4"
    def replace_ascii_fraction(match):
        numerator = float(match.group(1))
        denominator = float(match.group(2))
        if denominator == 0:
            return match.group(0)  # Return original if division by zero
        return str(numerator / denominator)

    text = ASCII_FRACTION_PATTERN.sub(replace_ascii_fraction, text)

    return text


def parse_quantity_ranges(text: str) -> Tuple[float, bool]:
    """
    Parse quantity ranges and return average

    Args:
        text: String potentially containing range like "1-2" or "1 to 2"

    Returns:
        Tuple of (average_quantity, is_estimate)
    """
    # First parse fractions
    text = parse_fractions(text)

    # Look for ranges
    match = RANGE_PATTERN.search(text)
    if match:
        low = float(match.group(1))
        high = float(match.group(2))
        average = (low + high) / 2.0
        return average, True

    # Try to extract single number
    number_match = re.search(r'(\d+\.?\d*)', text)
    if number_match:
        return float(number_match.group(1)), False

    return 1.0, True  # Default fallback


def normalize_unit(uom: str) -> str:
    """
    Normalize unit of measure to standard form

    Args:
        uom: Unit string (may be variation)

    Returns:
        Normalized unit string
    """
    if not uom:
        return "each"

    # Clean and lowercase
    uom_clean = unidecode(uom.strip().lower())

    # Remove periods and extra spaces
    uom_clean = uom_clean.replace(".", "").strip()

    # Look up in mappings
    return UNIT_MAPPINGS.get(uom_clean, uom_clean)


def convert_to_oz(quantity: float, uom: str) -> float:
    """
    Convert quantity to ounces using conversion factors

    Args:
        quantity: Numeric quantity
        uom: Normalized unit of measure

    Returns:
        Quantity in ounces (approximate for volume)
    """
    normalized_uom = normalize_unit(uom)
    conversion_factor = CONVERSION_TO_OZ.get(normalized_uom, 1.0)
    return quantity * conversion_factor


def extract_quantity_uom(text: str) -> Dict[str, any]:
    """
    Extract quantity and unit from text like "2.5 oz" or "1/2 cup"

    Args:
        text: Text containing quantity and unit

    Returns:
        Dict with raw, quantity, uom, quantity_oz, estimate
    """
    # Parse fractions first
    text_parsed = parse_fractions(text)

    # Pattern to match quantity and unit
    # Handles: "2 cups", "2.5 oz", "1-2 tsp"
    pattern = re.compile(
        r'(\d+\.?\d*\s*[-–to]+\s*\d+\.?\d*|\d+\.?\d*)\s*([a-zA-Z]+\.?)',
        re.IGNORECASE
    )

    match = pattern.search(text_parsed)

    if match:
        quantity_str = match.group(1)
        uom_str = match.group(2)

        # Parse quantity (handling ranges)
        quantity, is_estimate = parse_quantity_ranges(quantity_str)

        # Normalize unit
        uom_normalized = normalize_unit(uom_str)

        # Convert to oz
        quantity_oz = convert_to_oz(quantity, uom_normalized)

        return {
            "raw": text,
            "quantity": quantity,
            "uom": uom_normalized,
            "quantity_oz": round(quantity_oz, 3),
            "estimate": is_estimate
        }

    # If no match, try to extract just number
    quantity, is_estimate = parse_quantity_ranges(text_parsed)

    return {
        "raw": text,
        "quantity": quantity,
        "uom": "each",
        "quantity_oz": round(quantity * 8.0, 3),  # Assume 8 oz per item
        "estimate": True
    }


def normalize_ingredient_text(ingredient_text: str) -> Dict[str, any]:
    """
    Main function to normalize ingredient text

    Args:
        ingredient_text: Raw ingredient string like "2½ cups all-purpose flour"

    Returns:
        Dict with parsed and normalized values
    """
    # Extract quantity and UOM
    parsed = extract_quantity_uom(ingredient_text)

    # Extract ingredient name (remove quantity and uom)
    # Simple approach: remove the quantity/uom match from start
    ingredient_name = ingredient_text
    pattern = re.compile(
        r'^(\d+\.?\d*\s*[-–to]+\s*\d+\.?\d*|\d+\.?\d*)\s*([a-zA-Z]+\.?)\s*',
        re.IGNORECASE
    )
    ingredient_name = pattern.sub('', parse_fractions(ingredient_name))
    ingredient_name = ingredient_name.strip()

    if not ingredient_name:
        ingredient_name = "Unknown Ingredient"

    parsed["ingredient_name"] = ingredient_name

    return parsed


def count_uom_hits(text: str) -> int:
    """
    Count how many known UOM patterns appear in text
    Used for confidence scoring

    Args:
        text: Text to analyze

    Returns:
        Count of UOM matches
    """
    if not text:
        return 0

    text_lower = text.lower()
    count = 0

    # Check for common UOMs
    uom_patterns = [
        r'\boz\b', r'\blb\b', r'\bcup\b', r'\btsp\b', r'\btbsp\b',
        r'\bgram\b', r'\bkg\b', r'\bml\b', r'\bliter\b',
        r'\bquart\b', r'\bgallon\b', r'\beach\b', r'\bbunch\b',
        r'\bcase\b', r'\bdozen\b', r'\bpint\b'
    ]

    for pattern in uom_patterns:
        matches = re.findall(pattern, text_lower)
        count += len(matches)

    return count

