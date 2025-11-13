#!/bin/bash
# Installation and setup script for LastPass Python CLI

set -e

echo "================================================"
echo "LastPass Python CLI - Installation Script"
echo "================================================"
echo ""

# Check Python version
echo "Checking Python version..."
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed."
    echo "Please install Python 3.8 or higher."
    exit 1
fi

PYTHON_VERSION=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:2])))')
echo "Found Python $PYTHON_VERSION"

# Check if version is >= 3.8
if ! python3 -c 'import sys; exit(0 if sys.version_info >= (3, 8) else 1)'; then
    echo "Error: Python 3.8 or higher is required."
    echo "Current version: $PYTHON_VERSION"
    exit 1
fi

echo "✓ Python version OK"
echo ""

# Install dependencies
echo "Installing dependencies..."
if command -v pip3 &> /dev/null; then
    PIP=pip3
elif command -v pip &> /dev/null; then
    PIP=pip
else
    echo "Error: pip is not installed."
    exit 1
fi

echo "Using: $PIP"
$PIP install -r requirements.txt

echo "✓ Dependencies installed"
echo ""

# Optional: Install development dependencies
read -p "Install development dependencies? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PIP install pytest pytest-cov black flake8 mypy
    echo "✓ Development dependencies installed"
fi
echo ""

# Optional: Install clipboard support
read -p "Install clipboard support? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    $PIP install pyperclip
    echo "✓ Clipboard support installed"
fi
echo ""

# Install package
echo "Installing lastpass package..."
$PIP install -e .
echo "✓ Package installed"
echo ""

# Create config directory
CONFIG_DIR="${XDG_CONFIG_HOME:-$HOME/.config}/lpass"
if [ ! -d "$CONFIG_DIR" ]; then
    echo "Creating config directory: $CONFIG_DIR"
    mkdir -p "$CONFIG_DIR"
    chmod 700 "$CONFIG_DIR"
    echo "✓ Config directory created"
fi
echo ""

# Run tests
read -p "Run tests? (y/N) " -n 1 -r
echo
if [[ $REPLY =~ ^[Yy]$ ]]; then
    echo "Running tests..."
    pytest tests/ -v
fi
echo ""

# Success message
echo "================================================"
echo "Installation completed successfully!"
echo "================================================"
echo ""
echo "Quick start:"
echo ""
echo "  # Login to LastPass"
echo "  lpass login your.email@example.com"
echo ""
echo "  # List your accounts"
echo "  lpass ls"
echo ""
echo "  # Show account details"
echo "  lpass show github --password"
echo ""
echo "  # Generate a password"
echo "  lpass generate 20"
echo ""
echo "For more information:"
echo "  - See README_PYTHON.md for complete documentation"
echo "  - See USAGE_GUIDE.md for detailed examples"
echo "  - Run 'lpass --help' for command reference"
echo ""
echo "Python API example:"
echo ""
echo "  from lastpass import LastPassClient"
echo "  client = LastPassClient()"
echo "  client.login('your.email@example.com', 'password')"
echo "  accounts = client.get_accounts()"
echo ""
