"""
Product Manager Module

This module handles all product-related operations including:
- Product CRUD operations (Create, Read, Update, Delete)
- Price calculations and unit conversions
- Data validation and file I/O operations
- Bulk operations for supplier data updates

Dependencies:
- pandas: For data manipulation
- os: For file operations
- locale: For currency formatting
- utils.validator: For data validation
- utils.file_loader: For file operations
- config: For configuration settings

Classes:
    None

Functions:
    get_text: Get translated text for UI
    initialize_product_data: Initialize product data file
    load_products: Load products from CSV file
    save_product: Save new product to file
    delete_product: Delete product from file
    update_product: Update existing product
    bulk_update_prices: Update prices from supplier data
    format_currency: Format amount as currency
    format_currency_small: Format small amounts as currency
    convert_to_oz: Convert quantity to ounces
    calculate_cost_per_oz: Calculate cost per ounce
    migrate_existing_data: Migrate existing data to new format
"""

import pandas as pd
import os
import locale
from datetime import datetime
from typing import Dict, List, Tuple, Optional, Union, Any
from pathlib import Path
from sqlalchemy import create_engine, text

# Import utilities
from utils.validator import validate_product_data, validate_sku, validate_price

# File operations - using pandas directly since utils.file_loader was removed
def load_csv_file(file_path: str) -> pd.DataFrame:
    """Load CSV file using pandas"""
    try:
        return pd.read_csv(file_path)
    except Exception as e:
        raise FileNotFoundError(f"Could not load file {file_path}: {e}")

def save_csv_file(df: pd.DataFrame, file_path: Union[str, Path]) -> None:
    """Save DataFrame to CSV file"""
    try:
        df.to_csv(str(file_path), index=False)
    except Exception as e:
        raise IOError(f"Could not save file {file_path}: {e}")

class FileLoadError(Exception):
    """Custom exception for file loading errors"""
    pass

from config import config

# Set locale for currency formatting
try:
    locale.setlocale(locale.LC_ALL, 'en_US.UTF-8')
except:
    try:
        locale.setlocale(locale.LC_ALL, 'en_US')
    except:
        pass  # Use default formatting if locale not available

# Language translations
TRANSLATIONS: Dict[str, Dict[str, str]] = {
    "en": {
        "page_title": "🧺 Product Database",
        "page_caption": "Manage your product catalog and inventory items",
        "add_new_product": "Add New Product",
        "product_name": "Product Name",
        "sku": "SKU",
        "pack": "Pack",
        "size": "Size",
        "category": "Category",
        "unit_of_measure": "Unit of Measure",
        "cost_per_unit": "Current Price per Unit",
        "cost_per_unit_help": "Enter the cost in dollars",
        "location": "Location",
        "location_help": "Select where this product is stored",
        "add_product_button": "Add Product",
        "cost_per_ounce_preview": "💡 Cost per ounce: {cost} (1 {unit} = {conversion} oz)",
        "please_enter_name": "Please enter a product name.",
        "product_exists": "Product '{name}' already exists!",
        "product_added": "{name} added to the product list!",
        "product_list": "Product List",
        "search_products": "🔍 Search products by name or SKU:",
        "filter_by_category": "Filter by category:",
        "all_categories": "All Categories",
        "showing_products": "Showing {filtered} of {total} products",
        "no_products_match": "No products match your search criteria.",
        "manage_products": "Manage Products",
        "delete_product": "Delete Product",
        "edit_product": "Edit Product",
        "delete_a_product": "Delete a Product",
        "select_product_delete": "Select product to delete:",
        "delete_button": "🗑️ Delete Product",
        "deleted_successfully": "Deleted '{name}' successfully!",
        "select_product_delete_warning": "Please select a product to delete.",
        "edit_a_product": "Edit a Product",
        "select_product_edit": "Select product to edit:",
        "editing": "Editing: **{name}**",
        "update_product_button": "💾 Update Product",
        "product_updated": "Updated '{name}' successfully!",
        "summary": "📊 Summary",
        "total_products": "Total Products",
        "most_expensive": "Most Expensive",
        "total_inventory_value": "Total Inventory Value",
        "top_category": "Top Category",
        "items": "items",
        "no_products_found": "No products found. Add a product to get started.",
        "na": "N/A",
        "bulk_update_title": "📊 Bulk Update from Supplier CSV",
        "upload_supplier_csv": "Upload supplier CSV file",
        "supplier_csv_preview": "Supplier CSV Preview:",
        "column_mapping": "Column Mapping:",
        "select_sku_column": "Select SKU column:",
        "select_price_column": "Select price column:",
        "update_prices_button": "Update Prices",
        "updated_products_count": "Updated {count} products with new pricing!"
    },
    "es": {
        "page_title": "🧺 Base de Datos de Productos",
        "page_caption": "Gestiona tu catálogo de productos e inventario",
        "add_new_product": "Agregar Nuevo Producto",
        "product_name": "Nombre del Producto",
        "sku": "SKU",
        "pack": "Paquete",
        "size": "Tamaño",
        "category": "Categoría",
        "unit_of_measure": "Unidad de Medida",
        "cost_per_unit": "Costo por Unidad",
        "cost_per_unit_help": "Ingresa el costo en dólares",
        "location": "Ubicación",
        "location_help": "Selecciona dónde se almacena este producto",
        "add_product_button": "Agregar Producto",
        "cost_per_ounce_preview": "💡 Costo por onza: {cost} (1 {unit} = {conversion} oz)",
        "please_enter_name": "Por favor ingresa un nombre de producto.",
        "product_exists": "¡El producto '{name}' ya existe!",
        "product_added": "¡{name} agregado a la lista de productos!",
        "product_list": "Lista de Productos",
        "search_products": "🔍 Buscar productos por nombre o SKU:",
        "filter_by_category": "Filtrar por categoría:",
        "all_categories": "Todas las Categorías",
        "showing_products": "Mostrando {filtered} de {total} productos",
        "no_products_match": "Ningún producto coincide con tu búsqueda.",
        "manage_products": "Gestionar Productos",
        "delete_product": "Eliminar Producto",
        "edit_product": "Editar Producto",
        "delete_a_product": "Eliminar un Producto",
        "select_product_delete": "Selecciona el producto a eliminar:",
        "delete_button": "🗑️ Eliminar Producto",
        "deleted_successfully": "¡'{name}' eliminado exitosamente!",
        "select_product_delete_warning": "Por favor selecciona un producto para eliminar.",
        "edit_a_product": "Editar un Producto",
        "select_product_edit": "Selecciona el producto a editar:",
        "editing": "Editando: **{name}**",
        "update_product_button": "💾 Actualizar Producto",
        "product_updated": "¡'{name}' actualizado exitosamente!",
        "summary": "📊 Resumen",
        "total_products": "Total de Productos",
        "most_expensive": "Más Caro",
        "total_inventory_value": "Valor Total del Inventario",
        "top_category": "Categoría Principal",
        "items": "artículos",
        "no_products_found": "No se encontraron productos. Agrega un producto para comenzar.",
        "na": "N/A",
        "bulk_update_title": "📊 Actualización Masiva desde CSV del Proveedor",
        "upload_supplier_csv": "Subir archivo CSV del proveedor",
        "supplier_csv_preview": "Vista Previa del CSV del Proveedor:",
        "column_mapping": "Mapeo de Columnas:",
        "select_sku_column": "Selecciona columna SKU:",
        "select_price_column": "Selecciona columna de precio:",
        "update_prices_button": "Actualizar Precios",
        "updated_products_count": "¡{count} productos actualizados con nuevos precios!"
    }
}

# File path for storing products
DATA_FILE = config.PRODUCTS_FILE

# Database engine cache
_DB_ENGINE = None

def _normalize_db_url(url: str) -> str:
    if not url:
        return url
    # Allow postgres:// scheme by mapping to SQLAlchemy's preferred driver URL
    if url.startswith("postgres://"):
        return url.replace("postgres://", "postgresql+psycopg2://", 1)
    return url

def _get_engine():
    global _DB_ENGINE
    if _DB_ENGINE is not None:
        return _DB_ENGINE
    db_url = _normalize_db_url(getattr(config, "DATABASE_URL", ""))
    if not db_url:
        return None
    _DB_ENGINE = create_engine(db_url, pool_pre_ping=True)
    return _DB_ENGINE

def _use_db() -> bool:
    return bool(getattr(config, "DATABASE_URL", ""))

# Unit conversion factors to ounces
UNIT_CONVERSIONS: Dict[str, float] = config.UNIT_CONVERSIONS

def get_text(key: str, lang: str = "en", **kwargs) -> str:
    """
    Get translated text for the given key

    Args:
        key: Translation key to look up
        lang: Language code ('en' or 'es')
        **kwargs: Format parameters for the text

    Returns:
        str: Translated text with parameters substituted

    Example:
        >>> get_text("product_added", "en", name="Apple")
        "Apple added to the product list!"
    """
    if lang not in TRANSLATIONS:
        lang = "en"
    text = TRANSLATIONS[lang].get(key, key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text

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
        return f"${amount:.2f}"

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
        return f"${amount:,.2f}"
    except (ValueError, TypeError):
        return f"${amount:.2f}"

def migrate_existing_data() -> Optional[str]:
    """
    Migrate existing data to include SKU, Location, and Pack Size columns if they don't exist

    Returns:
        Optional[str]: Success message or None if no migration needed

    Raises:
        FileLoadError: If file operations fail
    """
    try:
        # CSV migration is skipped when using DB storage
        if _use_db():
            return None
        if os.path.exists(DATA_FILE):
            df = load_csv_file(str(DATA_FILE))
            migration_messages = []

            if "SKU" not in df.columns:
                # Add SKU column with empty values
                df.insert(1, "SKU", "")
                migration_messages.append("SKU column")

            if "Location" not in df.columns:
                # Add Location column with default value (after SKU column)
                df.insert(2, "Location", "Dry Goods Storage")
                migration_messages.append("Location column")

            if "Pack Size" not in df.columns:
                # Add Pack Size column with empty values (after Category column)
                df.insert(4, "Pack Size", "")
                migration_messages.append("Pack Size column")

            if "Current Price per Unit" not in df.columns:
                # Rename "Cost per Unit" to "Current Price per Unit" and add new columns
                if "Cost per Unit" in df.columns:
                    df = df.rename(columns={"Cost per Unit": "Current Price per Unit"})
                else:
                    df.insert(6, "Current Price per Unit", "")
                migration_messages.append("Current Price per Unit column")

            if "Last Price per Unit" not in df.columns:
                # Add Last Price per Unit column
                df.insert(7, "Last Price per Unit", "")
                migration_messages.append("Last Price per Unit column")

            if "Last Updated Date" not in df.columns:
                # Add Last Updated Date column
                df.insert(8, "Last Updated Date", "")
                migration_messages.append("Last Updated Date column")

            if migration_messages:
                save_csv_file(df, DATA_FILE)
                return f"Data migrated to include {', '.join(migration_messages)}!"
    except Exception as e:
        raise FileLoadError(f"Error migrating data: {e}")

    return None

def initialize_product_data() -> Optional[str]:
    """
    Initialize the product data file if it doesn't exist

    Returns:
        Optional[str]: Migration message or None if no initialization needed

    Raises:
        FileLoadError: If file operations fail
    """
    try:
        # Skip CSV initialization when using DB
        if _use_db():
            return None
        if not os.path.exists("data"):
            os.makedirs("data")
        if not os.path.exists(DATA_FILE):
            df = pd.DataFrame({
                "Product Name": pd.Series(dtype="str"),
                "SKU": pd.Series(dtype="str"),
                "Location": pd.Series(dtype="str"),
                "Category": pd.Series(dtype="str"),
                "Pack Size": pd.Series(dtype="str"),
                "Unit": pd.Series(dtype="str"),
                "Current Price per Unit": pd.Series(dtype="float"),
                "Last Price per Unit": pd.Series(dtype="float"),
                "Last Updated Date": pd.Series(dtype="str"),
                "Cost per Oz": pd.Series(dtype="float")  # New column for cost per ounce
            })
            df.to_csv(DATA_FILE, index=False)
        else:
            # Migrate existing data to include new columns
            return migrate_existing_data()
    except Exception as e:
        raise FileLoadError(f"Error initializing product data: {e}")

    return None

def convert_to_oz(quantity: Union[float, int], unit: str) -> float:
    """
    Convert quantity to ounces based on unit

    Args:
        quantity: Quantity to convert
        unit: Unit of measurement

    Returns:
        float: Quantity in ounces

    Example:
        >>> convert_to_oz(1, "lb")
        16.0
    """
    conversion = UNIT_CONVERSIONS.get(unit.lower(), 1)
    return quantity * conversion

def calculate_cost_per_oz(cost_per_unit: Union[float, int], unit: str) -> float:
    """
    Calculate cost per ounce for a given unit and cost

    Args:
        cost_per_unit: Cost per unit
        unit: Unit of measurement

    Returns:
        float: Cost per ounce

    Example:
        >>> calculate_cost_per_oz(16, "lb")
        1.0
    """
    conversion = UNIT_CONVERSIONS.get(unit.lower(), 1)
    return cost_per_unit / conversion if conversion > 0 else 0

def save_product(product: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Save a new product to the data file

    Args:
        product: Product dictionary with required fields

    Returns:
        Tuple[bool, str]: (success, message)

    Raises:
        FileLoadError: If file operations fail
        ValidationError: If product data is invalid
    """
    try:
        if _use_db():
            # Validate product data
            is_valid, errors = validate_product_data(product)
            if not is_valid:
                return False, f"Validation errors: {', '.join(errors)}"

            engine = _get_engine()
            if engine is None:
                return False, "Database engine not available"

            # Check duplicate by product_name
            with engine.connect() as conn:
                exists = conn.execute(
                    text("SELECT 1 FROM product_inventory WHERE product_name = :name LIMIT 1"),
                    {"name": product['name']}
                ).first()
                if exists:
                    return False, get_text("product_exists", "en", name=product['name'])

            cost_per_oz = calculate_cost_per_oz(product['cost'], product['unit'])
            creation_date = datetime.now().date()
            params = {
                "product_name": product['name'],
                "sku": product.get('sku', ''),
                "location": product.get('location', 'Dry Goods Storage'),
                "category": product.get('category', ''),
                "pack_size": product.get('pack_size', ''),
                "pack": int(product.get('pack', 0)) if str(product.get('pack', '')).isdigit() else None,
                "size": product.get('size', ''),
                "unit": product['unit'],
                "current_price_per_unit": float(product['cost']),
                "last_price_per_unit": float(product['cost']),
                "last_updated_date": creation_date,
                "cost_per_oz": float(cost_per_oz),
            }
            with engine.begin() as conn:
                conn.execute(text(
                    """
                    INSERT INTO product_inventory (
                        product_name, sku, location, category,
                        pack_size, pack, size, unit,
                        current_price_per_unit, last_price_per_unit,
                        last_updated_date, cost_per_oz
                    ) VALUES (
                        :product_name, :sku, :location, :category,
                        :pack_size, :pack, :size, :unit,
                        :current_price_per_unit, :last_price_per_unit,
                        :last_updated_date, :cost_per_oz
                    )
                    """
                ), params)
            return True, get_text("product_added", "en", name=product['name'])

        # Validate product data
        is_valid, errors = validate_product_data(product)
        if not is_valid:
            return False, f"Validation errors: {', '.join(errors)}"

        # Load existing products
        products_df = load_products()

        # Check if product already exists
        if not products_df.empty and product['name'] in products_df['Product Name'].values:
            return False, get_text("product_exists", "en", name=product['name'])

        # Calculate cost per ounce
        cost_per_oz = calculate_cost_per_oz(product['cost'], product['unit'])

        # Create new product row
        # For new products, set initial price as "last price" for baseline tracking
        creation_date = datetime.now().strftime('%Y-%m-%d')
        new_product = {
            'Product Name': product['name'],
            'SKU': product.get('sku', ''),
            'Location': product.get('location', 'Dry Goods Storage'),
            'Category': product.get('category', ''),
            'Pack': product.get('pack', ''),
            'Size': product.get('size', ''),
            'Unit': product['unit'],
            'Current Price per Unit': product['cost'],
            'Last Price per Unit': product['cost'],  # Set initial price as baseline
            'Last Updated Date': creation_date,    # Record creation date
            'Cost per Oz': cost_per_oz
        }

        # Add to DataFrame
        new_df = pd.DataFrame([new_product])
        if products_df.empty:
            products_df = new_df
        else:
            products_df = pd.concat([products_df, new_df], ignore_index=True)

        # Save to file
        if save_csv_file is None:
            raise FileLoadError("save_csv_file function is not defined")
        save_csv_file(products_df, str(DATA_FILE))

        return True, get_text("product_added", "en", name=product['name'])

    except Exception as e:
        raise FileLoadError(f"Error saving product: {e}")

def load_products() -> pd.DataFrame:
    """
    Load products from the data file

    Returns:
        pd.DataFrame: Products data

    Raises:
        FileLoadError: If file operations fail
    """
    try:
        if _use_db():
            engine = _get_engine()
            if engine is None:
                return pd.DataFrame({
                    col: pd.Series(dtype='object') for col in [
                        'Product Name', 'SKU', 'Location', 'Category', 'Pack Size', 'Pack', 'Size', 'Unit',
                        'Current Price per Unit', 'Last Price per Unit', 'Last Updated Date', 'Cost per Oz'
                    ]
                })
            query = (
                "SELECT product_name, sku, location, category, pack_size, pack, size, unit, "
                "current_price_per_unit, last_price_per_unit, last_updated_date, cost_per_oz "
                "FROM product_inventory"
            )
            with engine.connect() as conn:
                df = pd.read_sql_query(text(query), conn)
            # Rename columns to match legacy CSV-based schema expected by app
            rename_map = {
                'product_name': 'Product Name',
                'sku': 'SKU',
                'location': 'Location',
                'category': 'Category',
                'pack_size': 'Pack Size',
                'pack': 'Pack',
                'size': 'Size',
                'unit': 'Unit',
                'current_price_per_unit': 'Current Price per Unit',
                'last_price_per_unit': 'Last Price per Unit',
                'last_updated_date': 'Last Updated Date',
                'cost_per_oz': 'Cost per Oz'
            }
            return df.rename(columns=rename_map)
        if not os.path.exists(DATA_FILE):
            # Initialize if file doesn't exist
            initialize_product_data()
            return pd.DataFrame({col: pd.Series(dtype='object') for col in ['Product Name', 'SKU', 'Location', 'Category', 'Pack Size', 'Unit', 'Current Price per Unit', 'Last Price per Unit', 'Last Updated Date', 'Cost per Oz']})

        df = load_csv_file(str(DATA_FILE))
        return df if isinstance(df, pd.DataFrame) else pd.DataFrame()
    except Exception as e:
        raise FileLoadError(f"Error loading products: {e}")

def get_products_count() -> int:
    """
    Return the total number of products using the active storage backend.

    When DATABASE_URL is set, counts rows from product_inventory.
    Otherwise, returns length of the CSV DataFrame.
    """
    try:
        if _use_db():
            engine = _get_engine()
            if engine is None:
                return 0
            with engine.connect() as conn:
                row = conn.execute(text("SELECT COUNT(*) FROM product_inventory")).first()
                return int(row[0]) if row and row[0] is not None else 0
        # Fallback to CSV count
        df = load_products()
        return int(len(df))
    except Exception:
        return 0

def delete_product(product_name: str) -> Tuple[bool, str]:
    """
    Delete a product from the data file

    Args:
        product_name: Name of the product to delete

    Returns:
        Tuple[bool, str]: (success, message)

    Raises:
        FileLoadError: If file operations fail
    """
    try:
        if _use_db():
            engine = _get_engine()
            if engine is None:
                return False, "Database engine not available"
            with engine.begin() as conn:
                result = conn.execute(
                    text("DELETE FROM product_inventory WHERE product_name = :name"),
                    {"name": product_name}
                )
                if result.rowcount == 0:
                    return False, f"Product '{product_name}' not found."
            return True, get_text("deleted_successfully", "en", name=product_name)
        products_df = load_products()

        if product_name not in products_df['Product Name'].values:
            return False, f"Product '{product_name}' not found."

        # Remove the product
        products_df = products_df[products_df['Product Name'] != product_name]
        products_df = pd.DataFrame(products_df)  # Ensure it's a DataFrame

        # Save updated data
        if save_csv_file is None:
            raise FileLoadError("save_csv_file function is not defined")
        save_csv_file(products_df, str(DATA_FILE))

        return True, get_text("deleted_successfully", "en", name=product_name)

    except Exception as e:
        raise FileLoadError(f"Error deleting product: {e}")

def update_product(old_name: str, updated_product: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Update an existing product in the data file

    Args:
        old_name: Original product name
        updated_product: Updated product data

    Returns:
        Tuple[bool, str]: (success, message)

    Raises:
        FileLoadError: If file operations fail
        ValidationError: If product data is invalid
    """
    try:
        if _use_db():
            # Validate updated product data
            is_valid, errors = validate_product_data(updated_product)
            if not is_valid:
                return False, f"Validation errors: {', '.join(errors)}"

            engine = _get_engine()
            if engine is None:
                return False, "Database engine not available"

            with engine.begin() as conn:
                row = conn.execute(
                    text("SELECT current_price_per_unit FROM product_inventory WHERE product_name = :name"),
                    {"name": old_name}
                ).first()
                if not row:
                    return False, f"Product '{old_name}' not found."
                current_price = float(row[0])
                new_price = float(updated_product['cost'])
                cost_per_oz = calculate_cost_per_oz(updated_product['cost'], updated_product['unit'])

                params = {
                    "old_name": old_name,
                    "product_name": updated_product['name'],
                    "sku": updated_product.get('sku', ''),
                    "location": updated_product.get('location', 'Dry Goods Storage'),
                    "category": updated_product.get('category', ''),
                    "pack_size": updated_product.get('pack_size', ''),
                    "pack": int(updated_product.get('pack', 0)) if str(updated_product.get('pack', '')).isdigit() else None,
                    "size": updated_product.get('size', ''),
                    "unit": updated_product['unit'],
                    "current_price_per_unit": new_price,
                    "cost_per_oz": float(cost_per_oz),
                }

                if current_price != new_price:
                    params.update({
                        "last_price_per_unit": current_price,
                        "last_updated_date": datetime.now().date(),
                    })
                    stmt = text(
                        """
                        UPDATE product_inventory SET
                            product_name = :product_name,
                            sku = :sku,
                            location = :location,
                            category = :category,
                            pack_size = :pack_size,
                            pack = :pack,
                            size = :size,
                            unit = :unit,
                            current_price_per_unit = :current_price_per_unit,
                            last_price_per_unit = :last_price_per_unit,
                            last_updated_date = :last_updated_date,
                            cost_per_oz = :cost_per_oz
                        WHERE product_name = :old_name
                        """
                    )
                else:
                    stmt = text(
                        """
                        UPDATE product_inventory SET
                            product_name = :product_name,
                            sku = :sku,
                            location = :location,
                            category = :category,
                            pack_size = :pack_size,
                            pack = :pack,
                            size = :size,
                            unit = :unit,
                            current_price_per_unit = :current_price_per_unit,
                            cost_per_oz = :cost_per_oz
                        WHERE product_name = :old_name
                        """
                    )
                conn.execute(stmt, params)
            return True, get_text("product_updated", "en", name=updated_product['name'])
        # Validate updated product data
        is_valid, errors = validate_product_data(updated_product)
        if not is_valid:
            return False, f"Validation errors: {', '.join(errors)}"

        products_df = load_products()

        if old_name not in products_df['Product Name'].values:
            return False, f"Product '{old_name}' not found."

        # Calculate new cost per ounce
        cost_per_oz = calculate_cost_per_oz(updated_product['cost'], updated_product['unit'])

        # Check if price has changed
        mask = products_df['Product Name'] == old_name
        current_price = products_df.loc[mask, 'Current Price per Unit'].iloc[0]
        new_price = updated_product['cost']

        # Update the product
        products_df.loc[mask, 'Product Name'] = updated_product['name']
        products_df.loc[mask, 'SKU'] = updated_product.get('sku', '')
        products_df.loc[mask, 'Location'] = updated_product.get('location', 'Dry Goods Storage')
        products_df.loc[mask, 'Category'] = updated_product.get('category', '')
        products_df.loc[mask, 'Pack'] = updated_product.get('pack', '')
        products_df.loc[mask, 'Size'] = updated_product.get('size', '')
        products_df.loc[mask, 'Unit'] = updated_product['unit']

        # Handle price history
        if current_price != new_price:
            # Price changed - update history
            products_df.loc[mask, 'Last Price per Unit'] = current_price
            products_df.loc[mask, 'Last Updated Date'] = datetime.now().strftime('%Y-%m-%d')

        products_df.loc[mask, 'Current Price per Unit'] = new_price
        products_df.loc[mask, 'Cost per Oz'] = cost_per_oz

        # Save updated data
        save_csv_file(products_df, DATA_FILE)

        return True, get_text("product_updated", "en", name=updated_product['name'])

    except Exception as e:
        raise FileLoadError(f"Error updating product: {e}")

def bulk_update_prices(supplier_df: pd.DataFrame, sku_column: str, price_column: str) -> Tuple[bool, str]:
    """
    Update product prices from supplier CSV data

    Args:
        supplier_df: Supplier data DataFrame
        sku_column: Name of the SKU column in supplier data
        price_column: Name of the price column in supplier data

    Returns:
        Tuple[bool, str]: (success, message)

    Raises:
        FileLoadError: If file operations fail
    """
    try:
        if _use_db():
            engine = _get_engine()
            if engine is None:
                return False, "Database engine not available"
            updated_count = 0
            with engine.begin() as conn:
                for _, supplier_row in supplier_df.iterrows():
                    sku_val = str(supplier_row[sku_column]).strip()
                    try:
                        new_price = float(supplier_row[price_column])
                    except (TypeError, ValueError):
                        continue

                    row = conn.execute(
                        text("SELECT unit, current_price_per_unit FROM product_inventory WHERE sku = :sku"),
                        {"sku": sku_val}
                    ).first()
                    if not row:
                        continue
                    unit, current_price = row[0], float(row[1])
                    params = {
                        "sku": sku_val,
                        "current_price_per_unit": new_price,
                        "cost_per_oz": calculate_cost_per_oz(new_price, unit) if unit else None,
                    }
                    if current_price != new_price:
                        params.update({
                            "last_price_per_unit": current_price,
                            "last_updated_date": datetime.now().date(),
                        })
                        stmt = text(
                            """
                            UPDATE product_inventory SET
                                current_price_per_unit = :current_price_per_unit,
                                last_price_per_unit = :last_price_per_unit,
                                last_updated_date = :last_updated_date,
                                cost_per_oz = :cost_per_oz
                            WHERE sku = :sku
                            """
                        )
                    else:
                        stmt = text(
                            """
                            UPDATE product_inventory SET
                                current_price_per_unit = :current_price_per_unit,
                                cost_per_oz = :cost_per_oz
                            WHERE sku = :sku
                            """
                        )
                    conn.execute(stmt, params)
                    updated_count += 1
            if updated_count > 0:
                return True, get_text("updated_products_count", "en", count=updated_count)
            return False, "No products were updated. Check SKU matching."

        # Fallback to CSV behavior
        products_df = load_products()
        updated_count = 0

        for _, supplier_row in supplier_df.iterrows():
            sku = supplier_row[sku_column]
            new_price = float(supplier_row[price_column])

            # Convert SKU to int to handle float/int comparison
            sku_int = int(float(sku))

            # Find matching product by SKU - handle both string and int types
            mask = products_df['SKU'] == sku_int
            if mask.any():
                current_price = products_df.loc[mask, 'Current Price per Unit'].iloc[0]

                # Always update the price (even if same) to ensure cost per oz recalculation
                # Update price history if price changed
                if current_price != new_price:
                    products_df.loc[mask, 'Last Price per Unit'] = current_price
                    products_df.loc[mask, 'Last Updated Date'] = datetime.now().strftime('%Y-%m-%d')

                # Update price and recalculate cost per ounce
                products_df.loc[mask, 'Current Price per Unit'] = new_price
                # Get the unit for all matching rows (should be the same for all)
                unit_series = products_df.loc[mask, 'Unit']
                # Use the first unit if available, else skip cost per oz update
                if not unit_series.empty:
                    unit = unit_series.iloc[0]
                    cost_per_oz = calculate_cost_per_oz(new_price, unit)
                    products_df.loc[mask, 'Cost per Oz'] = cost_per_oz
                updated_count += 1

        if updated_count > 0:
            save_csv_file(products_df, DATA_FILE)
            return True, get_text("updated_products_count", "en", count=updated_count)
        else:
            return False, "No products were updated. Check SKU matching."

    except Exception as e:
        raise FileLoadError(f"Error updating prices: {e}")

def find_product_by_sku(sku: str) -> Optional[Dict[str, Any]]:
    """
    Find a product by SKU

    Args:
        sku: Product SKU to search for

    Returns:
        Product dict or None if not found
    """
    try:
        if _use_db():
            engine = _get_engine()
            if engine is None:
                return None
            sku_str = str(sku).strip()
            with engine.connect() as conn:
                row = conn.execute(
                    text("SELECT product_name, sku, location, category, pack_size, pack, size, unit, current_price_per_unit, last_price_per_unit, last_updated_date, cost_per_oz FROM product_inventory WHERE sku = :sku LIMIT 1"),
                    {"sku": sku_str}
                ).mappings().first()
                if not row:
                    return None
                data = dict(row)
                # Map to legacy CSV-style keys expected by callers
                rename_map = {
                    'product_name': 'Product Name',
                    'sku': 'SKU',
                    'location': 'Location',
                    'category': 'Category',
                    'pack_size': 'Pack Size',
                    'pack': 'Pack',
                    'size': 'Size',
                    'unit': 'Unit',
                    'current_price_per_unit': 'Current Price per Unit',
                    'last_price_per_unit': 'Last Price per Unit',
                    'last_updated_date': 'Last Updated Date',
                    'cost_per_oz': 'Cost per Oz'
                }
                return {rename_map.get(k, k): v for k, v in data.items()}
        products_df = load_products()

        if products_df.empty:
            return None

        # Convert SKU to string for comparison
        sku_str = str(sku).strip()

        # Find matching product
        mask = products_df['SKU'].astype(str).str.strip() == sku_str

        if mask.any():
            product_row = products_df[mask].iloc[0]
            return product_row.to_dict()

        return None

    except Exception as e:
        return None


def normalize_unit(unit_str: str) -> str:
    """
    Normalize supplier unit codes to valid system units

    Args:
        unit_str: Unit string from supplier (e.g., 'CS', 'EA', 'LB', 'BX')

    Returns:
        Normalized unit string that matches valid units
    """
    if not unit_str:
        return 'each'

    unit_lower = str(unit_str).strip().lower()

    # Map common supplier codes to valid units
    unit_mapping = {
        # Case variations
        'cs': 'case',
        'case': 'case',
        'ca': 'case',
        'bx': 'case',
        'box': 'case',

        # Each variations
        'ea': 'each',
        'each': 'each',
        'pc': 'each',
        'piece': 'each',
        'unit': 'each',

        # Pound variations
        'lb': 'lb',
        'lbs': 'lb',
        'pound': 'lb',
        'pounds': 'lb',
        '#': 'lb',

        # Ounce variations
        'oz': 'oz',
        'ounce': 'oz',
        'ounces': 'oz',

        # Gallon variations
        'gal': 'gallon',
        'gallon': 'gallon',
        'gallons': 'gallon',
        'gl': 'gallon',

        # Quart variations
        'qt': 'quart',
        'quart': 'quart',
        'quarts': 'quart',
        'qts': 'quart',

        # Liter variations
        'l': 'liter',
        'liter': 'liter',
        'litre': 'liter',
        'lt': 'liter',
        'ltr': 'liter',

        # Gram variations
        'g': 'grams',
        'gram': 'grams',
        'grams': 'grams',
        'gm': 'grams',
        'kg': 'grams',  # We could convert kg to grams later
        'kilo': 'grams',
        'kilogram': 'grams',

        # Bottle/container (treat as each)
        'bt': 'each',
        'btl': 'each',
        'bottle': 'each',
        'container': 'each',
        'can': 'each',
        'jar': 'each',
        'bag': 'each',
        'pk': 'each',
        'pack': 'each',
        'package': 'each'
    }

    return unit_mapping.get(unit_lower, 'each')  # Default to 'each' if unknown


def sanitize_sku(sku) -> str:
    """
    Sanitize SKU to meet validation requirements:
    - 3-20 characters
    - Alphanumeric with optional hyphens
    - No leading/trailing hyphens

    Args:
        sku: Raw SKU (string, int, float, or any type)

    Returns:
        Sanitized SKU string (or empty if can't be sanitized)
    """
    import re
    import math

    # Handle None or empty
    if sku is None or str(sku).strip() == '':
        return ''

    # Convert to string, handling floats specially
    if isinstance(sku, float):
        # Check if it's NaN
        if math.isnan(sku):
            return ''
        # Convert float to int to remove decimal point (e.g., 1821537.0 → 1821537)
        sku = str(int(sku))
    else:
        sku = str(sku).strip()

    if not sku:
        return ''

    # Replace invalid characters with hyphens
    # Keep only alphanumeric and hyphens
    sku = re.sub(r'[^a-zA-Z0-9-]', '-', sku)

    # Remove consecutive hyphens
    sku = re.sub(r'-+', '-', sku)

    # Remove leading/trailing hyphens
    sku = sku.strip('-')

    # Truncate to 20 characters if too long
    if len(sku) > 20:
        sku = sku[:20].rstrip('-')

    # If less than 3 characters, return empty (invalid)
    if len(sku) < 3:
        return ''

    return sku


def convert_import_to_save_format(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Convert imported product dict from database format to save_product format

    Args:
        product: Product dict with database column names (Product Name, SKU, etc.)

    Returns:
        Product dict with save_product format (name, sku, cost, etc.)
    """
    # Normalize the unit before saving
    raw_unit = product.get('Unit', '')
    normalized_unit = normalize_unit(raw_unit)

    # Convert cost to float (may come as string from CSV)
    raw_cost = product.get('Current Price per Unit', 0)
    try:
        cost = float(raw_cost) if raw_cost else 0.0
    except (ValueError, TypeError):
        cost = 0.0

    # Sanitize SKU to meet validation requirements
    import sys
    raw_sku = product.get('SKU', '')
    print(f"[DEBUG] Original SKU: '{raw_sku}' (type: {type(raw_sku)}, length: {len(str(raw_sku))})", file=sys.stderr)
    sanitized_sku = sanitize_sku(raw_sku)
    print(f"[DEBUG] Sanitized SKU: '{sanitized_sku}' (length: {len(sanitized_sku)})", file=sys.stderr)

    return {
        'name': product.get('Product Name', ''),
        'sku': sanitized_sku,
        'location': product.get('Location', 'Dry Goods Storage'),
        'category': product.get('Category', ''),
        'pack': product.get('Pack', ''),
        'size': product.get('Size', ''),
        'unit': normalized_unit,
        'cost': cost
    }


def bulk_import_products(products: List[Dict[str, Any]], update_duplicates: bool = False) -> Tuple[int, int, int, List[str]]:
    """
    Import multiple products at once

    Args:
        products: List of product dictionaries
        update_duplicates: If True, update existing products; if False, skip them

    Returns:
        Tuple of (imported_count, updated_count, skipped_count, errors)
    """
    # Debug logging
    import sys
    print(f"[DEBUG] bulk_import_products called with {len(products)} products", file=sys.stderr)
    print(f"[DEBUG] update_duplicates: {update_duplicates}", file=sys.stderr)

    try:
        products_df = load_products()
        print(f"[DEBUG] Loaded {len(products_df)} existing products from file", file=sys.stderr)

        imported_count = 0
        updated_count = 0
        skipped_count = 0
        errors = []

        for idx, product in enumerate(products):
            try:
                print(f"[DEBUG] Processing product {idx+1}/{len(products)}: {product.get('Product Name', 'Unknown')}", file=sys.stderr)
                print(f"[DEBUG] Original SKU: '{product.get('SKU', '')}'", file=sys.stderr)
                print(f"[DEBUG] Original unit: '{product.get('Unit', 'N/A')}'", file=sys.stderr)

                # Convert from database format to save format
                converted_product = convert_import_to_save_format(product)
                print(f"[DEBUG] Sanitized SKU: '{converted_product.get('sku', '')}' (length: {len(str(converted_product.get('sku', '')))})", file=sys.stderr)
                print(f"[DEBUG] Normalized unit: '{converted_product.get('unit', 'N/A')}'", file=sys.stderr)
                print(f"[DEBUG] Converted product keys: {list(converted_product.keys())}", file=sys.stderr)

                # Check if product exists by SKU
                existing_product = find_product_by_sku(product.get('SKU', ''))

                if existing_product:
                    print(f"[DEBUG] Product exists (SKU: {product.get('SKU', '')})", file=sys.stderr)
                    if update_duplicates:
                        # Update existing product
                        old_name = existing_product['Product Name']
                        success, message = update_product(old_name, converted_product)
                        if success:
                            updated_count += 1
                            print(f"[DEBUG] Updated: {old_name}", file=sys.stderr)
                        else:
                            errors.append(f"{product.get('Product Name', 'Unknown')}: {message}")
                            print(f"[DEBUG] Update failed: {message}", file=sys.stderr)
                    else:
                        # Skip duplicate
                        skipped_count += 1
                        print(f"[DEBUG] Skipped duplicate", file=sys.stderr)
                else:
                    print(f"[DEBUG] New product, attempting to save...", file=sys.stderr)
                    # Import new product
                    success, message = save_product(converted_product)
                    if success:
                        imported_count += 1
                        print(f"[DEBUG] Successfully saved!", file=sys.stderr)
                    else:
                        errors.append(f"{product.get('Product Name', 'Unknown')}: {message}")
                        print(f"[DEBUG] Save failed: {message}", file=sys.stderr)

            except Exception as e:
                error_msg = f"{product.get('Product Name', 'Unknown')}: {str(e)}"
                errors.append(error_msg)
                print(f"[DEBUG] Exception: {error_msg}", file=sys.stderr)
                import traceback
                traceback.print_exc(file=sys.stderr)

        print(f"[DEBUG] Final counts - Imported: {imported_count}, Updated: {updated_count}, Skipped: {skipped_count}, Errors: {len(errors)}", file=sys.stderr)
        return imported_count, updated_count, skipped_count, errors

    except Exception as e:
        print(f"[DEBUG] Fatal exception in bulk_import_products: {str(e)}", file=sys.stderr)
        import traceback
        traceback.print_exc(file=sys.stderr)
        return 0, 0, 0, [f"Fatal error: {str(e)}"]
