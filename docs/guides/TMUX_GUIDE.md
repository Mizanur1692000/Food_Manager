# tmux Quick Reference Guide

## Getting Started

### Launch Your Development Environment
```bash
# From anywhere, run:
./setup_tmux.sh

# Then attach:
tmux attach -t restaurant-app
```

### Your Layout
```
┌─────────────────┬─────────────────┐
│ Development     │ Git/Data Ops    │
│ (Pane 0)        │ (Pane 1)        │
│ - Edit code     │ - git commands  │
│ - File ops      │ - CSV imports   │
│                 │ - Data checks   │
├─────────────────┼─────────────────┤
│ Streamlit App   │ Testing         │
│ (Pane 2)        │ (Pane 3)        │
│ streamlit run   │ pytest          │
│ Home.py         │ debugging       │
└─────────────────┴─────────────────┘
```

---

## Essential tmux Commands

**All tmux commands start with the prefix: `Ctrl+b`**
(Press Ctrl+b, release, then press the command key)

### Navigation
| Command | Action |
|---------|--------|
| `Ctrl+b` → `←↑→↓` | Move between panes (arrow keys) |
| `Ctrl+b` → `q` | Show pane numbers |
| `Ctrl+b` → `o` | Cycle through panes |
| `Ctrl+b` → `z` | Zoom/unzoom current pane (fullscreen toggle) |

### Session Management
| Command | Action |
|---------|--------|
| `Ctrl+b` → `d` | **Detach** (session keeps running in background) |
| `tmux attach -t restaurant-app` | **Reattach** to session |
| `tmux ls` | List all sessions |
| `tmux kill-session -t restaurant-app` | Kill the session |

### Pane Management
| Command | Action |
|---------|--------|
| `Ctrl+b` → `"` | Split horizontally (new pane below) |
| `Ctrl+b` → `%` | Split vertically (new pane right) |
| `Ctrl+b` → `x` | Close current pane (confirm with y) |
| `Ctrl+b` → `{` | Swap pane with previous |
| `Ctrl+b` → `}` | Swap pane with next |
| `Ctrl+b` → `spacebar` | Cycle through layouts |

### Window Management (if you need more workspaces)
| Command | Action |
|---------|--------|
| `Ctrl+b` → `c` | Create new window |
| `Ctrl+b` → `n` | Next window |
| `Ctrl+b` → `p` | Previous window |
| `Ctrl+b` → `0-9` | Jump to window number |
| `Ctrl+b` → `,` | Rename current window |

### Copy Mode (scrolling back through output)
| Command | Action |
|---------|--------|
| `Ctrl+b` → `[` | Enter copy mode (use arrow keys to scroll) |
| `q` | Exit copy mode |
| `Space` | Start selection (in copy mode) |
| `Enter` | Copy selection |
| `Ctrl+b` → `]` | Paste |

### Other Useful Commands
| Command | Action |
|---------|--------|
| `Ctrl+b` → `?` | Show all keybindings |
| `Ctrl+b` → `t` | Show clock (fun!) |
| `Ctrl+b` → `:` | Enter command mode |

---

## Common Workflows

### Starting Your Work Day
```bash
# Start/resume your session
./setup_tmux.sh
tmux attach -t restaurant-app

# In Pane 2 (bottom-left): Start the app
streamlit run Home.py

# In Pane 0 (top-left): Work on code
# In Pane 3 (bottom-right): Run tests when needed
pytest

# When done for the day
Ctrl+b → d    # Detach (everything keeps running)
```

### Demo Day (Sysco Meeting)
```bash
# Before the meeting:
tmux attach -t restaurant-app

# Zoom pane 2 (Streamlit) for clean demo
Ctrl+b → ↓    # Move to Streamlit pane
Ctrl+b → z    # Zoom (fullscreen)

# Show code if needed
Ctrl+b → z    # Unzoom
Ctrl+b → ↑    # Back to dev pane

# Quick fix during demo
Ctrl+b → ←    # Jump to dev pane
# Make changes
Ctrl+b → ↓    # Back to Streamlit
# Refresh browser
```

### Recovering from Crashes
```bash
# If terminal crashes or closes
# Your session is STILL RUNNING!
tmux attach -t restaurant-app

# Everything will be exactly as you left it
# Streamlit still running, no lost work!
```

---

## Tips & Tricks

1. **Muscle Memory**: Practice `Ctrl+b` → arrow keys for navigation
2. **Zoom is your friend**: Use `Ctrl+b → z` to focus on one pane
3. **Detach freely**: Your session persists - close laptop, come back later
4. **Scrollback**: `Ctrl+b → [` then arrow keys to scroll through history
5. **Kill frozen pane**: `Ctrl+b → x` to close stuck processes

---

## Troubleshooting

**Q: I'm stuck in copy mode!**
A: Press `q` to exit

**Q: I can't type in any pane!**
A: You might be in copy mode - press `q`

**Q: How do I know which pane is active?**
A: Active pane has a green border (default)

**Q: I pressed Ctrl+b but nothing happened!**
A: Wait a second after pressing Ctrl+b, then press the next key

**Q: How do I exit tmux completely?**
A: Close all panes (`Ctrl+b → x` in each) OR `exit` in each pane

**Q: My layout got messed up!**
A: Run `./setup_tmux.sh` again (will recreate clean layout)

---

## For Your Sysco Meeting

**Pre-Meeting Setup:**
```bash
./setup_tmux.sh
tmux attach -t restaurant-app

# Pane 2: Start app
streamlit run Home.py

# Pane 1: Have sample Sysco CSV ready
ls -la data/*.csv

# Pane 3: Pre-run tests to verify everything works
pytest -v
```

**During Meeting:**
- Keep Streamlit pane zoomed (`Ctrl+b → z`)
- Unzoom if you need to show code (`Ctrl+b → z` again)
- Everything organized and professional!

---

## Quick Reference Card

```
PREFIX: Ctrl+b (then release, then press command)

Essential Navigation:
  ← ↑ → ↓   Move between panes
  z         Zoom current pane
  d         Detach (keeps running)
  x         Close current pane
  ?         Help menu

From Terminal:
  tmux attach -t restaurant-app    Reattach
  ./setup_tmux.sh                  Create session
```

---

**Happy tmuxing! 🚀**
