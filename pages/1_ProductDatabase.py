import streamlit as st
import pandas as pd
from modules.product_manager import (
    get_text, initialize_product_data, load_products, save_product,
    delete_product, update_product, bulk_update_prices, format_currency,
    format_currency_small, UNIT_CONVERSIONS, calculate_cost_per_oz,
    find_product_by_sku, bulk_import_products, get_products_count
)
from modules.product_importer import (
    detect_csv_format, parse_sysco_format, parse_standard_csv,
    preview_csv_data, suggest_column_mappings, validate_mappings,
    apply_column_mapping, save_mapping_template, load_mapping_template,
    list_templates, detect_duplicates, process_import_batch,
    combine_pack_size, REQUIRED_FIELDS, OPTIONAL_FIELDS
)
import tempfile
import os

# --- Helper Functions ---

def filter_products(df, search_term, selected_category, selected_location):
    """Apply search and filter to products DataFrame."""
    filtered_df = df.copy()
    if search_term:
        mask = (
            filtered_df['Product Name'].str.contains(search_term, case=False, na=False) |
            filtered_df['SKU'].str.contains(search_term, case=False, na=False)
        )
        filtered_df = filtered_df[mask]
    if selected_category != "All Categories":
        filtered_df = filtered_df[filtered_df['Category'] == selected_category]
    if selected_location != "All Locations":
        filtered_df = filtered_df[filtered_df['Location'] == selected_location]
    return filtered_df

def format_display_df(display_df):
    """Formats the display DataFrame for Streamlit presentation."""
    try:
        # Format current price
        display_df['Current Price per Unit'] = [
            format_currency(x) for x in display_df['Current Price per Unit']
        ]
        # Format last price
        display_df['Last Price per Unit'] = [
            format_currency(x) if pd.notna(x) and x != '' and x is not None else '-'
            for x in display_df['Last Price per Unit']
        ]
        # Format last updated date
        display_df['Last Updated Date'] = [
            str(x) if pd.notna(x) and x != '' and x is not None else '-'
            for x in display_df['Last Updated Date']
        ]
        # Format cost per Oz
        display_df['Cost per Oz'] = [
            format_currency_small(x) for x in display_df['Cost per Oz']
        ]
    except Exception as e:
        st.error(f"Error formatting display data: {e}")
    return display_df

def show_summary(products_df, current_lang):
    """Show product summary statistics."""
    st.subheader(get_text("summary", current_lang))
    col1, col2, col3, col4 = st.columns(4)

    with col1:
        total_count = get_products_count()
        st.metric(get_text("total_products", current_lang), total_count)

    with col2:
        if not products_df.empty:
            most_expensive = products_df.loc[products_df['Current Price per Unit'].idxmax()]
            st.metric(get_text("most_expensive", current_lang),
                      most_expensive['Product Name'],
                      format_currency(most_expensive['Current Price per Unit']))
        else:
            st.metric(get_text("most_expensive", current_lang), get_text("na", current_lang))

    with col3:
        if not products_df.empty:
            total_value = products_df['Current Price per Unit'].sum()
            st.metric(get_text("total_inventory_value", current_lang),
                      format_currency(total_value))
        else:
            st.metric(get_text("total_inventory_value", current_lang), get_text("na", current_lang))

    with col4:
        if not products_df.empty:
            category_counts = products_df['Category'].value_counts()
            top_category = category_counts.index[0] if not category_counts.empty else get_text("na", current_lang)
            count = category_counts.iloc[0] if not category_counts.empty else 0
            st.metric(get_text("top_category", current_lang),
                      str(top_category),
                      f"{count} {get_text('items', current_lang)}")
        else:
            st.metric(get_text("top_category", current_lang), get_text("na", current_lang))

def add_product_form(current_lang):
    """Form for adding a new product."""
    st.subheader(get_text("add_new_product", current_lang))
    with st.form("add_product_form"):
        col1, col2 = st.columns(2)
        with col1:
            product_name = st.text_input(get_text("product_name", current_lang))
            sku = st.text_input(get_text("sku", current_lang))
            location_options = ["Walk-in Cooler", "Dry Goods Storage", "Freezer"]
            location = st.selectbox(get_text("location", current_lang), location_options, help=get_text("location_help", current_lang))
            category = st.text_input(get_text("category", current_lang))
            pack_size = st.text_input(get_text("pack_size", current_lang))
        with col2:
            unit_options = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]
            unit = st.selectbox(get_text("unit_of_measure", current_lang), unit_options)
            cost_per_unit = st.number_input(
                get_text("cost_per_unit", current_lang),
                min_value=0.0,
                step=0.01,
                help=get_text("cost_per_unit_help", current_lang)
            )
        # Cost per ounce preview
        if cost_per_unit > 0 and unit:
            conversion = UNIT_CONVERSIONS.get(unit.lower(), 1)
            cost_per_oz = calculate_cost_per_oz(cost_per_unit, unit)
            st.info(get_text("cost_per_ounce_preview", current_lang,
                             cost=format_currency_small(cost_per_oz),
                             unit=unit,
                             conversion=conversion))
        submitted = st.form_submit_button(get_text("add_product_button", current_lang))
        if submitted:
            if not product_name:
                st.error(get_text("please_enter_name", current_lang))
            else:
                product = {
                    'name': product_name,
                    'sku': sku,
                    'location': location,
                    'category': category,
                    'pack_size': pack_size,
                    'unit': unit,
                    'cost': cost_per_unit
                }
                success, message = save_product(product)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def manage_products_tab(products_df, current_lang):
    """Tab for managing and editing/deleting products."""
    st.subheader(get_text("manage_products", current_lang))
    if products_df.empty:
        st.info(get_text("no_products_found", current_lang))
        return

    # Delete Product
    st.write("### " + get_text("delete_a_product", current_lang))
    product_to_delete = st.selectbox(get_text("select_product_delete", current_lang),
                                     products_df['Product Name'].tolist())
    if st.button(get_text("delete_button", current_lang)):
        if product_to_delete:
            success, message = delete_product(product_to_delete)
            if success:
                st.success(message)
                st.rerun()
            else:
                st.error(message)
        else:
            st.warning(get_text("select_product_delete_warning", current_lang))
    st.divider()

    # Edit Product
    st.write("### " + get_text("edit_a_product", current_lang))
    product_to_edit = st.selectbox(get_text("select_product_edit", current_lang),
                                   products_df['Product Name'].tolist())
    if product_to_edit:
        product_row = products_df[products_df['Product Name'] == product_to_edit].iloc[0]
        st.write(get_text("editing", current_lang, name=product_to_edit))

        with st.form("edit_product_form"):
            col1, col2 = st.columns(2)
            with col1:
                new_name = st.text_input(get_text("product_name", current_lang), value=product_row['Product Name'])
                new_sku = st.text_input(get_text("sku", current_lang), value=product_row['SKU'])
                new_category = st.text_input(get_text("category", current_lang), value=product_row['Category'])
                new_pack = st.text_input("Pack", value=product_row.get('Pack', ''))
                new_size = st.text_input("Size", value=product_row.get('Size', ''))
            with col2:
                location_options = ["Walk-in Cooler", "Dry Goods Storage", "Freezer"]
                current_location = product_row.get('Location', 'Dry Goods Storage')
                new_location = st.selectbox(get_text("location", current_lang), location_options,
                                            index=location_options.index(current_location) if current_location in location_options else 1,
                                            help=get_text("location_help", current_lang))
                unit_options = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]
                new_unit = st.selectbox(
                    get_text("unit_of_measure", current_lang),
                    unit_options,
                    index=unit_options.index(product_row['Unit']) if product_row['Unit'] in unit_options else 0)
                new_cost = st.number_input(get_text("cost_per_unit", current_lang),
                                           value=float(product_row['Current Price per Unit']),
                                           min_value=0.0,
                                           step=0.01)
            submitted = st.form_submit_button(get_text("update_product_button", current_lang))
            if submitted:
                updated_product = {
                    'name': new_name,
                    'sku': new_sku,
                    'location': new_location,
                    'category': new_category,
                    'pack': new_pack,
                    'size': new_size,
                    'unit': new_unit,
                    'cost': new_cost
                }
                success, message = update_product(product_to_edit, updated_product)
                if success:
                    st.success(message)
                    st.rerun()
                else:
                    st.error(message)

def bulk_update_tab(current_lang):
    """Tab for bulk updating prices via supplier CSV."""
    st.subheader(get_text("bulk_update_title", current_lang))
    uploaded_file = st.file_uploader(get_text("upload_supplier_csv", current_lang), type=['csv'])

    if uploaded_file is not None:
        try:
            supplier_df = pd.read_csv(uploaded_file)
            st.write("### " + get_text("supplier_csv_preview", current_lang))
            st.dataframe(supplier_df.head(), width='stretch')
            st.write("### " + get_text("column_mapping", current_lang))
            col1, col2 = st.columns(2)
            with col1:
                sku_column = st.selectbox(get_text("select_sku_column", current_lang), supplier_df.columns.tolist())
            with col2:
                price_column = st.selectbox(get_text("select_price_column", current_lang), supplier_df.columns.tolist())

            if st.button(get_text("update_prices_button", current_lang)):
                if sku_column and price_column:
                    success, message = bulk_update_prices(supplier_df, sku_column, price_column)
                    if success:
                        st.success(message)
                        st.rerun()
                    else:
                        st.error(message)
                else:
                    st.error("Please select both SKU and Price columns.")
        except Exception as e:
            st.error(f"Error reading CSV file: {e}")

def import_products_tab(products_df, current_lang):
    """Tab for importing products from supplier CSV files with smart mapping."""
    st.subheader("📥 Import Products from Supplier CSV")
    st.caption("Upload supplier CSV files with intelligent column mapping and duplicate handling")

    # Initialize session state
    if 'import_uploaded_df' not in st.session_state:
        st.session_state.import_uploaded_df = None
    if 'import_format' not in st.session_state:
        st.session_state.import_format = None
    if 'import_mappings' not in st.session_state:
        st.session_state.import_mappings = {}
    if 'import_price_field' not in st.session_state:
        st.session_state.import_price_field = None
    if 'import_defaults' not in st.session_state:
        st.session_state.import_defaults = {}
    if 'import_preview_data' not in st.session_state:
        st.session_state.import_preview_data = None
    if 'import_results' not in st.session_state:
        st.session_state.import_results = None
    if 'import_step' not in st.session_state:
        st.session_state.import_step = 1

    last_import_summary = st.session_state.pop('last_import_summary', None)
    if last_import_summary:
        imported = last_import_summary.get("imported", 0)
        updated = last_import_summary.get("updated", 0)
        skipped = last_import_summary.get("skipped", 0)
        st.success(
            f"\U0001f389 Import complete: {imported} new, {updated} updated, {skipped} skipped."
        )
        errors = last_import_summary.get("errors") or []
        if errors:
            with st.expander("\u26a0\ufe0f Import notes", expanded=False):
                for error in errors:
                    st.warning(error)

    # Step indicator
    steps = ["📤 Upload", "🔗 Map Columns", "⚙️ Configure", "👁️ Preview", "✅ Import"]
    cols = st.columns(5)
    for idx, (col, step) in enumerate(zip(cols, steps), 1):
        with col:
            if idx == st.session_state.import_step:
                st.markdown(f"**{step}**")
            elif idx < st.session_state.import_step:
                st.markdown(f"~~{step}~~")
            else:
                st.markdown(f"_{step}_")

    st.divider()

    # Step 1: Upload & Preview
    if st.session_state.import_step == 1:
        st.markdown("### Step 1: Upload CSV File")

        uploaded_file = st.file_uploader(
            "Choose a supplier CSV file",
            type=['csv'],
            help="Upload SYSCO format or standard CSV files"
        )

        if uploaded_file is not None:
            try:
                # Save to temp file to allow multiple reads
                with tempfile.NamedTemporaryFile(delete=False, suffix='.csv') as tmp_file:
                    tmp_file.write(uploaded_file.getvalue())
                    tmp_path = tmp_file.name

                # Detect format
                temp_df = pd.read_csv(tmp_path, header=None, nrows=5)
                format_type = detect_csv_format(temp_df)

                # Parse based on format
                if format_type == 'sysco':
                    st.info("🔍 Detected: SYSCO format (with H/F/P row prefixes)")
                    df = parse_sysco_format(tmp_path)
                else:
                    st.info("🔍 Detected: Standard CSV format")
                    df = parse_standard_csv(tmp_path)

                # Clean up temp file
                os.unlink(tmp_path)

                # Store in session
                st.session_state.import_uploaded_df = df
                st.session_state.import_format = format_type

                # Show preview
                st.success(f"✅ Successfully loaded {len(df)} rows")
                st.markdown("**Preview (first 10 rows):**")
                st.dataframe(preview_csv_data(df, 10), width='stretch')

                # Show available columns
                st.markdown(f"**Available columns ({len(df.columns)}):**")
                st.write(", ".join(df.columns.tolist()))

                if st.button("Next: Map Columns →", type="primary"):
                    st.session_state.import_step = 2
                    st.rerun()

            except Exception as e:
                st.error(f"Error loading CSV: {str(e)}")
                st.info("Make sure your CSV file is properly formatted")

    # Step 2: Column Mapping
    elif st.session_state.import_step == 2:
        st.markdown("### Step 2: Map Columns")

        df = st.session_state.import_uploaded_df
        supplier_columns = df.columns.tolist()

        # Auto-map on first load (if not already mapped and no template loaded)
        if 'import_auto_mapped' not in st.session_state:
            suggestions = suggest_column_mappings(supplier_columns)
            if suggestions:
                for app_field, (supplier_col, confidence) in suggestions.items():
                    st.session_state.import_mappings[app_field] = supplier_col
                st.session_state.import_auto_mapped = True
                st.session_state.import_suggestions = suggestions
                st.info(f"✨ Auto-mapped {len(suggestions)} fields based on column names. Review and adjust below.")

        # Template management and controls
        col1, col2, col3 = st.columns([2, 2, 1])
        with col1:
            templates = list_templates()
            if templates:
                selected_template = st.selectbox(
                    "📋 Load saved template",
                    [""] + templates,
                    help="Select a previously saved mapping template"
                )
                if selected_template:
                    template_data = load_mapping_template(selected_template)
                    if template_data and 'column_mappings' in template_data:
                        st.session_state.import_mappings = template_data['column_mappings'].copy()
                        if 'price_field' in template_data:
                            st.session_state.import_price_field = template_data['price_field']
                        if 'defaults' in template_data:
                            st.session_state.import_defaults = template_data['defaults'].copy()
                        st.success(f"✅ Loaded template: {selected_template}")

        with col2:
            if st.button("🤖 Re-run Auto-Map", use_container_width=True):
                suggestions = suggest_column_mappings(supplier_columns)
                for app_field, (supplier_col, confidence) in suggestions.items():
                    st.session_state.import_mappings[app_field] = supplier_col
                st.session_state.import_suggestions = suggestions
                st.success(f"Auto-mapped {len(suggestions)} fields")
                st.rerun()

        with col3:
            if st.button("🔄 Clear", use_container_width=True):
                st.session_state.import_mappings = {}
                st.session_state.import_suggestions = {}
                st.rerun()

        st.divider()

        # Mapping Summary Table
        st.markdown("**📊 Current Mapping Summary:**")
        mapping_summary = []
        for app_field in list(REQUIRED_FIELDS.keys()):
            current_mapping = st.session_state.import_mappings.get(app_field, "")

            # Get sample data
            if current_mapping and current_mapping in df.columns:
                sample_values = df[current_mapping].head(3).dropna().tolist()
                sample_str = ", ".join([str(v)[:25] for v in sample_values[:2]])
                if len(sample_str) > 50:
                    sample_str = sample_str[:50] + "..."
                status = "✅"
            else:
                sample_str = "❌ Not mapped"
                status = "❌"

            # Get confidence if available
            confidence = ""
            if hasattr(st.session_state, 'import_suggestions') and app_field in st.session_state.import_suggestions:
                conf_score = st.session_state.import_suggestions[app_field][1]
                if conf_score >= 90:
                    confidence = f"🎯 {conf_score}%"
                elif conf_score >= 70:
                    confidence = f"⚠️ {conf_score}%"
                else:
                    confidence = f"❓ {conf_score}%"

            mapping_summary.append({
                "": status,
                "Required Field": app_field,
                "→ Your CSV Column": current_mapping or "❌ MISSING",
                "Confidence": confidence,
                "Sample Data": sample_str
            })

        summary_df = pd.DataFrame(mapping_summary)
        st.dataframe(summary_df, width='stretch', hide_index=True)

        st.divider()

        # Interactive mapping interface with sample preview
        st.markdown("**🎯 Adjust Field Mappings:**")
        st.caption("Review the auto-suggested mappings and adjust if needed. Sample data is shown for verification.")

        # Required fields with visual preview
        for app_field, patterns in REQUIRED_FIELDS.items():
            # Create columns for layout
            col_field, col_select, col_preview = st.columns([2, 3, 4])

            with col_field:
                st.markdown(f"**{app_field}** ⭐")
                st.caption(f"Examples: {', '.join(patterns[:2])}")

            with col_select:
                current_mapping = st.session_state.import_mappings.get(app_field, "")
                selected = st.selectbox(
                    f"Select column",
                    [""] + supplier_columns,
                    index=supplier_columns.index(current_mapping) + 1 if current_mapping in supplier_columns else 0,
                    key=f"map_{app_field}",
                    label_visibility="collapsed"
                )
                if selected:
                    st.session_state.import_mappings[app_field] = selected
                elif app_field in st.session_state.import_mappings:
                    del st.session_state.import_mappings[app_field]

            with col_preview:
                # Show sample data from selected column
                if selected and selected in df.columns:
                    sample_values = df[selected].head(5).dropna().tolist()
                    if sample_values:
                        sample_text = " | ".join([str(v)[:30] for v in sample_values[:3]])
                        st.success(f"📝 {sample_text}")
                    else:
                        st.warning("⚠️ Column is empty")
                else:
                    st.error("❌ Not mapped - required!")

            st.markdown("---")

        # Optional fields
        with st.expander("📎 Optional Fields (Expand to map)", expanded=False):
            for app_field, patterns in OPTIONAL_FIELDS.items():
                col_field, col_select, col_preview = st.columns([2, 3, 4])

                with col_field:
                    st.markdown(f"**{app_field}**")
                    st.caption(f"Examples: {', '.join(patterns[:2])}")

                with col_select:
                    current_mapping = st.session_state.import_mappings.get(app_field, "")
                    selected = st.selectbox(
                        f"Select column",
                        [""] + supplier_columns,
                        index=supplier_columns.index(current_mapping) + 1 if current_mapping in supplier_columns else 0,
                        key=f"map_opt_{app_field}",
                        label_visibility="collapsed"
                    )
                    if selected:
                        st.session_state.import_mappings[app_field] = selected
                    elif app_field in st.session_state.import_mappings:
                        del st.session_state.import_mappings[app_field]

                with col_preview:
                    if selected and selected in df.columns:
                        sample_values = df[selected].head(3).dropna().tolist()
                        if sample_values:
                            sample_text = " | ".join([str(v)[:30] for v in sample_values[:2]])
                            st.info(f"📝 {sample_text}")
                    else:
                        st.caption("Optional - leave blank if not needed")

                st.markdown("---")

        # Validate mappings
        is_valid, errors = validate_mappings(st.session_state.import_mappings)

        if not is_valid:
            st.error("⚠️ **Missing required field mappings:**")
            for error in errors:
                st.write(f"  • {error}")
        else:
            st.success("✅ **All required fields are mapped!** Ready to proceed.")

        # Save template option
        with st.expander("💾 Save this mapping as a template"):
            st.caption("Save these mappings to reuse for future imports from the same supplier")
            template_name = st.text_input("Template name", placeholder="e.g., SYSCO Standard, US Foods, etc.")
            if st.button("Save Template"):
                if template_name:
                    template_data = {
                        "name": template_name,
                        "format_type": st.session_state.import_format,
                        "column_mappings": st.session_state.import_mappings.copy(),
                        "price_field": st.session_state.import_price_field,
                        "defaults": st.session_state.import_defaults.copy()
                    }
                    success, message = save_mapping_template(template_name, template_data)
                    if success:
                        st.success(message)
                    else:
                        st.error(message)
                else:
                    st.warning("Please enter a template name")

        # Navigation
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back"):
                st.session_state.import_step = 1
                # Clear auto-map flag to re-run on next visit
                if 'import_auto_mapped' in st.session_state:
                    del st.session_state['import_auto_mapped']
                st.rerun()
        with col2:
            if st.button("Next: Configure →", type="primary", disabled=not is_valid):
                st.session_state.import_step = 3
                st.rerun()

    # Step 3: Configuration
    elif st.session_state.import_step == 3:
        st.markdown("### Step 3: Configure Import Settings")

        df = st.session_state.import_uploaded_df

        # Price field selection
        st.markdown("**Select Price Field:**")
        price_candidates = [col for col in df.columns if any(term in str(col).lower() for term in ['price', 'cost', '$', 'case', 'split'])]

        selected_price_field = st.radio(
            "Which column contains the price to import?",
            price_candidates if price_candidates else df.columns.tolist(),
            index=price_candidates.index(st.session_state.import_price_field) if st.session_state.import_price_field in price_candidates else 0
        )
        st.session_state.import_price_field = selected_price_field

        # Update mapping for price
        st.session_state.import_mappings["Current Price per Unit"] = selected_price_field

        st.divider()

        # Default values
        st.markdown("**Default Values for Missing Fields:**")
        col1, col2 = st.columns(2)

        with col1:
            default_location = st.selectbox(
                "Default Location",
                ["Walk-in Cooler", "Dry Goods Storage", "Freezer"],
                index=1
            )
            st.session_state.import_defaults["Location"] = default_location

        with col2:
            default_category = st.text_input(
                "Default Category (if not mapped)",
                value=st.session_state.import_defaults.get("Category", "Imported")
            )
            st.session_state.import_defaults["Category"] = default_category

        # Pack and Size info (for SYSCO)
        if st.session_state.import_format == 'sysco':
            st.markdown("**Pack & Size Configuration:**")
            st.info("SYSCO files have separate Pack, Size, and Unit columns. These will be imported as separate fields.")

            pack_cols = [col for col in df.columns if any(term in str(col).lower() for term in ['pack', 'size', 'unit'])]
            if pack_cols:
                st.write(f"Detected columns: {', '.join(pack_cols)}")

        # Navigation
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back"):
                st.session_state.import_step = 2
                st.rerun()
        with col2:
            if st.button("Next: Preview →", type="primary"):
                st.session_state.import_step = 4
                st.rerun()

    # Step 4: Preview & Validation
    elif st.session_state.import_step == 4:
        st.markdown("### Step 4: Preview & Validate")

        df = st.session_state.import_uploaded_df

        # Apply column mapping
        mapped_df = apply_column_mapping(df, st.session_state.import_mappings)

        # Process batch for validation
        results = process_import_batch(
            mapped_df,
            products_df,
            st.session_state.import_defaults
        )

        st.session_state.import_results = results

        # Show summary
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("✅ Ready to Import", len(results['ready']))
        with col2:
            st.metric("⚠️ Duplicates", len(results['duplicates']))
        with col3:
            st.metric("❌ Errors", len(results['errors']))
        with col4:
            total = len(results['ready']) + len(results['duplicates']) + len(results['errors'])
            st.metric("📊 Total Rows", total)

        # Show errors if any
        if results['errors']:
            with st.expander("❌ Errors", expanded=True):
                for error in results['errors']:
                    st.error(f"Row {error['row']}: {error['product_name']} - {error['error']}")

        # Show duplicates
        if results['duplicates']:
            with st.expander("⚠️ Duplicate Products", expanded=True):
                st.warning(f"Found {len(results['duplicates'])} products that already exist in your database")
                for dup in results['duplicates'][:5]:  # Show first 5
                    product = dup['product']
                    st.write(f"**{product.get('Product Name')}** (SKU: {product.get('SKU')}) - {dup['reason']}")
                if len(results['duplicates']) > 5:
                    st.info(f"... and {len(results['duplicates']) - 5} more")

        # Preview table
        st.markdown("**Preview (first 20 products to import):**")
        preview_products = results['ready'][:20]
        if preview_products:
            preview_df = pd.DataFrame(preview_products)
            display_cols = ['Product Name', 'SKU', 'Category', 'Pack', 'Size', 'Current Price per Unit', 'Location']
            display_cols = [col for col in display_cols if col in preview_df.columns]
            st.dataframe(preview_df[display_cols], width='stretch')
        else:
            st.info("No products ready to import")

        # Navigation
        col1, col2 = st.columns([1, 4])
        with col1:
            if st.button("← Back"):
                st.session_state.import_step = 3
                st.rerun()
        with col2:
            can_proceed = len(results['ready']) > 0 or len(results['duplicates']) > 0
            if st.button("Next: Import →", type="primary", disabled=not can_proceed):
                st.session_state.import_step = 5
                st.rerun()

    # Step 5: Import Execution
    elif st.session_state.import_step == 5:
        st.markdown("### Step 5: Import Products")

        results = st.session_state.import_results

        # Handle duplicates
        if results['duplicates']:
            st.markdown("**🔄 Duplicate Handling**")
            st.write(f"Found {len(results['duplicates'])} duplicate product(s)")

            duplicate_action = st.radio(
                "How should duplicates be handled?",
                ["Review each one individually", "Update all duplicates", "Skip all duplicates"],
                help="Choose how to handle products that already exist in your database"
            )

            if duplicate_action == "Review each one individually":
                st.info("You will review each duplicate in the next step")
                products_to_import = results['ready']
                handle_duplicates_individually = True
            elif duplicate_action == "Update all duplicates":
                st.warning("All duplicate products will be updated with new data")
                products_to_import = results['ready'] + [dup['product'] for dup in results['duplicates']]
                handle_duplicates_individually = False
                update_duplicates = True
            else:  # Skip all
                st.info("Duplicate products will be skipped")
                products_to_import = results['ready']
                handle_duplicates_individually = False
                update_duplicates = False
        else:
            products_to_import = results['ready']
            handle_duplicates_individually = False
            update_duplicates = False

        st.divider()

        # Import button
        if not handle_duplicates_individually:
            st.markdown(f"**Ready to import {len(products_to_import)} product(s)**")

            if st.button("🚀 Start Import", type="primary", use_container_width=True):
                progress_bar = st.progress(0)
                status_text = st.empty()

                # Perform import
                imported, updated, skipped, errors = bulk_import_products(
                    products_to_import,
                    update_duplicates=update_duplicates if results['duplicates'] else False
                )

                progress_bar.progress(100)

                # Show results
                st.success("✅ Import Complete!")

                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("✅ Imported", imported)
                with col2:
                    st.metric("🔄 Updated", updated)
                with col3:
                    st.metric("⏭️ Skipped", skipped)

                if errors:
                    with st.expander("❌ Errors"):
                        for error in errors:
                            st.error(error)

                st.balloons()

                # Persist results for the next run and refresh the product list view
                summary = {
                    "imported": imported,
                    "updated": updated,
                    "skipped": skipped,
                }
                if errors:
                    summary["errors"] = errors

                import_keys = [key for key in st.session_state.keys() if key.startswith('import_')]
                for key in import_keys:
                    del st.session_state[key]

                st.session_state['last_import_summary'] = summary
                st.rerun()
        else:
            # Individual duplicate review
            st.markdown("**Review Duplicates Individually:**")
            st.info("Coming in next update - for now, choose 'Update all' or 'Skip all' above")

        # Navigation
        if st.button("← Back"):
            st.session_state.import_step = 4
            st.rerun()

def main():
    """Ingredient Database page - Manage ingredient catalog and inventory items"""

    # Language toggle
    lang = st.radio("Language", ["English", "Spanish"], horizontal=True)
    current_lang = "es" if lang == "Spanish" else "en"

    st.header("🥘 Ingredient Database")
    st.markdown("Manage your ingredient catalog and inventory items")

    # Initialize product data
    init_result = initialize_product_data()
    if init_result:
        st.success(init_result)

    # Load existing products
    products_df = load_products()

    # Create tabs
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📋 Ingredient List",
        "➕ Add New Ingredient",
        "⚙️ Manage Ingredients",
        "💰 Bulk Update Prices",
        "📥 Import Ingredients"
    ])

    # Tab 1: Product List
    with tab1:
        st.subheader(get_text("product_list", current_lang))
        if products_df.empty:
            st.info(get_text("no_products_found", current_lang))
        else:
            # Search and filter
            search_term = st.text_input(get_text("search_products", current_lang))
            col1, col2 = st.columns(2)
            with col1:
                categories = ["All Categories"] + sorted(products_df['Category'].dropna().unique().tolist())
                selected_category = st.selectbox(get_text("filter_by_category", current_lang), categories)
            with col2:
                locations = ["All Locations"] + sorted(products_df['Location'].dropna().unique().tolist())
                selected_location = st.selectbox("Filter by Location", locations)
            filtered_df = filter_products(products_df, search_term, selected_category, selected_location)

            st.write(get_text("showing_products", current_lang,
                              filtered=len(filtered_df),
                              total=get_products_count()))
            if filtered_df.empty:
                st.info(get_text("no_products_match", current_lang))
            else:
                display_df = format_display_df(filtered_df.copy())
                st.dataframe(display_df, width='stretch')
            show_summary(products_df, current_lang)

    # Tab 2: Add New Product
    with tab2:
        add_product_form(current_lang)

    # Tab 3: Manage Products
    with tab3:
        manage_products_tab(products_df, current_lang)

    # Tab 4: Bulk Update from Supplier CSV
    with tab4:
        bulk_update_tab(current_lang)

    # Tab 5: Import Products
    with tab5:
        import_products_tab(products_df, current_lang)

if __name__ == "__main__":
    main()

# --------------------------- Suggestions for Further Refactoring ---------------------------
# 1. Consider moving repeated lists for units, locations, categories to a config/constants file.
# 2. Extract all get_text string IDs to a constants file to make the code more manageable and easier to translate.
# 3. Validate data types and possible nulls/typos earlier, e.g., check column existence or standardize column names.
# 4. For production use, add exception handling/logging around file/database/data operations (not just Streamlit error).
# 5. Modularize all "forms" and "display" logic into separate modules to keep UI and logic layers more distinct.
# 6. For larger scale, use class-based state management for the product catalog.
# 7. If the app grows, consider splitting each tab into a submodule.
