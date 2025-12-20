from __future__ import annotations

from functools import lru_cache
import importlib
import os
import shutil
from typing import Tuple


@lru_cache(maxsize=1)
def require_tesseract() -> Tuple[bool, str]:
    """Confirm the Tesseract OCR executable and Python binding are available."""
    if shutil.which("tesseract") is None:
        return False, "Tesseract OCR executable not found on PATH. Install it to enable OCR-based imports."
    try:
        importlib.import_module("pytesseract")
    except ModuleNotFoundError:
        return False, "Python package 'pytesseract' is missing. Install it to enable OCR-based imports."
    return True, ""


@lru_cache(maxsize=1)
def require_anthropic_key() -> Tuple[bool, str, str]:
    """Locate the Anthropic API key and ensure the SDK is importable."""
    try:
        import streamlit as st  # type: ignore
    except ModuleNotFoundError:
        st = None  # pragma: no cover

    key = ""
    if st is not None:
        key = st.secrets.get("ANTHROPIC_API_KEY", "")
    if not key:
        key = os.environ.get("ANTHROPIC_API_KEY", "")
    if not key:
        return False, "", "Anthropic API key not configured. Add it to Streamlit secrets or the ANTHROPIC_API_KEY environment variable."

    try:
        importlib.import_module("anthropic")
    except ModuleNotFoundError:
        return False, "", "Python package 'anthropic' is missing. Install it to enable recipe import."

    return True, key, ""
