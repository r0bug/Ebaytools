# eBay Tools - Claude Code Memory

## Project Overview
This is an eBay listing management tool suite with photo processing, price analysis, and automated listing generation capabilities.

## SSH Configuration for GitHub
**IMPORTANT**: This repository uses a custom SSH key named `ebaytools`

### When SSH/Git Push Fails:
1. Run the setup script: `./setup_ssh.sh`
2. Or manually run:
   ```bash
   eval "$(ssh-agent -s)"
   ssh-add ~/.ssh/ebaytools
   ```

### SSH Key Details:
- Key file: `~/.ssh/ebaytools`
- Public key: `~/.ssh/ebaytools.pub`
- GitHub username: r0bug
- Repository: github.com:r0bug/Ebaytools.git

## Recent Major Changes
1. **Item Selection UI** - Added checkboxes for selecting items to process
2. **Auto Price All Feature** - Automated batch pricing using eBay sold listings
3. **Scrollable UI** - Fixed layout issues on high-resolution displays
4. **Windows Installer Fixes** - Fixed batch files to use correct module names

## Key Files
- Main processor: `ebay_tools/ebay_tools/apps/processor.py`
- Windows version: `windows_installer/ebay_tools/apps/processor.py`
- Windows batch: `windows_installer/ebay_processor.bat`

## Common Commands
- Test processor: `python -m ebay_tools.apps.processor`
- Run setup script: `./setup_ssh.sh`
- Push changes: `git add . && git commit -m "message" && git push`

## UI Layout Issues Resolution
The processor now has a scrollable main window to prevent buttons from going off-screen on high-resolution displays. All UI elements are contained within a scrollable canvas with mouse wheel support.

## Auto Pricing Feature
The "Auto Price All" button performs automated batch pricing of processed items using eBay sold listing data. It's prominently displayed in the progress frame with emoji styling for visibility.