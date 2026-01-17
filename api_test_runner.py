
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

def test_generate_ai_recipe(prompt):
    """Call active AI recipe endpoint: POST /recipes/generate"""
    print("--- Running: Generate AI Recipe ---")
    url = f"{BASE_URL}/recipes/generate"
    payload = {"prompt": prompt, "match_threshold": 75}
    try:
        response = requests.post(url, json=payload)
        print_response(response)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Is the API server running? ({e})")

def test_analyze_allergens(ingredients):
    """Call active allergen endpoint: POST /allergens/analyze"""
    print("--- Running: Analyze Allergens ---")
    url = f"{BASE_URL}/allergens/analyze"
    try:
        response = requests.post(url, json=ingredients)
        print_response(response)
    except requests.exceptions.ConnectionError as e:
        print(f"❌ Connection Error: Is the API server running? ({e})")

# Note: legacy QR/recipe-level endpoints are disabled. Use /allergens/analyze.

def main():
    parser = argparse.ArgumentParser(description="AI API Test Runner for Food Manager")
    subparsers = parser.add_subparsers(dest="command", required=True)

    # Sub-parser for generating a recipe (AI)
    parser_gen = subparsers.add_parser("generate_recipe", help="Generate a recipe using AI")
    parser_gen.add_argument("prompt", help="The text prompt for the AI recipe generator")

    # Sub-parser for analyzing allergens (ingredient list)
    parser_analyze = subparsers.add_parser("analyze_allergens", help="Analyze ingredients for allergens")
    parser_analyze.add_argument("ingredients_json", help="JSON array of ingredients (product_name, quantity, unit)")
    
    # Legacy QR endpoint removed from active API; no CLI command.

    args = parser.parse_args()

    if args.command == "generate_recipe":
        test_generate_ai_recipe(args.prompt)
    elif args.command == "analyze_allergens":
        try:
            ingredients = json.loads(args.ingredients_json)
        except json.JSONDecodeError:
            print("Invalid JSON for ingredients. Provide a JSON array.")
            return
        test_analyze_allergens(ingredients)

if __name__ == "__main__":
    # First, ensure 'requests' is installed
    try:
        import requests
    except ImportError:
        print("The 'requests' library is not installed. Please run 'pip install requests'.")
        exit(1)
        
    main()
