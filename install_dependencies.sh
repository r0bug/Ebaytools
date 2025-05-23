#!/bin/bash
# eBay Tools Dependency Installer for Linux/macOS
# Comprehensive installation script with automatic platform detection

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Print colored output
print_error() { echo -e "${RED}❌ $1${NC}"; }
print_success() { echo -e "${GREEN}✅ $1${NC}"; }
print_warning() { echo -e "${YELLOW}⚠️  $1${NC}"; }
print_info() { echo -e "${BLUE}ℹ️  $1${NC}"; }

# Print header
echo -e "${BLUE}=============================================${NC}"
echo -e "${BLUE}   eBay Tools Dependency Installer v3.0.0${NC}"
echo -e "${BLUE}=============================================${NC}"
echo "Platform: $(uname -s) $(uname -r)"
echo "Architecture: $(uname -m)"
echo

# Detect platform
PLATFORM=$(uname -s | tr '[:upper:]' '[:lower:]')
INSTALL_SUCCESS=1
PYTHON_CMD=""

# Function to check if command exists
command_exists() {
    command -v "$1" >/dev/null 2>&1
}

# Find Python installation
find_python() {
    print_info "Detecting Python installation..."
    
    # Try different Python commands
    for cmd in python3 python py; do
        if command_exists "$cmd"; then
            VERSION=$("$cmd" --version 2>&1 | grep -o '[0-9]\+\.[0-9]\+')
            MAJOR=$(echo "$VERSION" | cut -d. -f1)
            MINOR=$(echo "$VERSION" | cut -d. -f2)
            
            if [ "$MAJOR" -eq 3 ] && [ "$MINOR" -ge 8 ]; then
                PYTHON_CMD="$cmd"
                print_success "Found Python $VERSION using '$cmd' command"
                return 0
            fi
        fi
    done
    
    print_error "Python 3.8+ not found!"
    echo "Please install Python 3.8 or higher:"
    echo "  Ubuntu/Debian: sudo apt-get install python3 python3-pip"
    echo "  RHEL/CentOS:   sudo yum install python3 python3-pip"
    echo "  macOS:         brew install python3"
    echo "  Or download from: https://www.python.org/downloads/"
    exit 1
}

# Install system dependencies for Linux
install_linux_deps() {
    print_info "Installing Linux system dependencies..."
    
    if command_exists apt-get; then
        print_info "Using apt-get (Debian/Ubuntu)..."
        sudo apt-get update
        sudo apt-get install -y \
            python3-tk python3-dev python3-pip \
            libjpeg-dev libpng-dev libfreetype6-dev \
            liblcms2-dev libwebp-dev libharfbuzz-dev \
            libfribidi-dev libxcb1-dev || {
            print_warning "Some system packages failed to install"
        }
        print_success "Debian/Ubuntu dependencies installed"
        
    elif command_exists yum; then
        print_info "Using yum (RHEL/CentOS)..."
        sudo yum install -y \
            tkinter python3-devel python3-pip \
            libjpeg-turbo-devel libpng-devel \
            freetype-devel lcms2-devel || {
            print_warning "Some system packages failed to install"
        }
        print_success "RHEL/CentOS dependencies installed"
        
    elif command_exists pacman; then
        print_info "Using pacman (Arch Linux)..."
        sudo pacman -S --noconfirm \
            tk python python-pip libjpeg-turbo \
            libpng freetype2 lcms2 || {
            print_warning "Some system packages failed to install"
        }
        print_success "Arch Linux dependencies installed"
        
    else
        print_warning "Package manager not detected"
        print_info "You may need to install system dependencies manually:"
        print_info "- Python development headers"
        print_info "- tkinter GUI framework"
        print_info "- Image processing libraries (jpeg, png, freetype)"
    fi
}

# Install system dependencies for macOS
install_macos_deps() {
    print_info "Installing macOS system dependencies..."
    
    if command_exists brew; then
        print_info "Using Homebrew..."
        brew install python-tk jpeg libpng freetype || {
            print_warning "Some Homebrew packages failed to install"
        }
        print_success "macOS dependencies installed"
    else
        print_warning "Homebrew not found"
        print_info "Install Homebrew from: https://brew.sh/"
        print_info "Then run: brew install python-tk jpeg libpng freetype"
    fi
}

# Install Python packages
install_python_packages() {
    print_info "Installing Python packages..."
    
    # Upgrade pip first
    print_info "Upgrading pip..."
    "$PYTHON_CMD" -m pip install --upgrade pip || {
        print_warning "Failed to upgrade pip, continuing..."
    }
    
    # Core packages
    local core_packages=(
        "requests>=2.25.1"
        "pillow>=8.2.0"
        "beautifulsoup4>=4.9.3"
    )
    
    print_info "Installing core packages..."
    for package in "${core_packages[@]}"; do
        package_name=$(echo "$package" | cut -d'>=' -f1)
        echo "Installing $package_name..."
        if "$PYTHON_CMD" -m pip install "$package"; then
            print_success "$package_name installed"
        else
            print_error "Failed to install $package_name"
            INSTALL_SUCCESS=0
        fi
    done
    
    # Optional packages
    local optional_packages=(
        "lxml"
        "numpy"
        "certifi"
        "urllib3"
        "charset-normalizer"
    )
    
    print_info "Installing optional packages..."
    for package in "${optional_packages[@]}"; do
        echo "Installing $package..."
        if "$PYTHON_CMD" -m pip install "$package"; then
            print_success "$package installed (optional)"
        else
            print_warning "$package installation failed (optional)"
        fi
    done
}

# Test imports
test_imports() {
    print_info "Testing critical imports..."
    
    # Test tkinter
    if "$PYTHON_CMD" -c "import tkinter; print('✓ tkinter working')" 2>/dev/null; then
        print_success "tkinter GUI framework working"
    else
        print_error "tkinter not working - GUI will not function"
        INSTALL_SUCCESS=0
    fi
    
    # Test requests
    if "$PYTHON_CMD" -c "import requests; print('✓ requests working')" 2>/dev/null; then
        print_success "requests HTTP library working"
    else
        print_error "requests not working"
        INSTALL_SUCCESS=0
    fi
    
    # Test Pillow
    if "$PYTHON_CMD" -c "from PIL import Image; print('✓ Pillow working')" 2>/dev/null; then
        print_success "Pillow image processing working"
    else
        print_error "Pillow not working"
        INSTALL_SUCCESS=0
    fi
    
    # Test BeautifulSoup
    if "$PYTHON_CMD" -c "from bs4 import BeautifulSoup; print('✓ BeautifulSoup working')" 2>/dev/null; then
        print_success "BeautifulSoup HTML parsing working"
    else
        print_error "BeautifulSoup not working"
        INSTALL_SUCCESS=0
    fi
}

# Create test script
create_test_script() {
    cat > test_ebay_tools.py << 'EOF'
#!/usr/bin/env python3
"""eBay Tools Installation Test"""

def test_gui():
    """Test GUI functionality"""
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("eBay Tools Test")
        root.geometry("300x100")
        
        label = tk.Label(root, text="✅ GUI Test Successful!")
        label.pack(pady=20)
        
        button = tk.Button(root, text="Close", command=root.destroy)
        button.pack()
        
        print("✅ GUI test window created")
        print("Close the window to continue...")
        root.mainloop()
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

if __name__ == "__main__":
    print("Testing eBay Tools installation...")
    if test_gui():
        print("🎉 Installation test passed!")
    else:
        print("❌ Installation test failed")
EOF
    
    chmod +x test_ebay_tools.py
    print_success "Test script created: test_ebay_tools.py"
}

# Print summary
print_summary() {
    echo
    echo -e "${BLUE}=============================================${NC}"
    echo -e "${BLUE}   Installation Summary${NC}"
    echo -e "${BLUE}=============================================${NC}"
    
    if [ $INSTALL_SUCCESS -eq 1 ]; then
        echo
        print_success "All dependencies installed successfully!"
        echo
        print_info "Your system is ready to run eBay Tools."
        echo
        print_info "Next steps:"
        echo "1. Run: python3 test_ebay_tools.py"
        echo "2. Extract the eBay Tools package"
        echo "3. Run applications using Python modules:"
        echo "   python3 -m ebay_tools.apps.setup"
        echo "   python3 -m ebay_tools.apps.processor"
        echo "   python3 -m ebay_tools.apps.viewer"
        echo "   python3 -m ebay_tools.apps.price_analyzer"
        echo
    else
        echo
        print_error "Installation completed with errors!"
        echo
        print_warning "Some dependencies failed to install."
        print_info "eBay Tools may not function correctly."
        echo
        print_info "Common solutions:"
        echo "- Install missing system packages"
        echo "- Check internet connection"
        echo "- Update Python to latest version"
        echo "- Use virtual environment: python3 -m venv ebay_env"
        echo
    fi
    
    echo -e "${BLUE}=============================================${NC}"
}

# Main installation process
main() {
    find_python
    
    # Install system dependencies based on platform
    case "$PLATFORM" in
        linux)
            install_linux_deps
            ;;
        darwin)
            install_macos_deps
            ;;
        *)
            print_warning "Unknown platform: $PLATFORM"
            print_info "System dependencies may need manual installation"
            ;;
    esac
    
    install_python_packages
    test_imports
    create_test_script
    print_summary
    
    return $INSTALL_SUCCESS
}

# Run main function
if main; then
    print_success "Installation completed successfully!"
    exit 0
else
    print_error "Installation failed. Please check errors above."
    exit 1
fi