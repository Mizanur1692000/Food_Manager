"""
Utility script to add recipe_id to existing recipes that don't have one
Run this once to migrate existing recipes
"""

from modules.recipe_engine import ensure_recipe_ids

if __name__ == "__main__":
    print("Checking for recipes without recipe_id...")
    updated_count = ensure_recipe_ids()

    if updated_count > 0:
        print(f"✅ Added recipe_id to {updated_count} recipe(s)")
    else:
        print("✅ All recipes already have recipe_id")

