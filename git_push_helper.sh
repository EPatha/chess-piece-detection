#!/bin/bash
# Helper script untuk commit dan push ke GitHub

echo "🚀 Git Push Helper - Chess Vision for Blind"
echo "==========================================="
echo ""

# Check if there are changes
if git diff --quiet && git diff --staged --quiet && [ -z "$(git ls-files --others --exclude-standard)" ]; then
    echo "✅ No changes to commit"
    exit 0
fi

# Show status
echo "📋 Current status:"
git status --short
echo ""

# Ask for confirmation
read -p "⚠️  Add all files? (y/n) " -n 1 -r
echo ""

if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "📦 Adding files..."
    git add .
    
    echo ""
    echo "📋 Files staged for commit:"
    git status --short
    echo ""
    
    read -p "📝 Commit message (press Enter for default): " COMMIT_MSG
    
    if [ -z "$COMMIT_MSG" ]; then
        COMMIT_MSG="Update: Add DroidCam USB support and documentation"
    fi
    
    echo ""
    echo "💾 Committing..."
    git commit -m "$COMMIT_MSG"
    
    echo ""
    read -p "🚀 Push to GitHub? (y/n) " -n 1 -r
    echo ""
    
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        echo "📤 Pushing to origin main..."
        git push origin main
        echo ""
        echo "✅ Done! Changes pushed to GitHub"
    else
        echo "⏸  Skipped push. Run 'git push origin main' manually later."
    fi
else
    echo "❌ Cancelled"
fi
