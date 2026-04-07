#!/bin/bash

REPO_DIR="$HOME/ai-logging-agent"
REMOTE="https://github.com/ingchrist/ai-logging-agent.git"
BRANCH="main"

# Make sure we're in the right directory
cd "$REPO_DIR" || exit 1

# Make sure remote is set
git remote set-url origin "$REMOTE" 2>/dev/null || git remote add origin "$REMOTE"

echo "👀 Watching $REPO_DIR for changes..."
echo "🚀 Will auto-push to $REMOTE"
echo "-----------------------------------------"

while true; do
    # Check if there are any changes
    if ! git diff --quiet || ! git diff --cached --quiet || [ -n "$(git ls-files --others --exclude-standard)" ]; then
        echo "📝 Change detected at $(date '+%Y-%m-%d %H:%M:%S')"

        git add -A

        # Commit with timestamp
        git commit -m "making some improvements at $(date '+%Y-%m-%d %H:%M:%S')"

        # Push
        if git push origin "$BRANCH"; then
            echo "✅ Pushed successfully!"
        else
            echo "❌ Push failed — check your credentials"
        fi
    fi

    # Check every 5 seconds
    sleep 60
    
done