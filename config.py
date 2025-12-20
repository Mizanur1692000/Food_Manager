"""
Configuration Management for Restaurant Kitchen Inventory App

This module provides centralized configuration settings for the application,
including data paths, UI settings, business logic parameters, and file handling.
"""

import os
from typing import Dict, List, Any, Optional
from pathlib import Path

class Config:
    """Centralized configuration class for the application"""

    # ===============================================================================
    # DATA PATHS AND FILES
    # ===============================================================================

    # Base directories
    BASE_DIR = Path(__file__).parent
    DATA_DIR = BASE_DIR / "data"

    # Data files
    PRODUCTS_FILE = DATA_DIR / "product_data.csv"
    RECIPES_FILE = DATA_DIR / "recipes.json"
    SUPPLIER_PRICING_FILE = DATA_DIR / "test_supplier_pricing.csv"
    LOGO_FILE = DATA_DIR / "Curated Restaurant Consulting Logo for Business Card.png"
    INVENTORY_FILE = DATA_DIR / "inventory.csv"
    INVENTORY_COUNTS_FILE = DATA_DIR / "inventory_counts.json"
    COUNT_HISTORY_FILE = DATA_DIR / "count_history.json"
    IMPORT_TEMPLATES_FILE = DATA_DIR / "import_templates.json"
    ALLERGEN_DATABASE_FILE = DATA_DIR / "allergen_database.json"
    VARIANCE_HISTORY_FILE = DATA_DIR / "variance_history.json"

    # Backup and output directories
    BACKUP_DIR = DATA_DIR / "backups"
    QR_CODE_DIR = DATA_DIR / "allergen_qr_codes"

    # ===============================================================================
    # UI SETTINGS
    # ===============================================================================

    # Language settings
    DEFAULT_LANGUAGE = "en"
    SUPPORTED_LANGUAGES = ["en", "es"]
    LANGUAGE_NAMES = {
        "en": "English",
        "es": "Spanish"
    }

    # Page configuration
    PAGE_TITLE = "Restaurant Kitchen Inventory"
    PAGE_ICON = "🍽️"
    LAYOUT = "wide"
    INITIAL_SIDEBAR_STATE = "expanded"

    # Company information
    COMPANY_NAME = "Curated Restaurant Consulting"
    APP_TITLE = "🍽️ Restaurant Kitchen Inventory"

    # ===============================================================================
    # BUSINESS LOGIC SETTINGS
    # ===============================================================================

    # Currency settings
    DEFAULT_CURRENCY = "USD"
    CURRENCY_SYMBOL = "$"
    CURRENCY_FORMAT = "{symbol}{amount:,.2f}"

    # Units and measurements
    DEFAULT_UNIT = "oz"
    VALID_UNITS = ["oz", "lb", "case", "each", "gallon", "liter", "quart", "grams"]

    # Unit conversion factors to ounces
    UNIT_CONVERSIONS = {
        "oz": 1,           # 1 oz = 1 oz
        "lb": 16,          # 1 lb = 16 oz
        "case": 192,       # 1 case = 12 lb = 192 oz (typical case)
        "each": 8,         # 1 each = 8 oz (typical individual item)
        "gallon": 128,     # 1 gallon = 128 oz
        "liter": 33.814,   # 1 liter = 33.814 oz
        "quart": 32,       # 1 quart = 32 oz
        "grams": 0.035274  # 1 gram = 0.035274 oz
    }

    # Recipe settings
    DEFAULT_SERVINGS = 4
    DEFAULT_PREP_TIME = 30  # minutes
    DEFAULT_COOK_TIME = 45  # minutes

    # Inventory settings
    MIN_INVENTORY_LEVEL = 0
    MAX_INVENTORY_LEVEL = 10000
    LOW_STOCK_THRESHOLD = 10

    # ===============================================================================
    # FILE HANDLING SETTINGS
    # ===============================================================================

    # File upload settings
    MAX_FILE_SIZE_MB = 10
    MAX_FILE_SIZE_BYTES = MAX_FILE_SIZE_MB * 1024 * 1024
    ALLOWED_FILE_EXTENSIONS = [".csv", ".json", ".xlsx", ".xls"]
    ALLOWED_IMAGE_EXTENSIONS = [".png", ".jpg", ".jpeg", ".gif"]

    # CSV settings
    CSV_ENCODING = "utf-8"
    CSV_DELIMITER = ","

    # Backup settings
    MAX_BACKUP_FILES = 10
    BACKUP_SUFFIX = "_backup"

    # ===============================================================================
    # RECIPE IMPORT SETTINGS
    # ===============================================================================

    # Allowed recipe file types
    ALLOWED_RECIPE_FILE_EXTENSIONS = [".docx", ".pdf", ".csv", ".xlsx", ".png", ".jpg", ".jpeg"]
    REJECTED_FILE_EXTENSIONS = [".xlsm", ".docm", ".xlsb"]  # Files with macros
    MAX_RECIPE_FILE_SIZE_MB = 20
    MAX_RECIPE_FILE_SIZE_BYTES = MAX_RECIPE_FILE_SIZE_MB * 1024 * 1024
    PDF_MAX_PAGES = 50
    ROUTE_PER_PAGE = True

    # Text confidence multi-metric thresholds
    TEXT_CONF = {
        "min_chars": 200,
        "min_words": 30,
        "min_uom_hits": 2
    }

    # Ingredient mapping thresholds
    MAP_THRESH = {
        "auto": 90,   # Green badge - auto-map
        "warn": 70    # Yellow badge - warn user
    }

    # Known UOM patterns for confidence detection
    KNOWN_UOMS = [
        "oz", "lb", "cup", "tsp", "tbsp", "gram", "kg", "ml",
        "liter", "quart", "gallon", "each", "bunch", "case", "dozen",
        "pint", "fl oz", "bag", "box", "jar", "can", "package"
    ]

    # Unicode fraction mappings
    UNICODE_FRACTIONS = {
        "½": 0.5, "⅓": 0.33, "⅔": 0.67, "¼": 0.25, "¾": 0.75,
        "⅕": 0.2, "⅖": 0.4, "⅗": 0.6, "⅘": 0.8, "⅙": 0.17, "⅚": 0.83,
        "⅐": 0.14, "⅛": 0.125, "⅜": 0.375, "⅝": 0.625, "⅞": 0.875
    }

    # ===============================================================================
    # VALIDATION SETTINGS
    # ===============================================================================

    # Product validation
    MIN_SKU_LENGTH = 3
    MAX_SKU_LENGTH = 20
    MIN_PRODUCT_NAME_LENGTH = 1
    MAX_PRODUCT_NAME_LENGTH = 100

    # Recipe validation
    MIN_SERVINGS = 1
    MAX_SERVINGS = 1000
    MIN_PREP_TIME = 0
    MAX_PREP_TIME = 1440  # 24 hours in minutes
    MIN_COOK_TIME = 0
    MAX_COOK_TIME = 1440  # 24 hours in minutes

    # ===============================================================================
    # LOGGING SETTINGS
    # ===============================================================================

    LOG_LEVEL = "INFO"
    LOG_FORMAT = "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    LOG_FILE = BASE_DIR / "logs" / "app.log"

    # ===============================================================================
    # ERROR HANDLING SETTINGS
    # ===============================================================================

    # Error messages
    ERROR_MESSAGES = {
        "file_not_found": "File not found: {file_path}",
        "invalid_data": "Invalid data format: {details}",
        "validation_error": "Validation error: {field} - {message}",
        "save_error": "Error saving data: {details}",
        "load_error": "Error loading data: {details}",
        "permission_error": "Permission denied: {operation}",
        "network_error": "Network error: {details}",
        "unknown_error": "An unexpected error occurred: {details}"
    }

    # ===============================================================================
    # UI COMPONENT SETTINGS
    # ===============================================================================

    # Form settings
    FORM_SUBMIT_BUTTON_TEXT = "Submit"
    FORM_CANCEL_BUTTON_TEXT = "Cancel"
    FORM_RESET_BUTTON_TEXT = "Reset"

    # Table settings
    TABLE_PAGE_SIZE = 50
    TABLE_MAX_ROWS = 1000

    # Chart settings
    CHART_HEIGHT = 400
    CHART_WIDTH = 800
    CHART_COLORS = ["#1f77b4", "#ff7f0e", "#2ca02c", "#d62728", "#9467bd"]

    # ===============================================================================
    # METHODS
    # ===============================================================================

    @classmethod
    def ensure_directories(cls) -> None:
        """Ensure all required directories exist"""
        directories = [
            cls.DATA_DIR,
            cls.BACKUP_DIR,
            cls.LOG_FILE.parent
        ]

        for directory in directories:
            directory.mkdir(parents=True, exist_ok=True)

    @classmethod
    def get_file_path(cls, file_type: str) -> Path:
        """Get the full path for a specific file type"""
        file_mapping = {
            "products": cls.PRODUCTS_FILE,
            "recipes": cls.RECIPES_FILE,
            "supplier_pricing": cls.SUPPLIER_PRICING_FILE,
            "logo": cls.LOGO_FILE
        }

        return file_mapping.get(file_type, cls.DATA_DIR / f"{file_type}")

    @classmethod
    def get_backup_path(cls, original_file: Path) -> Path:
        """Get backup path for a file"""
        backup_name = f"{original_file.stem}{cls.BACKUP_SUFFIX}{original_file.suffix}"
        return cls.BACKUP_DIR / backup_name

    @classmethod
    def is_valid_unit(cls, unit: str) -> bool:
        """Check if unit is valid"""
        return unit.lower() in cls.VALID_UNITS

    @classmethod
    def get_unit_conversion(cls, unit: str) -> float:
        """Get conversion factor for unit to ounces"""
        return cls.UNIT_CONVERSIONS.get(unit.lower(), 1.0)

    @classmethod
    def format_currency(cls, amount: float) -> str:
        """Format amount as currency"""
        return cls.CURRENCY_FORMAT.format(
            symbol=cls.CURRENCY_SYMBOL,
            amount=amount
        )

    @classmethod
    def get_error_message(cls, error_type: str, **kwargs) -> str:
        """Get formatted error message"""
        message_template = cls.ERROR_MESSAGES.get(error_type, "Unknown error")
        return message_template.format(**kwargs)

    @classmethod
    def validate_file_size(cls, file_size_bytes: int) -> bool:
        """Validate file size is within limits"""
        return file_size_bytes <= cls.MAX_FILE_SIZE_BYTES

    @classmethod
    def validate_file_extension(cls, filename: str, allowed_extensions: Optional[List[str]] = None) -> bool:
        """Validate file extension"""
        extensions_to_check = allowed_extensions if allowed_extensions is not None else cls.ALLOWED_FILE_EXTENSIONS

        file_ext = Path(filename).suffix.lower()
        return file_ext in [ext.lower() for ext in extensions_to_check]

# Create global config instance
config = Config()

# Ensure directories exist on import
config.ensure_directories()
