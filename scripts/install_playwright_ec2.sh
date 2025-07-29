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
echo "Trying Playwright versions in order of compatibility..."

# Try different Playwright versions (older versions are more compatible with GLIBC 2.26)
#PLAYWRIGHT_VERSIONS=("1.25.0" "1.30.0" "1.35.0" "1.40.0" "1.45.0")
PLAYWRIGHT_VERSIONS=("1.24.0" "1.45.0")

for version in "${PLAYWRIGHT_VERSIONS[@]}"; do
    echo "Trying Playwright version $version..."
    
    # Uninstall any existing playwright
    pip uninstall -y playwright pytest-playwright 2>/dev/null || true
    
    # Install specific version
    echo "Installing Playwright $version..."
    if pip install "playwright==$version"; then
        echo "✅ Successfully installed Playwright $version"
        
        echo "Installing pytest-playwright..."
#        if pip install "pytest-playwright==0.2.0"; then
        if pip install "pytest-playwright"; then
            echo "✅ Successfully installed pytest-playwright"
            
            # Try to install browsers
            echo "Installing Playwright browsers for version $version..."
            if playwright install; then
                echo "✅ Playwright browsers installed successfully!"
                break
            else
                echo "⚠️  Browser installation failed for version $version, trying next..."
                continue
            fi
        else
            echo "❌ Failed to install pytest-playwright, trying next..."
            continue
        fi
    else
        echo "❌ Failed to install Playwright $version, trying next..."
        continue
    fi
done

# Test browser compatibility
echo ""
echo "Testing browser compatibility..."
if python $portal/tests/e2e/test_browser_compatibility.py; then
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