import streamlit as st
import pandas as pd
from datetime import datetime
import json

# Import modules
from modules.summary_engine import (
    get_summary_text, get_count_summary_by_location, get_all_counts_summary,
    export_summary_to_csv, get_summary_csv_data, get_summary_statistics
)
from modules.inventory_engine import load_counts, load_count_history, update_count_item
from utils.shared_functions import format_currency, format_currency_small

def main():
    """Inventory Summary page - View comprehensive inventory summaries and financial analysis"""
    
    st.header(get_summary_text("page_title"))
    st.markdown(get_summary_text("page_caption"))
    
    # Load data
    counts_data = load_counts()
    history_data = load_count_history()
    
    # Sidebar for navigation
    st.sidebar.title("📊 Summary Options")
    
    # Main navigation
    page_options = [
        "Count Summary",
        "All Counts Overview", 
        "Location Analysis",
        "Financial Summary"
    ]
    
    selected_page = st.sidebar.selectbox(
        "Select Summary Type:",
        page_options
    )
    
    # ===============================================================================
    # COUNT SUMMARY
    # ===============================================================================
    if selected_page == "Count Summary":
        st.subheader("📋 Individual Count Summary")
        
        # Get all available counts
        all_counts = []
        if counts_data:
            all_counts.extend(list(counts_data.keys()))
        if history_data:
            for count in history_data:
                if isinstance(count, dict):
                    all_counts.append(count.get('count_name', 'Unknown'))
                else:
                    all_counts.append(str(count))
        
        if not all_counts:
            st.info("No counts available. Create a count first to see summaries.")
            return
        
        # Select count to summarize
        selected_count = st.selectbox(
            "Select Count to Summarize:",
            all_counts
        )
        
        if selected_count:
            summary = get_count_summary_by_location(selected_count)
            
            if summary:
                # Count overview
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Status", summary['status'].replace('_', ' ').title())
                with col2:
                    st.metric("Total Value", format_currency(summary['total_counted_value']))
                with col3:
                    st.metric("Expected Value", format_currency(summary['total_expected_value']))
                with col4:
                    variance = summary['total_counted_value'] - summary['total_expected_value']
                    st.metric("Value Variance", format_currency(variance))
                
                # Export button
                csv_data, filename = get_summary_csv_data(selected_count)
                if csv_data:
                    st.download_button(
                        label="📊 Download Summary CSV",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        help="Download detailed summary with location breakdown"
                    )
                else:
                    st.error("Error generating summary CSV data")
                
                st.markdown("---")
                
                # Location breakdown with editable counts
                st.subheader("📍 Summary by Location")
                
                # Track if any updates were made
                updates_made = False
                
                for location in summary['sorted_locations']:
                    location_data = summary['location_summaries'][location]
                    
                    with st.expander(f"📍 {location} ({location_data['items_counted']}/{location_data['total_items']} items counted)"):
                        # Location metrics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Items Counted", f"{location_data['items_counted']}/{location_data['total_items']}")
                        with col2:
                            st.metric("Total Counted", f"{location_data['total_counted_qty']:.1f}")
                        with col3:
                            st.metric("Counted Value", format_currency(location_data['total_counted_value']))
                        with col4:
                            st.metric("Expected Value", format_currency(location_data['total_expected_value']))
                        
                        # Editable items table
                        st.markdown("**Product Details (Editable):**")
                        st.info("💡 You can edit the actual counts directly below. Click 'Update' to save changes.")
                        
                        # Create editable form for each item
                        for i, item in enumerate(location_data['items']):
                            st.markdown(f"**{item['product_name']}** (SKU: {item['sku']})")
                            
                            col1, col2, col3, col4 = st.columns(4)
                            
                            with col1:
                                st.write(f"Expected: {item['expected_qty']:.1f} {item['unit']}")
                            
                            with col2:
                                # Create a unique key for each number input
                                key = f"actual_qty_{selected_count}_{item['sku']}_{location}_{i}"
                                current_actual = item['actual_qty'] if item['actual_qty'] is not None else 0.0
                                new_actual = st.number_input(
                                    f"Actual ({item['unit']})",
                                    value=float(current_actual),
                                    min_value=0.0,
                                    step=0.1,
                                    key=key,
                                    help=f"Enter the actual count for {item['product_name']}"
                                )
                            
                            with col3:
                                st.write(f"Unit Price: {format_currency(item['unit_price'])}")
                            
                            with col4:
                                # Update button for this specific item
                                update_key = f"update_{selected_count}_{item['sku']}_{location}_{i}"
                                if st.button("Update", key=update_key, type="secondary"):
                                    if new_actual != current_actual:
                                        success, message = update_count_item(
                                            selected_count, 
                                            item['product_name'], 
                                            new_actual
                                        )
                                        if success:
                                            st.success("✅ Updated!")
                                            updates_made = True
                                            # Rerun to refresh the data
                                            st.rerun()
                                        else:
                                            st.error(f"❌ {message}")
                                    else:
                                        st.info("No change detected")
                            
                            # Show variance and value
                            col5, col6 = st.columns(2)
                            with col5:
                                new_actual_value = new_actual * item['unit_price']
                                st.write(f"Value: {format_currency(new_actual_value)}")
                            
                            with col6:
                                if item['actual_qty'] is not None or new_actual > 0:
                                    variance = new_actual - item['expected_qty']
                                    variance_percent = (variance / item['expected_qty'] * 100) if item['expected_qty'] > 0 else 0
                                    
                                    variance_color = "🟢" if abs(variance_percent) <= 5 else "🟡" if abs(variance_percent) <= 10 else "🔴"
                                    st.write(f"{variance_color} Variance: {variance:+.1f} ({variance_percent:+.1f}%)")
                            
                            st.markdown("---")
                
                # Show summary after any updates
                if updates_made:
                    st.success("✅ Count data updated successfully! The summary has been refreshed.")
                    st.rerun()
                
                # Display read-only summary table
                st.markdown("**📊 Summary Table (Read-Only):**")
                
                # Create DataFrame for display
                items_data = []
                for location in summary['sorted_locations']:
                    location_data = summary['location_summaries'][location]
                    for item in location_data['items']:
                        items_data.append({
                            'Product': item['product_name'],
                            'SKU': item['sku'],
                            'Location': location,
                            'Expected': f"{item['expected_qty']:.1f} {item['unit']}",
                            'Actual': f"{item['actual_qty']:.1f} {item['unit']}" if item['actual_qty'] is not None else "Not counted",
                            'Unit Price': format_currency(item['unit_price']),
                            'Expected Value': format_currency(item['expected_value']),
                            'Actual Value': format_currency(item['actual_value']),
                            'Variance': f"{item['variance']:+.1f}",
                            'Variance %': f"{item['variance_percent']:+.1f}%",
                            'Status': "✅ Counted" if item['is_counted'] else "⏳ Pending"
                        })
                
                df = pd.DataFrame(items_data)
                st.dataframe(df, width='stretch')
            else:
                st.error("Error loading count summary.")
    
    # ===============================================================================
    # ALL COUNTS OVERVIEW
    # ===============================================================================
    elif selected_page == "All Counts Overview":
        st.subheader("📊 All Counts Overview")
        
        all_counts = get_all_counts_summary()
        
        if not all_counts:
            st.info("No counts available. Create a count first to see overview.")
            return
        
        # Overall statistics
        stats = get_summary_statistics()
        if stats:
            col1, col2, col3, col4 = st.columns(4)
            with col1:
                st.metric("Total Counts", stats['total_counts'])
            with col2:
                st.metric("Active Counts", stats['active_counts'])
            with col3:
                st.metric("Completed Counts", stats['completed_counts'])
            with col4:
                st.metric("Total Value", format_currency(stats['total_value_all_counts']))
        
        st.markdown("---")
        
        # Counts list
        st.markdown("**All Counts:**")
        
        for count in all_counts:
            status_icon = "🟢" if count['is_active'] else "✅"
            status_text = "Active" if count['is_active'] else "Completed"
            
            with st.expander(f"{status_icon} {count['count_name']} - {status_text}"):
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    st.write(f"**Created:** {count['created_date']}")
                    st.write(f"**Status:** {count['status'].replace('_', ' ').title()}")
                
                with col2:
                    st.metric("Total Value", format_currency(count['total_counted_value']))
                    st.metric("Expected Value", format_currency(count['total_expected_value']))
                
                with col3:
                    variance = count['total_counted_value'] - count['total_expected_value']
                    st.metric("Value Variance", format_currency(variance))
                    
                    if count['overall_summary']:
                        accuracy = count['overall_summary']['accuracy_percent']
                        st.metric("Accuracy", f"{accuracy:.1f}%")
                
                # Location summary
                st.markdown("**Locations:**")
                for location in count['sorted_locations']:
                    location_data = count['location_summaries'][location]
                    st.write(f"📍 **{location}**: {location_data['items_counted']}/{location_data['total_items']} items - {format_currency(location_data['total_counted_value'])}")
    
    # ===============================================================================
    # LOCATION ANALYSIS
    # ===============================================================================
    elif selected_page == "Location Analysis":
        st.subheader("📍 Location Analysis")
        
        all_counts = get_all_counts_summary()
        
        if not all_counts:
            st.info("No counts available for location analysis.")
            return
        
        # Get all unique locations
        all_locations = set()
        for count in all_counts:
            all_locations.update(count['sorted_locations'])
        
        selected_location = st.selectbox(
            "Select Location to Analyze:",
            sorted(all_locations)
        )
        
        if selected_location:
            # Analyze location across all counts
            location_data = []
            
            for count in all_counts:
                if selected_location in count['location_summaries']:
                    location_summary = count['location_summaries'][selected_location]
                    
                    location_data.append({
                        'Count Name': count['count_name'],
                        'Date': count['created_date'][:10],
                        'Status': count['status'],
                        'Items Counted': location_summary['items_counted'],
                        'Total Items': location_summary['total_items'],
                        'Counted Value': location_summary['total_counted_value'],
                        'Expected Value': location_summary['total_expected_value'],
                        'Value Variance': location_summary['total_counted_value'] - location_summary['total_expected_value']
                    })
            
            if location_data:
                df = pd.DataFrame(location_data)
                st.dataframe(df, width='stretch')
                
                # Location trends
                st.markdown("**Location Trends:**")
                
                # Calculate trends
                if len(location_data) > 1:
                    recent_counts = location_data[:3]  # Last 3 counts
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        avg_value = sum(d['Counted Value'] for d in recent_counts) / len(recent_counts)
                        st.metric("Average Value", format_currency(avg_value))
                    
                    with col2:
                        avg_variance = sum(d['Value Variance'] for d in recent_counts) / len(recent_counts)
                        st.metric("Average Variance", format_currency(avg_variance))
                    
                    with col3:
                        avg_items = sum(d['Items Counted'] for d in recent_counts) / len(recent_counts)
                        st.metric("Average Items Counted", f"{avg_items:.1f}")
            else:
                st.info(f"No data available for {selected_location}")
    
    # ===============================================================================
    # FINANCIAL SUMMARY
    # ===============================================================================
    elif selected_page == "Financial Summary":
        st.subheader("💰 Financial Summary")
        
        all_counts = get_all_counts_summary()
        
        if not all_counts:
            st.info("No counts available for financial analysis.")
            return
        
        # Financial overview
        total_value = sum(count['total_counted_value'] for count in all_counts)
        total_expected = sum(count['total_expected_value'] for count in all_counts)
        total_variance = total_value - total_expected
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Total Inventory Value", format_currency(total_value))
        with col2:
            st.metric("Total Expected Value", format_currency(total_expected))
        with col3:
            st.metric("Total Variance", format_currency(total_variance))
        with col4:
            variance_percent = (total_variance / total_expected * 100) if total_expected > 0 else 0
            st.metric("Variance %", f"{variance_percent:+.1f}%")
        
        st.markdown("---")
        
        # Value by location
        st.markdown("**Value by Location:**")
        
        location_totals = {}
        for count in all_counts:
            for location in count['sorted_locations']:
                if location not in location_totals:
                    location_totals[location] = {
                        'total_value': 0,
                        'total_expected': 0,
                        'counts': 0
                    }
                
                location_data = count['location_summaries'][location]
                location_totals[location]['total_value'] += location_data['total_counted_value']
                location_totals[location]['total_expected'] += location_data['total_expected_value']
                location_totals[location]['counts'] += 1
        
        # Display location totals
        for location in sorted(location_totals.keys()):
            data = location_totals[location]
            variance = data['total_value'] - data['total_expected']
            
            with st.expander(f"📍 {location} (${data['total_value']:,.2f})"):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Value", format_currency(data['total_value']))
                with col2:
                    st.metric("Expected Value", format_currency(data['total_expected']))
                with col3:
                    st.metric("Variance", format_currency(variance))
                
                st.write(f"**Counts included:** {data['counts']}")

if __name__ == "__main__":
    main()