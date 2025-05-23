#!/usr/bin/env python3
"""
eBay Tools Dependency Installer
Comprehensive script to install all dependencies needed to run eBay Tools
Supports Windows, macOS, and Linux with automatic platform detection
"""

import sys
import subprocess
import os
import platform
import importlib.util
from pathlib import Path

class DependencyInstaller:
    def __init__(self):
        self.platform = platform.system().lower()
        self.python_version = sys.version_info
        self.errors = []
        self.installed_packages = []
        
    def print_header(self):
        """Print installation header"""
        print("=" * 60)
        print("    eBay Tools Dependency Installer v3.0.0")
        print("=" * 60)
        print(f"Platform: {platform.system()} {platform.release()}")
        print(f"Python: {sys.version}")
        print(f"Architecture: {platform.machine()}")
        print("=" * 60)
        print()
    
    def check_python_version(self):
        """Check if Python version is compatible"""
        print("Checking Python version...")
        if self.python_version < (3, 8):
            print(f"❌ ERROR: Python 3.8+ required, found {self.python_version.major}.{self.python_version.minor}")
            print("Please upgrade Python: https://www.python.org/downloads/")
            return False
        print(f"✅ Python {self.python_version.major}.{self.python_version.minor} is compatible")
        return True
    
    def check_pip(self):
        """Check if pip is available and upgrade it"""
        print("\nChecking pip...")
        try:
            import pip
            print("✅ pip is available")
        except ImportError:
            print("❌ pip not found, attempting to install...")
            try:
                subprocess.check_call([sys.executable, "-m", "ensurepip", "--upgrade"])
                print("✅ pip installed successfully")
            except subprocess.CalledProcessError as e:
                print(f"❌ Failed to install pip: {e}")
                return False
        
        # Upgrade pip
        print("Upgrading pip...")
        try:
            subprocess.check_call([sys.executable, "-m", "pip", "install", "--upgrade", "pip"])
            print("✅ pip upgraded successfully")
        except subprocess.CalledProcessError as e:
            print(f"⚠️ Warning: Failed to upgrade pip: {e}")
        
        return True
    
    def install_system_dependencies(self):
        """Install system-level dependencies based on platform"""
        print(f"\nInstalling system dependencies for {self.platform}...")
        
        if self.platform == "linux":
            self._install_linux_deps()
        elif self.platform == "darwin":  # macOS
            self._install_macos_deps()
        elif self.platform == "windows":
            self._install_windows_deps()
        else:
            print(f"⚠️ Unknown platform: {self.platform}, skipping system dependencies")
    
    def _install_linux_deps(self):
        """Install Linux system dependencies"""
        # Common packages needed for tkinter, image processing, etc.
        packages = [
            "python3-tk",  # tkinter GUI
            "python3-dev",  # Python development headers
            "libjpeg-dev",  # JPEG support for Pillow
            "libpng-dev",   # PNG support for Pillow
            "libfreetype6-dev",  # Font support for Pillow
            "liblcms2-dev",  # Color management for Pillow
            "libwebp-dev",   # WebP support for Pillow
            "libharfbuzz-dev",  # Text rendering for Pillow
            "libfribidi-dev",   # Text rendering for Pillow
            "libxcb1-dev",      # X11 support
        ]
        
        # Try different package managers
        if self._command_exists("apt-get"):
            print("Using apt-get (Debian/Ubuntu)...")
            try:
                subprocess.run(["sudo", "apt-get", "update"], check=True)
                subprocess.run(["sudo", "apt-get", "install", "-y"] + packages, check=True)
                print("✅ Linux dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Some system packages failed to install: {e}")
                
        elif self._command_exists("yum"):
            print("Using yum (RHEL/CentOS)...")
            packages_yum = [
                "tkinter", "python3-devel", "libjpeg-turbo-devel",
                "libpng-devel", "freetype-devel", "lcms2-devel"
            ]
            try:
                subprocess.run(["sudo", "yum", "install", "-y"] + packages_yum, check=True)
                print("✅ Linux dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Some system packages failed to install: {e}")
                
        elif self._command_exists("pacman"):
            print("Using pacman (Arch Linux)...")
            packages_arch = [
                "tk", "python", "libjpeg-turbo", "libpng", "freetype2", "lcms2"
            ]
            try:
                subprocess.run(["sudo", "pacman", "-S", "--noconfirm"] + packages_arch, check=True)
                print("✅ Linux dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Some system packages failed to install: {e}")
        else:
            print("⚠️ Package manager not detected, you may need to install system dependencies manually")
    
    def _install_macos_deps(self):
        """Install macOS system dependencies"""
        if self._command_exists("brew"):
            print("Using Homebrew...")
            packages = ["python-tk", "jpeg", "libpng", "freetype"]
            try:
                subprocess.run(["brew", "install"] + packages, check=True)
                print("✅ macOS dependencies installed")
            except subprocess.CalledProcessError as e:
                print(f"⚠️ Some Homebrew packages failed to install: {e}")
        else:
            print("⚠️ Homebrew not found, install from: https://brew.sh/")
            print("Then run: brew install python-tk jpeg libpng freetype")
    
    def _install_windows_deps(self):
        """Install Windows system dependencies"""
        print("Windows dependencies are typically included with Python")
        print("If you encounter issues, ensure you have:")
        print("- Python installed with tkinter support")
        print("- Visual C++ Redistributable (for some packages)")
        print("✅ Windows dependencies check complete")
    
    def install_python_packages(self):
        """Install Python packages from requirements"""
        print("\nInstalling Python packages...")
        
        # Core requirements
        core_packages = [
            "requests>=2.25.1",
            "pillow>=8.2.0", 
            "beautifulsoup4>=4.9.3"
        ]
        
        # Optional packages that enhance functionality
        optional_packages = [
            "lxml>=4.6.3",  # Faster XML/HTML parsing
            "numpy",        # Numerical operations (helps with image processing)
            "urllib3",      # Better HTTP handling
            "certifi",      # SSL certificates
            "charset-normalizer",  # Character encoding detection
        ]
        
        # Install core packages
        for package in core_packages:
            self._install_package(package, required=True)
        
        # Install optional packages (don't fail if these don't work)
        for package in optional_packages:
            self._install_package(package, required=False)
    
    def _install_package(self, package, required=True):
        """Install a single Python package"""
        package_name = package.split(">=")[0].split("==")[0]
        print(f"Installing {package_name}...")
        
        try:
            subprocess.check_call([
                sys.executable, "-m", "pip", "install", "--upgrade", package
            ], stdout=subprocess.DEVNULL, stderr=subprocess.PIPE)
            print(f"✅ {package_name} installed successfully")
            self.installed_packages.append(package_name)
        except subprocess.CalledProcessError as e:
            if required:
                print(f"❌ Failed to install {package_name}: {e}")
                self.errors.append(f"Required package {package_name} failed to install")
            else:
                print(f"⚠️ Optional package {package_name} failed to install")
    
    def verify_installation(self):
        """Verify that all critical packages can be imported"""
        print("\nVerifying installation...")
        
        critical_imports = [
            ("tkinter", "GUI framework"),
            ("requests", "HTTP requests"),
            ("PIL", "Image processing"),
            ("bs4", "HTML parsing")
        ]
        
        for module, description in critical_imports:
            try:
                if module == "tkinter":
                    import tkinter
                    # Test basic tkinter functionality
                    root = tkinter.Tk()
                    root.withdraw()  # Hide the window
                    root.destroy()
                elif module == "PIL":
                    from PIL import Image, ImageTk
                elif module == "bs4":
                    from bs4 import BeautifulSoup
                else:
                    __import__(module)
                print(f"✅ {module} ({description}) working correctly")
            except ImportError as e:
                print(f"❌ {module} ({description}) failed to import: {e}")
                self.errors.append(f"Critical module {module} not working")
            except Exception as e:
                print(f"⚠️ {module} ({description}) imported but has issues: {e}")
    
    def create_test_script(self):
        """Create a test script to verify everything works"""
        test_script = '''#!/usr/bin/env python3
"""
eBay Tools Installation Test
Run this script to verify your installation is working correctly
"""

def test_imports():
    """Test all critical imports"""
    print("Testing critical imports...")
    
    try:
        import tkinter as tk
        print("✅ tkinter GUI framework")
    except ImportError as e:
        print(f"❌ tkinter: {e}")
        return False
        
    try:
        import requests
        print("✅ requests HTTP library")
    except ImportError as e:
        print(f"❌ requests: {e}")
        return False
        
    try:
        from PIL import Image, ImageTk
        print("✅ Pillow image processing")
    except ImportError as e:
        print(f"❌ Pillow: {e}")
        return False
        
    try:
        from bs4 import BeautifulSoup
        print("✅ BeautifulSoup HTML parsing")
    except ImportError as e:
        print(f"❌ BeautifulSoup: {e}")
        return False
    
    return True

def test_gui():
    """Test basic GUI functionality"""
    print("\\nTesting GUI functionality...")
    try:
        import tkinter as tk
        root = tk.Tk()
        root.title("eBay Tools Test")
        root.geometry("300x100")
        
        label = tk.Label(root, text="✅ GUI Test Successful!")
        label.pack(pady=20)
        
        button = tk.Button(root, text="Close", command=root.destroy)
        button.pack()
        
        print("✅ GUI window created successfully")
        print("A test window should appear - close it to continue")
        root.mainloop()
        return True
    except Exception as e:
        print(f"❌ GUI test failed: {e}")
        return False

def test_image_processing():
    """Test image processing capabilities"""
    print("\\nTesting image processing...")
    try:
        from PIL import Image
        # Create a test image
        img = Image.new('RGB', (100, 100), color='red')
        print("✅ Image creation successful")
        
        # Test image operations
        img_resized = img.resize((50, 50))
        print("✅ Image resizing successful")
        
        return True
    except Exception as e:
        print(f"❌ Image processing test failed: {e}")
        return False

def test_web_requests():
    """Test web request functionality"""
    print("\\nTesting web requests...")
    try:
        import requests
        response = requests.get("https://httpbin.org/get", timeout=10)
        if response.status_code == 200:
            print("✅ Web requests working")
            return True
        else:
            print(f"⚠️ Web request returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Web request test failed: {e}")
        return False

if __name__ == "__main__":
    print("=" * 50)
    print("  eBay Tools Installation Test")
    print("=" * 50)
    
    success = True
    
    success &= test_imports()
    success &= test_image_processing()
    success &= test_web_requests()
    success &= test_gui()
    
    print("\\n" + "=" * 50)
    if success:
        print("🎉 ALL TESTS PASSED!")
        print("Your eBay Tools installation is ready to use!")
    else:
        print("❌ Some tests failed.")
        print("Check the error messages above and try reinstalling dependencies.")
    print("=" * 50)
'''
        
        with open("/tmp/test_ebay_tools.py", "w") as f:
            f.write(test_script)
        
        # Make executable
        os.chmod("/tmp/test_ebay_tools.py", 0o755)
        print("✅ Test script created: /tmp/test_ebay_tools.py")
    
    def _command_exists(self, command):
        """Check if a command exists in the system"""
        try:
            subprocess.run([command, "--version"], 
                         stdout=subprocess.DEVNULL, 
                         stderr=subprocess.DEVNULL, 
                         check=True)
            return True
        except (subprocess.CalledProcessError, FileNotFoundError):
            return False
    
    def print_summary(self):
        """Print installation summary"""
        print("\n" + "=" * 60)
        print("    Installation Summary")
        print("=" * 60)
        
        print(f"✅ Packages installed: {len(self.installed_packages)}")
        for package in self.installed_packages:
            print(f"   - {package}")
        
        if self.errors:
            print(f"\n❌ Errors encountered: {len(self.errors)}")
            for error in self.errors:
                print(f"   - {error}")
            print("\nPlease address these errors before using eBay Tools.")
        else:
            print("\n🎉 Installation completed successfully!")
            print("\nNext steps:")
            print("1. Run: python /tmp/test_ebay_tools.py")
            print("2. If tests pass, you can use eBay Tools applications")
            print("3. Launch applications using the batch files or Python modules")
        
        print("=" * 60)
    
    def run(self):
        """Run the complete installation process"""
        self.print_header()
        
        if not self.check_python_version():
            return False
        
        if not self.check_pip():
            return False
        
        self.install_system_dependencies()
        self.install_python_packages()
        self.verify_installation()
        self.create_test_script()
        self.print_summary()
        
        return len(self.errors) == 0

def main():
    installer = DependencyInstaller()
    success = installer.run()
    
    if success:
        print("\n🚀 Ready to run eBay Tools!")
        return 0
    else:
        print("\n❌ Installation incomplete. Please fix errors and try again.")
        return 1

if __name__ == "__main__":
    sys.exit(main())