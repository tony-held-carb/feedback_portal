#!/bin/bash

# Install Playwright on EC2 after conda environment creation
# This script handles the manual installation of Playwright to avoid conda compilation issues

set -e  # Exit on any error

echo "Installing Playwright manually on EC2..."
echo "========================================"

# Check if we're in the right conda environment
if [[ "$CONDA_DEFAULT_ENV" != "mini_conda_02" ]]; then
    echo "❌ Error: Please activate the mini_conda_02 environment first:"
    echo "   conda activate mini_conda_02"
    exit 1
fi

echo "✅ Conda environment: $CONDA_DEFAULT_ENV"

# Set Node.js path to use conda's version
export PLAYWRIGHT_NODEJS_PATH=~/miniconda3/envs/mini_conda_02/bin/node
echo "✅ Using Node.js: $PLAYWRIGHT_NODEJS_PATH"

# Install Playwright with specific versions
echo "Installing Playwright packages..."
pip install playwright==1.40.0 pytest-playwright==0.4.0

# Try to install browsers
echo "Installing Playwright browsers..."
echo "Note: This may show dependency warnings but should still work."

# Try different installation approaches
echo "Attempting playwright install..."
if playwright install; then
    echo "✅ Playwright browsers installed successfully!"
else
    echo "⚠️  Standard install failed, trying individual browsers..."
    
    # Try installing browsers individually
    for browser in firefox webkit chromium; do
        echo "Installing $browser..."
        if playwright install $browser; then
            echo "✅ $browser installed successfully!"
        else
            echo "⚠️  $browser installation failed, continuing..."
        fi
    done
fi

# Test browser compatibility
echo ""
echo "Testing browser compatibility..."
if python tests/e2e/test_browser_compatibility.py; then
    echo "✅ Browser compatibility test passed!"
else
    echo "⚠️  Browser compatibility test failed, but environment is ready for other tests."
fi

echo ""
echo "🎉 Playwright installation complete!"
echo "You can now run E2E tests with:"
echo "   pytest tests/e2e/ -v"
echo ""
echo "Note: If browsers don't work due to system dependencies,"
echo "      unit and integration tests will still work fine."