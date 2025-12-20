# 📝 Logs Folder - What It's For

## Overview

The `logs/` folder stores application activity logs for debugging and auditing purposes.

## Why It's Empty

**The folder is empty because:**
1. The app hasn't been run yet (or was recently started)
2. Logs are only created when the app runs and writes log entries
3. It's in `.gitignore`, so logs aren't committed to git

## What Gets Logged

### Main Application Log
**File:** `logs/app.log`

**Contains:**
- Application startup and shutdown events
- Error messages and stack traces
- Warning messages
- Info messages from the app

**When Created:** When the app starts and logging occurs

### Recipe Import Logs
**File:** `logs/recipe_imports.jsonl`

**Contains:** Structured JSON log entries for recipe imports:
- File uploads
- Text extraction from PDFs/DOCs
- AI parsing events
- Ingredient mapping
- Validation results
- Save operations
- Errors

**Format:** JSON Lines (one JSON object per line)

**When Created:** When you import recipes using the Recipe Builder → Import Recipes feature

## Log Configuration

From `config.py`:
```python
LOG_LEVEL = "INFO"  # Logs INFO, WARNING, ERROR, CRITICAL
LOG_FILE = "logs/app.log"
```

## Viewing Logs

### Application Log (`app.log`)
```bash
# Windows
type logs\app.log

# Mac/Linux
cat logs/app.log
```

### Import Logs (`recipe_imports.jsonl`)
```bash
# View last 10 import activities
cat logs/recipe_imports.jsonl | tail -10

# Or open in a text editor
```

## Log File Sizes

- **app.log** - Usually small (KB to MB), rotates when it gets large
- **recipe_imports.jsonl** - Grows over time, one line per import operation

## When To Check Logs

### Debug Issues
- Application crashes → Check `app.log`
- Recipe import failures → Check `recipe_imports.jsonl`
- Unexpected behavior → Check both

### Monitor Activity
- See what operations were performed
- Track recipe import history
- Audit application usage

## Privacy Note

Logs may contain:
- File names you uploaded
- Recipe names (but not full recipe data)
- Error messages and stack traces

**Keep logs private** - Don't share them publicly or commit to git.

## Maintenance

**Auto-management:**
- Logs are in `.gitignore` (not tracked in git)
- Old log rotation may be implemented
- You can manually delete logs if they get too large

**Manual cleanup:**
```bash
# Delete all logs (app will recreate on next run)
rm logs/*

# Windows PowerShell
Remove-Item logs\* -Force
```

## Summary

| File | Purpose | When Created |
|------|---------|--------------|
| `app.log` | General app logs | When app runs |
| `recipe_imports.jsonl` | Recipe import tracking | When importing recipes |

**The folder is empty now, but logs will appear when you use the app!**
