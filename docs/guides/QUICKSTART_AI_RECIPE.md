# 🚀 AI Recipe Generator - Quick Start

## 3-Minute Setup

### Step 1: Install Dependencies (30 seconds)

```bash
pip install -r requirements.txt
```

### Step 2: Get API Key (1 minute)

1. Go to: <https://console.anthropic.com/settings/keys>
2. Create account or log in
3. Click "Create Key"
4. Copy the key

### Step 3: Set Environment Variable (30 seconds)

**Windows:**
```powershell
$env:ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

**Mac/Linux:**
```bash
export ANTHROPIC_API_KEY='sk-ant-your-key-here'
```

### Step 4: Run & Test (1 minute)

```bash
streamlit run app.py
```

1. Click "AI Recipe Generator" in sidebar
2. See "✅ Claude API connected"
3. Enter prompt: "Crispy chicken wings, 8 servings"
4. Click "Generate"
5. Review → Edit → Save

**Done! 🎉**

---

## Example Prompts

### Quick Recipes

```
"Grilled chicken breast with lemon and herbs, 6 servings"
"Buffalo wings with blue cheese dressing, 8oz portions"
"House marinara sauce, makes 1 gallon"
```

### Detailed Recipes

```
"Japanese karaage (fried chicken):
- Crispy coating with potato starch
- Soy-ginger marinade
- 8 servings, 5oz each
- Include prep times"
```

### Prep Recipes

```
"Ranch dressing for salad station:
- Makes 1 gallon
- Buttermilk base
- 7 day shelf life"
```

---

## Troubleshooting

| Problem | Solution |
|---------|----------|
| "API key not found" | Set `ANTHROPIC_API_KEY` environment variable |
| "Module not found" | Run `pip install -r requirements.txt` |
| Low match rate | Lower threshold slider or add products |
| Recipe exists | Change name or delete old recipe |

---

## Costs

- **~$0.0015 per recipe** (~$1.50 per 1000 recipes)
- Free tier available from Anthropic
- Normal restaurant use: **< $5/month**

---

## Full Documentation

- 📖 **Complete Guide**: `AI_RECIPE_GENERATOR_GUIDE.md`
- 🔧 **Setup Details**: `setup_api_key.md`
- 📊 **Integration Info**: `INTEGRATION_SUMMARY.md`

---

**Get cooking with AI! 🤖🍽️**

