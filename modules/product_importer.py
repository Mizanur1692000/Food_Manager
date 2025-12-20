"""
Product Importer Module

Handles CSV import from supplier files with intelligent column mapping,
format detection, and template management.

Features:
- Multi-format support (SYSCO, standard CSV)
- Smart column mapping with fuzzy matching
- Reusable mapping templates
- Duplicate detection and handling
- Data validation and transformation
"""

import pandas as pd
import json
import os
from typing import Dict, List, Tuple, Optional, Any
from rapidfuzz import fuzz, process
from datetime import datetime
from config import config


# File paths
TEMPLATES_FILE = str(config.IMPORT_TEMPLATES_FILE)

# Required fields for product database
REQUIRED_FIELDS = {
    "Product Name": ["name", "product", "desc", "description", "item", "product_name",
                     "item_name", "ingredient", "ingredient_name", "product_description",
                     "item_description", "prod_name", "prod_desc"],
    "SKU": ["sku", "supc", "item_code", "code", "product_code", "item_number",
            "product_number", "item_no", "prod_code", "upc", "barcode"],
    "Category": ["category", "cat", "type", "group", "class", "classification",
                 "product_category", "item_category", "prod_cat"],
    "Unit": ["unit", "uom", "measure", "unit_of_measure", "selling_unit", "base_unit"],
    "Current Price per Unit": ["price", "cost", "unit_price", "case_price", "split_price",
                               "unit_cost", "each_price", "sell_price", "list_price",
                               "current_price", "price_per_unit", "cost_per_unit"]
}

OPTIONAL_FIELDS = {
    "Location": ["location", "storage", "area", "storage_location", "warehouse", "store_location",
                 "storage_area", "bin", "bin_location", "shelf", "zone"],
    "Pack": ["pack", "pack_type", "package", "pkg", "container"],
    "Size": ["size", "pack_size", "case_size", "package_size", "unit_size", "container_size",
             "qty", "quantity", "case_qty", "pack_qty", "case_count", "units_per_case",
             "pack_count", "case", "cs", "pack_unit"],
    "Brand": ["brand", "manufacturer", "mfr", "vendor", "supplier", "maker", "producer"]
}


def detect_csv_format(df: pd.DataFrame) -> str:
    """
    Detect the format of the uploaded CSV

    Args:
        df: DataFrame from uploaded CSV

    Returns:
        str: Format type ('sysco', 'standard')
    """
    # Check for SYSCO format indicators
    if df.shape[1] > 0:
        first_col = df.iloc[:, 0] if not df.empty else pd.Series()

        # SYSCO format has H/F/P row type indicators
        if not first_col.empty and first_col.astype(str).isin(['H', 'F', 'P']).sum() > 0:
            return 'sysco'

    return 'standard'


def _normalize_column_names(columns) -> list:
    """
    Normalize column names: handle NaN/None/empty values and deduplicate

    Args:
        columns: Column index or list of column names

    Returns:
        List of normalized, unique column names
    """
    import math

    normalized = []
    seen = {}

    for i, col in enumerate(columns):
        # Handle None, NaN, or empty strings
        if col is None or (isinstance(col, float) and math.isnan(col)) or str(col).strip() == '':
            col_name = f'Column_{i}'
        else:
            col_name = str(col).strip()

        # Deduplicate: if we've seen this name before, add a suffix
        if col_name in seen:
            seen[col_name] += 1
            col_name = f"{col_name}_{seen[col_name]}"
        else:
            seen[col_name] = 0

        normalized.append(col_name)

    return normalized


def parse_sysco_format(filepath: str) -> pd.DataFrame:
    """
    Parse SYSCO format CSV with H/F/P row prefixes

    Args:
        filepath: Path to SYSCO format CSV file

    Returns:
        pd.DataFrame: Cleaned product data (P rows only)
    """
    # Read the entire file
    df = pd.read_csv(filepath, header=None)

    # Find the header row (F row)
    header_row = df[df.iloc[:, 0] == 'F']
    if header_row.empty:
        # No F row, try to use first row as header
        df.columns = df.iloc[0]
        df = df[1:]
    else:
        # Use F row as column names (skip the first column which is 'F' itself)
        column_names = header_row.iloc[0].values[1:]  # Skip first value
        df.columns = ['_row_type'] + list(column_names)  # Temporary name for first column

    # Filter to only product rows (P rows)
    product_rows = df[df['_row_type'] == 'P'].copy()

    # Remove the first column (row type indicator)
    product_rows = product_rows.drop(columns=['_row_type'])

    # Reset index
    product_rows = product_rows.reset_index(drop=True)

    # Clean up and deduplicate column names
    product_rows.columns = _normalize_column_names(product_rows.columns)

    return product_rows


def parse_standard_csv(filepath: str) -> pd.DataFrame:
    """
    Parse standard CSV format

    Args:
        filepath: Path to CSV file

    Returns:
        pd.DataFrame: Product data
    """
    return pd.read_csv(filepath)


def preview_csv_data(df: pd.DataFrame, num_rows: int = 10) -> pd.DataFrame:
    """
    Get preview of CSV data

    Args:
        df: DataFrame to preview
        num_rows: Number of rows to return

    Returns:
        pd.DataFrame: Preview data with normalized column names
    """
    preview_df = df.head(num_rows).copy()

    # Ensure column names are unique for display (guard approach)
    preview_df.columns = _normalize_column_names(preview_df.columns)

    return preview_df


def suggest_column_mappings(supplier_columns: List[str], threshold: int = 70) -> Dict[str, Tuple[str, int]]:
    """
    Suggest column mappings using fuzzy matching

    Args:
        supplier_columns: List of column names from supplier CSV
        threshold: Minimum confidence score (0-100)

    Returns:
        Dict mapping app field to (supplier_column, confidence_score)
    """
    mappings = {}
    used_columns = set()

    # Combine required and optional fields
    all_fields = {**REQUIRED_FIELDS, **OPTIONAL_FIELDS}

    for app_field, patterns in all_fields.items():
        best_match = None
        best_score = 0

        # Check each supplier column
        for supplier_col in supplier_columns:
            if supplier_col in used_columns:
                continue

            supplier_col_lower = str(supplier_col).lower()

            # Try exact pattern matching first
            for pattern in patterns:
                if pattern in supplier_col_lower:
                    score = 100
                    if score > best_score:
                        best_score = score
                        best_match = supplier_col
                    break

            # Try fuzzy matching
            if best_score < 100:
                for pattern in patterns:
                    score = fuzz.ratio(pattern, supplier_col_lower)
                    if score > best_score and score >= threshold:
                        best_score = score
                        best_match = supplier_col

        if best_match and best_score >= threshold:
            mappings[app_field] = (best_match, best_score)
            used_columns.add(best_match)

    return mappings


def validate_mappings(mappings: Dict[str, str]) -> Tuple[bool, List[str]]:
    """
    Validate that required fields are mapped

    Args:
        mappings: Dict of app_field -> supplier_column

    Returns:
        Tuple of (is_valid, list_of_errors)
    """
    errors = []

    # Check required fields
    for required_field in REQUIRED_FIELDS.keys():
        if required_field not in mappings or not mappings[required_field]:
            errors.append(f"Required field '{required_field}' is not mapped")

    return len(errors) == 0, errors


def apply_column_mapping(df: pd.DataFrame, mappings: Dict[str, str]) -> pd.DataFrame:
    """
    Apply column mapping to transform supplier data to app format

    Args:
        df: Supplier DataFrame
        mappings: Dict of app_field -> supplier_column

    Returns:
        pd.DataFrame: Transformed data with app column names
    """
    result_df = pd.DataFrame()

    for app_field, supplier_col in mappings.items():
        if supplier_col in df.columns:
            result_df[app_field] = df[supplier_col]
        else:
            result_df[app_field] = None

    return result_df


def save_mapping_template(template_name: str, template_data: Dict[str, Any]) -> Tuple[bool, str]:
    """
    Save column mapping template

    Args:
        template_name: Name of the template
        template_data: Template configuration

    Returns:
        Tuple of (success, message)
    """
    try:
        # Load existing templates
        templates = load_all_templates()

        # Add/update template
        templates[template_name] = template_data

        # Save to file
        os.makedirs(os.path.dirname(TEMPLATES_FILE), exist_ok=True)
        with open(TEMPLATES_FILE, 'w') as f:
            json.dump(templates, f, indent=2)

        return True, f"Template '{template_name}' saved successfully"
    except Exception as e:
        return False, f"Error saving template: {str(e)}"


def load_mapping_template(template_name: str) -> Optional[Dict[str, Any]]:
    """
    Load column mapping template

    Args:
        template_name: Name of the template

    Returns:
        Dict with template data or None if not found
    """
    templates = load_all_templates()
    return templates.get(template_name)


def load_all_templates() -> Dict[str, Dict[str, Any]]:
    """
    Load all mapping templates

    Returns:
        Dict of template_name -> template_data
    """
    if not os.path.exists(TEMPLATES_FILE):
        return {}

    try:
        with open(TEMPLATES_FILE, 'r') as f:
            return json.load(f)
    except Exception:
        return {}


def list_templates() -> List[str]:
    """
    List all available template names

    Returns:
        List of template names
    """
    templates = load_all_templates()
    return list(templates.keys())


def detect_duplicates(df: pd.DataFrame, existing_products: pd.DataFrame) -> pd.DataFrame:
    """
    Detect products that already exist in database

    Args:
        df: New products DataFrame
        existing_products: Existing products DataFrame

    Returns:
        DataFrame with duplicate indicators
    """
    df = df.copy()
    df['is_duplicate'] = False
    df['duplicate_reason'] = ''

    if existing_products.empty:
        return df

    # Check for SKU matches
    if 'SKU' in df.columns and 'SKU' in existing_products.columns:
        for idx, row in df.iterrows():
            sku = str(row['SKU']).strip()
            if sku and sku in existing_products['SKU'].astype(str).values:
                df.at[idx, 'is_duplicate'] = True
                df.at[idx, 'duplicate_reason'] = 'SKU match'

    return df


def merge_product_data(supplier_row: pd.Series, defaults: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge supplier data with default values

    Args:
        supplier_row: Single row from supplier data
        defaults: Default values for missing fields

    Returns:
        Dict with complete product data
    """
    product = {}

    # Copy supplier data
    for col, val in supplier_row.items():
        if pd.notna(val) and str(val).strip():
            product[col] = val

    # Apply defaults for missing fields
    for field, default_val in defaults.items():
        if field not in product or not product[field]:
            product[field] = default_val

    return product


def calculate_derived_fields(product: Dict[str, Any]) -> Dict[str, Any]:
    """
    Calculate derived fields like Cost per Oz

    Args:
        product: Product data dict

    Returns:
        Product dict with calculated fields
    """
    from modules.product_manager import calculate_cost_per_oz

    # Calculate Cost per Oz if price and unit are available
    if 'Current Price per Unit' in product and 'Unit' in product:
        try:
            cost = float(product['Current Price per Unit'])
            unit = str(product['Unit']).lower()
            product['Cost per Oz'] = calculate_cost_per_oz(cost, unit)
        except (ValueError, TypeError):
            product['Cost per Oz'] = 0.0

    # Add timestamps
    product['Last Updated Date'] = datetime.now().strftime('%Y-%m-%d')

    return product


def process_import_batch(
    df: pd.DataFrame,
    existing_products: pd.DataFrame,
    defaults: Dict[str, Any],
    duplicate_action: str = 'ask'
) -> Dict[str, Any]:
    """
    Process batch import with validation and duplicate handling

    Args:
        df: DataFrame with mapped supplier data
        existing_products: Existing products DataFrame
        defaults: Default values for missing fields
        duplicate_action: 'ask', 'update', or 'skip'

    Returns:
        Dict with import results
    """
    results = {
        'ready': [],
        'duplicates': [],
        'errors': [],
        'warnings': []
    }

    # Detect duplicates
    df = detect_duplicates(df, existing_products)

    # Process each row
    for idx, row in df.iterrows():
        try:
            # Merge with defaults
            product = merge_product_data(row, defaults)

            # Calculate derived fields
            product = calculate_derived_fields(product)

            # Validate required fields
            missing_fields = []
            for field in REQUIRED_FIELDS.keys():
                if field not in product or not product[field]:
                    missing_fields.append(field)

            if missing_fields:
                results['errors'].append({
                    'row': idx,
                    'product_name': product.get('Product Name', 'Unknown'),
                    'error': f"Missing required fields: {', '.join(missing_fields)}"
                })
                continue

            # Check if duplicate
            if row.get('is_duplicate', False):
                results['duplicates'].append({
                    'row': idx,
                    'product': product,
                    'reason': row.get('duplicate_reason', 'Unknown')
                })
            else:
                results['ready'].append(product)

        except Exception as e:
            results['errors'].append({
                'row': idx,
                'product_name': row.get('Product Name', 'Unknown'),
                'error': str(e)
            })

    return results


def combine_pack_size(row: pd.Series, pack_col: str = None, size_col: str = None, unit_col: str = None) -> str:
    """
    Combine pack, size, and unit columns into single Pack Size field

    Args:
        row: DataFrame row
        pack_col: Name of pack column
        size_col: Name of size column
        unit_col: Name of unit column

    Returns:
        Combined pack size string
    """
    parts = []

    if pack_col and pack_col in row and pd.notna(row[pack_col]):
        parts.append(str(row[pack_col]))

    if size_col and size_col in row and pd.notna(row[size_col]):
        parts.append(str(row[size_col]))

    if unit_col and unit_col in row and pd.notna(row[unit_col]):
        parts.append(str(row[unit_col]))

    return ' '.join(parts) if parts else ''

