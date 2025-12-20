
import argparse
import json
import requests

BASE_URL = "http://localhost:8000"

def print_response(response):
    """Helper to print API response nicely."""
    print(f"Status Code: {response.status_code}")
    try:
        print("Response JSON:")
        print(json.dumps(response.json(), indent=2))
    except json.JSONDecodeError:
        print("Response Text:")
        print(response.text)
    print("-" * 30 + "\n")

def test_generate_ai_recipe(prompt, save=False):
    """Simulates POST /recipes/generate-ai"""
    print(f"--- Running: Generate AI Recipe (Save: {save}) ---")
    url = f"{BASE_URL}/recipes/generate-ai?save={str(save).lower()}"
    payload = {
        "prompt": prompt,
        "match_threshold": 75
    }
    try:
        response = requests.post(url, json=payload)
        print_response(response)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Is the API server running? ({e})")

def test_analyze_recipe_allergens(recipe_name, save=False):
    """Simulates POST /allergens/analyze-recipe"""
    print(f"--- Running: Analyze Recipe Allergens (Save: {save}) ---")
    url = f"{BASE_URL}/allergens/analyze-recipe?save={str(save).lower()}"
    payload = {
        "recipe_name": recipe_name,
        "db_confidence": 70
    }
    try:
        response = requests.post(url, json=payload)
        print_response(response)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Is the API server running? ({e})")

def test_generate_qr_code(recipe_name):
    """Simulates POST /allergens/generate-qr"""
    print("--- Running: Generate Allergen QR Code ---")
    url = f"{BASE_URL}/allergens/generate-qr"
    payload = {
        "recipe_name": recipe_name,
        "base_url": "http://example.com"
    }
    try:
        response = requests.post(url, json=payload)
        print_response(response)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Is the API server running? ({e})")

def main():
    parser = argparse.ArgumentParser(description="AI API Test Runner for Food Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for generating a recipe
    parser_gen = subparsers.add_parser("generate_recipe", help="Generate a recipe using AI")
    parser_gen.add_argument("prompt", help="The text prompt for the AI recipe generator")
    parser_gen.add_argument("--save", action="store_true", help="Save the generated recipe to the database")

    # Sub-parser for analyzing allergens
    parser_analyze = subparsers.add_parser("analyze_allergens", help="Analyze a recipe for allergens")
    parser_analyze.add_argument("recipe_name", help="The name of the recipe to analyze")
    parser_analyze.add_argument("--save", action="store_true", help="Save the allergen data to the recipe")
    
    # Sub-parser for generating a QR code
    parser_qr = subparsers.add_parser("generate_qr", help="Generate a QR code for a recipe's allergen report")
    parser_qr.add_argument("recipe_name", help="The name of the recipe for the QR code")

    args = parser.parse_args()

    if args.command == "generate_recipe":
        test_generate_ai_recipe(args.prompt, args.save)
    elif args.command == "analyze_allergens":
        test_analyze_recipe_allergens(args.recipe_name, args.save)
    elif args.command == "generate_qr":
        test_generate_qr_code(args.recipe_name)

if __name__ == "__main__":
    # First, ensure 'requests' is installed
    try:
        import requests
    except ImportError:
        print("The 'requests' library is not installed. Please run 'pip install requests'.")
        exit(1)
        
    main()
