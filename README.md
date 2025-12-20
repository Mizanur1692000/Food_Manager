# Restaurant Kitchen Inventory App

A comprehensive, modular Streamlit application for managing restaurant inventory, recipes, variance calculations, and physical count management with real-time editing capabilities.

## 🚀 Features

### 📦 **Product Database Management**

- **Location-based organization** - Track products by storage locations
- **Price history tracking** - Monitor current and historical pricing
- **Bulk import/export** - CSV-based data management
- **Category management** - Organized product categorization
- **SKU tracking** - Unique product identification

### 📋 **Recipe Builder**

- **Ingredient management** - Add/remove ingredients with quantities
- **Cost calculations** - Automatic recipe cost analysis
- **Category organization** - Recipe categorization system
- **Portion scaling** - Adjust recipe quantities
- **Cost per unit tracking** - Detailed cost breakdown

### 🤖 **AI Recipe Generator (NEW!)**

- **Claude AI integration** - Generate recipes from natural language prompts
- **Automatic ingredient mapping** - Fuzzy matching to product database
- **Smart unit conversion** - Auto-converts oz to lb, gallon, etc.
- **Cost estimation** - Uses real product prices for costing
- **Full integration** - Saves to existing recipe database

### 📥 **Recipe Import (NEW! PRODUCTION-GRADE)**

- **Multi-format support** - Import from DOCX, PDF, CSV, Excel, and images
- **Intelligent PDF routing** - Per-page text vs vision extraction
- **Claude Vision API** - Extract recipes from scanned documents and photos
- **Smart ingredient mapping** - Tiered confidence matching (auto/warn/unmapped)
- **Unit normalization** - Handle fractions, ranges, and conversions
- **Pydantic validation** - Ensure data consistency and quality
- **Cost calculation** - Automatic recipe costing from product database
- **Structured logging** - Track all import activities
- **Security features** - MIME validation, EXIF stripping, duplicate detection
- **Batch processing** - Import multiple recipes at once

### 📊 **Variance Calculator**

- **Expected vs Actual** - Compare planned vs actual usage
- **Cost variance analysis** - Financial impact calculations
- **Percentage tracking** - Variance percentage calculations
- **Detailed reporting** - Comprehensive variance reports

### 📋 **Sheet-to-Shelf Inventory**

- **Physical count management** - Conduct inventory counts
- **Location-based counting** - Sequential counting by location
- **Auto-save functionality** - Real-time count updates
- **Variance tracking** - Monitor count accuracy
- **Progress tracking** - Count completion status

### 📊 **Inventory Summary (NEW!)**

- **Editable count corrections** - Fix miscounts directly from summary
- **Location-based grouping** - Organized inventory analysis
- **Real-time calculations** - Auto-updating values and variances
- **Financial analysis** - Value calculations and cost tracking
- **Export functionality** - User-selectable download locations

### 💾 **Advanced Export Features**

- **User-selectable downloads** - Choose where to save CSV files
- **Detailed reporting** - Comprehensive data exports
- **Timestamped files** - Prevent file overwrites
- **Multiple export formats** - Count data and summary exports

## 🏗️ Project Structure

```
restuarnt_inventory_app/
├── app.py                    # Main Streamlit application
├── data/                     # Data storage (CSV, JSON, images)
│   ├── product_data.csv      # Product database
│   ├── recipes.json          # Recipe data
│   ├── inventory_counts.json # Active count data
│   └── count_history.json   # Historical count data
├── modules/                  # Business logic modules
│   ├── product_manager.py    # Product database management
│   ├── recipe_engine.py      # Recipe building and cost calculation
│   ├── variance_engine.py    # Variance analysis
│   ├── inventory_engine.py   # Physical count management
│   └── summary_engine.py     # Inventory summary and analysis
├── pages/                    # Streamlit UI pages
│   ├── 1_ProductDatabase.py  # Product management interface
│   ├── 2_RecipeBuilder.py    # Recipe creation and editing
│   ├── 3_VarianceCalculator.py # Variance analysis interface
│   ├── 4_SheetToShelfInventory.py # Physical count management
│   ├── 5_InventorySummary.py # Editable summary and analysis
│   └── 6_AI_Recipe_Generator.py # AI-powered recipe generation
├── ui_components/            # Reusable UI components
│   ├── forms.py             # Form components
│   ├── layout.py            # Layout utilities
│   └── sidebar.py           # Navigation sidebar
├── utils/                    # Utility functions
│   ├── shared_functions.py  # Shared utility functions
│   └── error_handler.py     # Error handling utilities
├── tests/                    # Unit tests
└── requirements.txt          # Python dependencies
```

## 🚀 Quick Start

### **System Requirements**

Before installing the application, ensure you have the following system dependencies:

#### **Tesseract OCR** (Required for recipe import from images and PDFs)

- **Ubuntu/Debian:**
  ```bash
  sudo apt-get update
  sudo apt-get install tesseract-ocr
  ```

- **macOS:**
  ```bash
  brew install tesseract
  ```

- **Windows:**
  Download and install from: https://github.com/UB-Mannheim/tesseract/wiki

- **Verify installation:**
  ```bash
  tesseract --version
  ```

### **Installation**

```bash
# Clone the repository
git remote add origin https://github.com/Mizanur1692000/Food_Manager.git

# Create and activate virtual environment (recommended)
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install Python dependencies
pip install -r requirements.txt

# Configure Streamlit secrets (for AI features)
cp .streamlit/secrets.toml.template .streamlit/secrets.toml
# Edit .streamlit/secrets.toml and add your ANTHROPIC_API_KEY
```

### **Running the App**

**Option 1: Using the run script (Recommended)**
```bash
# Make the script executable (first time only)
chmod +x run_app.sh

# Run the app
./run_app.sh
```

**Option 2: Manual start**
```bash
# Activate virtual environment
source venv_fresh/bin/activate  # On Windows: venv_fresh\Scripts\activate

# Start the Streamlit application
streamlit run app.py
```
# Start the Streamlit application for both streamlit and fastapi

python run_all.py

The app will open in your browser at `http://localhost:8501`

### **Running Tests**

```bash
# Run all unit tests
python -m unittest discover tests
```

## 📖 Usage Guide

### **1. Product Database Setup**

1. Navigate to "📦 Product Database"
2. Add products with locations, categories, and pricing
3. Use bulk import for large product lists
4. Track price history and updates

### **2. Recipe Management**

1. Go to "📋 Recipe Builder"
2. Create recipes with ingredients and quantities
3. View automatic cost calculations
4. Organize recipes by categories

### **2b. AI Recipe Generation** 🤖

1. Navigate to "🤖 AI Recipe Generator"
2. **Set API key** - Add `ANTHROPIC_API_KEY` environment variable
3. **Describe recipe** - Enter natural language prompt
4. **Review mapping** - Check ingredient matches to your products
5. **Edit & save** - Adjust as needed and save to recipe database
6. See [AI_RECIPE_GENERATOR_GUIDE.md](AI_RECIPE_GENERATOR_GUIDE.md) for detailed setup

### **2c. Import Recipes from Files** 📥

1. Go to "📋 Recipe Builder" and scroll to "📥 Import Recipes"
2. **Set API key** - Configure `ANTHROPIC_API_KEY` in `.streamlit/secrets.toml`
3. **Upload files** - Upload Word docs, PDFs, CSV/Excel, or mobile photos
4. **Process with AI** - Click "🤖 Process with AI" to extract recipes
5. **Review & edit** - Check ingredient matching and adjust as needed
6. **Save** - Add imported recipes to your database
7. See [RECIPE_IMPORT_GUIDE.md](RECIPE_IMPORT_GUIDE.md) for detailed instructions

### **3. Variance Analysis**

1. Access "📊 Variance Calculator"
2. Compare expected vs actual usage
3. Analyze cost variances and percentages
4. Generate detailed variance reports

### **4. Physical Inventory Counting**

1. Navigate to "📋 Sheet-to-Shelf Inventory"
2. Start a new count with location filtering
3. Count items sequentially by location
4. Auto-save functionality updates in real-time
5. Complete counts and move to history

### **5. Inventory Summary & Corrections**

1. Go to "📊 Inventory Summary"
2. View comprehensive count summaries by location
3. **Edit actual counts directly** - Fix miscounts without returning to counting page
4. Download detailed CSV reports to your chosen location
5. Analyze financial impact and variance trends

## 🆕 Latest Features

### **AI Recipe Generator** 🤖

- **Claude AI integration** - Natural language recipe generation
- **Intelligent ingredient mapping** - Fuzzy matching with 75%+ confidence
- **Automatic unit conversion** - Converts oz → lb, gallon, quart, dozen, etc.
- **Real product pricing** - Uses your actual product costs
- **Full compatibility** - Saves to same database as Recipe Builder
- **Review & edit** - Adjust ingredients, quantities, and instructions before saving
- **See setup guide**: [AI_RECIPE_GENERATOR_GUIDE.md](AI_RECIPE_GENERATOR_GUIDE.md)

### **Editable Summary Page**

- **Direct count corrections** - Edit actual counts from summary view
- **Real-time calculations** - Values and variances update automatically
- **Location-based organization** - Grouped by storage locations
- **Visual variance indicators** - Color-coded variance tracking

### **User-Selectable Downloads**

- **Choose download location** - Save CSV files where you want
- **Standard browser experience** - Native download dialogs
- **Timestamped filenames** - Prevent file overwrites
- **Multiple export types** - Count data and summary exports

### **Enhanced Inventory Management**

- **Location-based counting** - Sequential inventory by storage area
- **Auto-save functionality** - Real-time count updates
- **Progress tracking** - Monitor count completion status
- **Variance analysis** - Comprehensive accuracy reporting

## 🛠️ Technical Features

- **Modular Architecture** - Separated UI, business logic, and data layers
- **Multi-language Support** - English and Spanish interfaces
- **Real-time Updates** - Auto-save and live calculations
- **Error Handling** - Comprehensive error management
- **Data Validation** - Input validation and data integrity
- **Export Capabilities** - Multiple export formats and locations
- **Responsive Design** - Works on desktop and mobile devices

## 🧪 Testing

The application includes comprehensive unit tests for all major modules:

```bash
# Run specific test modules
python -m unittest tests.test_products
python -m unittest tests.test_recipes
python -m unittest tests.test_inventory
python -m unittest tests.test_variance

# Run all tests with coverage
python -m unittest discover tests -v
```

## 🚀 Deployment

### Dependency Maintenance

- **Dependencies are now pinned** to specific versions to ensure stability and prevent breaking changes
- **Regenerate the lock file** with `pip freeze > requirements.lock` and refresh `requirements.txt` every **90 days** (set a calendar reminder)
- **Review security advisories** for pinned packages during each refresh cycle before deploying
- When updating dependencies:
  ```bash
  # Activate your virtual environment
  source venv_fresh/bin/activate

  # Update packages (test in staging first!)
  pip install --upgrade <package-name>

  # Re-freeze dependencies
  pip freeze > requirements.lock

  # Sort and update requirements.txt
  python3 <<'EOF'
  from pathlib import Path
  lock = Path("requirements.lock").read_text().splitlines()
  Path("requirements.txt").write_text("\n".join(sorted(lock)) + "\n")
  EOF

  # Test thoroughly before deploying
  streamlit run app.py
  ```

## 🤝 Contributing

We welcome contributions! Please follow these guidelines:

1. **Fork the repository**
2. **Create a feature branch** (`git checkout -b feature/amazing-feature`)
3. **Add tests** for new functionality
4. **Commit changes** (`git commit -m 'Add amazing feature'`)
5. **Push to branch** (`git push origin feature/amazing-feature`)
6. **Open a Pull Request**

### **Development Guidelines**

- Add business logic to `modules/`
- Add UI components to `ui_components/`
- Add new pages to `pages/`
- Use shared functions from `utils/shared_functions.py`
- Include tests for new features
- Follow existing code patterns and naming conventions

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

For issues, questions, or feature requests:

- Open an issue on GitHub
- Check existing issues for solutions
- Review the documentation above

---

**Built with ❤️ using Streamlit, Pandas, and Python**
