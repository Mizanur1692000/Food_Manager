"""
Centralized Error Handling for Restaurant Kitchen Inventory App

This module provides comprehensive error handling, logging, and user-friendly
error messages for the application.
"""

import streamlit as st
import logging
import traceback
import sys
from typing import Dict, Any, Optional, Callable
from datetime import datetime
from pathlib import Path

# Import config for error messages
from config import config

# Configure logging
try:
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[
            logging.FileHandler(config.LOG_FILE),
            logging.StreamHandler(sys.stdout)
        ]
    )
except Exception:
    # Fallback if stdout is not available
    logging.basicConfig(
        level=getattr(logging, config.LOG_LEVEL),
        format=config.LOG_FORMAT,
        handlers=[logging.FileHandler(config.LOG_FILE)]
    )
logger = logging.getLogger(__name__)

class AppError(Exception):
    """Base exception class for application errors"""
    def __init__(self, message: str, error_type: str = "unknown_error", details: Optional[Dict[str, Any]] = None):
        self.message = message
        self.error_type = error_type
        self.details = details or {}
        super().__init__(self.message)

class ValidationError(AppError):
    """Exception for validation errors"""
    def __init__(self, field: str, message: str, details: Optional[Dict[str, Any]] = None):
        super().__init__(message, "validation_error", {"field": field, **(details or {})})

class FileError(AppError):
    """Exception for file operation errors"""
    def __init__(self, operation: str, file_path: str, details: Optional[Dict[str, Any]] = None):
        message = f"File operation failed: {operation} on {file_path}"
        super().__init__(message, "file_error", {"operation": operation, "file_path": file_path, **(details or {})})

class DataError(AppError):
    """Exception for data processing errors"""
    def __init__(self, operation: str, details: Optional[Dict[str, Any]] = None):
        message = f"Data operation failed: {operation}"
        super().__init__(message, "data_error", {"operation": operation, **(details or {})})

def handle_error(error: Exception, context: str = "", show_to_user: bool = True) -> None:
    """
    Centralized error handling function
    
    Args:
        error: The exception that occurred
        context: Context where the error occurred
        show_to_user: Whether to show error to user via Streamlit
    """
    # Log the error
    error_msg = f"Error in {context}: {str(error)}"
    logger.error(error_msg)
    logger.error(f"Traceback: {traceback.format_exc()}")
    
    # Show to user if requested
    if show_to_user:
        if isinstance(error, AppError):
            st.error(f"❌ {error.message}")
        else:
            st.error(f"❌ An error occurred: {str(error)}")
        
        # Show additional details in expander for debugging
        with st.expander("🔍 Error Details (Click to expand)"):
            st.code(traceback.format_exc())
            st.write(f"**Error Type:** {type(error).__name__}")
            st.write(f"**Context:** {context}")
            st.write(f"**Timestamp:** {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

def validate_file_upload(uploaded_file, allowed_types: list, max_size_mb: Optional[float] = None) -> tuple[bool, str]:
    """
    Validate uploaded file
    
    Args:
        uploaded_file: Streamlit uploaded file object
        allowed_types: List of allowed file types
        max_size_mb: Maximum file size in MB
    
    Returns:
        tuple[bool, str]: (is_valid, error_message)
    """
    if uploaded_file is None:
        return False, "No file uploaded"
    
    # Check file type
    if uploaded_file.type not in allowed_types:
        return False, f"Invalid file type. Allowed: {', '.join(allowed_types)}"
    
    # Check file size
    if max_size_mb is not None:
        max_size_bytes = max_size_mb * 1024 * 1024
        if uploaded_file.size > max_size_bytes:
            return False, f"File too large. Maximum size: {max_size_mb}MB"
    
    return True, ""

def safe_execute(func: Callable, *args, context: str = "", **kwargs) -> tuple[bool, Any]:
    """
    Safely execute a function with error handling
    
    Args:
        func: Function to execute
        *args: Function arguments
        context: Context for error reporting
        **kwargs: Function keyword arguments
    
    Returns:
        tuple[bool, Any]: (success, result_or_error_message)
    """
    try:
        result = func(*args, **kwargs)
        return True, result
    except Exception as e:
        handle_error(e, context, show_to_user=False)
        return False, str(e)

def validate_data_structure(data: Dict, required_fields: list, context: str = "") -> tuple[bool, list]:
    """
    Validate data structure has required fields
    
    Args:
        data: Data dictionary to validate
        required_fields: List of required field names
        context: Context for error reporting
    
    Returns:
        tuple[bool, list]: (is_valid, list_of_errors)
    """
    errors = []
    
    if not isinstance(data, dict):
        errors.append("Data must be a dictionary")
        return False, errors
    
    for field in required_fields:
        if field not in data or data[field] is None:
            errors.append(f"Missing required field: {field}")
        elif isinstance(data[field], str) and data[field].strip() == "":
            errors.append(f"Required field cannot be empty: {field}")
    
    if errors:
        logger.warning(f"Validation errors in {context}: {errors}")
    
    return len(errors) == 0, errors

def handle_network_error(func: Callable, *args, **kwargs) -> tuple[bool, Any]:
    """
    Handle network-related operations with retry logic
    
    Args:
        func: Function to execute
        *args: Function arguments
        **kwargs: Function keyword arguments
    
    Returns:
        tuple[bool, Any]: (success, result_or_error_message)
    """
    import time
    
    max_retries = 3
    retry_delay = 1  # seconds
    
    for attempt in range(max_retries):
        try:
            result = func(*args, **kwargs)
            return True, result
        except Exception as e:
            if "network" in str(e).lower() or "connection" in str(e).lower():
                if attempt < max_retries - 1:
                    logger.warning(f"Network error, retrying in {retry_delay}s (attempt {attempt + 1}/{max_retries})")
                    time.sleep(retry_delay)
                    retry_delay *= 2  # Exponential backoff
                    continue
                else:
                    logger.error(f"Network operation failed after {max_retries} attempts: {e}")
                    return False, f"Network error after {max_retries} attempts: {str(e)}"
            else:
                # Not a network error, don't retry
                logger.error(f"Non-network error: {e}")
                return False, str(e)
    
    return False, "Unknown error"

def log_operation(operation: str, details: Optional[Dict[str, Any]] = None) -> None:
    """
    Log an operation for debugging and monitoring
    
    Args:
        operation: Name of the operation
        details: Additional details about the operation
    """
    log_entry = {
        "operation": operation,
        "timestamp": datetime.now().isoformat(),
        "details": details or {}
    }
    logger.info(f"Operation: {operation} - {details}")

def create_error_summary(error: Exception) -> Dict[str, Any]:
    """
    Create a summary of an error for reporting
    
    Args:
        error: The exception that occurred
    
    Returns:
        Dict[str, Any]: Error summary
    """
    return {
        "error_type": type(error).__name__,
        "error_message": str(error),
        "timestamp": datetime.now().isoformat(),
        "traceback": traceback.format_exc(),
        "context": getattr(error, 'context', 'unknown')
    }

def display_error_to_user(error: Exception, user_friendly_message: Optional[str] = None) -> None:
    """
    Display error to user in a user-friendly way
    
    Args:
        error: The exception that occurred
        user_friendly_message: Custom user-friendly message
    """
    if user_friendly_message:
        st.error(f"❌ {user_friendly_message}")
    else:
        st.error(f"❌ {str(error)}")
    
    # Show technical details in expander
    with st.expander("🔍 Technical Details"):
        st.code(traceback.format_exc())

def handle_permission_error(operation: str, resource: str) -> None:
    """
    Handle permission-related errors
    
    Args:
        operation: Operation that failed
        resource: Resource that couldn't be accessed
    """
    error_msg = config.get_error_message("permission_error", operation=operation)
    logger.error(f"Permission error: {operation} on {resource}")
    st.error(f"❌ {error_msg}")

def handle_file_error(operation: str, file_path: str, error: Exception) -> None:
    """
    Handle file-related errors
    
    Args:
        operation: File operation that failed
        file_path: Path to the file
        error: The exception that occurred
    """
    error_msg = config.get_error_message("file_not_found", file_path=file_path)
    logger.error(f"File error: {operation} on {file_path} - {error}")
    st.error(f"❌ {error_msg}")

def handle_validation_error(field: str, message: str) -> None:
    """
    Handle validation errors
    
    Args:
        field: Field that failed validation
        message: Validation error message
    """
    error_msg = config.get_error_message("validation_error", field=field, message=message)
    logger.warning(f"Validation error: {field} - {message}")
    st.error(f"❌ {error_msg}")

# Decorator for automatic error handling
def with_error_handling(context: str = ""):
    """
    Decorator to automatically handle errors in functions
    
    Args:
        context: Context for error reporting
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                handle_error(e, context)
                return None
        return wrapper
    return decorator 