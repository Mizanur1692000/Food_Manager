# Recipe Import Feature Guide

## Overview

The Recipe Import feature allows you to upload recipe files in multiple formats and automatically convert them into structured recipes in your system. The feature uses Claude AI for intelligent text extraction and recipe parsing.

## Supported File Formats

- **DOCX** - Microsoft Word documents
- **PDF** - Adobe PDF files (both text-based and scanned)
- **CSV** - Comma-separated values with ingredient lists
- **XLSX/XLS** - Microsoft Excel spreadsheets
- **Images** - PNG, JPG, JPEG (recipe photos or scans)

## Features

### 1. Intelligent PDF Processing

- **Per-page routing**: Mixed PDFs with both text and scanned pages are handled automatically
- **Multi-metric confidence**: Uses character count, word count, and UOM (unit of measure) detection to determine best extraction method
- **Vision fallback**: Automatically uses Claude Vision API for low-confidence or scanned pages

### 2. Text Extraction

- **Native extraction**: Uses python-docx, pdfplumber, and openpyxl for clean text extraction
- **Header detection**: Automatically detects ingredient, quantity, and UOM columns in CSV/Excel files
- **Vision extraction**: Claude Vision API for images and scanned documents

### 3. Recipe Parsing

- **Structured extraction**: Claude AI extracts recipe name, ingredients, quantities, units, instructions, and more
- **Unit normalization**: Handles fractions (½, ¼), ranges (1-2 tsp), and various unit formats
- **Allergen detection**: Automatically identifies common allergens

### 4. Ingredient Mapping

- **Fuzzy matching**: Maps extracted ingredients to your product database using RapidFuzz
- **Tiered confidence**:
  - 🟢 **Green (≥90%)**: Auto-mapped with high confidence
  - 🟡 **Yellow (70-89%)**: Mapped with warning - needs review
  - 🔴 **Red (<70%)**: Unmapped - add to product database or map manually

### 5. Cost Calculation

- Automatically calculates ingredient costs based on your product database
- Converts all quantities to ounces for accurate costing
- Shows per-ingredient and total recipe costs

### 6. Validation

- **Pydantic schema validation**: Ensures data consistency and type safety
- **Error reporting**: Clear messages for validation failures
- **Graceful handling**: Allows partial saves with warnings

## How to Use

### Prerequisites

1. **Claude API Key**: Required for AI processing

   ```bash
   # Windows PowerShell
   $env:ANTHROPIC_API_KEY='sk-ant-...'

   # Mac/Linux
   export ANTHROPIC_API_KEY='sk-ant-...'
   ```

2. **Product Database**: Add products to your database first for accurate ingredient mapping

### Step-by-Step Guide

1. **Navigate to Recipe Builder**
   - Go to the "Recipe Builder" page
   - Click on the "📥 Import Recipes" tab

2. **Upload Files**
   - Click "Choose recipe files to import"
   - Select one or more recipe files (max 20MB each)
   - Supported formats: DOCX, PDF, CSV, XLSX, PNG, JPG, JPEG

3. **Process with AI**
   - Click the "🤖 Process with AI" button
   - Watch the progress for each file:
     - 📄 Extracting text...
     - 📑 PDF routing (if applicable)
     - 🧠 Parsing recipe...
     - ✅ Complete

4. **Review Imported Recipes**
   - Each processed file appears in an expandable panel
   - Review:
     - **Validation status**: Check for any warnings
     - **Mapping statistics**: See how many ingredients were mapped
     - **Recipe details**: Name, description, servings, times, category
     - **Ingredients table**: Review mapped products and costs
     - **Instructions**: Step-by-step cooking instructions
     - **Total cost**: Calculated recipe cost

5. **Edit as Needed**
   - Modify recipe name, description, servings, times, or category
   - Review ingredient mappings (especially yellow and red badges)
   - Check instructions for accuracy

6. **Save or Discard**
   - Click "💾 Save Recipe" to add to your recipe database
   - Click "🗑️ Discard" to remove without saving
   - Click "📋 View Details" to see full JSON data

## Best Practices

### For Best Results

1. **Clean Source Files**
   - Use clear, high-resolution images (300 DPI or higher)
   - Ensure text is readable in PDFs
   - Structure CSV/Excel files with headers (ingredient, quantity, unit)

2. **Product Database**
   - Keep your product database updated
   - Use consistent product naming
   - Include common ingredients and their units

3. **Review Mappings**
   - Always review yellow (⚠️) and red (❌) badge ingredients
   - Verify quantities and units match your expectations
   - Check that costs are calculated correctly

4. **Multiple Files**
   - Process similar recipe types together
   - Each file becomes a separate recipe
   - Review all before saving

### Troubleshooting

**"Extraction failed"**

- File may be too large (>20MB)
- PDF may have too many pages (>50)
- File may be corrupted or password-protected

**"Parsing failed"**

- Extracted text may not contain recognizable recipe format
- Try a different file format or clearer scan

**"No ingredients mapped"**

- Product database may be empty
- Ingredient names may not match products
- Add products to database first

**Low confidence badges**

- Claude may have difficulty reading ingredient names
- Manually verify and correct as needed
- Consider adding products to your database

## Technical Details

### Text Confidence Metrics

Per-page PDFs are routed using these thresholds:

- **Minimum characters**: 200
- **Minimum words**: 30
- **Minimum UOM hits**: 2 (oz, lb, cup, tsp, etc.)

If 2 or more metrics fail, the page is routed to Claude Vision API.

### Unit Conversion

The system handles:

- Unicode fractions: ½ → 0.5, ¼ → 0.25, ¾ → 0.75
- ASCII fractions: 1/2 → 0.5, 3/4 → 0.75
- Ranges: 1-2 tsp → 1.5 tsp (marked as estimate)
- Unit normalization: tablespoon/tbsp/T → tbsp

All quantities are converted to ounces for cost calculation.

### Security Features

- **Macro rejection**: .xlsm and .docm files are rejected
- **MIME validation**: File types are verified
- **EXIF stripping**: Image metadata is removed
- **Content hashing**: Duplicate detection via SHA256

### Structured Logging

All import events are logged to `logs/recipe_imports.jsonl`:

- File upload
- Text extraction
- PDF routing decisions
- Claude parsing
- Validation results
- Ingredient mapping stats
- Save success/failure

## Limitations

1. **File Size**: Maximum 20MB per file
2. **PDF Pages**: Maximum 50 pages per PDF
3. **API Costs**: Claude AI usage incurs API costs
4. **Accuracy**: AI parsing may require manual review
5. **Languages**: Best results with English recipes

## Future Enhancements

- Bulk recipe import from recipe websites
- Custom ingredient mapping rules
- Manual page selection for PDFs
- Nutrition fact extraction
- Recipe scaling adjustments
- Export imported recipes to various formats

## Support

For issues or questions:

1. Check the logs: `logs/recipe_imports.jsonl`
2. Review validation errors in the UI
3. Verify Claude API key is set correctly
4. Ensure product database has matching products

## Example Workflows

### Workflow 1: Import Scanned Recipe Card

1. Take a photo of recipe card (clear, well-lit)
2. Upload JPG/PNG to import tab
3. Click "Process with AI"
4. Review extracted recipe
5. Verify ingredients are mapped correctly
6. Save to database

### Workflow 2: Import PDF Cookbook

1. Upload PDF file (multiple recipes)
2. System processes each page
3. Review all extracted recipes
4. Edit names, categories, and mappings
5. Save desired recipes
6. Discard duplicates or unwanted recipes

### Workflow 3: Import Excel Ingredient List

1. Prepare Excel with columns: Ingredient, Quantity, Unit
2. Upload XLSX file
3. System detects structured format
4. Claude adds recipe details
5. Review and adjust
6. Save recipe

## API Key Management

Get your Claude API key from: <https://console.anthropic.com/settings/keys>

Store it as an environment variable or in `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-..."
```

## Cost Considerations

Claude API pricing (as of 2025):

- Vision API: ~$3 per 1000 images
- Text API: ~$3 per million input tokens

Typical costs per recipe import:

- Text PDF: $0.01 - $0.05
- Scanned PDF: $0.10 - $0.50 (depending on pages)
- Image: $0.03 - $0.10
- DOCX/CSV/Excel: $0.01 - $0.03

## Conclusion

The Recipe Import feature streamlines recipe data entry by leveraging AI to extract and structure recipe information from various file formats. With intelligent routing, fuzzy matching, and comprehensive validation, you can quickly build your recipe database while maintaining accuracy and cost control.
