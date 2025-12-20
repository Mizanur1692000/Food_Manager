"""
Structured logging for recipe imports
Tracks extraction, parsing, validation, and mapping decisions
"""

import json
import os
from datetime import datetime
from typing import Dict, Any
from pathlib import Path


# Log file path
LOG_DIR = Path("logs")
LOG_FILE = LOG_DIR / "recipe_imports.jsonl"


def ensure_log_directory():
    """Create logs directory if it doesn't exist"""
    LOG_DIR.mkdir(exist_ok=True)


def log_import_event(event_type: str, file_info: Dict[str, Any], details: Dict[str, Any]):
    """
    Write structured JSON log entry

    Args:
        event_type: Type of event (upload, extract, route, parse, validate, map, save, error)
        file_info: Dict with filename, hash, size
        details: Event-specific details
    """
    try:
        ensure_log_directory()

        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "event_type": event_type,
            "file": {
                "name": file_info.get("filename", "unknown"),
                "hash": file_info.get("file_hash", ""),
                "size_bytes": file_info.get("file_size", 0),
                "type": file_info.get("file_type", "unknown")
            },
            "details": details
        }

        # Append to log file
        with open(LOG_FILE, 'a', encoding='utf-8') as f:
            f.write(json.dumps(log_entry) + '\n')

    except Exception as e:
        # Don't fail the import if logging fails
        print(f"Warning: Failed to write log: {e}")


def log_file_upload(file_info: Dict[str, Any]):
    """Log file upload event"""
    log_import_event(
        "upload",
        file_info,
        {
            "action": "file_uploaded",
            "mime_type": file_info.get("mime_type", ""),
        }
    )


def log_extraction(file_info: Dict[str, Any], extraction_result: Dict[str, Any]):
    """Log text extraction event"""
    details = {
        "action": "text_extracted",
        "status": extraction_result.get("status", "unknown"),
        "text_length": len(extraction_result.get("text", "")),
    }

    # Add type-specific details
    if file_info.get("file_type") == "pdf":
        details["total_pages"] = extraction_result.get("total_pages", 0)
        details["text_pages"] = extraction_result.get("text_pages", 0)
        details["vision_pages"] = extraction_result.get("vision_pages", 0)
    elif file_info.get("file_type") == "csv":
        details["structured"] = extraction_result.get("structured", False)
        details["row_count"] = extraction_result.get("row_count", 0)
    elif file_info.get("file_type") == "xlsx":
        details["sheet_count"] = extraction_result.get("sheet_count", 0)

    log_import_event("extract", file_info, details)


def log_pdf_routing(file_info: Dict[str, Any], pages: list):
    """Log PDF per-page routing decisions"""
    routing_summary = {
        "action": "pdf_routing",
        "total_pages": len(pages),
        "routes": {}
    }

    # Count routes
    for page in pages:
        route = page.get("route", "unknown")
        routing_summary["routes"][route] = routing_summary["routes"].get(route, 0) + 1

    # Add confidence details
    low_confidence_pages = [
        p["page_number"] for p in pages
        if not p.get("confidence", {}).get("is_confident", True)
    ]

    if low_confidence_pages:
        routing_summary["low_confidence_pages"] = low_confidence_pages

    log_import_event("route", file_info, routing_summary)


def log_parsing(file_info: Dict[str, Any], parse_result: Dict[str, Any]):
    """Log Claude parsing event"""
    details = {
        "action": "claude_parsed",
        "status": parse_result.get("status", "unknown"),
    }

    if parse_result.get("recipe"):
        recipe = parse_result["recipe"]
        details["recipe_name"] = recipe.get("name", "Unknown")
        details["ingredient_count"] = len(recipe.get("ingredients", []))
        details["has_instructions"] = bool(recipe.get("instructions"))

    log_import_event("parse", file_info, details)


def log_validation(file_info: Dict[str, Any], validation_result: Dict[str, Any]):
    """Log Pydantic validation event"""
    details = {
        "action": "validated",
        "valid": validation_result.get("valid", False),
        "error_count": len(validation_result.get("errors", []))
    }

    if validation_result.get("errors"):
        details["errors"] = validation_result["errors"][:5]  # First 5 errors

    log_import_event("validate", file_info, details)


def log_mapping(file_info: Dict[str, Any], mapping_stats: Dict[str, Any]):
    """Log ingredient mapping event"""
    details = {
        "action": "ingredients_mapped",
        "total_ingredients": mapping_stats.get("total", 0),
        "auto_mapped": mapping_stats.get("auto_mapped", 0),
        "warn_mapped": mapping_stats.get("warn_mapped", 0),
        "unmapped": mapping_stats.get("unmapped", 0),
        "match_rate": mapping_stats.get("match_rate", 0)
    }

    log_import_event("map", file_info, details)


def log_save(file_info: Dict[str, Any], recipe_name: str, success: bool):
    """Log recipe save event"""
    details = {
        "action": "recipe_saved",
        "recipe_name": recipe_name,
        "success": success
    }

    log_import_event("save", file_info, details)


def log_error(file_info: Dict[str, Any], error_type: str, error_message: str):
    """Log error event"""
    details = {
        "action": "error",
        "error_type": error_type,
        "error_message": error_message[:500]  # Truncate long errors
    }

    log_import_event("error", file_info, details)


def get_import_logs(limit: int = 100) -> list:
    """
    Read recent import logs

    Args:
        limit: Maximum number of log entries to return

    Returns:
        List of log entries (most recent first)
    """
    try:
        if not LOG_FILE.exists():
            return []

        logs = []
        with open(LOG_FILE, 'r', encoding='utf-8') as f:
            for line in f:
                if line.strip():
                    try:
                        logs.append(json.loads(line))
                    except json.JSONDecodeError:
                        continue

        # Return most recent first
        return logs[-limit:][::-1]

    except Exception as e:
        print(f"Error reading logs: {e}")
        return []


def get_import_summary() -> Dict[str, Any]:
    """
    Get summary statistics of imports

    Returns:
        Dict with counts and success rates
    """
    try:
        logs = get_import_logs(limit=1000)

        summary = {
            "total_imports": 0,
            "successful_imports": 0,
            "failed_imports": 0,
            "by_file_type": {},
            "total_recipes_saved": 0,
            "total_pages_processed": 0,
            "vision_pages_used": 0,
        }

        file_hashes = set()

        for log in logs:
            event_type = log.get("event_type")
            file_hash = log.get("file", {}).get("hash")

            if event_type == "upload" and file_hash:
                file_hashes.add(file_hash)
                summary["total_imports"] += 1

                file_type = log.get("file", {}).get("type", "unknown")
                summary["by_file_type"][file_type] = summary["by_file_type"].get(file_type, 0) + 1

            elif event_type == "save":
                if log.get("details", {}).get("success"):
                    summary["successful_imports"] += 1
                    summary["total_recipes_saved"] += 1

            elif event_type == "error":
                summary["failed_imports"] += 1

            elif event_type == "route":
                details = log.get("details", {})
                summary["total_pages_processed"] += details.get("total_pages", 0)
                summary["vision_pages_used"] += details.get("routes", {}).get("vision", 0)

        summary["unique_files"] = len(file_hashes)

        if summary["total_imports"] > 0:
            summary["success_rate"] = round(
                summary["successful_imports"] / summary["total_imports"] * 100, 1
            )
        else:
            summary["success_rate"] = 0

        return summary

    except Exception as e:
        print(f"Error generating summary: {e}")
        return {}

