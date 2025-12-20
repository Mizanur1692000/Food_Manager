# 🤖 AI Recipe Generator - Setup & Usage Guide

## Overview

The AI Recipe Generator uses Claude AI to create professional restaurant recipes that automatically integrate with your existing product database. It handles:

- ✅ Recipe generation from natural language prompts
- ✅ Automatic ingredient mapping to your product database
- ✅ Unit conversions (oz → lb, gallon, etc.)
- ✅ Cost calculations using your actual product prices
- ✅ Full integration with existing Recipe Builder

---

## 🚀 Setup Instructions

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

This installs:

- `anthropic>=0.39.0` - Claude API client
- `rapidfuzz>=3.0.0` - Fuzzy ingredient matching

### 2. Get Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Sign up or log in
3. Create a new API key
4. Copy the key (starts with `sk-ant-...`)

### 3. Set Environment Variable

**Windows (PowerShell):**

```powershell
$env:ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
```

**Windows (Command Prompt):**

```cmd
set ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

**Mac/Linux:**

```bash
export ANTHROPIC_API_KEY='sk-ant-api03-your-key-here'
```

**For Persistent Setup (recommended):**

Add to your `.env` file in project root:

```
ANTHROPIC_API_KEY=sk-ant-api03-your-key-here
```

Then load it in your shell startup file (`.bashrc`, `.zshrc`, or PowerShell profile).

### 4. Run the App

```bash
streamlit run app.py
```

Navigate to **AI Recipe Generator** in the sidebar.

---

## 📖 How It Works

### The Process

1. **Prompt** → You describe the recipe in natural language
2. **Generate** → Claude creates a structured recipe with ingredients in ounces
3. **Map** → System fuzzy-matches ingredients to your product database
4. **Convert** → Ounces are converted to each product's native unit (lb, gallon, etc.)
5. **Review** → You can edit ingredients, quantities, and instructions
6. **Save** → Recipe is saved in the same format as manually-created recipes

### Integration Flow

```
Your Prompt
    ↓
Claude AI (JSON recipe)
    ↓
Fuzzy Matching → Your Product Database
    ↓
Unit Conversion (oz → lb/gallon/etc)
    ↓
Format Conversion → App Recipe Schema
    ↓
save_recipe() from recipe_engine.py
    ↓
data/recipes.json (same as Recipe Builder)
```

---

## 🎯 Usage Examples

### Example 1: Simple Dish

**Prompt:**

```
Crispy buffalo chicken wings with blue cheese dressing.
Make 6 servings with 8 oz portions.
```

**Result:**

- Claude generates full recipe with measurements in oz
- Ingredients mapped to your products (e.g., "chicken wings" → "Chicken Wings Fresh")
- Quantities converted (48 oz → 3 lbs)
- Cost calculated using your product prices

### Example 2: Complex Recipe

**Prompt:**

```
Japanese karaage (fried chicken) with the following specs:
- Crispy coating using potato starch
- Soy-ginger marinade with sake and garlic
- Served with lemon wedges and scallion garnish
- 8 servings, 5 oz portions
- Include prep and cook times
```

**Result:**

- Detailed ingredient list with precise measurements
- Step-by-step cooking instructions
- All ingredients matched to your database
- Ready to save and use in inventory calculations

### Example 3: Prep Recipe

**Prompt:**

```
House ranch dressing for salad station.
Makes 1 gallon yield, uses buttermilk, mayo, herbs.
Should last 7 days refrigerated.
```

**Result:**

- Prep recipe format
- Shelf life noted in instructions
- Scaled for volume production

---

## 🔧 Features & Settings

### Match Confidence Slider (50-95%)

Controls how strict ingredient matching is:

- **50-70%**: Loose matching, more ingredients mapped (may have incorrect matches)
- **75-85%**: Balanced (recommended)
- **90-95%**: Strict matching, only very confident matches

**Tip:** Start at 75%. If too many ingredients are unmapped, lower to 65%.

### Ingredient Mapping Results

After generation, you'll see:

- ✅ **Mapped**: Successfully matched to products
- ⚠️ **Unmapped**: No match found (can edit manually)
- **Match Rate %**: Overall matching success

Click "View Mapping Details" to see:

- AI ingredient name
- Matched product name
- Match confidence score
- Original amount (oz)
- Converted amount (lb, gallon, etc.)

### Editing Before Save

You can edit:

- Recipe name, description, category
- Servings, prep time, cook time
- Individual ingredients (add/remove/change)
- Quantities and units
- Cooking instructions

Changes are **not auto-saved** until you click "💾 Save Recipe".

---

## 🧪 Unit Conversion Reference

The system automatically converts Claude's oz measurements:

| From (oz) | To Unit | Conversion |
|-----------|---------|------------|
| 16 oz | 1 lb | ÷ 16 |
| 128 oz | 1 gallon | ÷ 128 |
| 32 oz | 1 quart | ÷ 32 |
| 33.814 oz | 1 liter | ÷ 33.814 |
| 24 oz | 1 dozen (eggs) | ÷ 24 (approx) |
| 1 oz | 1 bunch (herbs) | 1:1 (approx) |

**Note:** Conversions for `dozen`, `bunch`, `each`, and `case` are estimates and should be reviewed before saving.

---

## ⚠️ Troubleshooting

### "Claude API key not found"

- Check environment variable is set: `echo $ANTHROPIC_API_KEY`
- Restart terminal/IDE after setting variable
- Verify key starts with `sk-ant-`

### "Claude didn't return valid JSON"

- API might be rate-limited (wait 1 minute)
- Prompt might be too vague (be more specific)
- Click "View AI Raw Output" to see what was returned

### Low Match Rate (<50%)

- Your product database may use different naming conventions
- Try lowering match confidence threshold
- Add products to database that match common ingredient names
- Edit ingredients manually after generation

### Ingredients in Wrong Units

- Check your `product_data.csv` has correct `Unit` column values
- Common units: `lb`, `gallon`, `quart`, `dozen`, `each`, `bunch`, `case`
- Manually edit unit in the ingredient editor before saving

### Recipe Already Exists Error

- Recipe names must be unique
- Either delete the old recipe (Recipe Builder → Edit tab)
- Or change the new recipe name before saving

---

## 🔒 API Costs & Limits

### Claude API Pricing (as of 2025)

- **Claude Sonnet 4**: ~$3 per million input tokens
- Typical recipe: ~500 tokens = ~$0.0015 per recipe
- Very affordable for restaurant use

### Rate Limits

- Tier 1: 50 requests/minute
- Tier 2: 1000 requests/minute

For normal usage, you won't hit limits.

---

## 🎓 Best Practices

### Writing Effective Prompts

**✅ Good Prompts:**

```
"French onion soup with beef broth, gruyere cheese,
and caramelized onions. 8 servings, 12 oz bowls."

"Sheet pan chicken fajitas with bell peppers and onions.
Pre-marinated protein, 6 servings."

"House-made BBQ sauce with molasses and apple cider vinegar.
Makes 2 quarts, tangy Kansas City style."
```

**❌ Vague Prompts:**

```
"Make me soup"
"Chicken recipe"
"Something with pasta"
```

**Key Elements to Include:**

1. Dish name and style (e.g., "Italian", "Japanese", "BBQ")
2. Main ingredients
3. Servings and/or portion sizes
4. Special requirements (spicy, vegetarian, etc.)
5. Any technique notes (grilled, fried, slow-cooked)

### Recipe Categories

Choose appropriate categories for filtering:

- **Main Course**: Entrees, proteins
- **Appetizer**: Starters, small plates
- **Prep Recipe**: Sauces, dressings, marinades, batters
- **Soup / Salad**: Self-explanatory
- **Dessert**: Sweets
- **Bar**: Cocktails, drink mixes
- **Sauce / Dressing / Marinade**: Condiments

### Review Before Saving

Always check:

1. ✅ All ingredients mapped correctly
2. ✅ Quantities make sense (48 oz chicken = 3 lbs ✓)
3. ✅ Units match your purchasing units
4. ✅ Instructions are clear and complete
5. ✅ Category and servings are accurate

---

## 🔄 Integration with Other Pages

### Recipe Builder (Page 2)

- AI-generated recipes appear alongside manual recipes
- Edit them the same way
- Delete if needed

### Variance Calculator (Page 3)

- Use AI recipes in theoretical usage calculations
- Calculate actual vs theoretical variances

### Inventory Summary (Page 5)

- AI recipes included in cost analysis
- Same costing algorithm applies

---

## 📊 Testing

Run the test suite:

```bash
pytest tests/test_ai_recipe_generator.py -v
```

Tests cover:

- Unit conversions (oz → lb, gallon, etc.)
- Fuzzy ingredient matching
- Recipe format conversion
- Handling unmapped ingredients

---

## 🆘 Support

### Common Questions

**Q: Can I use this without internet?**
A: No, it requires Claude API which is cloud-based.

**Q: Will it work with my existing recipes?**
A: Yes! It saves to the same `recipes.json` file.

**Q: Can I edit AI recipes later?**
A: Absolutely. Use Recipe Builder → Edit tab.

**Q: What if an ingredient isn't in my database?**
A: It will show as "⚠️ Unmapped". Add the product first, or manually select a substitute.

**Q: Does it understand dietary restrictions?**
A: Yes! Include in prompt: "gluten-free", "vegetarian", "dairy-free", etc.

---

## 📝 Example Session

1. **Navigate** to AI Recipe Generator page
2. **Enter prompt**: "Korean fried chicken with gochujang glaze, 6 servings"
3. **Click** "Generate Recipe with AI"
4. **Review** mapping results: 5/5 ingredients mapped (100%)
5. **Edit** if needed (maybe adjust quantities)
6. **Click** "Save Recipe"
7. **Success!** Recipe now in Recipe Builder

---

## 🚀 Future Enhancements

Possible improvements:

- [ ] Batch recipe generation
- [ ] Recipe scaling (2x, 4x, etc.)
- [ ] Nutrition calculations
- [ ] Photo generation for recipes
- [ ] Multi-language recipe generation
- [ ] Import recipes from URLs
- [ ] Export to PDF with photos

---

## 📄 License & Credits

Part of Restaurant Inventory Management App
Powered by Anthropic Claude API
Fuzzy matching via RapidFuzz library

---

**Happy Recipe Creating! 🍽️**
