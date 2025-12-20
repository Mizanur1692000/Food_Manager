"""
Shared Functions Module

This module contains common functions used across multiple modules in the restaurant
inventory app, including data loading, translations, file operations, and utilities.

Functions:
    load_products: Load products from CSV file
    get_text: Get translated text for UI
    format_currency: Format amount as currency
    ensure_data_directory: Ensure data directory exists
    load_json_file: Load data from JSON file
    save_json_file: Save data to JSON file
"""

import pandas as pd
import os
import json
from datetime import datetime
from typing import Dict, Any, Optional, Union
from pathlib import Path

# Import config for file paths
from config import config

# ===============================================================================
# SHARED TRANSLATIONS
# ===============================================================================

TRANSLATIONS = {
    "en": {
        # Common UI elements
        "product": "Product",
        "quantity": "Quantity",
        "unit": "Unit",
        "location": "Location",
        "category": "Category",
        "cost": "Cost",
        "price": "Price",
        "notes": "Notes",
        "date": "Date",
        "status": "Status",
        
        # Common actions
        "save": "Save",
        "update": "Update",
        "delete": "Delete",
        "edit": "Edit",
        "add": "Add",
        "remove": "Remove",
        "cancel": "Cancel",
        "confirm": "Confirm",
        
        # Common messages
        "success": "Success!",
        "error": "Error",
        "warning": "Warning",
        "info": "Information",
        "loading": "Loading...",
        "no_data": "No data found",
        "please_select": "Please select an item",
        "please_enter": "Please enter a value",
        
        # File operations
        "file_saved": "File saved successfully!",
        "file_load_error": "Error loading file",
        "file_save_error": "Error saving file",
        
        # Data operations
        "data_updated": "Data updated successfully!",
        "data_deleted": "Data deleted successfully!",
        "data_added": "Data added successfully!",
        "item_not_found": "Item not found",
        "item_exists": "Item already exists",
        
        # Currency and formatting
        "currency_symbol": "$",
        "decimal_places": 2,
        
        # Common units
        "units": {
            "oz": "Ounces",
            "lb": "Pounds", 
            "case": "Case",
            "each": "Each",
            "gallon": "Gallon",
            "liter": "Liter",
            "quart": "Quart",
            "grams": "Grams"
        }
    },
    "es": {
        # Common UI elements
        "product": "Producto",
        "quantity": "Cantidad",
        "unit": "Unidad",
        "location": "Ubicación",
        "category": "Categoría",
        "cost": "Costo",
        "price": "Precio",
        "notes": "Notas",
        "date": "Fecha",
        "status": "Estado",
        
        # Common actions
        "save": "Guardar",
        "update": "Actualizar",
        "delete": "Eliminar",
        "edit": "Editar",
        "add": "Agregar",
        "remove": "Remover",
        "cancel": "Cancelar",
        "confirm": "Confirmar",
        
        # Common messages
        "success": "¡Éxito!",
        "error": "Error",
        "warning": "Advertencia",
        "info": "Información",
        "loading": "Cargando...",
        "no_data": "No se encontraron datos",
        "please_select": "Por favor selecciona un elemento",
        "please_enter": "Por favor ingresa un valor",
        
        # File operations
        "file_saved": "¡Archivo guardado exitosamente!",
        "file_load_error": "Error al cargar archivo",
        "file_save_error": "Error al guardar archivo",
        
        # Data operations
        "data_updated": "¡Datos actualizados exitosamente!",
        "data_deleted": "¡Datos eliminados exitosamente!",
        "data_added": "¡Datos agregados exitosamente!",
        "item_not_found": "Elemento no encontrado",
        "item_exists": "El elemento ya existe",
        
        # Currency and formatting
        "currency_symbol": "$",
        "decimal_places": 2,
        
        # Common units
        "units": {
            "oz": "Onzas",
            "lb": "Libras",
            "case": "Caja",
            "each": "Cada",
            "gallon": "Galón",
            "liter": "Litro",
            "quart": "Cuarto",
            "grams": "Gramos"
        }
    }
}

# ===============================================================================
# SHARED FUNCTIONS
# ===============================================================================

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """
    Get translated text for the given key
    
    Args:
        key: Translation key to look up
        lang: Language code ('en' or 'es')
        **kwargs: Format parameters for the text
    
    Returns:
        str: Translated text with parameters substituted
    """
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS[lang].get(key, key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text

def load_products() -> pd.DataFrame:
    """
    Load products from the Product Database CSV file
    
    Returns:
        pd.DataFrame: Products data or empty DataFrame if file doesn't exist
        
    Raises:
        Exception: If file operations fail
    """
    try:
        products_file = config.PRODUCTS_FILE
        if os.path.exists(products_file):
            return pd.read_csv(products_file)
        else:
            return pd.DataFrame()
    except Exception as e:
        print(f"Error loading products: {e}")
        return pd.DataFrame()

def format_currency(amount: Union[float, int, None]) -> str:
    """
    Format amount as currency with dollar sign and commas
    
    Args:
        amount: Amount to format
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> format_currency(1234.56)
        "$1,234.56"
    """
    try:
        if amount is None:
            return "$0.00"
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def format_currency_small(amount: Union[float, int, None]) -> str:
    """
    Format amount as currency for small values (2 decimal places)
    
    Args:
        amount: Amount to format
        
    Returns:
        str: Formatted currency string
        
    Example:
        >>> format_currency_small(2.5)
        "$2.50"
    """
    try:
        if amount is None:
            return "$0.00"
        return f"${amount:.2f}"
    except (ValueError, TypeError):
        return "$0.00"

def ensure_data_directory() -> None:
    """
    Ensure the data directory exists
    """
    try:
        os.makedirs("data", exist_ok=True)
    except Exception as e:
        print(f"Error creating data directory: {e}")

def load_json_file(file_path: Union[str, Path]) -> Dict[str, Any]:
    """
    Load data from JSON file
    
    Args:
        file_path: Path to JSON file
        
    Returns:
        Dict[str, Any]: Loaded data or empty dict if file doesn't exist
    """
    try:
        if os.path.exists(file_path):
            with open(file_path, 'r', encoding='utf-8') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        print(f"Error loading JSON file {file_path}: {e}")
        return {}

def save_json_file(data: Dict[str, Any], file_path: Union[str, Path]) -> bool:
    """
    Save data to JSON file
    
    Args:
        data: Data to save
        file_path: Path to save file
        
    Returns:
        bool: True if successful, False otherwise
    """
    try:
        ensure_data_directory()
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        return True
    except Exception as e:
        print(f"Error saving JSON file {file_path}: {e}")
        return False

def get_available_locations(products_df: pd.DataFrame) -> list:
    """
    Get list of available locations from products DataFrame
    
    Args:
        products_df: Products DataFrame
        
    Returns:
        list: List of unique locations
    """
    try:
        if products_df.empty or 'Location' not in products_df.columns:
            return []
        
        locations_series = pd.Series(products_df['Location'])
        locations_list = locations_series.dropna().unique().tolist()
        locations_list.sort()
        return locations_list
    except Exception as e:
        print(f"Error getting available locations: {e}")
        return []

def get_available_categories(products_df: pd.DataFrame) -> list:
    """
    Get list of available categories from products DataFrame
    
    Args:
        products_df: Products DataFrame
        
    Returns:
        list: List of unique categories
    """
    try:
        if products_df.empty or 'Category' not in products_df.columns:
            return []
        
        categories_series = pd.Series(products_df['Category'])
        categories_list = categories_series.dropna().unique().tolist()
        categories_list.sort()
        return categories_list
    except Exception as e:
        print(f"Error getting available categories: {e}")
        return []

def validate_required_fields(data: Dict[str, Any], required_fields: list) -> tuple[bool, list]:
    """
    Validate that required fields are present and not empty
    
    Args:
        data: Dictionary to validate
        required_fields: List of required field names
        
    Returns:
        tuple[bool, list]: (is_valid, list_of_errors)
    """
    errors = []
    
    for field in required_fields:
        if field not in data:
            errors.append(f"Missing required field: {field}")
        elif data[field] is None or data[field] == "":
            errors.append(f"Required field '{field}' cannot be empty")
    
    return len(errors) == 0, errors

def format_datetime(dt: Union[str, datetime]) -> str:
    """
    Format datetime for display
    
    Args:
        dt: Datetime object or string
        
    Returns:
        str: Formatted datetime string
    """
    try:
        if isinstance(dt, str):
            dt = datetime.fromisoformat(dt.replace('Z', '+00:00'))
        return dt.strftime('%Y-%m-%d %H:%M:%S')
    except Exception:
        return str(dt)

def get_current_datetime() -> str:
    """
    Get current datetime as ISO string
    
    Returns:
        str: Current datetime in ISO format
    """
    return datetime.now().isoformat() 