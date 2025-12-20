# Product Import Feature Guide

## Overview

The Product Import feature provides a comprehensive solution for importing supplier product data into your restaurant inventory system. It supports multiple CSV formats, intelligent column mapping, template management, and robust duplicate handling.

## Key Features

### 1. **Multi-Format Support**
- **SYSCO Format**: Automatically detects and parses SYSCO's proprietary CSV format with H/F/P row prefixes
- **Standard CSV**: Handles any standard CSV file with headers
- **Extensible**: Easy to add support for other supplier formats

### 2. **Intelligent Column Mapping**
- **AI-Powered Suggestions**: Uses fuzzy matching to automatically suggest column mappings
- **Manual Override**: Full control to manually map any column
- **Template System**: Save and reuse mappings for recurring suppliers

### 3. **Flexible Configuration**
- **Price Field Selection**: Choose which price column to import (Case $, Split $, etc.)
- **Default Values**: Set defaults for missing fields (Location, Category)
- **Pack Size Handling**: Automatically combines Pack/Size/Unit columns

### 4. **Duplicate Management**
- **Automatic Detection**: Identifies products that already exist by SKU
- **Multiple Strategies**: Update all, skip all, or review individually
- **Side-by-side Comparison**: Compare existing vs new data (coming soon)

### 5. **Data Validation**
- **Required Field Checking**: Ensures all mandatory fields are present
- **Preview Before Import**: See exactly what will be imported
- **Error Reporting**: Clear messages for any issues

## Getting Started

### Prerequisites

1. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

   Required packages (already included):
   - `pandas` - CSV processing
   - `rapidfuzz` - Fuzzy column matching
   - `streamlit` - UI framework

2. **Prepare Your CSV File**
   - Export product list from your supplier
   - Ensure the file has column headers
   - Save as .CSV format

### Accessing the Feature

1. Start the application:
   ```bash
   streamlit run app.py
   ```

2. Navigate to **Product Database** page

3. Click on the **📥 Import Products** tab

## Step-by-Step Import Process

### Step 1: Upload CSV File

1. Click **Browse files** or drag-and-drop your CSV file
2. The system will automatically detect the format (SYSCO or Standard)
3. Review the preview of first 10 rows
4. Check the list of available columns
5. Click **Next: Map Columns →**

**Supported Formats:**
- SYSCO format with H/F/P prefixes
- Standard CSV with any column names
- Maximum file size: Unlimited (performance may vary)

### Step 2: Map Columns

This is the most important step where you connect supplier columns to your database fields.

#### **Option A: Auto-Map with AI**
1. Click the **🤖 Auto-Map with AI** button
2. The system will suggest mappings based on fuzzy matching
3. Review and adjust any incorrect mappings

#### **Option B: Load Saved Template**
1. Select a previously saved template from the dropdown
2. Mappings will be applied automatically
3. Adjust if needed for this specific file

#### **Option C: Manual Mapping**
1. For each required field, select the corresponding supplier column
2. Optionally map optional fields (expand the section)
3. Use the pattern hints to help identify correct columns

**Required Fields:**
- **Product Name**: The product/item name or description
- **SKU**: Unique product identifier (SUPC, Item Code, etc.)
- **Category**: Product category or type
- **Unit**: Unit of measure (oz, lb, case, etc.)
- **Current Price per Unit**: Product price

**Optional Fields:**
- **Location**: Storage location
- **Pack Size**: Case/pack size information
- **Brand**: Product brand/manufacturer

#### **Saving Templates**
1. Once you have correct mappings, expand **💾 Save as Template**
2. Enter a memorable name (e.g., "SYSCO Weekly Import")
3. Click **Save Template**
4. Use this template for future imports from the same supplier

### Step 3: Configure Settings

#### **Price Field Selection**
- The system shows all columns that might contain prices
- Select which price you want to import:
  - **Case $**: Wholesale case price
  - **Split $**: Individual unit price
  - Or any custom price column

#### **Default Values**
Set defaults for products that are missing these fields:

- **Default Location**: Where to store products (Walk-in Cooler, Dry Goods Storage, Freezer)
- **Default Category**: Fallback category if not mapped (e.g., "Imported")

#### **Pack Size Configuration (SYSCO)**
For SYSCO files, Pack, Size, and Unit columns are automatically combined into a single Pack Size field.

### Step 4: Preview & Validate

Review the processed data before importing:

#### **Summary Metrics**
- **✅ Ready to Import**: Products that passed all validations
- **⚠️ Duplicates**: Products that already exist in your database
- **❌ Errors**: Products with missing required fields or other issues
- **📊 Total Rows**: Total number of products processed

#### **Error Review**
- Click on the **❌ Errors** expander to see specific issues
- Fix source data or adjust mappings if needed
- Go back to previous steps to make corrections

#### **Duplicate Review**
- Click on the **⚠️ Duplicate Products** expander
- See which products already exist
- You'll choose how to handle these in the next step

#### **Data Preview**
- Review a table of the first 20 products to be imported
- Verify Product Name, SKU, Category, Price, Pack Size, and Location
- Ensure data looks correct before proceeding

### Step 5: Import Products

#### **Duplicate Handling**

If duplicates were found, choose your strategy:

**Option 1: Review each one individually**
- *Coming soon* - Manual review of each duplicate
- For now, use Option 2 or 3

**Option 2: Update all duplicates**
- ✅ Use this to update prices and information for existing products
- Existing products will be overwritten with new data
- Original SKUs and Product Names are preserved

**Option 3: Skip all duplicates**
- ✅ Use this to only import new products
- Existing products remain unchanged
- Only products with unique SKUs are imported

#### **Execute Import**

1. Review the count of products to be imported
2. Click **🚀 Start Import** button
3. Watch the progress bar
4. View the import summary:
   - **✅ Imported**: New products added
   - **🔄 Updated**: Existing products modified
   - **⏭️ Skipped**: Duplicate products skipped
5. Check the errors expander for any issues
6. Click **Import Another File** to start over

## SYSCO Format Details

SYSCO uses a special CSV format with row type prefixes:

```csv
H,L0601,047,942355,Chicken and Dumplings,...
F,SUPC,Case Qty,Split Qty,Code,Item Status,...
P,1821537,,,,,4,5LB,LB,IMPERIAL FRESH,...
P,1094721,,,,,1,50 LB,LB,IMPERIAL FRESH,...
```

- **H row**: Header row with metadata
- **F row**: Field names (column headers)
- **P rows**: Product data

The import system automatically:
1. Detects this format
2. Extracts the F row as column names
3. Filters to only P rows (product data)
4. Removes the row type prefix column

## Template Management

### Creating Templates

Templates save your column mappings, price field selection, and default values for reuse.

**When to Create a Template:**
- After successfully mapping columns from a supplier
- For suppliers you import from regularly
- To standardize imports across your team

**What's Saved in a Template:**
- Column mappings (which supplier column maps to which field)
- Format type (SYSCO or standard)
- Price field selection
- Default values (location, category)

### Using Templates

1. In Step 2 (Map Columns), select your template from the dropdown
2. All mappings are applied automatically
3. Make adjustments if the supplier changed their format
4. Update the template if needed

### Template Storage

Templates are stored in `data/import_templates.json`

**Default Templates:**
- **SYSCO**: Pre-configured for SYSCO's standard format

You can manually edit this file to:
- Share templates with team members
- Backup your configurations
- Create templates programmatically

## Troubleshooting

### "Error loading CSV"
- **Cause**: File is not a valid CSV or has encoding issues
- **Solution**: Open in Excel and re-save as CSV (UTF-8)

### "Missing required field mappings"
- **Cause**: Not all required fields are mapped
- **Solution**: Check that Product Name, SKU, Category, Unit, and Price are all mapped

### "No products ready to import"
- **Cause**: All products failed validation or are duplicates
- **Solution**: Check the Errors expander for specific issues

### Duplicate SKUs in import file
- **Cause**: Your source file has the same SKU multiple times
- **Solution**: The system will process each occurrence; the last one wins

### Products not appearing after import
- **Cause**: Import was successful but you're viewing filtered results
- **Solution**: Go to Product List tab and clear all filters

### SYSCO file not detected correctly
- **Cause**: File doesn't have standard H/F/P prefixes
- **Solution**: The system will treat it as standard CSV; map columns manually

## Best Practices

### 1. **Start with a Small Test**
- Import 5-10 products first
- Verify the results
- Then import the full file

### 2. **Save Templates**
- Create templates for each supplier
- Name them clearly (e.g., "SYSCO Weekly", "US Foods Monthly")
- Update templates when supplier changes format

### 3. **Regular Updates**
- Use "Update all duplicates" for weekly price updates
- Use "Skip all duplicates" when adding new products only

### 4. **Data Cleanup**
- Review the preview carefully
- Check that categories make sense
- Verify prices are in the correct column

### 5. **Backup Before Large Imports**
- Copy `data/product_data.csv` before major imports
- Keep previous versions for rollback if needed

## Advanced Usage

### Custom Default Values

Edit `data/import_templates.json` to add custom defaults:

```json
{
  "My Supplier": {
    "defaults": {
      "Location": "Custom Storage Area",
      "Category": "Special Category",
      "Brand": "House Brand"
    }
  }
}
```

### Batch Imports

To import from multiple suppliers:
1. Import first supplier file
2. Click "Import Another File"
3. Repeat for each supplier
4. Use appropriate template for each

### Integration with Existing Workflows

The import feature complements existing features:
- **After Import**: Use Bulk Update tab for price-only updates
- **Before Recipes**: Import products before building recipes
- **With Inventory**: Import products before counting inventory

## API Reference

For developers extending the system:

### Key Functions

**`detect_csv_format(df)`**
- Detects SYSCO vs standard CSV format
- Returns: 'sysco' or 'standard'

**`suggest_column_mappings(columns, threshold=70)`**
- Suggests mappings using fuzzy matching
- Returns: Dict of {app_field: (supplier_col, confidence)}

**`process_import_batch(df, existing_products, defaults)`**
- Processes and validates import data
- Returns: Dict with ready/duplicates/errors

**`bulk_import_products(products, update_duplicates=False)`**
- Imports multiple products at once
- Returns: Tuple of (imported, updated, skipped, errors)

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Review error messages in the import interface
3. Check the console for detailed error logs
4. Refer to the test file: `tests/test_product_import.py`

## Version History

**v1.0** (Current)
- Initial release
- SYSCO format support
- AI-powered column mapping
- Template management
- Duplicate detection
- Bulk import functionality

**Coming Soon:**
- Individual duplicate review with side-by-side comparison
- Additional supplier format templates
- Excel file support (.xlsx)
- Import history and rollback
- Scheduled imports

