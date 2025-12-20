# AI Recipe Generator - API Key Setup

## Quick Setup Guide

### 1. Get Your Claude API Key

1. Visit [Anthropic Console](https://console.anthropic.com/settings/keys)
2. Sign up or log in
3. Click "Create Key"
4. Copy the key (starts with `sk-ant-`)

### 2. Set Environment Variable

Choose your operating system:

#### Windows (PowerShell)

```powershell
# Temporary (current session only)
$env:ANTHROPIC_API_KEY='sk-ant-api03-YOUR-KEY-HERE'

# Permanent (user-level)
[System.Environment]::SetEnvironmentVariable('ANTHROPIC_API_KEY', 'sk-ant-api03-YOUR-KEY-HERE', 'User')
```

#### Windows (Command Prompt)

```cmd
# Temporary (current session only)
set ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE

# Permanent (system-wide - requires admin)
setx ANTHROPIC_API_KEY "sk-ant-api03-YOUR-KEY-HERE"
```

#### Mac / Linux

```bash
# Temporary (current session only)
export ANTHROPIC_API_KEY='sk-ant-api03-YOUR-KEY-HERE'

# Permanent - Add to ~/.bashrc or ~/.zshrc
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-YOUR-KEY-HERE"' >> ~/.bashrc
source ~/.bashrc

# OR for zsh users
echo 'export ANTHROPIC_API_KEY="sk-ant-api03-YOUR-KEY-HERE"' >> ~/.zshrc
source ~/.zshrc
```

### 3. Verify Setup

```bash
# Windows PowerShell
echo $env:ANTHROPIC_API_KEY

# Windows CMD
echo %ANTHROPIC_API_KEY%

# Mac/Linux
echo $ANTHROPIC_API_KEY
```

Should output your key starting with `sk-ant-`

### 4. Restart Your Application

If you already have the Streamlit app running:

1. Stop it (Ctrl+C)
2. Restart: `streamlit run app.py`
3. Navigate to "AI Recipe Generator"
4. You should see "✅ Claude API connected"

---

## Alternative: Create `.env` File (Optional)

For local development, you can create a `.env` file:

1. Create file named `.env` in project root
2. Add this line:

   ```
   ANTHROPIC_API_KEY=sk-ant-api03-YOUR-KEY-HERE
   ```

3. Install python-dotenv: `pip install python-dotenv`
4. Add to top of `pages/6_AI_Recipe_Generator.py`:

   ```python
   from dotenv import load_dotenv
   load_dotenv()
   ```

---

## Security Best Practices

⚠️ **NEVER commit your API key to git!**

- Add `.env` to `.gitignore`
- Don't share your key in screenshots or documentation
- Rotate keys if accidentally exposed
- Use environment variables instead of hardcoding

---

## Troubleshooting

### "API key not found" error

- Make sure you've set the environment variable
- Restart your terminal/IDE after setting it
- Check spelling: `ANTHROPIC_API_KEY` (exact case)

### "Invalid API key" error

- Verify key starts with `sk-ant-`
- Check for extra spaces or quotes
- Generate a new key from Anthropic Console

### Still not working?

- Print the env var to check: `echo $env:ANTHROPIC_API_KEY`
- Try restarting your computer
- Check [AI_RECIPE_GENERATOR_GUIDE.md](AI_RECIPE_GENERATOR_GUIDE.md) for more help

---

## API Costs

Claude API is very affordable:

- ~$3 per 1 million input tokens
- Average recipe = 500 tokens ≈ $0.0015
- 1000 recipes ≈ $1.50

For typical restaurant use, monthly costs are minimal.

