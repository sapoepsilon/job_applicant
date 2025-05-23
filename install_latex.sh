#!/bin/bash

# LaTeX Installation Script for macOS
# This script checks for and installs LaTeX (pdflatex) if not present

echo "Checking for LaTeX installation..."

# Check if pdflatex is already installed
if command -v pdflatex &> /dev/null; then
    echo "✅ pdflatex is already installed!"
    echo "Version: $(pdflatex --version | head -n 1)"
    echo "Location: $(which pdflatex)"
    exit 0
fi

echo "❌ pdflatex not found. Installing LaTeX..."

# Check if Homebrew is installed
if ! command -v brew &> /dev/null; then
    echo "Homebrew not found. Installing Homebrew first..."
    /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
fi

# Install BasicTeX (smaller alternative to full MacTeX)
echo "Installing BasicTeX via Homebrew..."
brew install --cask basictex

# Add TeX binaries to PATH
echo "Adding TeX binaries to PATH..."
export PATH="/Library/TeX/texbin:$PATH"

# Update tlmgr and install necessary packages
echo "Updating TeX package manager..."
sudo tlmgr update --self

# Install commonly needed LaTeX packages for resume generation
echo "Installing essential LaTeX packages..."
sudo tlmgr install collection-basic
sudo tlmgr install collection-latex
sudo tlmgr install collection-latexextra
sudo tlmgr install collection-fontsrecommended

echo "✅ LaTeX installation complete!"
echo ""
echo "Please restart your terminal or run:"
echo "  export PATH=\"/Library/TeX/texbin:\$PATH\""
echo ""
echo "To make this permanent, add the above line to your ~/.zshrc or ~/.bash_profile"