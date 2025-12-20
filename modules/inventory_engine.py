import pandas as pd
import os
from datetime import datetime
import json
from config import config

# Import shared functions
from utils.shared_functions import (
    get_text, load_products, format_currency, format_currency_small,
    load_json_file, save_json_file, get_available_locations
)

# Language translations for inventory-specific text
INVENTORY_TRANSLATIONS = {
    "en": {
        "page_title": "📦 Inventory Management",
        "page_caption": "Track inventory levels and manage stock",
        "current_inventory": "Current Inventory",
        "add_inventory": "Add Inventory",
        "update_inventory": "Update Inventory",
        "product": "Product",
        "quantity": "Quantity",
        "unit": "Unit",
        "date": "Date",
        "notes": "Notes",
        "add_button": "Add to Inventory",
        "update_button": "Update Inventory",
        "inventory_added": "Inventory added successfully!",
        "inventory_updated": "Inventory updated successfully!",
        "no_products": "No products found. Add products first.",
        "select_product": "Select a product:",
        "enter_quantity": "Enter quantity:",
        "enter_notes": "Enter notes (optional):",
        "inventory_summary": "Inventory Summary",
        "total_items": "Total Items",
        "total_value": "Total Value",
        "low_stock": "Low Stock Items",
        "out_of_stock": "Out of Stock",
        # Sheet-to-Shelf translations
        "sheet_to_shelf_title": "📋 Sheet-to-Shelf Inventory",
        "sheet_to_shelf_caption": "Conduct physical inventory counts and track stock levels",
        "start_count": "Start New Count",
        "continue_count": "Continue Count",
        "count_history": "Count History",
        "export_counts": "Export Counts",
        "count_name": "Count Name",
        "count_date": "Count Date",
        "count_status": "Status",
        "expected_qty": "Expected Qty",
        "actual_qty": "Actual Qty",
        "variance": "Variance",
        "variance_percent": "Variance %",
        "location": "Location",
        "count_notes": "Count Notes",
        "save_count": "Save Count",
        "save_count_success": "Count saved successfully!",
        "count_not_found": "Count not found!",
        "delete_count": "Delete Count",
        "delete_count_success": "Count deleted successfully!",
        "count_summary": "Count Summary",
        "items_counted": "Items Counted",
        "total_variance": "Total Variance",
        "accuracy_percent": "Accuracy %",
        "high_variance": "High Variance Items",
        "filter_by_location": "Filter by Location",
        "all_locations": "All Locations",
        "count_details": "Count Details",
        "edit_count": "Edit Count",
        "update_count": "Update Count",
        "count_updated": "Count updated successfully!",
        "no_counts_found": "No counts found. Start a new count to get started.",
        "count_in_progress": "Count in Progress",
        "complete_count": "Complete Count",
        "count_completed": "Count completed successfully!",
        "count_validation": "Count Validation",
        "validate_counts": "Validate Counts",
        "validation_passed": "Validation passed!",
        "validation_failed": "Validation failed!",
        "count_export": "Export Count Data",
        "export_csv": "Export to CSV",
        "export_json": "Export to JSON",
        "export_success": "Export successful!",
        "export_error": "Export failed!",
        "count_comparison": "Count Comparison",
        "compare_counts": "Compare Counts",
        "select_count_1": "Select first count:",
        "select_count_2": "Select second count:",
        "comparison_results": "Comparison Results",
        "no_comparison_data": "No data available for comparison."
    },
    "es": {
        "page_title": "📦 Gestión de Inventario",
        "page_caption": "Rastrea niveles de inventario y gestiona stock",
        "current_inventory": "Inventario Actual",
        "add_inventory": "Agregar Inventario",
        "update_inventory": "Actualizar Inventario",
        "product": "Producto",
        "quantity": "Cantidad",
        "unit": "Unidad",
        "date": "Fecha",
        "notes": "Notas",
        "add_button": "Agregar al Inventario",
        "update_button": "Actualizar Inventario",
        "inventory_added": "¡Inventario agregado exitosamente!",
        "inventory_updated": "¡Inventario actualizado exitosamente!",
        "no_products": "No se encontraron productos. Agrega productos primero.",
        "select_product": "Selecciona un producto:",
        "enter_quantity": "Ingresa cantidad:",
        "enter_notes": "Ingresa notas (opcional):",
        "inventory_summary": "Resumen de Inventario",
        "total_items": "Total de Artículos",
        "total_value": "Valor Total",
        "low_stock": "Artículos con Poco Stock",
        "out_of_stock": "Sin Stock",
        # Sheet-to-Shelf translations
        "sheet_to_shelf_title": "📋 Inventario Hoja a Estante",
        "sheet_to_shelf_caption": "Realizar conteos físicos de inventario y rastrear niveles de stock",
        "start_count": "Iniciar Nuevo Conteo",
        "continue_count": "Continuar Conteo",
        "count_history": "Historial de Conteos",
        "export_counts": "Exportar Conteos",
        "count_name": "Nombre del Conteo",
        "count_date": "Fecha del Conteo",
        "count_status": "Estado",
        "expected_qty": "Cantidad Esperada",
        "actual_qty": "Cantidad Real",
        "variance": "Varianza",
        "variance_percent": "Varianza %",
        "location": "Ubicación",
        "count_notes": "Notas del Conteo",
        "save_count": "Guardar Conteo",
        "save_count_success": "¡Conteo guardado exitosamente!",
        "count_not_found": "¡Conteo no encontrado!",
        "delete_count": "Eliminar Conteo",
        "delete_count_success": "¡Conteo eliminado exitosamente!",
        "count_summary": "Resumen del Conteo",
        "items_counted": "Artículos Contados",
        "total_variance": "Varianza Total",
        "accuracy_percent": "Precisión %",
        "high_variance": "Artículos con Alta Varianza",
        "filter_by_location": "Filtrar por Ubicación",
        "all_locations": "Todas las Ubicaciones",
        "count_details": "Detalles del Conteo",
        "edit_count": "Editar Conteo",
        "update_count": "Actualizar Conteo",
        "count_updated": "¡Conteo actualizado exitosamente!",
        "no_counts_found": "No se encontraron conteos. Inicia un nuevo conteo para comenzar.",
        "count_in_progress": "Conteo en Progreso",
        "complete_count": "Completar Conteo",
        "count_completed": "¡Conteo completado exitosamente!",
        "count_validation": "Validación del Conteo",
        "validate_counts": "Validar Conteos",
        "validation_passed": "¡Validación exitosa!",
        "validation_failed": "¡Validación fallida!",
        "count_export": "Exportar Datos del Conteo",
        "export_csv": "Exportar a CSV",
        "export_json": "Exportar a JSON",
        "export_success": "¡Exportación exitosa!",
        "export_error": "¡Exportación fallida!",
        "count_comparison": "Comparación de Conteos",
        "compare_counts": "Comparar Conteos",
        "select_count_1": "Selecciona primer conteo:",
        "select_count_2": "Selecciona segundo conteo:",
        "comparison_results": "Resultados de Comparación",
        "no_comparison_data": "No hay datos disponibles para comparación."
    }
}

def get_inventory_text(key, lang="en", **kwargs):
    """Get translated text for inventory-specific keys"""
    if lang not in INVENTORY_TRANSLATIONS:
        lang = "en"
    text = INVENTORY_TRANSLATIONS[lang].get(key, key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text

# File paths
INVENTORY_FILE = str(config.INVENTORY_FILE)
COUNTS_FILE = str(config.INVENTORY_COUNTS_FILE)
COUNT_HISTORY_FILE = str(config.COUNT_HISTORY_FILE)

def load_inventory():
    """Load inventory data from CSV file"""
    try:
        if os.path.exists(INVENTORY_FILE):
            return pd.read_csv(INVENTORY_FILE)
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def save_inventory(inventory_df):
    """Save inventory data to CSV file"""
    try:
        os.makedirs("data", exist_ok=True)
        inventory_df.to_csv(INVENTORY_FILE, index=False)
        return True
    except Exception as e:
        return False

def add_inventory_item(product_name, quantity, unit, notes=""):
    """Add a new inventory item"""
    try:
        inventory_df = load_inventory()
        
        new_item = {
            'Product Name': product_name,
            'Quantity': quantity,
            'Unit': unit,
            'Date': datetime.now().strftime('%Y-%m-%d'),
            'Notes': notes
        }
        
        inventory_df = pd.concat([inventory_df, pd.DataFrame([new_item])], ignore_index=True)
        
        if save_inventory(inventory_df):
            return True, "Inventory added successfully!"
        else:
            return False, "Error saving inventory."
    except Exception as e:
        return False, f"Error adding inventory: {e}"

def update_inventory_item(product_name, new_quantity, notes=""):
    """Update existing inventory item"""
    try:
        inventory_df = load_inventory()
        
        # Find the item to update
        mask = inventory_df['Product Name'] == product_name
        if not mask.any():
            return False, f"Product '{product_name}' not found in inventory!"
        
        # Update quantity and notes
        inventory_df.loc[mask, 'Quantity'] = new_quantity
        if notes:
            inventory_df.loc[mask, 'Notes'] = notes
        inventory_df.loc[mask, 'Date'] = datetime.now().strftime('%Y-%m-%d')
        
        if save_inventory(inventory_df):
            return True, "Inventory updated successfully!"
        else:
            return False, "Error saving inventory."
    except Exception as e:
        return False, f"Error updating inventory: {e}"

def calculate_inventory_value(inventory_df, products_df):
    """Calculate total inventory value"""
    total_value = 0
    
    for _, inventory_item in inventory_df.iterrows():
        product_name = inventory_item['Product Name']
        quantity = inventory_item['Quantity']
        
        # Find matching product
        product_match = products_df[products_df['Product Name'] == product_name]
        
        if not product_match.empty:
            product = product_match.iloc[0]
            unit_cost = product['Current Price per Unit']
            total_value += quantity * unit_cost
    
    return total_value

def get_low_stock_items(inventory_df, threshold=10):
    """Get items with low stock"""
    low_stock = inventory_df[inventory_df['Quantity'] <= threshold]
    return low_stock

def get_out_of_stock_items(inventory_df):
    """Get items that are out of stock"""
    out_of_stock = inventory_df[inventory_df['Quantity'] <= 0]
    return out_of_stock

# ===============================================================================
# SHEET-TO-SHELF INVENTORY FUNCTIONS
# ===============================================================================

def load_counts():
    """Load inventory counts from JSON file"""
    return load_json_file(COUNTS_FILE)

def save_counts(counts_data):
    """Save inventory counts to JSON file"""
    return save_json_file(counts_data, COUNTS_FILE)

def load_count_history():
    """Load count history from JSON file"""
    data = load_json_file(COUNT_HISTORY_FILE)
    return data if isinstance(data, list) else []

def save_count_history(history_data):
    """Save count history to JSON file"""
    return save_json_file(history_data, COUNT_HISTORY_FILE)

def create_new_count(count_name, products_df, location_filter=None):
    """Create a new inventory count"""
    try:
        counts_data = load_counts()
        
        # Filter products by location if specified
        if location_filter and location_filter != "All Locations":
            products_df = products_df[products_df['Location'] == location_filter]
        
        # Debug: Check available columns
        print(f"Available columns: {list(products_df.columns)}")
        
        # Create count items
        count_items = []
        for _, product in products_df.iterrows():
            try:
                count_item = {
                    'product_name': product['Product Name'],
                    'sku': product['SKU'],
                    'expected_qty': 0,  # Default expected quantity - can be updated during count
                    'actual_qty': None,
                    'unit': product['Unit'],
                    'location': product['Location'],
                    'current_price': product['Current Price per Unit'],
                    'notes': ""
                }
                count_items.append(count_item)
            except KeyError as e:
                print(f"Missing column: {e}")
                print(f"Available columns: {list(product.index)}")
                raise
        
        # Create count record
        count_record = {
            'count_name': count_name,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'status': 'in_progress',
            'location_filter': location_filter,
            'items': count_items,
            'notes': ""
        }
        
        counts_data[count_name] = count_record
        
        if save_counts(counts_data):
            return True, f"Count '{count_name}' created successfully!"
        else:
            return False, "Error saving count data."
    except Exception as e:
        return False, f"Error creating count: {e}"

def get_count(count_name):
    """Get a specific count by name"""
    try:
        counts_data = load_counts()
        return counts_data.get(count_name)
    except Exception as e:
        return None

def update_count_item(count_name, product_name, actual_qty, notes=""):
    """Update an item in a count"""
    try:
        counts_data = load_counts()
        
        if count_name not in counts_data:
            return False, f"Count '{count_name}' not found!"
        
        count = counts_data[count_name]
        
        # Find and update the item
        for item in count['items']:
            if item['product_name'] == product_name:
                item['actual_qty'] = actual_qty
                if notes:
                    item['notes'] = notes
                break
        
        if save_counts(counts_data):
            return True, "Count item updated successfully!"
        else:
            return False, "Error saving count data."
    except Exception as e:
        return False, f"Error updating count item: {e}"

def auto_save_count_item(count_name, product_name, actual_qty, previous_qty=None):
    """Auto-save count item with change detection"""
    try:
        # Only save if the value has actually changed
        if previous_qty is None or actual_qty != previous_qty:
            success, message = update_count_item(count_name, product_name, actual_qty, "")
            return success, message
        else:
            return True, "No change detected"
    except Exception as e:
        return False, f"Error auto-saving count item: {e}"

def get_count_items_by_location(count_name):
    """Get count items organized by location for sequential counting"""
    try:
        count = get_count(count_name)
        if not count:
            return {}
        
        items = count['items']
        
        # Group items by location
        location_groups = {}
        for item in items:
            location = item['location']
            if location not in location_groups:
                location_groups[location] = []
            location_groups[location].append(item)
        
        # Sort locations for consistent order
        sorted_locations = sorted(location_groups.keys())
        
        return {
            'sorted_locations': sorted_locations,
            'location_groups': location_groups,
            'all_items': items
        }
    except Exception as e:
        return {}

def complete_count(count_name):
    """Complete a count and move to history"""
    try:
        counts_data = load_counts()
        history_data = load_count_history()
        
        if count_name not in counts_data:
            return False, f"Count '{count_name}' not found!"
        
        count = counts_data[count_name]
        count['status'] = 'completed'
        count['completed_date'] = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        
        # Calculate variances
        for item in count['items']:
            if item['actual_qty'] is not None:
                expected = item['expected_qty']
                actual = item['actual_qty']
                variance = actual - expected
                variance_percent = (variance / expected * 100) if expected > 0 else 0
                
                item['variance'] = variance
                item['variance_percent'] = variance_percent
        
        # Move to history
        history_data.append(count)
        
        # Remove from active counts
        del counts_data[count_name]
        
        if save_counts(counts_data) and save_count_history(history_data):
            return True, f"Count '{count_name}' completed successfully!"
        else:
            return False, "Error saving count data."
    except Exception as e:
        return False, f"Error completing count: {e}"

def delete_count(count_name):
    """Delete a count"""
    try:
        counts_data = load_counts()
        
        if count_name not in counts_data:
            return False, f"Count '{count_name}' not found!"
        
        del counts_data[count_name]
        
        if save_counts(counts_data):
            return True, f"Count '{count_name}' deleted successfully!"
        else:
            return False, "Error saving count data."
    except Exception as e:
        return False, f"Error deleting count: {e}"

def get_count_summary(count_name):
    """Get summary statistics for a count"""
    try:
        count = get_count(count_name)
        if not count:
            return None
        
        items = count['items']
        total_items = len(items)
        counted_items = len([item for item in items if item['actual_qty'] is not None])
        
        # Calculate variances
        variances = []
        total_variance = 0
        high_variance_items = []
        
        for item in items:
            if item['actual_qty'] is not None:
                expected = item['expected_qty']
                actual = item['actual_qty']
                variance = actual - expected
                variance_percent = (variance / expected * 100) if expected > 0 else 0
                
                variances.append(variance)
                total_variance += abs(variance)
                
                if abs(variance_percent) > 10:  # High variance threshold
                    high_variance_items.append(item)
        
        # Calculate accuracy
        accuracy = (counted_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'total_items': total_items,
            'counted_items': counted_items,
            'total_variance': total_variance,
            'accuracy_percent': accuracy,
            'high_variance_items': high_variance_items,
            'status': count['status']
        }
    except Exception as e:
        return None

def export_count_to_csv(count_name):
    """Export count data to CSV"""
    try:
        count = get_count(count_name)
        if not count:
            return False, f"Count '{count_name}' not found!"
        
        # Create DataFrame
        data = []
        for item in count['items']:
            data.append({
                'Product Name': item['product_name'],
                'SKU': item['sku'],
                'Expected Qty': item['expected_qty'],
                'Actual Qty': item['actual_qty'] if item['actual_qty'] is not None else '',
                'Unit': item['unit'],
                'Location': item['location'],
                'Current Price': item['current_price'],
                'Variance': item.get('variance', ''),
                'Variance %': item.get('variance_percent', ''),
                'Notes': item['notes']
            })
        
        df = pd.DataFrame(data)
        
        # Save to CSV
        filename = f"data/count_{count_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        return True, f"Count exported to {filename}"
    except Exception as e:
        return False, f"Error exporting count: {e}"

def get_count_csv_data(count_name):
    """Get count data as CSV string for download"""
    try:
        count = get_count(count_name)
        if not count:
            return None, f"Count '{count_name}' not found!"
        
        # Create DataFrame
        data = []
        for item in count['items']:
            data.append({
                'Product Name': item['product_name'],
                'SKU': item['sku'],
                'Expected Qty': item['expected_qty'],
                'Actual Qty': item['actual_qty'] if item['actual_qty'] is not None else '',
                'Unit': item['unit'],
                'Location': item['location'],
                'Current Price': item['current_price'],
                'Variance': item.get('variance', ''),
                'Variance %': item.get('variance_percent', ''),
                'Notes': item['notes']
            })
        
        df = pd.DataFrame(data)
        
        # Convert to CSV string
        csv_data = df.to_csv(index=False)
        
        return csv_data, f"count_{count_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
    except Exception as e:
        return None, f"Error generating CSV data: {e}"
