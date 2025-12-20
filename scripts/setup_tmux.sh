#!/bin/bash
# Restaurant App Development - tmux Session Setup

SESSION="restaurant-app"
WORKDIR="/home/jkatz015/repos/restaurant_inventory_app"

# Check if session already exists
tmux has-session -t $SESSION 2>/dev/null

if [ $? != 0 ]; then
    echo "Creating new tmux session: $SESSION"

    # Create new session with first window
    tmux new-session -d -s $SESSION -c $WORKDIR

    # Rename first window
    tmux rename-window -t $SESSION:0 'Dev'

    # Split window into 4 panes
    # Main pane (top-left): Development
    tmux send-keys -t $SESSION:0 "echo 'Pane 1: Development Terminal'" C-m
    tmux send-keys -t $SESSION:0 "clear" C-m

    # Split horizontally (creates bottom pane)
    tmux split-window -v -t $SESSION:0 -c $WORKDIR
    tmux send-keys -t $SESSION:0.1 "echo 'Pane 2: Streamlit App (run: streamlit run Home.py)'" C-m

    # Split bottom pane vertically (creates bottom-right)
    tmux split-window -h -t $SESSION:0.1 -c $WORKDIR
    tmux send-keys -t $SESSION:0.2 "echo 'Pane 3: Testing (run: pytest)'" C-m

    # Split top pane vertically (creates top-right)
    tmux select-pane -t $SESSION:0.0
    tmux split-window -h -t $SESSION:0.0 -c $WORKDIR
    tmux send-keys -t $SESSION:0.1 "echo 'Pane 4: Git/Data Operations'" C-m

    # Resize panes for better layout
    # Make top row bigger (development space)
    tmux resize-pane -t $SESSION:0.0 -y 20

    # Select the development pane to start
    tmux select-pane -t $SESSION:0.0

    echo "✓ Session created successfully!"
    echo ""
    echo "Layout:"
    echo "┌─────────────────┬─────────────────┐"
    echo "│ Development     │ Git/Data Ops    │"
    echo "│ (Pane 0)        │ (Pane 1)        │"
    echo "├─────────────────┼─────────────────┤"
    echo "│ Streamlit App   │ Testing         │"
    echo "│ (Pane 2)        │ (Pane 3)        │"
    echo "└─────────────────┴─────────────────┘"
    echo ""
else
    echo "Session '$SESSION' already exists."
fi

echo "To attach to the session, run:"
echo "  tmux attach -t $SESSION"
echo ""
echo "Inside tmux:"
echo "  Ctrl+b → arrow keys  = Navigate panes"
echo "  Ctrl+b → d          = Detach (keeps running)"
echo "  Ctrl+b → x          = Close current pane"
echo "  Ctrl+b → z          = Zoom current pane (toggle fullscreen)"
