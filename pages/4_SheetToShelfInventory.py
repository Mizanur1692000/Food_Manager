import streamlit as st
import pandas as pd
from datetime import datetime
import json
from typing import Dict, List, Any, Optional

# Import modules
from modules.inventory_engine import (
    get_inventory_text, load_counts, load_count_history, create_new_count, 
    get_count, update_count_item, auto_save_count_item, get_count_items_by_location,
    complete_count, delete_count, get_count_summary, export_count_to_csv, get_count_csv_data, get_available_locations
)
from utils.shared_functions import load_products

def main():
    """Sheet-to-Shelf Inventory page - Conduct physical inventory counts"""
    
    st.header(get_inventory_text("sheet_to_shelf_title"))
    st.markdown(get_inventory_text("sheet_to_shelf_caption"))
    
    # Load data
    products_df = load_products()
    counts_data: Dict[str, Any] = load_counts()
    history_data: List[Dict[str, Any]] = load_count_history()
    
    if products_df.empty:
        st.warning("No products found. Please add products in the Product Database first.")
        return
    
    # Sidebar for navigation
    st.sidebar.title("📋 Count Management")
    
    # Main navigation
    page_options = [
        "Start New Count",
        "Continue Count", 
        "Count History",
        "Export & Analysis"
    ]
    
    # Initialize session state for page selection
    if 'sheet_to_shelf_page' not in st.session_state:
        st.session_state.sheet_to_shelf_page = "Start New Count"
    
    selected_page = st.sidebar.selectbox(
        "Select Action:",
        page_options,
        index=page_options.index(st.session_state.sheet_to_shelf_page)
    )
    
    # Update session state when selection changes
    if selected_page != st.session_state.sheet_to_shelf_page:
        st.session_state.sheet_to_shelf_page = selected_page
    
    # ===============================================================================
    # START NEW COUNT
    # ===============================================================================
    if selected_page == "Start New Count":
        st.subheader("🆕 Start New Count")
        
        col1, col2 = st.columns(2)
        
        with col1:
            count_name = st.text_input(
                "Count Name:",
                placeholder="e.g., Weekly Count - July 14",
                help="Enter a descriptive name for this count"
            )
            
            # Location filter
            locations = ["All Locations"] + get_available_locations(products_df)
            location_filter = st.selectbox(
                "Filter by Location:",
                locations,
                help="Select a specific location or count all locations"
            )
        
        with col2:
            st.markdown("**Count Preview:**")
            if count_name:
                filtered_products = products_df
                if location_filter != "All Locations":
                    filtered_products = products_df[products_df['Location'] == location_filter]
                
                st.metric("Products to Count", len(filtered_products))
                locations_series = pd.Series(filtered_products['Location'])
                locations_list = locations_series.dropna().unique().tolist()
                st.metric("Locations", len(locations_list))
        
        # Start count button
        if st.button("🚀 Start Count", type="primary"):
            if not count_name:
                st.error("Please enter a count name.")
            else:
                success, message = create_new_count(count_name, products_df, location_filter)
                if success:
                    st.success(message)
                    # Switch to Continue Count after successful creation
                    st.session_state.sheet_to_shelf_page = "Continue Count"
                    st.rerun()
                else:
                    st.error(message)
    
    # ===============================================================================
    # CONTINUE COUNT
    # ===============================================================================
    elif selected_page == "Continue Count":
        st.subheader("📝 Continue Count")
        
        if not counts_data:
            st.info("No active counts found. Start a new count to begin.")
        else:
            # Select count to continue
            count_names = list(counts_data.keys())
            selected_count = st.selectbox(
                "Select Count to Continue:",
                count_names
            )
            
            if selected_count:
                count = counts_data[selected_count]
                
                # Count summary
                summary = get_count_summary(selected_count)
                if summary:
                    col1, col2, col3, col4 = st.columns(4)
                    with col1:
                        st.metric("Total Items", summary['total_items'])
                    with col2:
                        st.metric("Counted Items", summary['counted_items'])
                    with col3:
                        st.metric("Progress", f"{summary['accuracy_percent']:.1f}%")
                    with col4:
                        st.metric("High Variance Items", len(summary['high_variance_items']))
                
                # Count details
                st.markdown("**Count Details:**")
                st.write(f"**Created:** {count['created_date']}")
                st.write(f"**Location Filter:** {count.get('location_filter', 'All Locations')}")
                st.write(f"**Status:** {count['status'].replace('_', ' ').title()}")
                
                # Count items
                st.markdown("**Count Items:**")
                
                # Filter options
                col1, col2 = st.columns(2)
                with col1:
                    show_counted = st.checkbox("Show counted items", value=True)
                with col2:
                    show_uncounted = st.checkbox("Show uncounted items", value=True)
                
                # Get items organized by location from engine
                location_data = get_count_items_by_location(selected_count)
                if not location_data:
                    st.error("Error loading count data.")
                    return
                
                # Filter items based on show/hide preferences
                display_items = []
                for item in location_data['all_items']:
                    is_counted = item['actual_qty'] is not None
                    if (is_counted and show_counted) or (not is_counted and show_uncounted):
                        display_items.append(item)
                
                # Filter location groups to only include display items
                filtered_location_groups = {}
                for location in location_data['sorted_locations']:
                    location_items = [item for item in location_data['location_groups'][location] 
                                   if item in display_items]
                    if location_items:  # Only include locations with items to display
                        filtered_location_groups[location] = location_items
                
                sorted_locations = list(filtered_location_groups.keys())
                
                if display_items:
                    # Display items grouped by location for sequential counting
                    for location in sorted_locations:
                        location_items = filtered_location_groups[location]
                        
                        # Location header
                        st.markdown(f"### 📍 {location} ({len(location_items)} items)")
                        
                        # Display items in this location
                        for i, item in enumerate(location_items):
                            # Find the original index for proper key generation
                            original_index = display_items.index(item)
                            
                            with st.expander(f"{item['product_name']} - {item['sku']}"):
                                col1, col2 = st.columns(2)
                                
                                with col1:
                                    st.write(f"**SKU:** {item['sku']}")
                                    st.write(f"**Expected:** {item['expected_qty']} {item['unit']}")
                                    st.write(f"**Location:** {item['location']}")
                                
                                with col2:
                                    # Track previous value for auto-save
                                    prev_key = f"prev_actual_{original_index}"
                                    if prev_key not in st.session_state:
                                        st.session_state[prev_key] = item['actual_qty']
                                    
                                    actual_qty = st.number_input(
                                        "Actual Quantity:",
                                        min_value=0.0,
                                        value=float(item['actual_qty']) if item['actual_qty'] is not None else 0.0,
                                        step=0.1,
                                        key=f"actual_{original_index}"
                                    )
                                    
                                    # Auto-save when value changes
                                    if actual_qty != st.session_state[prev_key]:
                                        success, message = auto_save_count_item(
                                            selected_count, 
                                            item['product_name'], 
                                            actual_qty,
                                            st.session_state[prev_key]
                                        )
                                        if success:
                                            st.success("✅ Auto-saved")
                                            st.session_state[prev_key] = actual_qty
                                        else:
                                            st.error("❌ Save failed")
                                    
                                    if item['actual_qty'] is not None:
                                        variance = actual_qty - item['expected_qty']
                                        variance_percent = (variance / item['expected_qty'] * 100) if item['expected_qty'] > 0 else 0
                                        
                                        st.write(f"**Variance:** {variance:+.1f}")
                                        st.write(f"**Variance %:** {variance_percent:+.1f}%")
                
                # Complete count
                st.markdown("---")
                col1, col2 = st.columns(2)
                
                with col1:
                    if st.button("✅ Complete Count", type="primary"):
                        success, message = complete_count(selected_count)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
                
                with col2:
                    if st.button("🗑️ Delete Count", type="secondary"):
                        success, message = delete_count(selected_count)
                        if success:
                            st.success(message)
                            st.rerun()
                        else:
                            st.error(message)
    
    # ===============================================================================
    # COUNT HISTORY
    # ===============================================================================
    elif selected_page == "Count History":
        st.subheader("📊 Count History")
        
        if not history_data:
            st.info("No completed counts found. Complete a count to see it here.")
        else:
            # Display history
            for count in history_data:
                count_name = count.get('count_name', 'Unknown') if isinstance(count, dict) else 'Unknown'
                completed_date = count.get('completed_date', 'Unknown') if isinstance(count, dict) else 'Unknown'
                
                with st.expander(f"{count_name} - {completed_date}"):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        created_date = count.get('created_date', 'Unknown') if isinstance(count, dict) else 'Unknown'
                        location_filter = count.get('location_filter', 'All Locations') if isinstance(count, dict) else 'All Locations'
                        st.write(f"**Created:** {created_date}")
                        st.write(f"**Completed:** {completed_date}")
                        st.write(f"**Location Filter:** {location_filter}")
                    
                    with col2:
                        # Calculate summary
                        items = count.get('items', []) if isinstance(count, dict) else []
                        total_items = len(items)
                        counted_items = 0
                        
                        # Calculate variances
                        total_variance = 0
                        high_variance_items = []
                        
                        for item in items:
                            if isinstance(item, dict) and item.get('actual_qty') is not None:
                                counted_items += 1
                                variance = abs(item.get('variance', 0))
                                total_variance += variance
                                
                                if abs(item.get('variance_percent', 0)) > 10:
                                    high_variance_items.append(item)
                        
                        st.metric("Items Counted", f"{counted_items}/{total_items}")
                        st.metric("Total Variance", f"{total_variance:.1f}")
                        st.metric("High Variance Items", len(high_variance_items))
                    
                    # Show items with high variance
                    if high_variance_items:
                        st.markdown("**High Variance Items:**")
                        variance_data = []
                        for item in high_variance_items:
                            variance_data.append({
                                'Product': item['product_name'],
                                'Expected': item['expected_qty'],
                                'Actual': item['actual_qty'],
                                'Variance': item.get('variance', 0),
                                'Variance %': f"{item.get('variance_percent', 0):.1f}%",
                                'Location': item['location']
                            })
                        
                        df = pd.DataFrame(variance_data)
                        st.dataframe(df, width='stretch')
    
    # ===============================================================================
    # EXPORT & ANALYSIS
    # ===============================================================================
    elif selected_page == "Export & Analysis":
        st.subheader("📈 Export & Analysis")
        
        # Export active counts
        if counts_data:
            st.markdown("**Export Active Counts:**")
            count_names = list(counts_data.keys())
            export_count = st.selectbox(
                "Select count to export:",
                count_names
            )
            
            if export_count:
                col1, col2 = st.columns(2)
                
                with col1:
                    # Get CSV data for download
                    csv_data, filename = get_count_csv_data(export_count)
                    if csv_data:
                        st.download_button(
                            label="📊 Download CSV",
                            data=csv_data,
                            file_name=filename,
                            mime="text/csv",
                            help="Download count data as CSV file"
                        )
                    else:
                        st.error("Error generating CSV data")
                
                with col2:
                    # Show count summary
                    summary = get_count_summary(export_count)
                    if summary:
                        st.metric("Progress", f"{summary['accuracy_percent']:.1f}%")
                        st.metric("High Variance", len(summary['high_variance_items']))
        
        # Historical analysis
        if history_data:
            st.markdown("**Historical Analysis:**")
            
            # Count trends
            if len(history_data) > 1:
                st.markdown("**Count Trends:**")
                
                trend_data = []
                for count in history_data:
                    items = count.get('items', []) if isinstance(count, dict) else []
                    total_items = len(items)
                    counted_items = 0
                    
                    # Calculate average variance
                    total_variance = 0
                    variance_count = 0
                    
                    for item in items:
                        if isinstance(item, dict) and item.get('actual_qty') is not None:
                            counted_items += 1
                            variance = abs(item.get('variance', 0))
                            total_variance += variance
                            variance_count += 1
                    
                    avg_variance = total_variance / variance_count if variance_count > 0 else 0
                    
                    count_name = count.get('count_name', 'Unknown') if isinstance(count, dict) else 'Unknown'
                    completed_date = count.get('completed_date', 'Unknown') if isinstance(count, dict) else 'Unknown'
                    
                    trend_data.append({
                        'Count Name': count_name,
                        'Date': completed_date[:10] if completed_date != 'Unknown' else 'Unknown',
                        'Items Counted': counted_items,
                        'Total Items': total_items,
                        'Progress %': (counted_items / total_items * 100) if total_items > 0 else 0,
                        'Avg Variance': avg_variance
                    })
                
                df = pd.DataFrame(trend_data)
                st.dataframe(df, width='stretch')
        
        # Variance analysis
        if history_data:
            st.markdown("**Variance Analysis:**")
            
            all_variance_items = []
            for count in history_data:
                items = count.get('items', []) if isinstance(count, dict) else []
                count_name = count.get('count_name', 'Unknown') if isinstance(count, dict) else 'Unknown'
                
                for item in items:
                    if isinstance(item, dict) and item.get('actual_qty') is not None and abs(item.get('variance_percent', 0)) > 5:
                        all_variance_items.append({
                            'Count': count_name,
                            'Product': item.get('product_name', 'Unknown'),
                            'Location': item.get('location', 'Unknown'),
                            'Expected': item.get('expected_qty', 0),
                            'Actual': item.get('actual_qty', 0),
                            'Variance %': item.get('variance_percent', 0)
                        })
            
            if all_variance_items:
                variance_df = pd.DataFrame(all_variance_items)
                st.dataframe(variance_df, width='stretch')
            else:
                st.info("No significant variances found in historical data.")

if __name__ == "__main__":
    main()
