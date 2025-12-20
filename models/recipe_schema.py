"""
Pydantic schemas for recipe import validation
Ensures Claude AI output meets expected format and data types
"""

from pydantic import BaseModel, Field, field_validator, ConfigDict
from typing import List, Optional, Dict, Any
from datetime import datetime
from uuid import uuid4
import re


class PageProvenanceSchema(BaseModel):
    """Tracks how each page was processed"""
    page_number: int = Field(..., ge=1, description="Page number in source document")
    route: str = Field(..., pattern="^(text|vision)$", description="Processing route: text or vision")
    confidence: Dict[str, Any] = Field(default_factory=dict, description="Confidence metrics")

    model_config = ConfigDict(extra='allow')


class SourceMetadataSchema(BaseModel):
    """Source file information"""
    filename: str = Field(..., min_length=1, description="Original filename")
    file_type: str = Field(..., description="File type: pdf, docx, csv, xlsx, image")
    file_hash: Optional[str] = Field(None, description="SHA256 hash for duplicate detection")
    pages: Optional[List[PageProvenanceSchema]] = Field(default_factory=list, description="Page processing details")

    model_config = ConfigDict(extra='allow')


class AuditSchema(BaseModel):
    """Audit trail for recipe creation"""
    created_by: str = Field(default="system", description="User or system that created the recipe")
    created_at: str = Field(default_factory=lambda: datetime.now().isoformat(), description="ISO8601 timestamp")

    model_config = ConfigDict(extra='allow')


class IngredientSchema(BaseModel):
    """Individual ingredient with mapping and cost info"""
    raw_name: str = Field(..., min_length=1, description="Original ingredient name from source")
    mapped_name: Optional[str] = Field(None, description="Matched product name from database")
    quantity: float = Field(..., gt=0, description="Numeric quantity")
    uom: str = Field(..., min_length=1, description="Unit of measure")
    quantity_oz: Optional[float] = Field(None, ge=0, description="Converted quantity in ounces")
    price_per_oz: Optional[float] = Field(None, ge=0, description="Price per ounce from product database")
    total_cost: Optional[float] = Field(None, ge=0, description="Total cost for this ingredient")
    mapping_confidence: Optional[float] = Field(None, ge=0, le=100, description="Fuzzy match confidence 0-100")
    confidence_badge: Optional[str] = Field(None, pattern="^(green|yellow|red)?$", description="UI badge color")
    estimate: bool = Field(default=False, description="True if quantity was estimated from range")

    @field_validator('uom')
    @classmethod
    def validate_uom(cls, v: str) -> str:
        """Ensure UOM is not empty after stripping"""
        if not v.strip():
            raise ValueError("UOM cannot be empty")
        return v.strip().lower()

    @field_validator('quantity')
    @classmethod
    def validate_quantity(cls, v: float) -> float:
        """Ensure quantity is positive and reasonable"""
        if v <= 0:
            raise ValueError("Quantity must be positive")
        if v > 10000:
            raise ValueError("Quantity seems unreasonably large (>10000)")
        return v

    model_config = ConfigDict(extra='allow')


class AllergenMetadataSchema(BaseModel):
    """
    Detailed metadata for allergen detection and tracking.
    Provides audit information, detection confidence, and breakdown.
    """
    detection_methods: List[str] = Field(
        default_factory=list,
        description="Detection methods used (e.g. ['ai', 'database', 'manual'])"
    )
    last_updated: str = Field(
        default_factory=lambda: datetime.now().isoformat(timespec='seconds'),
        description="ISO8601 timestamp for most recent allergen update"
    )
    total_detected: int = Field(
        default=0, ge=0,
        description="Total distinct allergens detected"
    )
    fda_top_9_count: int = Field(
        default=0, ge=0,
        description="Number of FDA top 9 allergens present"
    )
    detected_allergens: List[str] = Field(
        default_factory=list,
        description="Names of all distinct detected allergens (for quick access)"
    )
    fda_allergens: List[str] = Field(
        default_factory=list,
        description="Subset of detected allergens belonging to the FDA Top 9 list"
    )
    confidence: Optional[float] = Field(
        None, ge=0, le=100,
        description="Optional average confidence level as percent (0-100) if AI detection was used"
    )
    reviewed_by_human: bool = Field(
        default=False,
        description="True if a human validated or corrected the allergen list"
    )

    model_config = ConfigDict(extra='allow')


class RecipeSchema(BaseModel):
    """Complete recipe structure with validation"""
    recipe_id: str = Field(default_factory=lambda: str(uuid4()), description="Unique recipe identifier")
    name: str = Field(..., min_length=1, max_length=200, description="Recipe name")
    description: Optional[str] = Field(None, description="Recipe description")
    yield_oz: Optional[float] = Field(None, ge=0, description="Total yield in ounces")
    portion_oz: Optional[float] = Field(None, ge=0, description="Portion size in ounces")
    servings: int = Field(default=4, ge=1, le=1000, description="Number of servings")
    prep_time: int = Field(default=0, ge=0, description="Prep time in minutes")
    cook_time: int = Field(default=0, ge=0, description="Cook time in minutes")
    category: str = Field(default="Other", description="Recipe category")
    ingredients: List[IngredientSchema] = Field(..., min_length=1, description="List of ingredients")
    instructions: List[str] = Field(default_factory=list, description="Cooking instructions as steps")
    allergens: List[str] = Field(default_factory=list, description="List of allergens")
    allergen_details: Optional[Dict[str, Any]] = Field(None, description="Detailed allergen detection information")
    allergen_metadata: Optional[AllergenMetadataSchema] = Field(None, description="Allergen detection metadata")
    source: Optional[SourceMetadataSchema] = Field(None, description="Source file metadata")
    audit: AuditSchema = Field(default_factory=AuditSchema, description="Audit information")

    @field_validator('name')
    @classmethod
    def validate_name(cls, v: str) -> str:
        """Clean and validate recipe name"""
        name = v.strip()
        if not name:
            raise ValueError("Recipe name cannot be empty")
        return name

    @field_validator('ingredients')
    @classmethod
    def validate_ingredients(cls, v: List[IngredientSchema]) -> List[IngredientSchema]:
        """Ensure at least one ingredient exists"""
        if not v:
            raise ValueError("Recipe must have at least one ingredient")
        return v

    @field_validator('category')
    @classmethod
    def validate_category(cls, v: str) -> str:
        """Ensure category is valid"""
        valid_categories = [
            "Main Course", "Appetizer", "Dessert", "Soup", "Salad",
            "Side Dish", "Beverage", "Sauce", "Dressing", "Marinade",
            "Prep Recipe", "Bar", "Other"
        ]
        if v not in valid_categories:
            # Allow it but normalize
            return "Other"
        return v

    model_config = ConfigDict(extra='allow')


def validate_recipe_dict(recipe_dict: Dict[str, Any]) -> tuple[bool, Optional[RecipeSchema], List[str]]:
    """
    Validate a recipe dictionary against the schema

    Returns:
        tuple: (is_valid, validated_recipe or None, list of error messages)
    """
    try:
        validated = RecipeSchema(**recipe_dict)
        return True, validated, []
    except Exception as e:
        # Extract error messages
        errors = []
        if hasattr(e, 'errors'):
            for error in e.errors():
                loc = " -> ".join(str(l) for l in error['loc'])
                msg = error['msg']
                errors.append(f"{loc}: {msg}")
        else:
            errors.append(str(e))

        return False, None, errors


def create_ingredient_dict(
    raw_name: str,
    quantity: float,
    uom: str,
    mapped_name: Optional[str] = None,
    **kwargs
) -> Dict[str, Any]:
    """
    Helper to create a valid ingredient dictionary
    """
    ingredient = {
        "raw_name": raw_name,
        "quantity": quantity,
        "uom": uom,
        "mapped_name": mapped_name,
    }
    ingredient.update(kwargs)
    return ingredient

