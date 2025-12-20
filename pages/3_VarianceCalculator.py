import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Import modules
from modules.variance_engine import (
    get_variance_text, load_recipes, load_products, load_variance_history,
    analyze_usage_variance, get_category_variance_analysis, get_high_variance_items,
    save_variance_analysis, get_variance_csv_data, get_variance_summary_statistics,
    calculate_theoretical_cost, calculate_actual_cost, calculate_variance
)
from utils.shared_functions import format_currency, format_currency_small

def main():
    """Variance Calculator page - Analyze cost variances between expected and actual usage"""
    
    st.header(get_variance_text("page_title"))
    st.markdown(get_variance_text("page_caption"))
    
    # Load data
    recipes = load_recipes()
    products_df = load_products()
    history_data = load_variance_history()
    
    if products_df.empty:
        st.warning("No products found. Please add products in the Product Database first.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("📊 Variance Analysis")
    
    # Main navigation
    page_options = [
        "Usage Variance Analysis",
        "Recipe Variance Analysis", 
        "Category Analysis",
        "High Variance Items",
        "Variance History",
        "Export & Reports"
    ]
    
    selected_page = st.sidebar.selectbox(
        "Select Analysis Type:",
        page_options
    )
    
    # ===============================================================================
    # USAGE VARIANCE ANALYSIS
    # ===============================================================================
    if selected_page == "Usage Variance Analysis":
        st.subheader("📊 Usage Variance Analysis")
        st.markdown("Compare expected vs actual usage to identify variances and their financial impact.")
        
        # Input section
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**Expected Usage Data:**")
            st.info("Enter expected usage quantities for each product.")
            
            # Expected usage input
            expected_usage = {}
            expected_products = st.multiselect(
                "Select products for expected usage:",
                options=products_df['Product Name'].tolist(),
                help="Choose products to track expected usage"
            )
            
            for product in expected_products:
                expected_qty = st.number_input(
                    f"Expected quantity for {product}:",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key=f"expected_{product}"
                )
                expected_usage[product] = expected_qty
        
        with col2:
            st.markdown("**Actual Usage Data:**")
            st.info("Enter actual usage quantities for each product.")
            
            # Actual usage input
            actual_usage = {}
            actual_products = st.multiselect(
                "Select products for actual usage:",
                options=products_df['Product Name'].tolist(),
                help="Choose products to track actual usage"
            )
            
            for product in actual_products:
                actual_qty = st.number_input(
                    f"Actual quantity for {product}:",
                    min_value=0.0,
                    value=0.0,
                    step=0.1,
                    key=f"actual_{product}"
                )
                actual_usage[product] = actual_qty
        
        # Analysis controls
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            analysis_name = st.text_input(
                "Analysis Name:",
                placeholder="e.g., Weekly Variance Analysis",
                help="Enter a name for this variance analysis"
            )
        
        with col2:
            time_period = st.text_input(
                "Time Period:",
                placeholder="e.g., Week of July 14",
                help="Enter the time period for this analysis"
            )
        
        with col3:
            variance_threshold = st.number_input(
                "High Variance Threshold (%):",
                min_value=1,
                max_value=50,
                value=10,
                help="Percentage threshold for high variance items"
            )
        
        # Calculate variance button
        if st.button("📊 Calculate Variance", type="primary"):
            if not expected_usage or not actual_usage:
                st.error("Please enter both expected and actual usage data.")
            elif not analysis_name:
                st.error("Please enter an analysis name.")
            else:
                # Perform variance analysis
                analysis_data = analyze_usage_variance(expected_usage, actual_usage, products_df)
                
                if analysis_data:
                    # Store in session state for display
                    st.session_state.variance_analysis = analysis_data
                    st.session_state.analysis_name = analysis_name
                    st.session_state.time_period = time_period
                    st.session_state.variance_threshold = variance_threshold
                    
                    st.success("✅ Variance analysis completed!")
                    st.rerun()
                else:
                    st.error("Error performing variance analysis.")
        
        # Display results if available
        if 'variance_analysis' in st.session_state:
            display_variance_results(st.session_state.variance_analysis)
    
    # ===============================================================================
    # RECIPE VARIANCE ANALYSIS
    # ===============================================================================
    elif selected_page == "Recipe Variance Analysis":
        st.subheader("📋 Recipe Variance Analysis")
        st.markdown("Compare theoretical vs actual recipe costs.")
        
        if not recipes:
            st.info("No recipes found. Create recipes in the Recipe Builder first.")
            return
        
        # Recipe selection
        recipe_name = st.selectbox(
            "Select Recipe:",
            options=list(recipes.keys())
        )
        
        if recipe_name:
            recipe = recipes[recipe_name]
            
            # Display theoretical ingredients
            st.markdown("**Theoretical Recipe:**")
            theoretical_cost, theoretical_ingredients = calculate_theoretical_cost(
                recipe_name, recipes, products_df
            )
            
            col1, col2 = st.columns(2)
            with col1:
                st.metric("Theoretical Cost", format_currency(theoretical_cost))
                st.metric("Ingredients", len(theoretical_ingredients))
            
            with col2:
                st.markdown("**Theoretical Ingredients:**")
                for ingredient in theoretical_ingredients:
                    st.write(f"• {ingredient['product_name']}: {ingredient['quantity']} {ingredient['unit']} (${ingredient['cost']:.2f})")
            
            st.markdown("---")
            
            # Actual ingredients input
            st.markdown("**Actual Ingredients Used:**")
            st.info("Enter the actual quantities used for this recipe.")
            
            actual_ingredients = []
            for ingredient in theoretical_ingredients:
                col1, col2 = st.columns([2, 1])
                
                with col1:
                    st.write(f"**{ingredient['product_name']}** (Expected: {ingredient['quantity']} {ingredient['unit']})")
                
                with col2:
                    actual_qty = st.number_input(
                        f"Actual {ingredient['unit']}:",
                        min_value=0.0,
                        value=float(ingredient['quantity']),
                        step=0.1,
                        key=f"actual_recipe_{ingredient['product_name']}"
                    )
                    
                    actual_ingredients.append({
                        'product_name': ingredient['product_name'],
                        'quantity': actual_qty,
                        'unit': ingredient['unit']
                    })
            
            # Calculate recipe variance
            if st.button("📊 Calculate Recipe Variance", type="primary"):
                actual_cost, actual_ingredient_costs = calculate_actual_cost(actual_ingredients, products_df)
                variance, variance_percent = calculate_variance(theoretical_cost, actual_cost)
                
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Theoretical Cost", format_currency(theoretical_cost))
                with col2:
                    st.metric("Actual Cost", format_currency(actual_cost))
                with col3:
                    st.metric("Variance", format_currency(variance))
                with col4:
                    st.metric("Variance %", f"{variance_percent:+.1f}%")
                
                # Variance status
                if variance > 0:
                    st.warning("⚠️ Over budget - Actual cost higher than theoretical")
                elif variance < 0:
                    st.success("✅ Under budget - Actual cost lower than theoretical")
                else:
                    st.info("✅ On budget - Actual cost matches theoretical")
    
    # ===============================================================================
    # CATEGORY ANALYSIS
    # ===============================================================================
    elif selected_page == "Category Analysis":
        st.subheader("📊 Category Variance Analysis")
        
        if 'variance_analysis' not in st.session_state:
            st.info("Please run a variance analysis first to view category breakdown.")
            return
        
        analysis_data = st.session_state.variance_analysis
        category_analysis = get_category_variance_analysis(analysis_data['variance_data'])
        
        if category_analysis:
            st.markdown("**Variance by Product Category:**")
            
            for category, data in category_analysis.items():
                with st.expander(f"📁 {category} ({data['item_count']} items)"):
                    col1, col2, col3, col4 = st.columns(4)
                    
                    with col1:
                        st.metric("Expected Cost", format_currency(data['total_expected_cost']))
                    with col2:
                        st.metric("Actual Cost", format_currency(data['total_actual_cost']))
                    with col3:
                        st.metric("Variance", format_currency(data['total_variance']))
                    with col4:
                        st.metric("Variance %", f"{data['variance_percent']:+.1f}%")
                    
                    # Category items table
                    st.markdown("**Items in Category:**")
                    category_items = []
                    for item in data['items']:
                        category_items.append({
                            'Product': item['product_name'],
                            'Expected': f"{item['expected_qty']:.1f} {item['unit']}",
                            'Actual': f"{item['actual_qty']:.1f} {item['unit']}",
                            'Expected Cost': format_currency(item['expected_cost']),
                            'Actual Cost': format_currency(item['actual_cost']),
                            'Variance': format_currency(item['variance']),
                            'Variance %': f"{item['variance_percent']:+.1f}%",
                            'Status': "🔴 Over" if item['variance'] > 0 else "🟢 Under" if item['variance'] < 0 else "🟡 On Target"
                        })
                    
                    df = pd.DataFrame(category_items)
                    st.dataframe(df, width='stretch')
        else:
            st.info("No category data available.")
    
    # ===============================================================================
    # HIGH VARIANCE ITEMS
    # ===============================================================================
    elif selected_page == "High Variance Items":
        st.subheader("⚠️ High Variance Items")
        
        if 'variance_analysis' not in st.session_state:
            st.info("Please run a variance analysis first to identify high variance items.")
            return
        
        analysis_data = st.session_state.variance_analysis
        threshold = st.session_state.get('variance_threshold', 10)
        
        high_variance_items = get_high_variance_items(analysis_data['variance_data'], threshold)
        
        if high_variance_items:
            st.markdown(f"**Items with variance above {threshold}%:**")
            
            # Summary metrics
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("High Variance Items", len(high_variance_items))
            with col2:
                total_high_variance_cost = sum(item['variance'] for item in high_variance_items)
                st.metric("Total Variance Cost", format_currency(total_high_variance_cost))
            with col3:
                avg_variance_percent = sum(abs(item['variance_percent']) for item in high_variance_items) / len(high_variance_items)
                st.metric("Average Variance %", f"{avg_variance_percent:.1f}%")
            
            # High variance items table
            st.markdown("**Detailed Breakdown:**")
            high_variance_data = []
            
            for item in high_variance_items:
                high_variance_data.append({
                    'Product': item['product_name'],
                    'Category': item['category'],
                    'Expected': f"{item['expected_qty']:.1f} {item['unit']}",
                    'Actual': f"{item['actual_qty']:.1f} {item['unit']}",
                    'Expected Cost': format_currency(item['expected_cost']),
                    'Actual Cost': format_currency(item['actual_cost']),
                    'Variance': format_currency(item['variance']),
                    'Variance %': f"{item['variance_percent']:+.1f}%",
                    'Status': "🔴 Over Budget" if item['variance'] > 0 else "🟢 Under Budget"
                })
            
            df = pd.DataFrame(high_variance_data)
            st.dataframe(df, width='stretch')
            
            # Recommendations
            st.markdown("**📋 Recommendations:**")
            over_budget_items = [item for item in high_variance_items if item['variance'] > 0]
            under_budget_items = [item for item in high_variance_items if item['variance'] < 0]
            
            if over_budget_items:
                st.warning("**Over Budget Items:**")
                for item in over_budget_items[:3]:  # Top 3
                    st.write(f"• **{item['product_name']}**: {item['variance_percent']:+.1f}% over budget")
                    st.write(f"  - Consider portion control, waste reduction, or price negotiation")
            
            if under_budget_items:
                st.success("**Under Budget Items:**")
                for item in under_budget_items[:3]:  # Top 3
                    st.write(f"• **{item['product_name']}**: {item['variance_percent']:+.1f}% under budget")
                    st.write(f"  - Verify quality standards are maintained")
        else:
            st.success(f"✅ No items found with variance above {threshold}%")
    
    # ===============================================================================
    # VARIANCE HISTORY
    # ===============================================================================
    elif selected_page == "Variance History":
        st.subheader("📚 Variance History")
        
        if not history_data:
            st.info("No variance analysis history found. Run analyses to build history.")
            return
        
        # Display history
        for analysis in history_data:
            with st.expander(f"📊 {analysis['analysis_name']} - {analysis['time_period']}"):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**Date:** {analysis['created_date']}")
                    st.write(f"**Period:** {analysis['time_period']}")
                
                with col2:
                    st.metric("Expected Cost", format_currency(analysis['total_expected_cost']))
                    st.metric("Actual Cost", format_currency(analysis['total_actual_cost']))
                
                with col3:
                    st.metric("Total Variance", format_currency(analysis['total_variance']))
                    st.metric("Variance %", f"{analysis['total_variance_percent']:+.1f}%")
                
                with col4:
                    high_variance_count = len(analysis['high_variance_items'])
                    st.metric("High Variance Items", high_variance_count)
                    
                    if analysis['total_variance'] > 0:
                        st.warning("⚠️ Over Budget")
                    elif analysis['total_variance'] < 0:
                        st.success("✅ Under Budget")
                    else:
                        st.info("✅ On Budget")
                
                # Quick summary
                st.markdown("**Summary:**")
                st.write(f"• **Items analyzed:** {len(analysis['variance_data'])}")
                st.write(f"• **Categories:** {len(analysis['category_analysis'])}")
                st.write(f"• **High variance items:** {high_variance_count}")
    
    # ===============================================================================
    # EXPORT & REPORTS
    # ===============================================================================
    elif selected_page == "Export & Reports":
        st.subheader("📤 Export & Reports")
        
        if 'variance_analysis' not in st.session_state:
            st.info("Please run a variance analysis first to export reports.")
            return
        
        analysis_data = st.session_state.variance_analysis
        analysis_name = st.session_state.analysis_name
        
        # Export options
        col1, col2 = st.columns(2)
        
        with col1:
            st.markdown("**📊 Export Variance Report:**")
            
            # Get CSV data for download
            csv_data, filename = get_variance_csv_data(analysis_data, analysis_name)
            if csv_data:
                st.download_button(
                    label="📥 Download Variance CSV",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    help="Download detailed variance analysis as CSV"
                )
            else:
                st.error("Error generating CSV data")
        
        with col2:
            st.markdown("**💾 Save Analysis:**")
            
            time_period = st.text_input(
                "Time Period:",
                value=st.session_state.get('time_period', ''),
                help="Enter time period for this analysis"
            )
            
            if st.button("💾 Save to History", type="primary"):
                success, message = save_variance_analysis(analysis_data, analysis_name, time_period)
                if success:
                    st.success(message)
                else:
                    st.error(message)
        
        # Summary statistics
        st.markdown("---")
        st.markdown("**📈 Summary Statistics:**")
        
        stats = get_variance_summary_statistics(analysis_data)
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            
            with col1:
                st.metric("Total Items", stats['total_items'])
                st.metric("Accuracy Rate", f"{stats['accuracy_rate']:.1f}%")
            
            with col2:
                st.metric("Over Budget Items", stats['positive_variance_items'])
                st.metric("Under Budget Items", stats['negative_variance_items'])
            
            with col3:
                st.metric("High Variance Items", stats['high_variance_items_count'])
                st.metric("On Target Items", stats['no_variance_items'])
            
            with col4:
                st.metric("Total Expected", format_currency(stats['total_expected_cost']))
                st.metric("Total Actual", format_currency(stats['total_actual_cost']))

def display_variance_results(analysis_data):
    """Display variance analysis results"""
    st.markdown("---")
    st.markdown("**📊 Variance Analysis Results:**")
    
    # Summary metrics
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Expected Cost", format_currency(analysis_data['total_expected_cost']))
    with col2:
        st.metric("Actual Cost", format_currency(analysis_data['total_actual_cost']))
    with col3:
        st.metric("Total Variance", format_currency(analysis_data['total_variance']))
    with col4:
        st.metric("Variance %", f"{analysis_data['total_variance_percent']:+.1f}%")
    
    # Variance status
    if analysis_data['total_variance'] > 0:
        st.warning("⚠️ Overall over budget - Actual costs higher than expected")
    elif analysis_data['total_variance'] < 0:
        st.success("✅ Overall under budget - Actual costs lower than expected")
    else:
        st.info("✅ On budget - Actual costs match expected")
    
    # Detailed results table
    st.markdown("**📋 Detailed Results:**")
    
    variance_data = analysis_data['variance_data']
    if variance_data:
        # Create DataFrame for display
        display_data = []
        for item in variance_data:
            display_data.append({
                'Product': item['product_name'],
                'Category': item['category'],
                'Expected': f"{item['expected_qty']:.1f} {item['unit']}",
                'Actual': f"{item['actual_qty']:.1f} {item['unit']}",
                'Expected Cost': format_currency(item['expected_cost']),
                'Actual Cost': format_currency(item['actual_cost']),
                'Variance': format_currency(item['variance']),
                'Variance %': f"{item['variance_percent']:+.1f}%",
                'Status': "🔴 Over" if item['variance'] > 0 else "🟢 Under" if item['variance'] < 0 else "🟡 On Target"
            })
        
        df = pd.DataFrame(display_data)
        st.dataframe(df, width='stretch')
    else:
        st.info("No variance data to display.")

if __name__ == "__main__":
    main()
