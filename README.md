# eBay Tools

A comprehensive automation suite for creating eBay listings using AI/LLM technology. This system provides an end-to-end workflow from photo organization to final listing generation with integrated pricing analysis.

## Features

- 🤖 **AI-Powered Description Generation** - Uses LLaVA, Claude, or GPT-4 Vision APIs
- 💰 **Automated Price Analysis** - Analyzes eBay sold listings for market pricing
- 📸 **Photo Processing** - Batch image processing with EXIF handling
- 📊 **CSV Export** - Generates eBay-compatible CSV files for bulk uploads
- 📋 **Queue Management** - Organize and process multiple items efficiently
- 🔄 **Complete Workflow** - From setup to final eBay listing
- 🌐 **HTML Gallery Creator** - Create classified ad-style galleries for local sales
- 📱 **Mobile Integration** - Android app for on-the-go photo collection

## Installation

### Windows
```bash
# Run the Windows installer
install_dependencies.bat

# Or use the Python installer
python install_dependencies.py
```

### macOS
```bash
# Quick install (if Python 3.8+ installed)
./quick_install_mac.sh

# Or full installation with all dependencies
./install_dependencies_mac.sh
```

### Linux
```bash
# Run the shell script installer
./install_dependencies.sh

# Or use the Python installer
python install_dependencies.py
```

## Quick Start

1. **Setup Tool** - Create item queues and add photos
   ```bash
   python -m ebay_tools.apps.setup
   ```

2. **Processor Tool** - AI analyzes photos and generates descriptions
   ```bash
   python -m ebay_tools.apps.processor
   ```

3. **Viewer Tool** - Review and edit generated descriptions
   ```bash
   python -m ebay_tools.apps.viewer
   ```

4. **Export** - Generate CSV for eBay bulk upload

## Applications

- **Setup Tool** (`setup.py`) - Create and manage work queues
- **Processor Tool** (`processor.py`) - AI-powered photo analysis
- **Viewer Tool** (`viewer.py`) - Review and export results
- **Price Analyzer** (`price_analyzer.py`) - Market price analysis
- **Gallery Creator** (`gallery_creator.py`) - Create HTML classified ad galleries
- **Mobile Import** (`mobile_import.py`) - Import data from mobile app
- **Direct Listing** (`direct_listing.py`) - Direct eBay API integration
- **CSV Export** (`csv_export.py`) - Export to eBay format

## Requirements

- Python 3.8 or higher
- 4 GB RAM minimum
- Internet connection for API calls
- API keys for LLM services (optional but recommended)

## Documentation

- [Full User Manual](eBay_Tools_User_Manual.md) - Comprehensive guide
- [Gallery Creator Guide](GALLERY_README.md) - HTML gallery documentation
- [Mobile Integration Guide](MOBILE_INTEGRATION.md) - Android app and import docs
- [macOS Installation](README_MAC.md) - macOS specific instructions
- [API Documentation](ebay_tools/README.md) - Technical details

## Project Structure

```
Ebaytools/
├── ebay_tools/              # Main package
│   ├── apps/                # GUI applications
│   ├── core/                # Core functionality
│   └── utils/               # Utility modules
├── windows_installer/       # Windows installer files
├── launchers/               # OS-specific launchers
│   └── mac/                 # macOS .command files
├── install_dependencies.py  # Cross-platform installer
├── install_dependencies_mac.sh  # macOS installer
└── README.md               # This file
```

## API Configuration

The tool supports multiple LLM providers:

- **LLaVA** - Free, good for basic analysis
- **Claude** - Excellent for detailed descriptions
- **GPT-4 Vision** - Premium quality, requires OpenAI API key

Configure your preferred API in Settings → API Configuration.

## Contributing

1. Fork the repository
2. Create your feature branch (`git checkout -b feature/amazing-feature`)
3. Commit your changes (`git commit -m 'Add amazing feature'`)
4. Push to the branch (`git push origin feature/amazing-feature`)
5. Open a Pull Request

## License

This project is licensed under the MIT License - see the LICENSE file for details.

## Support

- Report issues on [GitHub Issues](https://github.com/r0bug/Ebaytools/issues)
- Check the [User Manual](eBay_Tools_User_Manual.md) for detailed help
- See platform-specific guides for installation help

## Acknowledgments

- Built with Python and Tkinter
- Uses Pillow for image processing
- BeautifulSoup4 for web scraping
- Supports multiple LLM providers