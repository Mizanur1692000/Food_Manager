import re
import logging
from typing import Dict, List, Union, Tuple, Optional
from datetime import datetime, date

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

class ValidationError(Exception):
    """Custom exception for validation errors"""
    pass

def validate_email(email: str) -> bool:
    """
    Validate email format
    
    Args:
        email: Email address to validate
    
    Returns:
        bool: True if valid email format
    """
    if not email or not isinstance(email, str):
        return False
    
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None

def validate_sku(sku: str) -> bool:
    """
    Validate SKU format (alphanumeric, 3-20 characters, optional hyphens)
    
    Args:
        sku: SKU to validate
    
    Returns:
        bool: True if valid SKU format
    """
    if not sku or not isinstance(sku, str):
        return False
    
    # Remove hyphens for length check
    clean_sku = sku.replace('-', '')
    return (len(sku) >= 3 and len(sku) <= 20 and 
            clean_sku.isalnum() and 
            not sku.startswith('-') and 
            not sku.endswith('-'))

def validate_price(price: Union[str, float, int]) -> bool:
    """
    Validate price (positive number)
    
    Args:
        price: Price to validate
    
    Returns:
        bool: True if valid price
    """
    try:
        price_float = float(price)
        return price_float >= 0
    except (ValueError, TypeError):
        return False

def validate_required_field(value: Union[str, int, float, list, dict, None], field_name: str) -> Tuple[bool, str]:
    """
    Validate required field is not empty
    
    Args:
        value: Value to validate
        field_name: Name of the field for error message
    
    Returns:
        Tuple[bool, str]: (is_valid, error_message)
    """
    if value is None:
        return False, f"{field_name} is required"
    
    if isinstance(value, str) and value.strip() == "":
        return False, f"{field_name} cannot be empty"
    
    if isinstance(value, (list, dict)) and len(value) == 0:
        return False, f"{field_name} cannot be empty"
    
    return True, ""

def validate_product_data(product: Dict) -> Tuple[bool, List[str]]:
    """
    Validate product data structure
    
    Args:
        product: Product dictionary to validate
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'unit', 'cost']
    for field in required_fields:
        is_valid, error_msg = validate_required_field(product.get(field), field.title())
        if not is_valid:
            errors.append(error_msg)
    
    # Validate price
    if 'cost' in product and not validate_price(product['cost']):
        errors.append("Cost must be a positive number")
    
    # Validate SKU if provided
    if 'sku' in product and product['sku']:
        if not validate_sku(product['sku']):
            errors.append("SKU must be 3-20 characters, alphanumeric with optional hyphens")
    
    # Validate unit
    valid_units = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]
    if 'unit' in product and product['unit'] not in valid_units:
        errors.append(f"Unit must be one of: {', '.join(valid_units)}")
    
    return len(errors) == 0, errors

def validate_recipe_data(recipe: Dict) -> Tuple[bool, List[str]]:
    """
    Validate recipe data structure
    
    Args:
        recipe: Recipe dictionary to validate
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    # Required fields
    required_fields = ['name', 'servings', 'ingredients']
    for field in required_fields:
        is_valid, error_msg = validate_required_field(recipe.get(field), field.title())
        if not is_valid:
            errors.append(error_msg)
    
    # Validate servings
    if 'servings' in recipe:
        try:
            servings = int(recipe['servings'])
            if servings <= 0:
                errors.append("Servings must be a positive number")
        except (ValueError, TypeError):
            errors.append("Servings must be a valid number")
    
    # Validate ingredients
    if 'ingredients' in recipe and isinstance(recipe['ingredients'], list):
        if len(recipe['ingredients']) == 0:
            errors.append("Recipe must have at least one ingredient")
        else:
            for i, ingredient in enumerate(recipe['ingredients']):
                if not isinstance(ingredient, dict):
                    errors.append(f"Ingredient {i+1} must be a valid object")
                    continue
                
                # Validate ingredient fields
                ingredient_required = ['product_name', 'quantity', 'unit']
                for field in ingredient_required:
                    is_valid, error_msg = validate_required_field(
                        ingredient.get(field), f"Ingredient {i+1} {field.replace('_', ' ')}"
                    )
                    if not is_valid:
                        errors.append(error_msg)
                
                # Validate quantity
                if 'quantity' in ingredient:
                    try:
                        quantity = float(ingredient['quantity'])
                        if quantity <= 0:
                            errors.append(f"Ingredient {i+1} quantity must be positive")
                    except (ValueError, TypeError):
                        errors.append(f"Ingredient {i+1} quantity must be a valid number")
    
    return len(errors) == 0, errors

def validate_date_format(date_str: str, format: str = "%Y-%m-%d") -> bool:
    """
    Validate date string format
    
    Args:
        date_str: Date string to validate
        format: Expected date format
    
    Returns:
        bool: True if valid date format
    """
    try:
        datetime.strptime(date_str, format)
        return True
    except ValueError:
        return False

def validate_phone_number(phone: str) -> bool:
    """
    Validate phone number format (US format)
    
    Args:
        phone: Phone number to validate
    
    Returns:
        bool: True if valid phone format
    """
    if not phone or not isinstance(phone, str):
        return False
    
    # Remove all non-digit characters
    digits_only = re.sub(r'\D', '', phone)
    
    # Check if it's a valid US phone number (10 or 11 digits)
    return len(digits_only) in [10, 11]

def validate_zip_code(zip_code: str) -> bool:
    """
    Validate US ZIP code format
    
    Args:
        zip_code: ZIP code to validate
    
    Returns:
        bool: True if valid ZIP code format
    """
    if not zip_code or not isinstance(zip_code, str):
        return False
    
    # US ZIP code pattern: 5 digits or 5+4 format
    pattern = r'^\d{5}(-\d{4})?$'
    return re.match(pattern, zip_code) is not None

def validate_file_extension(filename: str, allowed_extensions: List[str]) -> bool:
    """
    Validate file extension
    
    Args:
        filename: Filename to validate
        allowed_extensions: List of allowed extensions (e.g., ['.csv', '.json'])
    
    Returns:
        bool: True if file has allowed extension
    """
    if not filename or not isinstance(filename, str):
        return False
    
    file_ext = filename.lower()
    return any(file_ext.endswith(ext.lower()) for ext in allowed_extensions)

def validate_file_size(file_size_bytes: int, max_size_mb: float) -> bool:
    """
    Validate file size
    
    Args:
        file_size_bytes: File size in bytes
        max_size_mb: Maximum file size in MB
    
    Returns:
        bool: True if file size is within limit
    """
    max_size_bytes = max_size_mb * 1024 * 1024
    return file_size_bytes <= max_size_bytes

def sanitize_filename(filename: str) -> str:
    """
    Sanitize filename for safe file operations
    
    Args:
        filename: Original filename
    
    Returns:
        str: Sanitized filename
    """
    if not filename:
        return ""
    
    # Remove or replace unsafe characters
    unsafe_chars = '<>:"/\\|?*'
    for char in unsafe_chars:
        filename = filename.replace(char, '_')
    
    # Remove leading/trailing spaces and dots
    filename = filename.strip(' .')
    
    # Ensure filename is not empty
    if not filename:
        filename = "unnamed_file"
    
    return filename

def validate_csv_structure(df, required_columns: List[str]) -> Tuple[bool, List[str]]:
    """
    Validate CSV structure has required columns
    
    Args:
        df: DataFrame to validate
        required_columns: List of required column names
    
    Returns:
        Tuple[bool, List[str]]: (is_valid, list_of_errors)
    """
    errors = []
    
    if df is None or df.empty:
        errors.append("DataFrame is empty or None")
        return False, errors
    
    missing_columns = [col for col in required_columns if col not in df.columns]
    if missing_columns:
        errors.append(f"Missing required columns: {', '.join(missing_columns)}")
    
    return len(errors) == 0, errors

def validate_numeric_range(value: Union[int, float], min_value: Optional[Union[int, float]] = None, 
                          max_value: Optional[Union[int, float]] = None) -> bool:
    """
    Validate numeric value is within specified range
    
    Args:
        value: Value to validate
        min_value: Minimum allowed value (None for no minimum)
        max_value: Maximum allowed value (None for no maximum)
    
    Returns:
        bool: True if value is within range
    """
    try:
        numeric_value = float(value)
        
        if min_value is not None and numeric_value < min_value:
            return False
        
        if max_value is not None and numeric_value > max_value:
            return False
        
        return True
    except (ValueError, TypeError):
        return False
