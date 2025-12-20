import streamlit as st
import os
import pandas as pd
from modules.recipe_engine import (
    get_recipe_text, load_products, load_recipes, save_recipe, update_recipe,
    delete_recipe, get_recipe_categories, filter_recipes_by_category,
    search_recipes, format_currency
)
from modules.file_extractor import process_uploaded_file
from modules.recipe_parser import process_recipe_import
from utils.import_logger import (
    log_file_upload, log_extraction, log_pdf_routing,
    log_parsing, log_validation, log_mapping, log_save, log_error
)
from utils.dependency_checks import require_anthropic_key, require_tesseract
from config import config

def main():
    """Recipe Builder page - Create and manage recipes with ingredient lists"""

    # Language toggle
    lang = st.radio("Language", ["English", "Spanish"], horizontal=True)
    current_lang = "es" if lang == "Spanish" else "en"

    st.header(get_recipe_text("page_title", current_lang))
    st.markdown(get_recipe_text("page_caption", current_lang))

    # Load data
    products_df = load_products()
    recipes = load_recipes()

    # Create tabs for different functions
    tab1, tab2, tab3, tab4 = st.tabs([
        get_recipe_text("create_recipe", current_lang),
        get_recipe_text("view_recipes", current_lang),
        get_recipe_text("edit_recipe", current_lang),
        "📥 Import Recipes"
    ])

    # Tab 1: Create Recipe
    with tab1:
        st.subheader(get_recipe_text("create_new_recipe", current_lang))

        # Initialize ingredients list
        if "ingredients" not in st.session_state:
            st.session_state.ingredients = []

        # Ingredients management outside of form
        st.write("### " + get_recipe_text("ingredients", current_lang))

        if products_df.empty:
            st.warning("No products available. Please add products first.")
        else:
            # Display existing ingredients
            for i, ingredient in enumerate(st.session_state.ingredients):
                col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                with col1:
                    product_name = st.selectbox(
                        get_recipe_text("product", current_lang),
                        products_df['Product Name'].tolist(),
                        key=f"product_{i}",
                        index=products_df['Product Name'].tolist().index(ingredient['product_name']) if ingredient['product_name'] in products_df['Product Name'].tolist() else 0
                    )
                with col2:
                    quantity = st.number_input(
                        get_recipe_text("quantity", current_lang),
                        min_value=0.0,
                        step=0.1,
                        value=float(ingredient['quantity']),
                        key=f"qty_{i}"
                    )
                with col3:
                    unit_options = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]
                    unit = st.selectbox(
                        get_recipe_text("unit", current_lang),
                        unit_options,
                        index=unit_options.index(ingredient['unit']) if ingredient['unit'] in unit_options else 0,
                        key=f"unit_{i}"
                    )
                with col4:
                    if st.button(get_recipe_text("remove", current_lang), key=f"remove_{i}"):
                        st.session_state.ingredients.pop(i)
                        st.rerun()

                # Update ingredient
                st.session_state.ingredients[i] = {
                    'product_name': product_name,
                    'quantity': quantity,
                    'unit': unit
                }

            # Add new ingredient button
            if st.button(get_recipe_text("add_ingredient", current_lang)):
                st.session_state.ingredients.append({
                    'product_name': products_df['Product Name'].iloc[0] if not products_df.empty else "",
                    'quantity': 1.0,
                    'unit': "oz"
                })
                st.rerun()

        # Recipe form
        with st.form("create_recipe_form"):
            col1, col2 = st.columns(2)

            with col1:
                recipe_name = st.text_input(get_recipe_text("recipe_name", current_lang))
                description = st.text_area(get_recipe_text("description", current_lang))
                servings = st.number_input(get_recipe_text("servings", current_lang), min_value=1, value=4, step=1)
                prep_time = st.number_input(get_recipe_text("prep_time", current_lang), min_value=0, value=30, step=1)

            with col2:
                cook_time = st.number_input(get_recipe_text("cook_time", current_lang), min_value=0, value=45, step=1)

                # Category dropdown with predefined options
                category_options = [
                    "Main Course", "Appetizer", "Dessert", "Soup", "Salad",
                    "Side Dish", "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"
                ]

                # Get existing categories from recipes and add to options (excluding "Test")
                existing_categories = get_recipe_categories(recipes)
                for cat in existing_categories:
                    if cat not in category_options and cat != "Test":
                        category_options.append(cat)

                category = st.selectbox(
                    get_recipe_text("category", current_lang),
                    category_options,
                    index=0
                )

                instructions = st.text_area(get_recipe_text("cooking_instructions", current_lang))

            submitted = st.form_submit_button(get_recipe_text("save_recipe", current_lang))

            if submitted:
                if not recipe_name:
                    st.error(get_recipe_text("please_enter_name", current_lang))
                else:
                    recipe_data = {
                        'name': recipe_name,
                        'description': description,
                        'servings': servings,
                        'prep_time': prep_time,
                        'cook_time': cook_time,
                        'category': category,
                        'instructions': instructions,
                        'ingredients': st.session_state.ingredients.copy()
                    }

                    success, message = save_recipe(recipe_data)
                    if success:
                        st.success(message)
                        # Clear ingredients for next recipe
                        st.session_state.ingredients = []
                        st.rerun()
                    else:
                        st.error(message)

    # Tab 2: View Recipes
    with tab2:
        st.subheader(get_recipe_text("view_all_recipes", current_lang))

        if not recipes:
            st.info(get_recipe_text("no_recipes_found", current_lang))
        else:
            # Filter by category
            categories = [get_recipe_text("all_categories", current_lang)] + get_recipe_categories(recipes)
            selected_category = st.selectbox(get_recipe_text("filter_by_category", current_lang), categories)

            # Filter recipes
            filtered_recipes = filter_recipes_by_category(recipes, selected_category)

            # Display recipes
            if filtered_recipes:
                st.write(get_recipe_text("showing_recipes", current_lang,
                                count=len(filtered_recipes),
                                category=selected_category))

                for recipe_name, recipe in filtered_recipes.items():
                    with st.expander(f"📋 {recipe_name}"):
                        col1, col2 = st.columns(2)

                        with col1:
                            st.write(f"**{get_recipe_text('description', current_lang)}:** {recipe.get('description', 'N/A')}")
                            st.write(f"**{get_recipe_text('servings', current_lang)}:** {recipe.get('servings', 'N/A')}")
                            st.write(f"**{get_recipe_text('category', current_lang)}:** {recipe.get('category', 'N/A')}")
                            st.write(f"**{get_recipe_text('prep_time', current_lang)}:** {recipe.get('prep_time', 'N/A')} min")
                            st.write(f"**{get_recipe_text('cook_time', current_lang)}:** {recipe.get('cook_time', 'N/A')} min")

                        with col2:
                            st.write(f"**{get_recipe_text('total_recipe_cost', current_lang)}:** {format_currency(recipe.get('total_cost', 0))}")
                            st.write(f"**{get_recipe_text('ingredients', current_lang)}:**")
                            for ingredient in recipe.get('ingredients', []):
                                st.write(f"  • {ingredient['quantity']} {ingredient['unit']} {ingredient['product_name']}")

                        if recipe.get('instructions'):
                            st.write(f"**{get_recipe_text('cooking_instructions', current_lang)}:**")
                            st.write(recipe['instructions'])
            else:
                st.info(get_recipe_text("no_recipes_category", current_lang, category=selected_category))

            # Summary statistics
            st.subheader("📊 " + get_recipe_text("summary", current_lang))
            col1, col2, col3 = st.columns(3)

            with col1:
                st.metric(get_recipe_text("total_recipes", current_lang), len(recipes))

            with col2:
                total_cost = sum(recipe.get('total_cost', 0) for recipe in recipes.values())
                st.metric(get_recipe_text("total_recipe_cost", current_lang), format_currency(total_cost))

            with col3:
                avg_cost = total_cost / len(recipes) if recipes else 0
                st.metric(get_recipe_text("average_recipe_cost", current_lang), format_currency(avg_cost))

    # Tab 3: Edit Recipe
    with tab3:
        st.subheader(get_recipe_text("edit_recipe_title", current_lang))

        if not recipes:
            st.info(get_recipe_text("no_recipes_edit", current_lang))
        else:
            # Search functionality
            search_term = st.text_input(get_recipe_text("search_recipe", current_lang))

            # Filter recipes by search
            filtered_recipes = search_recipes(recipes, search_term)

            if filtered_recipes:
                recipe_to_edit = st.selectbox(get_recipe_text("select_recipe_edit", current_lang),
                                            list(filtered_recipes.keys()))

                if recipe_to_edit:
                    recipe = filtered_recipes[recipe_to_edit]
                    st.write(get_recipe_text("editing_recipe", current_lang, name=recipe_to_edit))

                    # Initialize edit ingredients - always load current recipe ingredients
                    st.session_state.edit_ingredients = recipe.get('ingredients', []).copy()

                    # Edit ingredients outside of form
                    st.write("### " + get_recipe_text("ingredients", current_lang))

                    # Debug: Show current ingredients
                    if st.session_state.edit_ingredients:
                        st.info(f"Found {len(st.session_state.edit_ingredients)} ingredients to edit")
                    else:
                        st.warning("No ingredients found in recipe")

                    for i, ingredient in enumerate(st.session_state.edit_ingredients):
                        col1, col2, col3, col4 = st.columns([3, 1, 1, 1])
                        with col1:
                            # Check if product exists in current database
                            available_products = products_df['Product Name'].tolist()
                            current_product = ingredient['product_name']

                            if current_product not in available_products:
                                st.warning(f"Product '{current_product}' not found in database")

                            product_name = st.selectbox(
                                get_recipe_text("product", current_lang),
                                available_products,
                                key=f"edit_product_{i}",
                                index=available_products.index(current_product) if current_product in available_products else 0
                            )
                        with col2:
                            quantity = st.number_input(
                                get_recipe_text("quantity", current_lang),
                                min_value=0.0,
                                step=0.1,
                                value=float(ingredient['quantity']),
                                key=f"edit_qty_{i}"
                            )
                        with col3:
                            unit_options = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]
                            unit = st.selectbox(
                                get_recipe_text("unit", current_lang),
                                unit_options,
                                index=unit_options.index(ingredient['unit']) if ingredient['unit'] in unit_options else 0,
                                key=f"edit_unit_{i}"
                            )
                        with col4:
                            if st.button(get_recipe_text("remove", current_lang), key=f"edit_remove_{i}"):
                                st.session_state.edit_ingredients.pop(i)
                                st.rerun()

                        # Update ingredient
                        st.session_state.edit_ingredients[i] = {
                            'product_name': product_name,
                            'quantity': quantity,
                            'unit': unit
                        }

                    # Add new ingredient button
                    if st.button(get_recipe_text("add_ingredient", current_lang), key="edit_add"):
                        st.session_state.edit_ingredients.append({
                            'product_name': products_df['Product Name'].iloc[0] if not products_df.empty else "",
                            'quantity': 1.0,
                            'unit': "oz"
                        })
                        st.rerun()

                    # Edit recipe form
                    with st.form("edit_recipe_form"):
                        col1, col2 = st.columns(2)

                        with col1:
                            new_name = st.text_input(get_recipe_text("recipe_name", current_lang), value=recipe['name'])
                            new_description = st.text_area(get_recipe_text("description", current_lang), value=recipe.get('description', ''))
                            new_servings = st.number_input(get_recipe_text("servings", current_lang), min_value=1, value=int(recipe.get('servings', 4)), step=1)
                            new_prep_time = st.number_input(get_recipe_text("prep_time", current_lang), min_value=0, value=int(recipe.get('prep_time', 30)), step=1)

                        with col2:
                            new_cook_time = st.number_input(get_recipe_text("cook_time", current_lang), min_value=0, value=int(recipe.get('cook_time', 45)), step=1)

                            # Category dropdown for edit form
                            edit_category_options = [
                                "Main Course", "Appetizer", "Dessert", "Soup", "Salad",
                                "Side Dish", "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"
                            ]

                            # Get existing categories and add to options (excluding "Test")
                            existing_categories = get_recipe_categories(recipes)
                            for cat in existing_categories:
                                if cat not in edit_category_options and cat != "Test":
                                    edit_category_options.append(cat)

                            # Find current category index
                            current_category = recipe.get('category', '')
                            category_index = 0
                            if current_category in edit_category_options:
                                category_index = edit_category_options.index(current_category)

                            new_category = st.selectbox(
                                get_recipe_text("category", current_lang),
                                edit_category_options,
                                index=category_index
                            )

                            new_instructions = st.text_area(get_recipe_text("cooking_instructions", current_lang), value=recipe.get('instructions', ''))

                        col1, col2 = st.columns(2)
                        with col1:
                            if st.form_submit_button(get_recipe_text("update_recipe", current_lang)):
                                updated_recipe = {
                                    'name': new_name,
                                    'description': new_description,
                                    'servings': new_servings,
                                    'prep_time': new_prep_time,
                                    'cook_time': new_cook_time,
                                    'category': new_category,
                                    'instructions': new_instructions,
                                    'ingredients': st.session_state.edit_ingredients.copy()
                                }

                                success, message = update_recipe(recipe_to_edit, updated_recipe)
                                if success:
                                    st.success(message)
                                    # Clear edit ingredients
                                    st.session_state.edit_ingredients = []
                                    st.rerun()
                                else:
                                    st.error(message)

                        with col2:
                            if st.form_submit_button(get_recipe_text("delete_recipe", current_lang), type="secondary"):
                                success, message = delete_recipe(recipe_to_edit)
                                if success:
                                    st.success(message)
                                    st.rerun()
                                else:
                                    st.error(message)
            else:
                st.info(get_recipe_text("no_recipes_match", current_lang))

    # Tab 4: Import Recipes
    with tab4:
        st.subheader("📥 Import Recipes from Files")
        st.caption("Upload recipe files in multiple formats (DOCX, PDF, CSV, Excel, Images)")

        # Check for Claude API key from Streamlit secrets or environment
        anthropic_ok, anthropic_api_key, anthropic_msg = require_anthropic_key()
        if not anthropic_ok:
            st.error(f"⚠️ {anthropic_msg}")
            st.info("The import feature requires Claude AI for text extraction and recipe parsing.")
            st.info("Add your API key to `.streamlit/secrets.toml` file:")
            st.code('ANTHROPIC_API_KEY = "sk-ant-your-key-here"')
            st.info("Get your API key at: https://console.anthropic.com/settings/keys")
            st.stop()

        # File uploader
        st.markdown("### Upload Recipe Files")
        uploaded_files = st.file_uploader(
            "Choose recipe files to import",
            type=['docx', 'pdf', 'csv', 'xlsx', 'png', 'jpg', 'jpeg'],
            accept_multiple_files=True,
            help=f"Maximum {config.MAX_RECIPE_FILE_SIZE_MB}MB per file, {config.PDF_MAX_PAGES} pages for PDFs"
        )

        if uploaded_files:
            st.info(f"📁 {len(uploaded_files)} file(s) uploaded")

            # Check if Tesseract is needed for any uploaded files
            needs_ocr = any(file.name.lower().endswith((".pdf", ".png", ".jpg", ".jpeg")) for file in uploaded_files)
            if needs_ocr:
                ocr_ok, ocr_msg = require_tesseract()
                if not ocr_ok:
                    st.error(f"⚠️ {ocr_msg}")
                    st.info("See `RECIPE_IMPORT_GUIDE.md` for installation instructions.")
                    st.stop()

            # Initialize session state for import processing
            if "import_processing" not in st.session_state:
                st.session_state.import_processing = {}

            # Process files button
            if st.button("🤖 Process with AI", type="primary", use_container_width=True):
                st.session_state.import_processing = {}

                for uploaded_file in uploaded_files:
                    file_key = uploaded_file.name

                    with st.status(f"Processing {uploaded_file.name}...", expanded=True) as status:
                        try:
                            # Step 1: Extract text
                            st.write("📄 Extracting text...")
                            extraction_result = process_uploaded_file(uploaded_file, anthropic_api_key)

                            if extraction_result.get("status") == "error":
                                st.error(f"❌ Extraction failed: {extraction_result.get('error')}")
                                log_error(
                                    {"filename": uploaded_file.name, "file_hash": "", "file_size": 0},
                                    "extraction",
                                    extraction_result.get('error', 'Unknown error')
                                )
                                continue

                            # Log extraction
                            file_info = {
                                "filename": extraction_result.get("filename"),
                                "file_hash": extraction_result.get("file_hash"),
                                "file_size": extraction_result.get("file_size"),
                                "file_type": extraction_result.get("file_type")
                            }
                            log_extraction(file_info, extraction_result)

                            # Log PDF routing if applicable
                            if extraction_result.get("file_type") == "pdf" and extraction_result.get("pages"):
                                log_pdf_routing(file_info, extraction_result["pages"])
                                st.write(f"📑 PDF: {extraction_result['text_pages']} text pages, {extraction_result['vision_pages']} vision pages")

                            # Step 2: Parse with Claude
                            st.write("🧠 Parsing recipe...")
                            source_metadata = {
                                "filename": extraction_result.get("filename"),
                                "file_type": extraction_result.get("file_type"),
                                "file_hash": extraction_result.get("file_hash"),
                                "pages": extraction_result.get("pages", [])
                            }

                            # Reload products to ensure we have latest data
                            fresh_products_df = load_products()

                            parse_result = process_recipe_import(
                                extraction_result.get("text", ""),
                                anthropic_api_key,
                                fresh_products_df,
                                source_metadata,
                                match_threshold=50  # Lowered to capture fuzzy matches like "dumpling wrappers" → "Wonton Wrapper"
                            )

                            if parse_result.get("status") == "error":
                                st.error(f"❌ Parsing failed: {parse_result.get('error')}")
                                log_error(file_info, "parsing", parse_result.get('error', 'Unknown error'))
                                continue

                            # Log parsing, validation, mapping
                            log_parsing(file_info, parse_result)
                            log_validation(file_info, parse_result.get("validation", {}))
                            log_mapping(file_info, parse_result.get("mapping_stats", {}))

                            # Step 3: Store in session
                            st.session_state.import_processing[file_key] = {
                                "extraction": extraction_result,
                                "parse": parse_result,
                                "file_info": file_info
                            }

                            status.update(label=f"✅ {uploaded_file.name} processed", state="complete")

                        except Exception as e:
                            st.error(f"❌ Unexpected error: {str(e)}")
                            log_error(
                                {"filename": uploaded_file.name, "file_hash": "", "file_size": 0},
                                "unexpected",
                                str(e)
                            )

            # Display processed recipes
            if st.session_state.import_processing:
                st.markdown("---")
                st.markdown("### 📋 Review Imported Recipes")

                for file_key, data in st.session_state.import_processing.items():
                    parse_result = data["parse"]
                    recipe = parse_result.get("recipe", {})
                    validation = parse_result.get("validation", {})
                    mapping_stats = parse_result.get("mapping_stats", {})

                    with st.expander(f"📄 {file_key} - {recipe.get('name', 'Untitled')}", expanded=True):
                        # Validation status
                        if validation.get("valid"):
                            st.success("✅ Recipe validated successfully")
                        else:
                            st.warning("⚠️ Validation warnings:")
                            for error in validation.get("errors", []):
                                st.write(f"  • {error}")

                        # Mapping statistics
                        col1, col2, col3, col4 = st.columns(4)
                        with col1:
                            st.metric("Ingredients", mapping_stats.get("total", 0))
                        with col2:
                            st.metric("🟢 Auto-mapped", mapping_stats.get("auto_mapped", 0))
                        with col3:
                            st.metric("🟡 Needs Review", mapping_stats.get("warn_mapped", 0))
                        with col4:
                            st.metric("🔴 Unmapped", mapping_stats.get("unmapped", 0))

                        # Recipe details
                        col1, col2 = st.columns(2)
                        with col1:
                            recipe["name"] = st.text_input("Recipe Name", value=recipe.get("name", ""), key=f"name_{file_key}")
                            recipe["description"] = st.text_area("Description", value=recipe.get("description", ""), key=f"desc_{file_key}")
                            recipe["servings"] = st.number_input("Servings", min_value=1, value=int(recipe.get("servings", 4)), step=1, key=f"serv_{file_key}")

                        with col2:
                            recipe["prep_time"] = st.number_input("Prep Time (min)", min_value=0, value=int(recipe.get("prep_time", 0)), step=1, key=f"prep_{file_key}")
                            recipe["cook_time"] = st.number_input("Cook Time (min)", min_value=0, value=int(recipe.get("cook_time", 0)), step=1, key=f"cook_{file_key}")
                            recipe["category"] = st.selectbox(
                                "Category",
                                ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                                 "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"],
                                index=0 if not recipe.get("category") else
                                      ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                                       "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"].index(recipe.get("category", "Other"))
                                      if recipe.get("category") in ["Main Course", "Appetizer", "Dessert", "Soup", "Salad", "Side Dish",
                                                                      "Beverage", "Sauce", "Dressing", "Marinade", "Prep Recipe", "Bar", "Other"] else 0,
                                key=f"cat_{file_key}"
                            )

                        # Ingredients table
                        st.markdown("**Ingredients** (Edit as needed)")
                        ingredients = recipe.get("ingredients", [])

                        if ingredients:
                            # Create DataFrame for display
                            ing_display = []
                            for ing in ingredients:
                                badge = ing.get("confidence_badge", "red")
                                badge_emoji = {"green": "🟢", "yellow": "🟡", "red": "🔴"}.get(badge, "⚪")

                                ing_display.append({
                                    "Status": badge_emoji,
                                    "Ingredient": ing.get("raw_name", ""),
                                    "Mapped Product": ing.get("mapped_name", "NOT MAPPED"),
                                    "Qty": ing.get("quantity", 0),
                                    "Unit": ing.get("uom", ""),
                                    "Qty (oz)": ing.get("quantity_oz", 0),
                                    "Cost": f"${ing.get('total_cost', 0):.2f}",
                                    "Confidence": f"{ing.get('mapping_confidence', 0):.0f}%"
                                })

                            st.dataframe(
                                pd.DataFrame(ing_display),
                                width='stretch',
                                hide_index=True
                            )

                            # Show unmapped ingredients warning
                            unmapped_count = mapping_stats.get("unmapped", 0)
                            if unmapped_count > 0:
                                st.warning(f"⚠️ {unmapped_count} ingredient(s) couldn't be mapped to your product database. You can still save the recipe or add these products to your database first.")

                        # Instructions
                        if recipe.get("instructions"):
                            st.markdown("**Instructions**")
                            if isinstance(recipe["instructions"], list):
                                for i, step in enumerate(recipe["instructions"], 1):
                                    st.write(f"{i}. {step}")
                            else:
                                st.write(recipe["instructions"])

                        # Cost summary
                        st.markdown(f"**Total Recipe Cost:** ${recipe.get('total_cost', 0):.2f}")

                        # Action buttons
                        col1, col2, col3 = st.columns(3)
                        with col1:
                            if st.button(f"💾 Save Recipe", key=f"save_{file_key}", type="primary"):
                                # Convert recipe to format expected by save_recipe
                                recipe_to_save = {
                                    "name": recipe["name"],
                                    "description": recipe.get("description", ""),
                                    "servings": recipe.get("servings", 4),
                                    "prep_time": recipe.get("prep_time", 0),
                                    "cook_time": recipe.get("cook_time", 0),
                                    "category": recipe.get("category", "Other"),
                                    "instructions": "\n".join(recipe.get("instructions", [])) if isinstance(recipe.get("instructions"), list) else recipe.get("instructions", ""),
                                    "ingredients": [
                                        {
                                            "product_name": ing.get("mapped_name", ing.get("raw_name")),
                                            "quantity": ing.get("quantity", 0),
                                            "unit": ing.get("uom", "each")
                                        }
                                        for ing in recipe.get("ingredients", [])
                                        if ing.get("mapped_name")  # Only include mapped ingredients
                                    ]
                                }

                                if not recipe_to_save["ingredients"]:
                                    st.error("❌ Cannot save recipe without any mapped ingredients")
                                else:
                                    success, message = save_recipe(recipe_to_save)
                                    if success:
                                        st.success(f"✅ {message}")
                                        log_save(data["file_info"], recipe["name"], True)
                                        # Remove from processing
                                        del st.session_state.import_processing[file_key]
                                        st.balloons()
                                        st.rerun()
                                    else:
                                        st.error(f"❌ {message}")
                                        log_save(data["file_info"], recipe["name"], False)

                        with col2:
                            if st.button(f"🗑️ Discard", key=f"discard_{file_key}"):
                                del st.session_state.import_processing[file_key]
                                st.rerun()

                        with col3:
                            with st.popover("📋 View Details"):
                                st.json(recipe, expanded=False)

if __name__ == "__main__":
    main()
