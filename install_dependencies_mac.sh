#!/bin/bash

# eBay Tools macOS Installer
# Comprehensive installer for macOS systems

set -e  # Exit on error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_info() { echo -e "${BLUE}[INFO]${NC} $1"; }
print_success() { echo -e "${GREEN}[SUCCESS]${NC} $1"; }
print_warning() { echo -e "${YELLOW}[WARNING]${NC} $1"; }
print_error() { echo -e "${RED}[ERROR]${NC} $1"; }

# Print header
echo "=============================================="
echo "     eBay Tools macOS Installer v3.0.0"
echo "=============================================="
echo "System: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo "=============================================="
echo

# Check if running on macOS
if [[ "$(uname)" != "Darwin" ]]; then
    print_error "This installer is for macOS only. Use install_dependencies.sh for Linux."
    exit 1
fi

# Function to check if a command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Function to check Python version
check_python() {
    print_info "Checking Python installation..."
    
    # Check for python3
    if command_exists python3; then
        PYTHON_CMD="python3"
        PIP_CMD="pip3"
    elif command_exists python; then
        # Check if it's Python 3
        if python --version 2>&1 | grep -q "Python 3"; then
            PYTHON_CMD="python"
            PIP_CMD="pip"
        else
            print_error "Python 3 is required but not found"
            return 1
        fi
    else
        print_error "Python is not installed"
        return 1
    fi
    
    # Get Python version
    PYTHON_VERSION=$($PYTHON_CMD --version 2>&1 | cut -d' ' -f2)
    PYTHON_MAJOR=$(echo $PYTHON_VERSION | cut -d'.' -f1)
    PYTHON_MINOR=$(echo $PYTHON_VERSION | cut -d'.' -f2)
    
    print_info "Found Python $PYTHON_VERSION"
    
    # Check if version is 3.8+
    if [[ $PYTHON_MAJOR -lt 3 ]] || [[ $PYTHON_MAJOR -eq 3 && $PYTHON_MINOR -lt 8 ]]; then
        print_error "Python 3.8+ is required, found $PYTHON_VERSION"
        return 1
    fi
    
    print_success "Python $PYTHON_VERSION is compatible"
    return 0
}

# Function to install Homebrew
install_homebrew() {
    print_info "Checking for Homebrew..."
    
    if ! command_exists brew; then
        print_warning "Homebrew not found. Installing..."
        /bin/bash -c "$(curl -fsSL https://raw.githubusercontent.com/Homebrew/install/HEAD/install.sh)"
        
        # Add Homebrew to PATH for Apple Silicon Macs
        if [[ -f "/opt/homebrew/bin/brew" ]]; then
            eval "$(/opt/homebrew/bin/brew shellenv)"
            echo 'eval "$(/opt/homebrew/bin/brew shellenv)"' >> ~/.zprofile
        fi
        
        print_success "Homebrew installed successfully"
    else
        print_success "Homebrew is already installed"
        print_info "Updating Homebrew..."
        brew update
    fi
}

# Function to install Python via Homebrew
install_python() {
    print_info "Installing Python 3 via Homebrew..."
    
    if brew list python@3.11 &>/dev/null; then
        print_success "Python 3.11 is already installed"
    else
        brew install python@3.11
        print_success "Python 3.11 installed successfully"
    fi
    
    # Link python3 and pip3
    brew link --overwrite python@3.11
    
    # Update PATH
    export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"
    echo 'export PATH="/opt/homebrew/opt/python@3.11/bin:$PATH"' >> ~/.zshrc
}

# Function to install system dependencies
install_system_deps() {
    print_info "Installing system dependencies..."
    
    # Install required packages
    PACKAGES=(
        "python-tk"      # Tkinter support
        "jpeg"           # JPEG support for Pillow
        "libpng"         # PNG support for Pillow
        "freetype"       # Font support for Pillow
        "webp"           # WebP support for Pillow
        "libtiff"        # TIFF support for Pillow
        "little-cms2"    # Color management for Pillow
    )
    
    for package in "${PACKAGES[@]}"; do
        if brew list $package &>/dev/null; then
            print_info "$package is already installed"
        else
            print_info "Installing $package..."
            brew install $package
        fi
    done
    
    print_success "System dependencies installed"
}

# Function to install Python packages
install_python_packages() {
    print_info "Installing Python packages..."
    
    # Upgrade pip
    print_info "Upgrading pip..."
    $PYTHON_CMD -m pip install --upgrade pip
    
    # Install required packages
    print_info "Installing required Python packages..."
    $PIP_CMD install --upgrade requests>=2.25.1
    $PIP_CMD install --upgrade pillow>=8.2.0
    $PIP_CMD install --upgrade beautifulsoup4>=4.9.3
    
    # Install optional packages
    print_info "Installing optional Python packages..."
    $PIP_CMD install --upgrade lxml>=4.6.3 || print_warning "lxml installation failed (optional)"
    $PIP_CMD install --upgrade numpy || print_warning "numpy installation failed (optional)"
    
    print_success "Python packages installed"
}

# Function to verify installation
verify_installation() {
    print_info "Verifying installation..."
    
    # Test imports
    $PYTHON_CMD -c "import tkinter" || { print_error "tkinter import failed"; return 1; }
    $PYTHON_CMD -c "import requests" || { print_error "requests import failed"; return 1; }
    $PYTHON_CMD -c "from PIL import Image" || { print_error "PIL import failed"; return 1; }
    $PYTHON_CMD -c "from bs4 import BeautifulSoup" || { print_error "BeautifulSoup import failed"; return 1; }
    
    print_success "All required modules imported successfully"
    
    # Test tkinter GUI
    print_info "Testing GUI functionality..."
    $PYTHON_CMD -c "
import tkinter as tk
root = tk.Tk()
root.withdraw()
root.destroy()
print('GUI test passed')
" || { print_error "GUI test failed"; return 1; }
    
    print_success "Installation verified successfully"
    return 0
}

# Function to create app launchers
create_launchers() {
    print_info "Creating application launchers..."
    
    # Create launchers directory
    mkdir -p launchers/mac
    
    # Base launcher template
    create_launcher() {
        local app_name=$1
        local module_name=$2
        local script_name="launchers/mac/${app_name}.command"
        
        cat > "$script_name" << EOF
#!/bin/bash
# eBay Tools - $app_name Launcher for macOS

# Get the directory of this script
DIR="\$( cd "\$( dirname "\${BASH_SOURCE[0]}" )" && pwd )"
cd "\$DIR/../.."

# Set Python path
export PYTHONPATH="\$PWD:\$PYTHONPATH"

# Check if Python is available
if command -v python3 >/dev/null 2>&1; then
    PYTHON_CMD="python3"
elif command -v python >/dev/null 2>&1; then
    PYTHON_CMD="python"
else
    echo "Error: Python is not installed"
    echo "Please install Python 3.8 or higher"
    read -p "Press any key to exit..."
    exit 1
fi

# Run the application
echo "Starting $app_name..."
\$PYTHON_CMD -m ebay_tools.apps.$module_name

# Keep terminal open if there's an error
if [ \$? -ne 0 ]; then
    echo
    echo "An error occurred. Press any key to exit..."
    read -n 1
fi
EOF
        
        chmod +x "$script_name"
        print_success "Created launcher: $script_name"
    }
    
    # Create launchers for each app
    create_launcher "Setup" "setup"
    create_launcher "Processor" "processor"
    create_launcher "Viewer" "viewer"
    create_launcher "Price Analyzer" "price_analyzer"
    create_launcher "Gallery Creator" "gallery_creator"
    create_launcher "Direct Listing" "direct_listing"
    create_launcher "CSV Export" "csv_export"
    
    # Create main launcher
    cat > "launchers/mac/eBay Tools.command" << 'EOF'
#!/bin/bash
# eBay Tools - Main Launcher for macOS

# Get the directory of this script
DIR="$( cd "$( dirname "${BASH_SOURCE[0]}" )" && pwd )"
cd "$DIR"

# Terminal colors
RED='\033[0;31m'
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m'

clear
echo -e "${BLUE}============================================${NC}"
echo -e "${BLUE}          eBay Tools Suite v3.0.0          ${NC}"
echo -e "${BLUE}============================================${NC}"
echo
echo "Select an application to launch:"
echo
echo "  1) Setup Tool - Create and manage item queues"
echo "  2) Processor Tool - AI-powered photo analysis"
echo "  3) Viewer Tool - Review and export results"
echo "  4) Price Analyzer - Analyze eBay pricing"
echo "  5) Gallery Creator - Create HTML galleries"
echo "  6) Direct Listing - Direct eBay API listing"
echo "  7) CSV Export - Export to eBay CSV format"
echo
echo "  0) Exit"
echo
read -p "Enter your choice (0-7): " choice

case $choice in
    1) ./Setup.command ;;
    2) ./Processor.command ;;
    3) ./Viewer.command ;;
    4) ./Price\ Analyzer.command ;;
    5) ./Gallery\ Creator.command ;;
    6) ./Direct\ Listing.command ;;
    7) ./CSV\ Export.command ;;
    0) exit 0 ;;
    *) echo -e "${RED}Invalid choice${NC}"; sleep 2; exec "$0" ;;
esac
EOF
    
    chmod +x "launchers/mac/eBay Tools.command"
    print_success "Created main launcher"
}

# Function to create desktop shortcut
create_desktop_shortcut() {
    print_info "Creating desktop shortcut..."
    
    DESKTOP="$HOME/Desktop"
    if [ -d "$DESKTOP" ]; then
        ln -sf "$PWD/launchers/mac/eBay Tools.command" "$DESKTOP/eBay Tools"
        print_success "Desktop shortcut created"
    else
        print_warning "Desktop folder not found, skipping shortcut creation"
    fi
}

# Main installation flow
main() {
    # Check for Homebrew and install if needed
    install_homebrew
    
    # Check Python or install it
    if ! check_python; then
        print_warning "Installing Python via Homebrew..."
        install_python
        
        # Re-check Python
        if ! check_python; then
            print_error "Failed to install Python"
            exit 1
        fi
    fi
    
    # Install system dependencies
    install_system_deps
    
    # Install Python packages
    install_python_packages
    
    # Verify installation
    if ! verify_installation; then
        print_error "Installation verification failed"
        exit 1
    fi
    
    # Create launchers
    create_launchers
    
    # Create desktop shortcut
    create_desktop_shortcut
    
    # Print summary
    echo
    echo "=============================================="
    echo -e "${GREEN}   Installation completed successfully!${NC}"
    echo "=============================================="
    echo
    echo "You can now run eBay Tools using:"
    echo "  - Desktop shortcut: 'eBay Tools'"
    echo "  - Terminal: ./launchers/mac/eBay\\ Tools.command"
    echo "  - Individual apps in ./launchers/mac/"
    echo
    echo "First time users should start with the Setup Tool"
    echo "to create their first item queue."
    echo
    print_success "Happy selling!"
}

# Run main installation
main