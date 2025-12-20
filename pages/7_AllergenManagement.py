# -*- coding: utf-8 -*-
"""
Allergen Management Page

Dedicated page for detecting, managing, and reporting allergens in recipes.
Features:
- AI-powered allergen detection
- Database fuzzy matching
- Manual allergen tagging
- QR code generation for public allergen reports
- Batch processing
"""

import os
import json
import streamlit as st
import pandas as pd
from io import BytesIO
import base64

from modules.allergen_engine import (
    detect_allergens_ai,
    detect_allergens_database,
    combine_allergen_detections,
    generate_allergen_report,
    generate_qr_code,
    generate_qr_code_svg,
    save_allergen_data,
    get_recipe_allergens,
    load_allergen_database,
    FDA_TOP_9,
    ADDITIONAL_ALLERGENS
)
from modules.recipe_engine import load_recipes
from utils.shared_functions import get_text
from utils.dependency_checks import require_anthropic_key

# Note: st.set_page_config is called in ui_components/layout.py via app.py


def main():
    """Main allergen management page"""

    st.title("⚠️ Allergen Management")
    st.caption("AI-powered allergen detection, manual tagging, and QR code generation for guest safety")

    # Get API key using dependency guard (optional for this page - AI features disabled without it)
    anthropic_ok, anthropic_api_key, anthropic_msg = require_anthropic_key()
    if not anthropic_ok:
        anthropic_api_key = ""  # AI features will be disabled

    # Load data
    recipes = load_recipes()
    allergen_db = load_allergen_database()

    if not recipes:
        st.warning("No recipes found. Please create recipes first in the Recipe Builder page.")
        st.stop()

    st.success(f"✅ Loaded {len(recipes)} recipe(s)")

    # Sidebar configuration
    with st.sidebar:
        st.header("⚙️ Configuration")

        # API status
        if anthropic_api_key:
            st.success("🤖 Claude AI: Connected")
        else:
            st.warning("🤖 Claude AI: Not configured")
            st.info("Add API key to `.streamlit/secrets.toml` to enable AI detection")

        st.divider()

        # Base URL for QR codes
        base_url = st.text_input(
            "Base URL for QR Codes",
            value="http://localhost:8501",
            help="URL where your Streamlit app is hosted"
        )

        # Detection settings
        st.subheader("Detection Settings")
        db_confidence = st.slider(
            "Database Match Confidence",
            min_value=50,
            max_value=100,
            value=70,
            step=5,
            help="Minimum confidence for fuzzy matching"
        )

        # Display allergen database info
        st.divider()
        st.subheader("📚 Allergen Database")
        patterns_count = sum(len(patterns) for patterns in allergen_db.get("ingredient_patterns", {}).values())
        st.metric("Total Patterns", patterns_count)
        st.metric("Allergen Types", len(allergen_db.get("allergen_metadata", {})))

    # Main content tabs
    tab1, tab2, tab3 = st.tabs([
        "🔍 Analyze Recipe",
        "📊 Batch Analysis",
        "📋 View Reports"
    ])

    # ==================== TAB 1: Analyze Recipe ====================
    with tab1:
        st.subheader("Analyze Individual Recipe")

        # Recipe selection
        col1, col2 = st.columns([2, 1])
        with col1:
            recipe_names = list(recipes.keys())
            selected_recipe = st.selectbox(
                "Select Recipe to Analyze",
                recipe_names,
                help="Choose a recipe to detect allergens"
            )

        with col2:
            # Show existing allergen status
            if selected_recipe:
                recipe_data = recipes[selected_recipe]
                existing_allergens = recipe_data.get("allergens", [])
                if existing_allergens:
                    st.info(f"✅ {len(existing_allergens)} allergen(s) detected")
                else:
                    st.warning("⚠️ No allergens detected yet")

        if selected_recipe:
            recipe = recipes[selected_recipe]
            ingredients = recipe.get("ingredients", [])

            # Display recipe info
            with st.expander("📝 Recipe Details", expanded=False):
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.write(f"**Category:** {recipe.get('category', 'N/A')}")
                    st.write(f"**Servings:** {recipe.get('servings', 'N/A')}")
                with col2:
                    st.write(f"**Prep Time:** {recipe.get('prep_time', 0)} min")
                    st.write(f"**Cook Time:** {recipe.get('cook_time', 0)} min")
                with col3:
                    st.write(f"**Total Cost:** ${recipe.get('total_cost', 0):.2f}")

                st.write("**Ingredients:**")
                for ing in ingredients:
                    product = ing.get('product_name', 'Unknown')
                    qty = ing.get('quantity', '')
                    unit = ing.get('unit', '')
                    st.write(f"- {product} ({qty} {unit})")

            st.divider()

            # Detection methods
            st.subheader("🔎 Detection Methods")

            col1, col2 = st.columns(2)

            with col1:
                st.write("#### 🤖 AI Detection")
                if anthropic_api_key:
                    if st.button("🚀 Run AI Analysis", type="primary", width="stretch"):
                        with st.spinner("Claude is analyzing ingredients..."):
                            ai_result = detect_allergens_ai(
                                ingredients,
                                anthropic_api_key,
                                selected_recipe
                            )

                            if ai_result:
                                st.session_state['ai_result'] = ai_result
                                st.success(f"✅ AI detected {len(ai_result.get('detected_allergens', []))} allergen(s)")
                            else:
                                st.error("❌ AI detection failed")
                else:
                    st.warning("AI detection requires API key")

                # Display AI results
                if 'ai_result' in st.session_state:
                    ai_result = st.session_state['ai_result']
                    st.write(f"**Detected:** {', '.join(ai_result.get('detected_allergens', []))}")
                    if ai_result.get('notes'):
                        st.info(ai_result['notes'])

            with col2:
                st.write("#### 📚 Database Matching")
                if st.button("🔍 Run Database Match", width="stretch"):
                    with st.spinner("Matching against allergen database..."):
                        db_result = detect_allergens_database(ingredients, db_confidence)
                        st.session_state['db_result'] = db_result
                        st.success(f"✅ Database matched {len(db_result.get('detected_allergens', []))} allergen(s)")

                # Display DB results
                if 'db_result' in st.session_state:
                    db_result = st.session_state['db_result']
                    st.write(f"**Detected:** {', '.join(db_result.get('detected_allergens', []))}")

            st.divider()

            # Manual tagging
            st.subheader("✏️ Manual Allergen Tagging")

            col1, col2 = st.columns(2)

            with col1:
                st.write("**FDA Top 9 Allergens**")
                fda_selections = []
                for allergen in FDA_TOP_9:
                    display_name = allergen_db.get("allergen_metadata", {}).get(allergen, {}).get("display_name", allergen)
                    icon = allergen_db.get("allergen_metadata", {}).get(allergen, {}).get("icon", "")
                    if st.checkbox(f"{icon} {display_name}", key=f"fda_{allergen}"):
                        fda_selections.append(allergen)

            with col2:
                st.write("**Additional Allergens**")
                additional_selections = []
                for allergen in ADDITIONAL_ALLERGENS:
                    display_name = allergen_db.get("allergen_metadata", {}).get(allergen, {}).get("display_name", allergen)
                    icon = allergen_db.get("allergen_metadata", {}).get(allergen, {}).get("icon", "")
                    if st.checkbox(f"{icon} {display_name}", key=f"add_{allergen}"):
                        additional_selections.append(allergen)

            manual_allergens = fda_selections + additional_selections

            if manual_allergens:
                st.info(f"✅ {len(manual_allergens)} allergen(s) manually selected")

            st.divider()

            # Combine and generate report
            st.subheader("📊 Combined Allergen Report")

            col1, col2 = st.columns([1, 1])

            with col1:
                if st.button("🔗 Combine All Detections", type="primary", width="stretch"):
                    ai_result = st.session_state.get('ai_result')
                    db_result = st.session_state.get('db_result')

                    combined = combine_allergen_detections(
                        db_result,
                        ai_result,
                        manual_allergens if manual_allergens else None
                    )

                    st.session_state['combined_result'] = combined
                    st.success(f"✅ Combined report generated: {combined.get('total_detected', 0)} total allergen(s)")

            with col2:
                if 'combined_result' in st.session_state:
                    if st.button("💾 Save to Recipe", width="stretch"):
                        combined = st.session_state['combined_result']
                        if save_allergen_data(selected_recipe, combined):
                            st.success("✅ Allergen data saved to recipe!")
                            st.balloons()
                            # Refresh recipes
                            st.rerun()
                        else:
                            st.error("❌ Failed to save allergen data")

            # Display combined results
            if 'combined_result' in st.session_state:
                combined = st.session_state['combined_result']

                st.divider()

                # Summary metrics
                col1, col2, col3, col4 = st.columns(4)
                with col1:
                    st.metric("Total Allergens", combined.get('total_detected', 0))
                with col2:
                    st.metric("FDA Top 9", combined.get('fda_top_9_count', 0))
                with col3:
                    methods = combined.get('detection_methods', [])
                    st.metric("Detection Methods", len(methods))
                with col4:
                    confidence_avg = sum(
                        details.get('confidence', 0)
                        for details in combined.get('allergen_details', {}).values()
                    ) / max(combined.get('total_detected', 1), 1)
                    st.metric("Avg Confidence", f"{confidence_avg:.0f}%")

                # Detailed allergen list
                st.write("### Detected Allergens")

                allergen_details = combined.get('allergen_details', {})

                for allergen, details in allergen_details.items():
                    icon = details.get('metadata', {}).get('icon', '⚠️')
                    display_name = details.get('display_name', allergen)
                    confidence = details.get('confidence', 0)
                    sources = details.get('sources', [])
                    fda = details.get('metadata', {}).get('fda_top_9', False)

                    # Color based on confidence
                    if confidence >= 90:
                        status_color = "🟢"
                    elif confidence >= 70:
                        status_color = "🟡"
                    else:
                        status_color = "🔴"

                    fda_badge = "⭐ FDA Top 9" if fda else ""

                    with st.expander(f"{icon} {status_color} {display_name} ({confidence}% confidence) {fda_badge}"):
                        st.write(f"**Detection Sources:** {', '.join(sources)}")
                        st.write(f"**Description:** {details.get('metadata', {}).get('description', 'N/A')}")

                        matched_ings = details.get('matched_ingredients', [])
                        if matched_ings:
                            st.write("**Matched Ingredients:**")
                            for ing in matched_ings:
                                st.write(f"- {ing.get('ingredient', 'Unknown')}")

                        if details.get('ai_reason'):
                            st.info(f"AI Insight: {details['ai_reason']}")

                # QR Code Generation
                st.divider()
                st.subheader("📱 Generate QR Code")

                col1, col2 = st.columns([1, 1])

                with col1:
                    qr_format = st.radio("QR Code Format", ["PNG (Raster)", "SVG (Vector)"], horizontal=True)

                    if st.button("🎨 Generate QR Code", width="stretch"):
                        # Get or create recipe ID
                        recipe_id = recipe.get('recipe_id')
                        if not recipe_id:
                            from uuid import uuid4
                            recipe_id = str(uuid4())

                        try:
                            if qr_format == "PNG (Raster)":
                                file_path, img_bytes = generate_qr_code(
                                    recipe_id,
                                    selected_recipe,
                                    base_url
                                )
                                st.session_state['qr_image'] = img_bytes
                                st.session_state['qr_path'] = file_path
                                st.session_state['qr_format'] = 'png'
                            else:
                                file_path, svg_string = generate_qr_code_svg(
                                    recipe_id,
                                    selected_recipe,
                                    base_url
                                )
                                st.session_state['qr_svg'] = svg_string
                                st.session_state['qr_path'] = file_path
                                st.session_state['qr_format'] = 'svg'

                            st.success(f"✅ QR code generated: {file_path}")
                            st.session_state['qr_url'] = f"{base_url}/public_allergen_report?recipe_id={recipe_id}"

                        except Exception as e:
                            st.error(f"❌ QR generation failed: {e}")

                with col2:
                    # Display QR code
                    if 'qr_image' in st.session_state and st.session_state.get('qr_format') == 'png':
                        st.image(st.session_state['qr_image'], caption="Allergen QR Code", use_container_width=True)

                        # Download button
                        st.download_button(
                            label="⬇️ Download QR Code (PNG)",
                            data=st.session_state['qr_image'],
                            file_name=f"allergen_qr_{selected_recipe.replace(' ', '_')}.png",
                            mime="image/png",
                            use_container_width=True
                        )

                    elif 'qr_svg' in st.session_state and st.session_state.get('qr_format') == 'svg':
                        # Display SVG (Streamlit doesn't have native SVG support, use HTML)
                        st.components.v1.html(
                            f'<div style="text-align: center;">{st.session_state["qr_svg"]}</div>',
                            height=300
                        )

                        # Download button
                        st.download_button(
                            label="⬇️ Download QR Code (SVG)",
                            data=st.session_state['qr_svg'],
                            file_name=f"allergen_qr_{selected_recipe.replace(' ', '_')}.svg",
                            mime="image/svg+xml",
                            use_container_width=True
                        )

                if 'qr_url' in st.session_state:
                    st.info(f"🔗 Public URL: {st.session_state['qr_url']}")

    # ==================== TAB 2: Batch Analysis ====================
    with tab2:
        st.subheader("📊 Batch Allergen Analysis")
        st.info("Analyze multiple recipes at once")

        # Select recipes for batch processing
        selected_recipes = st.multiselect(
            "Select Recipes for Batch Analysis",
            list(recipes.keys()),
            help="Choose multiple recipes to analyze"
        )

        if selected_recipes:
            st.write(f"**{len(selected_recipes)} recipe(s) selected**")

            col1, col2 = st.columns(2)

            with col1:
                batch_method = st.radio(
                    "Detection Method",
                    ["Database Only", "AI Only (requires API key)", "Both"],
                    help="Choose detection method for batch processing"
                )

            with col2:
                auto_save = st.checkbox("Auto-save results to recipes", value=True)

            if st.button("🚀 Run Batch Analysis", type="primary", width="stretch"):
                progress_bar = st.progress(0)
                status_text = st.empty()

                results = []

                for idx, recipe_name in enumerate(selected_recipes):
                    status_text.text(f"Analyzing {recipe_name}...")

                    recipe = recipes[recipe_name]
                    ingredients = recipe.get("ingredients", [])

                    db_result = None
                    ai_result = None

                    # Database detection
                    if batch_method in ["Database Only", "Both"]:
                        db_result = detect_allergens_database(ingredients, db_confidence)

                    # AI detection
                    if batch_method in ["AI Only (requires API key)", "Both"] and anthropic_api_key:
                        ai_result = detect_allergens_ai(ingredients, anthropic_api_key, recipe_name)

                    # Combine results
                    combined = combine_allergen_detections(db_result, ai_result, None)

                    # Save if auto-save enabled
                    if auto_save:
                        save_allergen_data(recipe_name, combined)

                    results.append({
                        "recipe": recipe_name,
                        "allergens": len(combined.get('allergens', [])),
                        "fda_top_9": combined.get('fda_top_9_count', 0),
                        "methods": ', '.join(combined.get('detection_methods', []))
                    })

                    progress_bar.progress((idx + 1) / len(selected_recipes))

                status_text.text("✅ Batch analysis complete!")

                # Display results table
                st.divider()
                st.subheader("Batch Results")

                results_df = pd.DataFrame(results)
                st.dataframe(results_df, use_container_width=True)

                # Summary stats
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Recipes Analyzed", len(results))
                with col2:
                    total_allergens = results_df['allergens'].sum()
                    st.metric("Total Allergens Detected", total_allergens)
                with col3:
                    avg_allergens = results_df['allergens'].mean()
                    st.metric("Avg Allergens/Recipe", f"{avg_allergens:.1f}")

                if auto_save:
                    st.success("✅ All results saved to recipes!")

    # ==================== TAB 3: View Reports ====================
    with tab3:
        st.subheader("📋 Allergen Reports")

        # Filter recipes with allergen data
        recipes_with_allergens = {
            name: recipe for name, recipe in recipes.items()
            if recipe.get('allergens') or recipe.get('allergen_details')
        }

        if not recipes_with_allergens:
            st.info("No recipes with allergen data yet. Analyze recipes in the other tabs.")
        else:
            st.success(f"Found {len(recipes_with_allergens)} recipe(s) with allergen data")

            # Recipe selector
            view_recipe = st.selectbox(
                "Select Recipe to View Report",
                list(recipes_with_allergens.keys())
            )

            if view_recipe:
                recipe = recipes_with_allergens[view_recipe]
                allergens = recipe.get('allergens', [])
                allergen_details = recipe.get('allergen_details', {})
                allergen_metadata = recipe.get('allergen_metadata', {})

                # Generate full report
                report = generate_allergen_report(
                    view_recipe,
                    {
                        'allergens': allergens,
                        'allergen_details': allergen_details,
                        'detection_methods': allergen_metadata.get('detection_methods', []),
                        'total_detected': allergen_metadata.get('total_detected', len(allergens)),
                        'fda_top_9_count': allergen_metadata.get('fda_top_9_count', 0)
                    },
                    recipe.get('ingredients', [])
                )

                # Display report
                st.divider()

                st.write(f"## {report['recipe_name']}")
                st.caption(f"Report generated: {report['report_date']}")

                # Summary
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Total Allergens", report['total_allergens'])
                with col2:
                    st.metric("FDA Top 9", report['fda_top_9_present'])
                with col3:
                    st.metric("Detection Methods", len(report['detection_methods']))

                # FDA Top 9 Allergens
                if report['fda_allergens']:
                    st.write("### ⭐ FDA Top 9 Allergens Present")
                    cols = st.columns(3)
                    for idx, allergen in enumerate(report['fda_allergens']):
                        with cols[idx % 3]:
                            st.info(f"{allergen['icon']} **{allergen['name']}** ({allergen['confidence']}%)")
                            st.caption(allergen['description'])

                # Other Allergens
                if report['other_allergens']:
                    st.write("### 📋 Other Allergens")
                    cols = st.columns(3)
                    for idx, allergen in enumerate(report['other_allergens']):
                        with cols[idx % 3]:
                            st.warning(f"{allergen['icon']} **{allergen['name']}** ({allergen['confidence']}%)")
                            st.caption(allergen['description'])

                # Disclaimer
                st.divider()
                st.warning(f"⚠️ **Disclaimer:** {report['disclaimer']}")

                # Export options
                st.divider()
                col1, col2 = st.columns(2)

                with col1:
                    # Export as JSON
                    report_json = json.dumps(report, indent=2)
                    st.download_button(
                        label="📥 Download Report (JSON)",
                        data=report_json,
                        file_name=f"allergen_report_{view_recipe.replace(' ', '_')}.json",
                        mime="application/json",
                        use_container_width=True
                    )

                with col2:
                    # Print-friendly view
                    if st.button("🖨️ Print View", width="stretch"):
                        st.info("Use browser's Print function (Ctrl+P / Cmd+P) to print this page")


if __name__ == "__main__":
    main()

