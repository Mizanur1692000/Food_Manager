import streamlit as st
import importlib
import os
import sys

# Add pages directory to path for dynamic imports
sys.path.append('pages')

# Import UI components
from ui_components.layout import create_main_layout, display_header
from ui_components.sidebar import setup_sidebar

# Language translations for main app
MAIN_TRANSLATIONS = {
    "en": {
        "app_title": "🍽️ Restaurant Kitchen Inventory",
        "company_name": "Curated Restaurant Consulting"
    },
    "es": {
        "app_title": "🍽️ Inventario de Cocina de Restaurante",
        "company_name": "Curated Restaurant Consulting"
    }
}

def get_main_text(key, lang="en"):
    """Get translated text for main app"""
    if lang not in MAIN_TRANSLATIONS:
        lang = "en"
    return MAIN_TRANSLATIONS[lang].get(key, key)

# ===============================================================================
# SESSION STATE INITIALIZATION
# ===============================================================================

if 'current_page' not in st.session_state:
    st.session_state.current_page = "1_ProductDatabase"

# ===============================================================================
# UTILITY FUNCTIONS
# ===============================================================================

def load_page_module(page_name):
    """Dynamically load page modules using importlib"""
    try:
        # Remove .py extension if present
        page_name = page_name.replace('.py', '')

        # Import the module
        module = importlib.import_module(page_name)

        # Check if the module has a main function
        if hasattr(module, 'main'):
            return module.main
        else:
            st.error(f"Page {page_name} does not have a main() function")
            return None
    except ImportError as e:
        st.error(f"Could not import page {page_name}: {e}")
        return None
    except Exception as e:
        st.error(f"Error loading page {page_name}: {e}")
        return None

# ===============================================================================
# MAIN APPLICATION
# ===============================================================================

def main():
    """Main application entry point"""

    # Create main layout and get logo
    logo = create_main_layout()

    # Setup sidebar and get selected page
    selected_page, current_lang = setup_sidebar()

    # Display header with logo, title, and company name
    display_header(
        logo=logo,
        title=get_main_text("app_title", current_lang),
        company_name=get_main_text("company_name", current_lang)
    )

    # Load and execute the selected page
    if selected_page:
        page_function = load_page_module(selected_page)
        if page_function:
            try:
                page_function()
            except Exception as e:
                st.error(f"Error executing page {selected_page}: {e}")
                st.info("Please check that the page module is properly implemented.")
        else:
            # Show placeholder content if page module not found
            st.info(f"Page {selected_page} is not yet implemented.")
            st.markdown("### TODO: Implement page functionality")
            st.markdown(f"Create the `{selected_page}.py` file in the `pages/` directory with a `main()` function.")
    else:
        st.warning("No page selected. Please choose a page from the sidebar.")

# ===============================================================================
# APPLICATION ENTRY POINT
# ===============================================================================

if __name__ == "__main__":
    main()
