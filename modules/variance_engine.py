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

# Language translations for variance-specific text
VARIANCE_TRANSLATIONS = {
    "en": {
        "page_title": "📊 Variance Calculator",
        "page_caption": "Calculate and analyze cost variances between expected and actual usage",
        "theoretical_cost": "Theoretical Cost",
        "actual_cost": "Actual Cost",
        "variance": "Variance",
        "variance_percentage": "Variance %",
        "recipe": "Recipe",
        "ingredients": "Ingredients",
        "theoretical_ingredients": "Theoretical Ingredients",
        "actual_ingredients": "Actual Ingredients",
        "add_ingredient": "Add Ingredient",
        "calculate_variance": "Calculate Variance",
        "variance_results": "Variance Results",
        "positive_variance": "Positive Variance (Over Budget)",
        "negative_variance": "Negative Variance (Under Budget)",
        "no_variance": "No Variance",
        "total_theoretical": "Total Theoretical Cost",
        "total_actual": "Total Actual Cost",
        "total_variance": "Total Variance",
        "variance_analysis": "Variance Analysis",
        "cost_breakdown": "Cost Breakdown",
        # New variance-specific translations
        "usage_tracking": "Usage Tracking",
        "expected_usage": "Expected Usage",
        "actual_usage": "Actual Usage",
        "usage_variance": "Usage Variance",
        "financial_impact": "Financial Impact",
        "category_analysis": "Category Analysis",
        "high_variance_items": "High Variance Items",
        "variance_trends": "Variance Trends",
        "time_period": "Time Period",
        "product_category": "Product Category",
        "variance_threshold": "Variance Threshold",
        "export_variance": "Export Variance Report",
        "variance_summary": "Variance Summary",
        "accuracy_rate": "Accuracy Rate",
        "cost_per_unit": "Cost per Unit",
        "total_quantity": "Total Quantity",
        "variance_reason": "Variance Reason",
        "corrective_action": "Corrective Action",
        "variance_history": "Variance History",
        "trend_analysis": "Trend Analysis",
        "seasonal_patterns": "Seasonal Patterns",
        "forecast_adjustment": "Forecast Adjustment",
        "waste_analysis": "Waste Analysis",
        "profit_impact": "Profit Impact",
        "variance_report": "Variance Report",
        "detailed_breakdown": "Detailed Breakdown",
        "summary_report": "Summary Report",
        "export_csv": "Export to CSV",
        "export_success": "Export successful",
        "export_error": "Export failed",
        "no_data": "No data available",
        "loading": "Loading variance data...",
        "error_loading": "Error loading variance data",
        "variance_calculated": "Variance calculated successfully",
        "high_variance_alert": "High variance detected",
        "variance_within_threshold": "Variance within acceptable range"
    },
    "es": {
        "page_title": "📊 Calculadora de Varianza",
        "page_caption": "Calcula y analiza varianzas de costos entre uso esperado y real",
        "theoretical_cost": "Costo Teórico",
        "actual_cost": "Costo Real",
        "variance": "Varianza",
        "variance_percentage": "Varianza %",
        "recipe": "Receta",
        "ingredients": "Ingredientes",
        "theoretical_ingredients": "Ingredientes Teóricos",
        "actual_ingredients": "Ingredientes Reales",
        "add_ingredient": "Agregar Ingrediente",
        "calculate_variance": "Calcular Varianza",
        "variance_results": "Resultados de Varianza",
        "positive_variance": "Varianza Positiva (Sobre Presupuesto)",
        "negative_variance": "Varianza Negativa (Bajo Presupuesto)",
        "no_variance": "Sin Varianza",
        "total_theoretical": "Costo Teórico Total",
        "total_actual": "Costo Real Total",
        "total_variance": "Varianza Total",
        "variance_analysis": "Análisis de Varianza",
        "cost_breakdown": "Desglose de Costos",
        # New variance-specific translations
        "usage_tracking": "Seguimiento de Uso",
        "expected_usage": "Uso Esperado",
        "actual_usage": "Uso Real",
        "usage_variance": "Varianza de Uso",
        "financial_impact": "Impacto Financiero",
        "category_analysis": "Análisis por Categoría",
        "high_variance_items": "Artículos con Alta Varianza",
        "variance_trends": "Tendencias de Varianza",
        "time_period": "Período de Tiempo",
        "product_category": "Categoría de Producto",
        "variance_threshold": "Umbral de Varianza",
        "export_variance": "Exportar Reporte de Varianza",
        "variance_summary": "Resumen de Varianza",
        "accuracy_rate": "Tasa de Precisión",
        "cost_per_unit": "Costo por Unidad",
        "total_quantity": "Cantidad Total",
        "variance_reason": "Razón de Varianza",
        "corrective_action": "Acción Correctiva",
        "variance_history": "Historial de Varianza",
        "trend_analysis": "Análisis de Tendencias",
        "seasonal_patterns": "Patrones Estacionales",
        "forecast_adjustment": "Ajuste de Pronóstico",
        "waste_analysis": "Análisis de Desperdicio",
        "profit_impact": "Impacto en Ganancias",
        "variance_report": "Reporte de Varianza",
        "detailed_breakdown": "Desglose Detallado",
        "summary_report": "Reporte Resumen",
        "export_csv": "Exportar a CSV",
        "export_success": "Exportación exitosa",
        "export_error": "Exportación fallida",
        "no_data": "No hay datos disponibles",
        "loading": "Cargando datos de varianza...",
        "error_loading": "Error cargando datos de varianza",
        "variance_calculated": "Varianza calculada exitosamente",
        "high_variance_alert": "Varianza alta detectada",
        "variance_within_threshold": "Varianza dentro del rango aceptable"
    }
}

def get_variance_text(key, lang="en", **kwargs):
    """Get translated text for variance-specific keys"""
    if lang not in VARIANCE_TRANSLATIONS:
        lang = "en"
    text = VARIANCE_TRANSLATIONS[lang].get(key, key)
    if text is None:
        text = key
    return text.format(**kwargs) if kwargs else text

# File paths
RECIPES_FILE = str(config.RECIPES_FILE)
PRODUCTS_FILE = str(config.PRODUCTS_FILE)
VARIANCE_HISTORY_FILE = str(config.VARIANCE_HISTORY_FILE)

def load_recipes():
    """Load recipes from JSON file"""
    try:
        if os.path.exists(RECIPES_FILE):
            with open(RECIPES_FILE, 'r') as f:
                return json.load(f)
        else:
            return {}
    except Exception as e:
        return {}

def load_products():
    """Load products from CSV file"""
    try:
        if os.path.exists(PRODUCTS_FILE):
            return pd.read_csv(PRODUCTS_FILE)
        else:
            return pd.DataFrame()
    except Exception as e:
        return pd.DataFrame()

def load_variance_history():
    """Load variance history from JSON file"""
    try:
        if os.path.exists(VARIANCE_HISTORY_FILE):
            with open(VARIANCE_HISTORY_FILE, 'r') as f:
                return json.load(f)
        else:
            return []
    except Exception as e:
        return []

def save_variance_history(history_data):
    """Save variance history to JSON file"""
    try:
        os.makedirs("data", exist_ok=True)
        with open(VARIANCE_HISTORY_FILE, 'w') as f:
            json.dump(history_data, f, indent=2)
        return True
    except Exception as e:
        return False

def calculate_theoretical_cost(recipe_name, recipes, products_df):
    """Calculate theoretical cost for a recipe"""
    if recipe_name not in recipes:
        return 0, []
    
    recipe = recipes[recipe_name]
    ingredients = recipe.get('ingredients', [])
    total_cost = 0
    ingredient_costs = []
    
    for ingredient in ingredients:
        product_name = ingredient['product_name']
        quantity = ingredient['quantity']
        unit = ingredient['unit']
        
        # Find matching product
        product_match = products_df[products_df['Product Name'] == product_name]
        
        if not product_match.empty:
            product = product_match.iloc[0]
            product_cost = product['Current Price per Unit']
            cost = quantity * product_cost
            
            ingredient_costs.append({
                'product_name': product_name,
                'quantity': quantity,
                'unit': unit,
                'cost': cost,
                'unit_price': product_cost
            })
            total_cost += cost
    
    return total_cost, ingredient_costs

def calculate_actual_cost(actual_ingredients, products_df):
    """Calculate actual cost based on actual ingredients used"""
    total_cost = 0
    ingredient_costs = []
    
    for ingredient in actual_ingredients:
        product_name = ingredient['product_name']
        quantity = ingredient['quantity']
        unit = ingredient['unit']
        
        # Find matching product
        product_match = products_df[products_df['Product Name'] == product_name]
        
        if not product_match.empty:
            product = product_match.iloc[0]
            product_cost = product['Current Price per Unit']
            cost = quantity * product_cost
            
            ingredient_costs.append({
                'product_name': product_name,
                'quantity': quantity,
                'unit': unit,
                'cost': cost,
                'unit_price': product_cost
            })
            total_cost += cost
    
    return total_cost, ingredient_costs

def calculate_variance(theoretical_cost, actual_cost):
    """Calculate variance between theoretical and actual costs"""
    variance = actual_cost - theoretical_cost
    variance_percentage = (variance / theoretical_cost * 100) if theoretical_cost != 0 else 0
    
    return variance, variance_percentage

def get_variance_status(variance):
    """Get variance status (positive, negative, or none)"""
    if variance > 0:
        return "positive"
    elif variance < 0:
        return "negative"
    else:
        return "none"

def analyze_usage_variance(expected_usage, actual_usage, products_df):
    """Analyze variance between expected and actual usage"""
    try:
        variance_data = []
        total_expected_cost = 0
        total_actual_cost = 0
        total_variance = 0
        
        for product_name in set(list(expected_usage.keys()) + list(actual_usage.keys())):
            expected_qty = expected_usage.get(product_name, 0)
            actual_qty = actual_usage.get(product_name, 0)
            
            # Find product info
            product_match = products_df[products_df['Product Name'] == product_name]
            if not product_match.empty:
                product = product_match.iloc[0]
                unit_price = product['Current Price per Unit']
                category = product.get('Category', 'Unknown')
                unit = product.get('Unit', 'units')
                
                # Calculate costs
                expected_cost = expected_qty * unit_price
                actual_cost = actual_qty * unit_price
                variance = actual_cost - expected_cost
                variance_percent = (variance / expected_cost * 100) if expected_cost > 0 else 0
                
                # Calculate quantity variance
                qty_variance = actual_qty - expected_qty
                qty_variance_percent = (qty_variance / expected_qty * 100) if expected_qty > 0 else 0
                
                variance_data.append({
                    'product_name': product_name,
                    'category': category,
                    'expected_qty': expected_qty,
                    'actual_qty': actual_qty,
                    'qty_variance': qty_variance,
                    'qty_variance_percent': qty_variance_percent,
                    'unit': unit,
                    'unit_price': unit_price,
                    'expected_cost': expected_cost,
                    'actual_cost': actual_cost,
                    'variance': variance,
                    'variance_percent': variance_percent,
                    'status': get_variance_status(variance)
                })
                
                total_expected_cost += expected_cost
                total_actual_cost += actual_cost
                total_variance += variance
        
        return {
            'variance_data': variance_data,
            'total_expected_cost': total_expected_cost,
            'total_actual_cost': total_actual_cost,
            'total_variance': total_variance,
            'total_variance_percent': (total_variance / total_expected_cost * 100) if total_expected_cost > 0 else 0
        }
    except Exception as e:
        return None

def get_category_variance_analysis(variance_data):
    """Analyze variance by product category"""
    try:
        category_analysis = {}
        
        for item in variance_data:
            category = item['category']
            
            if category not in category_analysis:
                category_analysis[category] = {
                    'items': [],
                    'total_expected_cost': 0,
                    'total_actual_cost': 0,
                    'total_variance': 0,
                    'item_count': 0
                }
            
            category_analysis[category]['items'].append(item)
            category_analysis[category]['total_expected_cost'] += item['expected_cost']
            category_analysis[category]['total_actual_cost'] += item['actual_cost']
            category_analysis[category]['total_variance'] += item['variance']
            category_analysis[category]['item_count'] += 1
        
        # Calculate percentages for each category
        for category in category_analysis:
            data = category_analysis[category]
            data['variance_percent'] = (data['total_variance'] / data['total_expected_cost'] * 100) if data['total_expected_cost'] > 0 else 0
            data['status'] = get_variance_status(data['total_variance'])
        
        return category_analysis
    except Exception as e:
        return {}

def get_high_variance_items(variance_data, threshold=10):
    """Get items with variance above threshold percentage"""
    try:
        high_variance = []
        
        for item in variance_data:
            if abs(item['variance_percent']) > threshold:
                high_variance.append(item)
        
        return sorted(high_variance, key=lambda x: abs(x['variance_percent']), reverse=True)
    except Exception as e:
        return []

def save_variance_analysis(analysis_data, analysis_name, time_period):
    """Save variance analysis to history"""
    try:
        history_data = load_variance_history()
        
        analysis_record = {
            'analysis_name': analysis_name,
            'time_period': time_period,
            'created_date': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'total_expected_cost': analysis_data['total_expected_cost'],
            'total_actual_cost': analysis_data['total_actual_cost'],
            'total_variance': analysis_data['total_variance'],
            'total_variance_percent': analysis_data['total_variance_percent'],
            'variance_data': analysis_data['variance_data'],
            'category_analysis': get_category_variance_analysis(analysis_data['variance_data']),
            'high_variance_items': get_high_variance_items(analysis_data['variance_data'])
        }
        
        history_data.append(analysis_record)
        
        if save_variance_history(history_data):
            return True, "Variance analysis saved successfully!"
        else:
            return False, "Error saving variance analysis."
    except Exception as e:
        return False, f"Error saving variance analysis: {e}"

def get_variance_csv_data(analysis_data, analysis_name):
    """Get variance analysis as CSV string for download"""
    try:
        variance_data = analysis_data['variance_data']
        
        # Create detailed CSV data
        csv_data = []
        
        for item in variance_data:
            csv_data.append({
                'Product Name': item['product_name'],
                'Category': item['category'],
                'Expected Qty': item['expected_qty'],
                'Actual Qty': item['actual_qty'],
                'Quantity Variance': item['qty_variance'],
                'Quantity Variance %': f"{item['qty_variance_percent']:.2f}%",
                'Unit': item['unit'],
                'Unit Price': item['unit_price'],
                'Expected Cost': item['expected_cost'],
                'Actual Cost': item['actual_cost'],
                'Cost Variance': item['variance'],
                'Cost Variance %': f"{item['variance_percent']:.2f}%",
                'Status': item['status']
            })
        
        df = pd.DataFrame(csv_data)
        csv_string = df.to_csv(index=False)
        
        return csv_string, f"variance_analysis_{analysis_name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.csv"
        
    except Exception as e:
        return None, f"Error generating CSV data: {e}"

def get_variance_summary_statistics(analysis_data):
    """Get summary statistics for variance analysis"""
    try:
        variance_data = analysis_data['variance_data']
        
        total_items = len(variance_data)
        positive_variance_items = len([item for item in variance_data if item['variance'] > 0])
        negative_variance_items = len([item for item in variance_data if item['variance'] < 0])
        no_variance_items = len([item for item in variance_data if item['variance'] == 0])
        
        high_variance_items = get_high_variance_items(variance_data)
        
        # Calculate accuracy rate (items within 5% variance)
        accurate_items = len([item for item in variance_data if abs(item['variance_percent']) <= 5])
        accuracy_rate = (accurate_items / total_items * 100) if total_items > 0 else 0
        
        return {
            'total_items': total_items,
            'positive_variance_items': positive_variance_items,
            'negative_variance_items': negative_variance_items,
            'no_variance_items': no_variance_items,
            'high_variance_items_count': len(high_variance_items),
            'accuracy_rate': accuracy_rate,
            'total_expected_cost': analysis_data['total_expected_cost'],
            'total_actual_cost': analysis_data['total_actual_cost'],
            'total_variance': analysis_data['total_variance'],
            'total_variance_percent': analysis_data['total_variance_percent']
        }
    except Exception as e:
        return None
