# Allergen Management Feature Guide

## Overview

The Allergen Management feature provides comprehensive allergen detection, tracking, and reporting capabilities for your restaurant recipes. This feature combines AI-powered analysis, database matching, and manual tagging to help ensure guest safety and regulatory compliance.

## Key Features

### 1. **Multi-Method Allergen Detection**
- **AI Detection**: Uses Claude AI to analyze ingredients and identify potential allergens
- **Database Matching**: Fuzzy matches ingredients against a comprehensive allergen database
- **Manual Tagging**: Allows staff to manually tag allergens for accuracy

### 2. **FDA Top 9 Allergens**
The system specifically tracks the FDA's major food allergens:
1. Milk (dairy products)
2. Eggs
3. Fish (finned fish)
4. Shellfish (crustacean shellfish)
5. Tree nuts (almonds, walnuts, cashews, etc.)
6. Peanuts
7. Wheat
8. Soybeans (soy)
9. Sesame

### 3. **Additional Allergens**
Also tracks common allergens and sensitivities:
- Gluten
- Corn
- Sulfites
- Nightshades (tomatoes, peppers, eggplant)
- Mustard
- Celery
- Lupin

### 4. **QR Code Generation**
- Creates QR codes that link to public allergen reports
- Codes can be printed and displayed at point-of-sale
- Guests can scan codes with their phones to view allergen information
- No login required for guests

### 5. **Batch Processing**
- Analyze multiple recipes at once
- Auto-save results to recipe database
- Ideal for menu updates and new recipe additions

## Getting Started

### Prerequisites

1. **Install Required Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

2. **Configure Claude API Key (Optional)**
   For AI-powered detection, set your Anthropic API key:

   **Windows (PowerShell):**
   ```powershell
   $env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
   ```

   **Mac/Linux:**
   ```bash
   export ANTHROPIC_API_KEY='sk-ant-your-key-here'
   ```

3. **Migrate Existing Recipes**
   If you have existing recipes without `recipe_id` fields:
   ```bash
   python utils/migrate_recipe_ids.py
   ```

### Accessing the Feature

1. Start the Streamlit app:
   ```bash
   streamlit run app.py
   ```

2. Navigate to **Allergen Management** in the sidebar

## Using the Feature

### Analyze Individual Recipe

1. **Select Recipe**: Choose a recipe from the dropdown
2. **Run Detection Methods**:
   - Click **🚀 Run AI Analysis** to use Claude AI
   - Click **🔍 Run Database Match** to use fuzzy matching
   - Check boxes for **Manual Allergen Tagging**
3. **Combine Results**: Click **🔗 Combine All Detections** to merge all findings
4. **Review Report**: Check detected allergens with confidence scores
5. **Save**: Click **💾 Save to Recipe** to persist allergen data
6. **Generate QR Code**: Create a QR code linking to the public report

### Batch Analysis

1. Go to the **📊 Batch Analysis** tab
2. Select multiple recipes using the multiselect dropdown
3. Choose detection method (Database, AI, or Both)
4. Enable **Auto-save results** if desired
5. Click **🚀 Run Batch Analysis**
6. Review results table and summary metrics

### View Reports

1. Go to the **📋 View Reports** tab
2. Select a recipe with allergen data
3. View comprehensive allergen report
4. Export report as JSON for records

## QR Code Usage

### For Restaurant Staff

1. Generate QR code for each recipe/menu item
2. Download QR code (PNG for printing, SVG for design work)
3. Print and display QR codes:
   - On table tents
   - In menu descriptions
   - At POS stations
   - On digital menu boards

### For Guests

1. Guests scan QR code with smartphone camera
2. Browser opens to public allergen report page
3. Report shows:
   - Recipe name and ingredients
   - FDA Top 9 allergens (highlighted)
   - Additional allergens
   - Confidence scores
   - Important disclaimers

**No app installation or login required!**

## Allergen Database

The system includes a comprehensive allergen database with:
- **900+ ingredient patterns** mapped to allergens
- **16 allergen categories** with metadata
- **Icons and descriptions** for clear communication
- **Confidence scoring** for fuzzy matches

### Database Location
`data/allergen_database.json`

You can customize this file to add more patterns or adjust matching rules.

## Data Storage

### Recipe Data Structure

When allergen analysis is saved, the following fields are added to the recipe:

```json
{
  "name": "Recipe Name",
  "recipe_id": "unique-uuid",
  "allergens": ["milk", "eggs", "wheat"],
  "allergen_details": {
    "milk": {
      "display_name": "Milk/Dairy",
      "confidence": 95,
      "detection_method": "ai",
      "sources": ["ai", "database"],
      "matched_ingredients": [...],
      "metadata": {...}
    }
  },
  "allergen_metadata": {
    "detection_methods": ["ai", "database", "manual"],
    "last_updated": "2025-10-20T10:30:00",
    "total_detected": 3,
    "fda_top_9_count": 3
  }
}
```

### File Locations

- **Recipes**: `data/recipes.json`
- **Allergen Database**: `data/allergen_database.json`
- **QR Codes**: `data/allergen_qr_codes/`

## Public Allergen Report Page

### URL Format
```
http://your-domain:8501/public_allergen_report?recipe_id={recipe_id}
```

### Features
- Mobile-friendly responsive design
- High-contrast for accessibility
- Clear visual indicators (icons, color coding)
- Expandable ingredient details
- Important disclaimer notices
- No authentication required

### Customization

The public report page includes CSS styling that can be customized in:
`pages/public_allergen_report.py`

Look for the `st.markdown()` section with `<style>` tags.

## Best Practices

### For Accuracy

1. **Use Multiple Detection Methods**: Combine AI, database, and manual tagging
2. **Review AI Results**: AI may flag potential allergens that require verification
3. **Keep Database Updated**: Add new ingredient patterns as needed
4. **Manual Verification**: Always have trained staff review allergen reports
5. **Update Regularly**: Re-analyze recipes when ingredients change

### For Safety

1. **Display Disclaimers**: Always include cross-contamination warnings
2. **Train Staff**: Ensure servers understand allergen information
3. **Update Promptly**: Re-analyze recipes when suppliers or ingredients change
4. **Verify Confidence**: Pay attention to confidence scores (aim for 90%+)
5. **Document Changes**: Keep records of allergen analysis dates

### For Guest Communication

1. **Clear Signage**: Display QR codes prominently
2. **Verbal Communication**: Train staff to ask about allergies
3. **Emergency Protocols**: Have procedures for allergic reactions
4. **Manager Availability**: Ensure manager can discuss allergens with guests
5. **Ingredient Lists**: Keep printed ingredient lists available

## Troubleshooting

### AI Detection Not Working

**Issue**: AI analysis button doesn't work or returns errors

**Solutions**:
1. Verify API key is set: Check environment variable `ANTHROPIC_API_KEY`
2. Check API key validity at https://console.anthropic.com/
3. Ensure internet connection is active
4. Check Anthropic API status

### QR Code Not Generating

**Issue**: QR code generation fails

**Solutions**:
1. Verify recipe has `recipe_id` field (run migration script)
2. Check `data/allergen_qr_codes/` directory exists and is writable
3. Ensure qrcode and segno libraries are installed
4. Check base URL is correctly configured

### Public Report Page Not Loading

**Issue**: QR code scans lead to error page

**Solutions**:
1. Verify Streamlit app is running and accessible
2. Check recipe_id in URL is valid
3. Ensure recipe has allergen data saved
4. Verify public_allergen_report.py file exists in pages/

### Low Confidence Scores

**Issue**: Database matching returns low confidence scores

**Solutions**:
1. Lower confidence threshold slider (min 50%)
2. Add ingredient patterns to allergen database
3. Use manual tagging for accuracy
4. Consider using AI detection for better matching

## API Reference

### Key Functions (modules/allergen_engine.py)

#### `detect_allergens_ai(ingredients, api_key, recipe_name)`
Uses Claude AI to detect allergens from ingredients

**Parameters**:
- `ingredients`: List of ingredient dictionaries
- `api_key`: Anthropic API key
- `recipe_name`: Recipe name for context

**Returns**: Dictionary with detected allergens and details

#### `detect_allergens_database(ingredients, min_confidence)`
Fuzzy matches ingredients against allergen database

**Parameters**:
- `ingredients`: List of ingredient dictionaries
- `min_confidence`: Minimum match confidence (0-100)

**Returns**: Dictionary with detected allergens and match details

#### `combine_allergen_detections(db_result, ai_result, manual_allergens)`
Combines results from multiple detection methods

**Parameters**:
- `db_result`: Database detection result
- `ai_result`: AI detection result
- `manual_allergens`: List of manually selected allergens

**Returns**: Combined allergen data with merged confidence scores

#### `generate_qr_code(recipe_id, recipe_name, base_url)`
Generates PNG QR code linking to public report

**Parameters**:
- `recipe_id`: Unique recipe identifier
- `recipe_name`: Recipe name (for filename)
- `base_url`: Base URL of Streamlit app

**Returns**: Tuple of (file_path, image_bytes)

#### `save_allergen_data(recipe_name, allergen_data)`
Saves allergen data to recipe in recipes.json

**Parameters**:
- `recipe_name`: Name of recipe
- `allergen_data`: Allergen detection data

**Returns**: Boolean success status

## Compliance Notes

### FDA Food Allergen Labeling

This feature is designed to help with allergen awareness but does not replace:
- Professional food safety consultation
- Legal compliance review
- Proper staff training
- Standard operating procedures

**Always**:
- Consult with food safety professionals
- Review local regulations
- Train staff on allergen protocols
- Maintain documentation
- Update procedures regularly

### Disclaimers

The allergen detection system:
- Provides guidance, not guarantees
- May not catch all allergen sources
- Cannot prevent cross-contamination
- Should be used as part of comprehensive allergen program

## Support

### Documentation
- Main README: `README.md`
- Recipe Import Guide: `RECIPE_IMPORT_GUIDE.md`
- AI Recipe Generator: `AI_RECIPE_GENERATOR_GUIDE.md`

### Community
For questions, suggestions, or issues:
1. Check existing documentation
2. Review allergen database for customization
3. Contact system administrator

## Updates and Maintenance

### Regular Tasks
- Review allergen database quarterly
- Update ingredient patterns as menu changes
- Re-analyze recipes when suppliers change
- Train new staff on feature usage
- Audit QR codes for accuracy

### Version History
- **v1.0** (2025-10-20): Initial allergen management release
  - AI-powered detection
  - Database fuzzy matching
  - Manual tagging
  - QR code generation
  - Public report pages
  - Batch processing

## Future Enhancements

Potential features for future releases:
- Multi-language support for reports
- Email/SMS allergen alerts
- Integration with POS systems
- Dietary restriction tracking (vegan, vegetarian, etc.)
- Nutrition information alongside allergens
- Guest allergen profile management
- Allergen trend analytics

---

**Remember**: Guest safety is paramount. This tool assists but doesn't replace proper training, procedures, and vigilance.

