# -*- coding: utf-8 -*-
"""
Public Allergen Report Page

Accessible via QR code without authentication.
Displays allergen information for a specific recipe in a clean, mobile-friendly format.
"""

import streamlit as st
from modules.allergen_engine import get_recipe_by_id, load_allergen_database
from modules.recipe_engine import load_recipes

# Note: st.set_page_config is called in ui_components/layout.py via app.py
# For this public-facing page, the mobile-friendly config may need to be adjusted in layout.py

# Custom CSS for clean, accessible design
st.markdown("""
<style>
    /* Hide Streamlit branding */
    #MainMenu {visibility: hidden;}
    footer {visibility: hidden;}
    header {visibility: hidden;}

    /* Mobile-friendly styling */
    .allergen-card {
        background-color: #f8f9fa;
        border-left: 4px solid #dc3545;
        padding: 15px;
        margin: 10px 0;
        border-radius: 5px;
    }

    .fda-allergen {
        border-left-color: #dc3545;
        background-color: #fff3cd;
    }

    .other-allergen {
        border-left-color: #ffc107;
        background-color: #f8f9fa;
    }

    .allergen-icon {
        font-size: 2em;
        margin-right: 10px;
    }

    .allergen-name {
        font-size: 1.5em;
        font-weight: bold;
        color: #212529;
    }

    .allergen-description {
        font-size: 0.9em;
        color: #6c757d;
        margin-top: 5px;
    }

    .confidence-badge {
        display: inline-block;
        padding: 3px 8px;
        border-radius: 12px;
        font-size: 0.8em;
        font-weight: bold;
        margin-left: 10px;
    }

    .confidence-high {
        background-color: #d4edda;
        color: #155724;
    }

    .confidence-medium {
        background-color: #fff3cd;
        color: #856404;
    }

    .confidence-low {
        background-color: #f8d7da;
        color: #721c24;
    }

    .disclaimer-box {
        background-color: #fff3cd;
        border: 2px solid #ffc107;
        padding: 15px;
        border-radius: 5px;
        margin: 20px 0;
    }

    .recipe-title {
        font-size: 2em;
        font-weight: bold;
        color: #212529;
        margin-bottom: 10px;
    }

    .section-header {
        font-size: 1.3em;
        font-weight: bold;
        color: #495057;
        margin-top: 20px;
        margin-bottom: 10px;
        border-bottom: 2px solid #dee2e6;
        padding-bottom: 5px;
    }
</style>
""", unsafe_allow_html=True)


def render_allergen_card(allergen_info: dict, is_fda: bool = False):
    """Render an allergen card with icon and details"""
    name = allergen_info.get('name', 'Unknown')
    icon = allergen_info.get('icon', '⚠️')
    description = allergen_info.get('description', '')
    confidence = allergen_info.get('confidence', 0)
    matched_ingredients = allergen_info.get('matched_ingredients', [])

    # Determine confidence badge
    if confidence >= 90:
        badge_class = "confidence-high"
        badge_text = "High Confidence"
    elif confidence >= 70:
        badge_class = "confidence-medium"
        badge_text = "Medium Confidence"
    else:
        badge_class = "confidence-low"
        badge_text = "Low Confidence"

    card_class = "allergen-card fda-allergen" if is_fda else "allergen-card other-allergen"

    st.markdown(f"""
    <div class="{card_class}">
        <span class="allergen-icon">{icon}</span>
        <span class="allergen-name">{name}</span>
        <span class="confidence-badge {badge_class}">{confidence}%</span>
        <div class="allergen-description">{description}</div>
    </div>
    """, unsafe_allow_html=True)

    if matched_ingredients:
        with st.expander("🔍 View matched ingredients"):
            for ing in matched_ingredients:
                st.write(f"• {ing}")


def main():
    """Main public allergen report page"""

    # Get recipe_id from query params
    query_params = st.query_params
    recipe_id = query_params.get("recipe_id", None)

    if not recipe_id:
        st.error("⚠️ No recipe specified")
        st.info("This page requires a recipe ID in the URL.")
        st.stop()

    # Load recipe by ID
    recipe = get_recipe_by_id(recipe_id)

    if not recipe:
        st.error("❌ Recipe not found")
        st.info(f"Recipe ID '{recipe_id}' does not exist in the database.")
        st.stop()

    # Load allergen database for metadata
    allergen_db = load_allergen_database()
    allergen_metadata_db = allergen_db.get("allergen_metadata", {})

    # Extract allergen information
    recipe_name = recipe.get('name', 'Unknown Recipe')
    allergens = recipe.get('allergens', [])
    allergen_details = recipe.get('allergen_details', {})
    allergen_metadata = recipe.get('allergen_metadata', {})

    if not allergens and not allergen_details:
        st.warning("⚠️ No allergen information available for this recipe")
        st.info(f"Allergen data has not been analyzed yet for '{recipe_name}'.")
        st.stop()

    # Header
    st.markdown(f'<div class="recipe-title">⚠️ {recipe_name}</div>', unsafe_allow_html=True)
    st.caption(f"Allergen Information • Last updated: {allergen_metadata.get('last_updated', 'N/A')}")

    # Summary metrics
    col1, col2, col3 = st.columns(3)
    with col1:
        total_allergens = allergen_metadata.get('total_detected', len(allergens))
        st.metric("Total Allergens", total_allergens)
    with col2:
        fda_count = allergen_metadata.get('fda_top_9_count', 0)
        st.metric("FDA Top 9", fda_count)
    with col3:
        detection_methods = allergen_metadata.get('detection_methods', [])
        method_text = "AI+DB+Manual" if len(detection_methods) >= 3 else ", ".join(detection_methods).upper()
        st.metric("Detection", method_text)

    st.divider()

    # Organize allergens by FDA Top 9 vs Others
    fda_allergens = []
    other_allergens = []

    for allergen_key in allergens:
        # Get details from allergen_details or fallback to basic info
        if allergen_key in allergen_details:
            details = allergen_details[allergen_key]
        else:
            # Fallback: construct from allergen_metadata_db
            details = allergen_metadata_db.get(allergen_key, {})

        allergen_info = {
            'name': details.get('display_name', allergen_key.title()),
            'icon': details.get('metadata', {}).get('icon') or details.get('icon', '⚠️'),
            'description': details.get('metadata', {}).get('description') or details.get('description', ''),
            'confidence': details.get('confidence', 100),
            'matched_ingredients': [
                ing.get('ingredient', '')
                for ing in details.get('matched_ingredients', [])
            ]
        }

        # Check if FDA Top 9
        is_fda = (
            details.get('metadata', {}).get('fda_top_9', False) or
            allergen_metadata_db.get(allergen_key, {}).get('fda_top_9', False)
        )

        if is_fda:
            fda_allergens.append(allergen_info)
        else:
            other_allergens.append(allergen_info)

    # Display FDA Top 9 Allergens
    if fda_allergens:
        st.markdown('<div class="section-header">⭐ FDA Major Food Allergens (Top 9)</div>', unsafe_allow_html=True)
        st.warning("These are the most common food allergens regulated by the FDA. Please inform your server of any allergies.")

        for allergen in fda_allergens:
            render_allergen_card(allergen, is_fda=True)

    # Display Other Allergens
    if other_allergens:
        st.markdown('<div class="section-header">📋 Additional Allergens</div>', unsafe_allow_html=True)
        st.info("These are additional allergens that may cause sensitivities or intolerances.")

        for allergen in other_allergens:
            render_allergen_card(allergen, is_fda=False)

    # Ingredients list
    st.divider()
    st.markdown('<div class="section-header">🥘 Recipe Ingredients</div>', unsafe_allow_html=True)

    ingredients = recipe.get('ingredients', [])
    if ingredients:
        cols = st.columns(2)
        for idx, ing in enumerate(ingredients):
            with cols[idx % 2]:
                product_name = ing.get('product_name', 'Unknown')
                qty = ing.get('quantity', '')
                unit = ing.get('unit', '')
                st.write(f"• {product_name} ({qty} {unit})")
    else:
        st.info("Ingredient list not available")

    # Disclaimer
    st.divider()
    st.markdown("""
    <div class="disclaimer-box">
        <h4>⚠️ Important Disclaimer</h4>
        <p>
            This allergen information is provided as a general guide based on recipe ingredients.
            It is not a substitute for professional medical advice.
        </p>
        <p>
            <strong>Please note:</strong>
        </p>
        <ul>
            <li>Cross-contamination may occur during food preparation</li>
            <li>Ingredient suppliers may change without notice</li>
            <li>Always inform your server of any food allergies or dietary restrictions</li>
            <li>If you have severe allergies, consult with restaurant management before ordering</li>
        </ul>
        <p>
            <strong>In case of allergic reaction, seek immediate medical attention.</strong>
        </p>
    </div>
    """, unsafe_allow_html=True)

    # Footer
    st.divider()
    st.caption("Report generated by Restaurant Kitchen Inventory System")
    st.caption("For questions or concerns, please speak with your server or manager.")


if __name__ == "__main__":
    main()

