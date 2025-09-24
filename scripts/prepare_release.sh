#!/bin/bash
# Release preparation script for us-stock-recommender

set -e

echo "🚀 US Stock Recommender - Release Preparation Script"
echo "=================================================="

# Check if version is provided
if [ $# -eq 0 ]; then
    echo "❌ Error: Please provide a version number"
    echo "Usage: $0 <version> [--dry-run]"
    echo "Example: $0 1.0.1"
    exit 1
fi

VERSION=$1
DRY_RUN=""

if [ "$2" == "--dry-run" ]; then
    DRY_RUN="--dry-run"
    echo "🧪 Running in dry-run mode"
fi

echo "📝 Preparing release for version: $VERSION"

# Validate version format (semantic versioning)
if ! [[ $VERSION =~ ^[0-9]+\.[0-9]+\.[0-9]+$ ]]; then
    echo "❌ Error: Version must be in format X.Y.Z (e.g., 1.0.1)"
    exit 1
fi

# Check if we're on main branch
CURRENT_BRANCH=$(git branch --show-current)
if [ "$CURRENT_BRANCH" != "main" ]; then
    echo "❌ Error: Must be on main branch for release"
    echo "Current branch: $CURRENT_BRANCH"
    exit 1
fi

# Check for uncommitted changes
if [ -n "$(git status --porcelain)" ]; then
    echo "❌ Error: Working directory is not clean"
    echo "Please commit or stash your changes first"
    git status
    exit 1
fi

# Update version in pyproject.toml
echo "📝 Updating version in pyproject.toml..."
if [ -z "$DRY_RUN" ]; then
    sed -i.bak "s/^version = .*/version = \"$VERSION\"/" pyproject.toml
    rm pyproject.toml.bak
    echo "✅ Updated version to $VERSION"
else
    echo "🧪 Would update version to $VERSION"
fi

# Install build dependencies
echo "📦 Installing build dependencies..."
pip install build twine pytest

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Build package
echo "📦 Building package..."
python -m build

# Check package
echo "🔍 Checking package..."
python -m twine check dist/*

# Show package info
echo "📊 Package information:"
ls -la dist/

if [ -z "$DRY_RUN" ]; then
    # Commit version update
    echo "💾 Committing version update..."
    git add pyproject.toml
    git commit -m "🔖 Bump version to $VERSION"
    
    # Create and push tag
    echo "🏷️  Creating git tag..."
    git tag -a "v$VERSION" -m "Release version $VERSION"
    
    echo "📤 Pushing changes and tag..."
    git push origin main
    git push origin "v$VERSION"
    
    echo "✅ Release preparation completed!"
    echo ""
    echo "📋 Next steps:"
    echo "1. Go to GitHub releases page"
    echo "2. Create a new release for tag v$VERSION"
    echo "3. Add release notes"
    echo "4. Publish the release"
    echo "5. GitHub Actions will automatically publish to PyPI"
    echo ""
    echo "🌐 GitHub releases: https://github.com/lvyongyu/us-stock-recommender/releases"
else
    echo "🧪 Dry run completed successfully!"
    echo "Run without --dry-run to actually create the release"
fi
