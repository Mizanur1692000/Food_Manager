# Recipe Import - Quick Start Guide

## 🚀 Get Started in 5 Minutes

### Step 1: Install Dependencies

```bash
pip install -r requirements.txt
```

This installs all required packages including:

- python-docx (Word files)
- pdfplumber (PDF extraction)
- pydantic (validation)
- pint (unit conversion)
- And more...

### Step 2: Set Claude API Key

**Windows PowerShell:**

```powershell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Mac/Linux:**

```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Or** create `.streamlit/secrets.toml`:

```toml
ANTHROPIC_API_KEY = "sk-ant-your-key-here"
```

Get your API key: <https://console.anthropic.com/settings/keys>

### Step 3: Add Products to Database

Before importing recipes, add some products to your database:

1. Go to "Product Database" page
2. Add common ingredients (flour, sugar, butter, etc.)
3. Include quantities and units

This allows accurate ingredient mapping and cost calculation.

### Step 4: Import Your First Recipe

1. **Navigate**: Go to Recipe Builder → Import Recipes tab
2. **Upload**: Click "Choose recipe files" and select a recipe file
   - Try a PDF, DOCX, or image of a recipe
3. **Process**: Click "🤖 Process with AI"
4. **Review**: Check the extracted recipe
   - Verify recipe name, ingredients, quantities
   - Check ingredient mapping (green = good, yellow = review, red = unmapped)
   - Review total cost
5. **Save**: Click "💾 Save Recipe"

### Step 5: Try Different Formats

Test the feature with various file types:

- **PDF**: Recipe from a cookbook
- **DOCX**: Word document with recipe
- **Image**: Photo of a recipe card
- **Excel**: Ingredient list spreadsheet
- **CSV**: Structured ingredient data

## 💡 Pro Tips

### For Best Results

1. **High-Quality Scans**
   - Use 300 DPI or higher for images
   - Ensure good lighting and contrast
   - Avoid shadows and distortion

2. **Clear Text**
   - Use legible fonts
   - Avoid handwriting (or ensure very clear)
   - Check PDF is not password-protected

3. **Structured Data**
   - Excel/CSV: Use headers (Ingredient, Quantity, Unit)
   - PDFs: Prefer text-based over scanned
   - Word: Use tables for ingredients

4. **Review Mappings**
   - 🟢 Green badges are good to go
   - 🟡 Yellow badges should be reviewed
   - 🔴 Red badges need product database entries

### Common Issues & Solutions

**❌ "API key not found"**

- Set `ANTHROPIC_API_KEY` environment variable
- Or add to `.streamlit/secrets.toml`

**❌ "No products found"**

- Add products to your database first
- Go to Product Database page

**❌ "Extraction failed"**

- Check file size (must be < 20MB)
- Try a different file format
- Ensure file is not corrupted

**⚠️ "Many unmapped ingredients"**

- Add more products to your database
- Use standard ingredient names
- Review and manually map

**⚠️ "Low confidence"**

- Try higher resolution image
- Use text-based PDF instead of scan
- Manually edit extracted text

## 📊 Understanding Results

### Confidence Badges

- **🟢 Green (≥90%)**: Auto-mapped, high confidence
- **🟡 Yellow (70-89%)**: Mapped but needs review
- **🔴 Red (<70%)**: Not mapped, add to database

### Cost Calculation

- All quantities converted to ounces
- Price per oz from your product database
- Total cost = sum of all ingredients
- Unmapped ingredients show $0.00

### Validation Status

- **✅ Valid**: Recipe passed all checks
- **⚠️ Warnings**: Some fields need attention
- **❌ Errors**: Critical issues, cannot save

## 🎯 Example Workflow

1. **Prepare**: Take photo of recipe card with phone
2. **Upload**: Upload JPG to import tab
3. **Process**: Click Process with AI
4. **Wait**: ~30 seconds for extraction and parsing
5. **Review**:
   - Recipe name: ✓
   - Ingredients: 8 found, 6 mapped (🟢), 2 need review (🟡)
   - Cost: $12.50
6. **Edit**: Fix 2 yellow ingredients or add to database
7. **Save**: Click Save Recipe
8. **Done**: Recipe now in your database!

## 🔗 Related Documentation

- **Full Guide**: See `RECIPE_IMPORT_GUIDE.md` for detailed instructions
- **Implementation**: See `RECIPE_IMPORT_IMPLEMENTATION.md` for technical details
- **API Guide**: See `AI_RECIPE_GENERATOR_GUIDE.md` for Claude AI setup

## 🆘 Need Help?

1. Check logs: `logs/recipe_imports.jsonl`
2. Review error messages in UI
3. Verify API key is set
4. Ensure products exist in database
5. Try simpler file format first

## ✨ What's Next?

After importing your first recipe:

- Import multiple recipes at once
- Try different file formats
- Build your recipe database
- Calculate recipe costs
- Generate shopping lists

## 🎉 You're Ready!

Start importing recipes and building your database. The AI will handle the heavy lifting of extraction and parsing, while you focus on reviewing and perfecting your recipes.

Happy cooking! 👨‍🍳👩‍🍳

