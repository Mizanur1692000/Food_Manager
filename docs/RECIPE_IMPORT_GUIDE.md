# Recipe Import Feature Guide

The Recipe Builder includes a powerful AI-powered recipe import feature that can extract recipes from various file formats.

## Supported File Types

- **Word Documents** (.docx) - Standard recipe documents
- **PDF Files** (.pdf) - Scanned or digital recipes
- **CSV/Excel** (.csv, .xlsx) - Structured recipe data
- **Images** (.png, .jpg, .jpeg) - Photos from mobile phones or scanned recipes

## How to Import Recipes

### Step 1: Navigate to Recipe Import
1. Open the app and go to **📋 Recipe Builder**
2. Scroll down to the **"📥 Import Recipes"** section

### Step 2: Set Up API Key
The recipe import feature requires an Anthropic API key for AI-powered extraction:

**Option 1: Streamlit Secrets (Recommended)**
```bash
# Create or edit .streamlit/secrets.toml
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit the file and add your API key:
ANTHROPIC_API_KEY = "your-api-key-here"
```

**Option 2: Environment Variable**
```bash
export ANTHROPIC_API_KEY="your-api-key-here"
```

Get your API key from: https://console.anthropic.com/

### Step 3: Upload Recipe Files
1. Click **"Browse files"** button
2. Select one or more recipe files (you can upload multiple files at once)
3. Supported formats:
   - `.docx` - Microsoft Word documents
   - `.pdf` - PDF files (up to 50 pages)
   - `.csv`, `.xlsx` - Spreadsheets
   - `.png`, `.jpg`, `.jpeg` - Photos/images

### Step 4: Process with AI
1. Click the **"🤖 Process with AI"** button
2. The system will:
   - Extract text from your files
   - Parse recipe structure (name, ingredients, instructions)
   - Match ingredients to your product database
   - Calculate recipe costs
3. Watch the progress indicator for each file

### Step 5: Review & Edit
After processing, you'll see:
- **Recipe name** and description
- **Ingredients list** with matched products
- **Mapping confidence** (how well ingredients matched)
- **Estimated cost** based on your product prices

Color-coded ingredient mapping:
- 🟢 **Green (Auto-mapped)** - High confidence match (>75%)
- 🟡 **Yellow (Review)** - Medium confidence (50-75%)
- 🔴 **Red (Unmapped)** - No match found (<50%)

Edit any fields as needed:
- Change ingredient names
- Adjust quantities
- Modify units
- Update product mappings

### Step 6: Save to Database
1. Review the imported recipe
2. Make any necessary adjustments
3. Click **"💾 Save Recipe"** to add it to your recipe database
4. The recipe will now appear in your recipe list

## Tips for Best Results

### For Mobile Photos
- Take photos in good lighting
- Ensure text is clear and legible
- Avoid glare and shadows
- Hold phone steady to prevent blur

### For PDF Files
- The system automatically detects whether to use text extraction or vision
- Scanned PDFs will use Claude Vision for better accuracy
- Text-based PDFs are processed faster

### For Word Documents
- Use clear formatting
- Separate ingredients and instructions
- Include measurements and quantities

### Ingredient Matching
- The AI tries to match ingredients to your existing products
- Review yellow and red matches carefully
- You can manually select the correct product from dropdown
- Add missing products to your database first for better matching

## Troubleshooting

### "API key not configured"
**Solution:** Set up your Anthropic API key in `.streamlit/secrets.toml` or as an environment variable.

### "Extraction failed"
**Possible causes:**
- File is corrupted
- File is too large (>10MB)
- Unsupported format
**Solution:** Try converting to a different format or reducing file size.

### "No ingredients found"
**Possible causes:**
- Recipe format not recognized
- Poor image quality
- Missing ingredient section
**Solution:** Ensure your recipe has a clear ingredients list. Try editing the document to improve formatting.

### "Module not found" errors
**Solution:** Make sure all dependencies are installed:
```bash
./venv_fresh/bin/pip install -r requirements.txt
```

Or use the run script:
```bash
./run_app.sh
```

## File Size Limits

- **Maximum file size:** 10MB per file
- **PDF page limit:** 50 pages
- **Multiple files:** Can upload and process multiple files at once

## Example Workflow

1. Take a photo of your grandmother's handwritten recipe card
2. Upload the photo to Recipe Builder
3. Click "Process with AI"
4. Review the extracted recipe name and ingredients
5. Verify ingredient matches (e.g., "flour" → "All Purpose Flour")
6. Adjust quantities if needed
7. Save to your recipe database
8. Recipe is now ready to use for cost calculations!

## Privacy & Data

- Uploaded files are processed temporarily and not stored
- Recipe text is sent to Anthropic's Claude API for parsing
- See Anthropic's privacy policy: https://www.anthropic.com/privacy
- Your product database stays on your server

---

**Need more help?** Check the main README.md or open an issue on GitHub.
