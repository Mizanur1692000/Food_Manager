import streamlit as st
import pandas as pd

def create_file_uploader(label, file_types, key=None, help_text=None):
    """Create a file uploader with consistent styling"""
    return st.file_uploader(
        label=label,
        type=file_types,
        key=key,
        help=help_text
    )

def create_text_input(label, key=None, value="", placeholder="", help_text=None):
    """Create a text input field"""
    return st.text_input(
        label=label,
        value=value,
        key=key,
        placeholder=placeholder,
        help=help_text
    )

def create_number_input(label, min_value=0.0, max_value=None, value=0.0, step=0.01, key=None, help_text=None):
    """Create a number input field"""
    return st.number_input(
        label=label,
        min_value=min_value,
        max_value=max_value,
        value=value,
        step=step,
        key=key,
        help=help_text
    )

def create_selectbox(label, options, key=None, index=0, help_text=None):
    """Create a selectbox dropdown"""
    return st.selectbox(
        label=label,
        options=options,
        index=index,
        key=key,
        help=help_text
    )

def create_multiselect(label, options, key=None, default=None, help_text=None):
    """Create a multiselect dropdown"""
    return st.multiselect(
        label=label,
        options=options,
        default=default,
        key=key,
        help=help_text
    )

def create_checkbox(label, key=None, value=False, help_text=None):
    """Create a checkbox"""
    return st.checkbox(
        label=label,
        value=value,
        key=key,
        help=help_text
    )

def create_button(label, key=None, help_text=None):
    """Create a button"""
    return st.button(
        label=label,
        key=key,
        help=help_text
    )

def create_dataframe_display(df, title=None, width=None):
    """Creates a styled dataframe display with an optional title."""
    if title:
        st.markdown(f"##### {title}")
    
    # Determine width setting
    container_width = width == 'stretch'

    with st.container(border=True):
        st.dataframe(df, use_container_width=container_width)

def create_success_message(message):
    """Display a success message"""
    st.success(message)

def create_error_message(message):
    """Display an error message"""
    st.error(message)

def create_info_message(message):
    """Display an info message"""
    st.info(message)

def create_warning_message(message):
    """Display a warning message"""
    st.warning(message)

def create_form_section(title):
    """Create a form section with title"""
    st.subheader(title)
    st.markdown("---")

def create_two_column_layout():
    """Create a two-column layout for forms"""
    return st.columns(2)

def create_three_column_layout():
    """Create a three-column layout for forms"""
    return st.columns(3)

def create_expander(title, expanded=False):
    """Create an expander widget"""
    return st.expander(title, expanded=expanded)

def create_tabs(tab_names):
    """Create tabs for organizing content"""
    return st.tabs(tab_names)

def create_progress_bar():
    """Create a progress bar"""
    return st.progress(0)

def create_spinner(text):
    """Create a spinner for loading states"""
    return st.spinner(text)
