import pandas as pd
from datetime import datetime
import json
from config import config

# Import shared functions
from utils.shared_functions import (
    get_text, load_products, format_currency, format_currency_small,
    load_json_file, save_json_file, get_available_locations
)

# Language translations for summary-specific text
SUMMARY_TRANSLATIONS = {
    "en": {
        "page_title": "📊 Inventory Summary",
        "page_caption": "View comprehensive inventory summaries and financial analysis",
        "summary_by_location": "Summary by Location",
        "total_counted": "Total Counted",
        "total_value": "Total Value",
        "items_counted": "Items Counted",
        "variance_analysis": "Variance Analysis",
        "high_variance_items": "High Variance Items",
        "location_summary": "Location Summary",
        "product_details": "Product Details",
        "expected_qty": "Expected Qty",
        "actual_qty": "Actual Qty",
        "variance": "Variance",
        "variance_percent": "Variance %",
        "unit_value": "Unit Value",
        "total_value": "Total Value",
        "count_date": "Count Date",
        "count_name": "Count Name",
        "status": "Status",
        "progress": "Progress",
        "accuracy": "Accuracy",
        "export_summary": "Export Summary",
        "no_data": "No data available",
        "loading": "Loading summary data...",
        "error_loading": "Error loading summary data",
        "summary_generated": "Summary generated successfully",
        "export_success": "Summary exported successfully",
        "export_error": "Error exporting summary"
    },
    "es": {
        "page_title": "📊 Resumen de Inventario",
        "page_caption": "Ver resúmenes completos de inventario y análisis financiero",
        "summary_by_location": "Resumen por Ubicación",
        "total_counted": "Total Contado",
        "total_value": "Valor Total",
        "items_counted": "Artículos Contados",
        "variance_analysis": "Análisis de Varianza",
        "high_variance_items": "Artículos con Alta Varianza",
        "location_summary": "Resumen de Ubicación",
        "product_details": "Detalles del Producto",
        "expected_qty": "Cantidad Esperada",
        "actual_qty": "Cantidad Real",
        "variance": "Varianza",
        "variance_percent": "Varianza %",
        "unit_value": "Valor Unitario",
        "total_value": "Valor Total",
        "count_date": "Fecha del Conteo",
        "count_name": "Nombre del Conteo",
        "status": "Estado",
        "progress": "Progreso",
        "accuracy": "Precisión",
        "export_summary": "Exportar Resumen",
        "no_data": "No hay datos disponibles",
        "loading": "Cargando datos del resumen...",
        "error_loading": "Error cargando datos del resumen",
        "summary_generated": "Resumen generado exitosamente",
        "export_success": "Resumen exportado exitosamente",
        "export_error": "Error exportando resumen"
    }
}

def get_summary_text(key, lang="en", **kwargs):
    """Get translated text for summary-specific keys"""
    if lang not in SUMMARY_TRANSLATIONS:
        lang = "en"
    text = SUMMARY_TRANSLATIONS[lang].get(key, key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text

def get_count_summary_by_location(count_name):
    """Get comprehensive summary of a count organized by location"""
    try:
        from modules.inventory_engine import get_count, get_count_summary
        
        count = get_count(count_name)
        if not count:
            return None
        
        summary = get_count_summary(count_name)
        if not summary:
            return None
        
        # Load products for pricing information
        products_df = load_products()
        
        # Group items by location
        location_summaries = {}
        total_counted_value = 0
        total_expected_value = 0
        
        for item in count['items']:
            location = item['location']
            
            if location not in location_summaries:
                location_summaries[location] = {
                    'items': [],
                    'total_counted_qty': 0,
                    'total_expected_qty': 0,
                    'total_counted_value': 0,
                    'total_expected_value': 0,
                    'items_counted': 0,
                    'total_items': 0
                }
            
            # Get product pricing
            product_info = products_df[products_df['Product Name'] == item['product_name']]
            unit_price = 0
            if not product_info.empty:
                unit_price = product_info.iloc[0]['Current Price per Unit']
            
            # Calculate values
            expected_value = item['expected_qty'] * unit_price
            actual_value = (item['actual_qty'] or 0) * unit_price
            
            # Create item summary
            item_summary = {
                'product_name': item['product_name'],
                'sku': item['sku'],
                'expected_qty': item['expected_qty'],
                'actual_qty': item['actual_qty'],
                'unit': item['unit'],
                'unit_price': unit_price,
                'expected_value': expected_value,
                'actual_value': actual_value,
                'variance': (item['actual_qty'] or 0) - item['expected_qty'],
                'variance_percent': ((item['actual_qty'] or 0) - item['expected_qty']) / item['expected_qty'] * 100 if item['expected_qty'] > 0 else 0,
                'is_counted': item['actual_qty'] is not None
            }
            
            location_summaries[location]['items'].append(item_summary)
            location_summaries[location]['total_items'] += 1
            
            if item['actual_qty'] is not None:
                location_summaries[location]['items_counted'] += 1
                location_summaries[location]['total_counted_qty'] += item['actual_qty']
                location_summaries[location]['total_counted_value'] += actual_value
            
            location_summaries[location]['total_expected_qty'] += item['expected_qty']
            location_summaries[location]['total_expected_value'] += expected_value
            
            total_counted_value += actual_value
            total_expected_value += expected_value
        
        # Sort locations
        sorted_locations = sorted(location_summaries.keys())
        
        return {
            'count_name': count['count_name'],
            'created_date': count['created_date'],
            'status': count['status'],
            'location_summaries': location_summaries,
            'sorted_locations': sorted_locations,
            'total_counted_value': total_counted_value,
            'total_expected_value': total_expected_value,
            'overall_summary': summary
        }
        
    except Exception as e:
        return None

def get_all_counts_summary():
    """Get summary of all active and completed counts"""
    try:
        from modules.inventory_engine import load_counts, load_count_history
        
        counts_data = load_counts()
        history_data = load_count_history()
        
        all_counts = []
        
        # Add active counts
        for count_name, count in counts_data.items():
            summary = get_count_summary_by_location(count_name)
            if summary:
                summary['is_active'] = True
                all_counts.append(summary)
        
        # Add completed counts
        for count in history_data:
            if isinstance(count, dict) and 'count_name' in count:
                summary = get_count_summary_by_location(count['count_name'])
                if summary:
                    summary['is_active'] = False
                    all_counts.append(summary)
        
        # Sort by date (newest first)
        all_counts.sort(key=lambda x: x['created_date'], reverse=True)
        
        return all_counts
        
    except Exception as e:
        return []

def export_summary_to_csv(count_name):
    """Export count summary to CSV with location breakdown"""
    try:
        summary = get_count_summary_by_location(count_name)
        if not summary:
            return False, "Count not found or no data available"
        
        # Create detailed CSV data
        csv_data = []
        
        for location in summary['sorted_locations']:
            location_data = summary['location_summaries'][location]
            
            for item in location_data['items']:
                csv_data.append({
                    'Count Name': summary['count_name'],
                    'Location': location,
                    'Product Name': item['product_name'],
                    'SKU': item['sku'],
                    'Expected Qty': item['expected_qty'],
                    'Actual Qty': item['actual_qty'] if item['actual_qty'] is not None else '',
                    'Unit': item['unit'],
                    'Unit Price': item['unit_price'],
                    'Expected Value': item['expected_value'],
                    'Actual Value': item['actual_value'],
                    'Variance': item['variance'],
                    'Variance %': item['variance_percent'],
                    'Counted': 'Yes' if item['is_counted'] else 'No'
                })
        
        df = pd.DataFrame(csv_data)

        # Save to CSV
        filename = config.DATA_DIR / f"summary_{count_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        df.to_csv(filename, index=False)
        
        return True, f"Summary exported to {filename}"
        
    except Exception as e:
        return False, f"Error exporting summary: {e}"

def get_summary_csv_data(count_name):
    """Get summary data as CSV string for download"""
    try:
        summary = get_count_summary_by_location(count_name)
        if not summary:
            return None, "Count not found or no data available"
        
        # Create detailed CSV data
        csv_data = []
        
        for location in summary['sorted_locations']:
            location_data = summary['location_summaries'][location]
            
            for item in location_data['items']:
                csv_data.append({
                    'Count Name': summary['count_name'],
                    'Location': location,
                    'Product Name': item['product_name'],
                    'SKU': item['sku'],
                    'Expected Qty': item['expected_qty'],
                    'Actual Qty': item['actual_qty'] if item['actual_qty'] is not None else '',
                    'Unit': item['unit'],
                    'Unit Price': item['unit_price'],
                    'Expected Value': item['expected_value'],
                    'Actual Value': item['actual_value'],
                    'Variance': item['variance'],
                    'Variance %': item['variance_percent'],
                    'Counted': 'Yes' if item['is_counted'] else 'No'
                })
        
        df = pd.DataFrame(csv_data)
        
        # Convert to CSV string
        csv_string = df.to_csv(index=False)
        
        return csv_string, f"summary_{count_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
    except Exception as e:
        return None, f"Error generating CSV data: {e}"

def get_summary_statistics():
    """Get overall summary statistics across all counts"""
    try:
        all_counts = get_all_counts_summary()
        
        if not all_counts:
            return None
        
        total_counts = len(all_counts)
        active_counts = len([c for c in all_counts if c['is_active']])
        completed_counts = total_counts - active_counts
        
        total_value_all_counts = sum(c['total_counted_value'] for c in all_counts)
        avg_count_value = total_value_all_counts / total_counts if total_counts > 0 else 0
        
        return {
            'total_counts': total_counts,
            'active_counts': active_counts,
            'completed_counts': completed_counts,
            'total_value_all_counts': total_value_all_counts,
            'avg_count_value': avg_count_value
        }
        
    except Exception as e:
        return None 