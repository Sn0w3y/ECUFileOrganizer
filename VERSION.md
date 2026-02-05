# Version & Changelog

## Version 1.6 (January 27, 2026)

### Auto-Open Folder & Automatic Log.txt Creation

**New Features**
- ✅ **Open folder checkbox**: New checkbox in Settings section "Open folder when file is saved"
- ✅ **Automatic folder opening**: Opens Windows Explorer to destination folder after organizing file
- ✅ **Automatic Log.txt creation**: Creates Log.txt file in same folder as organized .bin file
- ✅ **Complete documentation**: Log.txt contains all vehicle and file information
- ✅ **Professional formatting**: Clean, organized log format
- ✅ **Persistent setting**: Open folder preference saved automatically

**How It Works**
1. Checkbox in Settings: "Open folder when file is saved" (default: checked)
2. User organizes a file → Clicks "Save & Organize"
3. File moves to destination folder
4. Log.txt automatically created with:
   - Organization timestamp
   - Vehicle information (Make, Model, Date, ECU, Read Method, Mileage, Registration)
   - File information (Filename, Size, Full path)
5. If checkbox enabled → Folder opens in Windows Explorer automatically
6. User sees both .bin file and Log.txt immediately

**Log.txt Content**
```
ECU File Organization Log
==================================================

Organized Date/Time: 2026-01-27 14:30:25

Vehicle Information:
--------------------
Make:           Volkswagen
Model:          Golf 2008 VI
Date:           20260127
ECU Type:       PCR2.1
Read Method:    Normal Read-OBD
Mileage:        45000 km
Registration:   AB12345

File Information:
-----------------
Filename:       Golf_20260127_123456.bin
File Size:      2.45 MB (2,564,321 bytes)
Folder:         Volkswagen_Golf_2008_VI_...
Full Path:      C:\Desktop\ECU_files\...

Organized by ECU File Organizer v1.6
https://buymeacoffee.com/autobyte
```

**Use Cases**
- Quick verification after organizing
- Professional customer documentation
- Service history tracking
- Warranty claim records
- Fast workflow (immediate folder access)

**Technical Details**
- `toggle_open_folder()`: Handles checkbox state, saves to settings
- `create_log_file()`: Generates formatted Log.txt with UTF-8 encoding
- `os.startfile(dest_folder)`: Opens folder in Windows Explorer (Windows native)
- Setting key: `open_folder_on_save` (default: True)
- Error handling: Non-critical operations, fails silently
- Non-blocking: Doesn't interrupt workflow

**UI Changes**
- New checkbox added below "Run on Windows startup"
- Checkbox state persists across sessions
- About dialog updated to show v1.6 features

**Benefits**
- ✅ Faster workflow (immediate folder access)
- ✅ Better documentation (automatic log creation)
- ✅ Professional records (complete information)
- ✅ Time savings (no manual notes needed)
- ✅ Easy verification (see files immediately)
- ✅ Customer-ready documentation

---

## Version 1.5 (January 27, 2026)

### Edit History - Fix Mistakes After Organizing

**Major New Feature**
- ✅ **History button**: Blue "📜 History" button in main window (name changed from "Edit History" per user feedback)
- ✅ **Folder list dialog**: Shows up to 50 most recent organized folders sorted by modification date
- ✅ **Smart folder parsing**: Automatically extracts Make, Model, Date, ECU, Read Method, Mileage, Registration from folder names
- ✅ **Edit dialog with live preview**: Edit any field and see new folder name update in real-time
- ✅ **Safe folder renaming**: Confirmation dialog before renaming, duplicate detection, validation
- ✅ **Automatic make folder handling**: Moves folder to new make folder if make changed, cleans up empty old folders
- ✅ **Help menu integration**: Also accessible from Help → History menu

**Bug Fixes in v1.5**
- ✅ **Fixed History button crash**: App was crashing when clicking History button
  - **Cause**: Wrong variable name (`self.destination_base` vs `self.settings['destination_base']`)
  - **Fix**: Updated all references to use correct settings dictionary
  - **Functions Fixed**: `show_edit_history()`, `get_organized_folders()`, `save_folder_edit()`
- ✅ **Fixed window title duplication**: Title was showing "ECU File Organizer v1.5 - ECU File Organizer"
  - **Cause**: Qt combining window title + application name
  - **Fix**: Set application name to include version, set window title to empty string
  - **Result**: Clean title showing "ECU File Organizer v1.5" (once)
  - **Lines Changed**: 609, 1478, 1480, 1485, 1487

**Error Handling & Debugging**
- ✅ Comprehensive try-catch blocks in all History functions
- ✅ Graceful error messages instead of crashes
- ✅ User-friendly error dialogs
- ✅ Console debug output for troubleshooting
- ✅ Checks if destination folder is set before accessing History
- ✅ Validates folder existence before editing

**How It Works**
1. Click "📝 Edit History" button in main window
2. Select folder from list (sorted by modification date, newest first)
3. Edit dialog opens with all fields pre-filled from folder name
4. Edit any fields (Make, Model, Date, ECU, Read Method, Mileage, Registration)
5. Live preview shows new folder name as you type
6. Click "Save Changes" → Confirmation dialog
7. Folder renamed with new information

**Folder Parsing Logic**
- Extracts components from folder name: Make_Model_Date_ECU_ReadMethod_Mileage_Registration
- Make: First component
- Model: Between make and date
- Date: 8-digit number (YYYYMMDD)
- ECU: Between date and read method
- Read Method: OBD, Bench, Boot, or Virtual
- Mileage: Component ending with "km"
- Registration: Last component (if doesn't end with "km")

**Use Cases**
- Fix typos in mileage (e.g., 4500 → 45000)
- Add missing registration number
- Correct read method selection
- Fix date errors
- Update any field after organizing
- Correct make spelling (folder moves to correct make folder)

**Safety Features**
- Duplicate detection: Won't rename if new name already exists
- Validation: Requires make and model at minimum
- Confirmation: Shows before/after comparison, requires user confirmation
- Old folder cleanup: Removes empty make folders automatically
- Error handling: Clear error messages for all failure cases

**Technical Details**
- get_organized_folders(): Scans all make folders, returns list with path/name/make/modified time
- parse_folder_name(): Intelligent parsing of folder name components
- show_edit_history(): Main dialog with QListWidget showing folders
- edit_selected_folder(): Edit dialog with QFormLayout and live preview
- save_folder_edit(): Validates, confirms, and renames folder using shutil.move()
- List limit: Shows 50 most recent folders (performance optimization)
- Sorting: By modification time, newest first

**UI Integration**
- Button location: Main window, between "Minimize to Tray" and "Exit"
- Button color: Blue (#2196F3) to distinguish from other buttons
- Button icon: 📝 emoji
- Dialog size: Edit History: 800x600px, Edit Dialog: 600px min width
- List widget: Single selection, current row selected by default
- Preview: Gray background, updates on any field change

**Benefits**
- No need for manual folder renaming in Windows Explorer
- Fix mistakes immediately or later
- All file organization information editable
- Safe with confirmation and validation
- Professional workflow support
- Time-saving for bulk corrections

---

## Version 1.4 (January 24, 2026)

### Duplicate Detection - Intelligent Handling by Registration Number

**Major New Feature**
- ✅ **Registration-based duplicate detection**: Automatically checks if folders already exist for the same registration number
- ✅ **Smart duplicate dialog**: Shows list of existing folders with option to add to existing or create new
- ✅ **Multiple folder selection**: If multiple existing folders, choose which one to use
- ✅ **File overwrite protection**: Automatically adds timestamp if file with same name exists in destination folder
- ✅ **Flexible organization**: Your choice - keep all reads together or separate by date/service

**How It Works**
1. User fills in registration number in pop-up form
2. User clicks "Save & Organize"
3. App searches ALL folders for this registration number
4. If found → Shows duplicate dialog with options:
   - "📁 Add to Existing Folder" - Add file to existing folder (keeps related files together)
   - "✨ Create New Folder" - Proceed with creating new folder (normal flow)
   - "❌ Cancel" - Cancel operation
5. If adding to existing and multiple folders found → User selects which folder
6. If file name exists in destination → Timestamp added (e.g., file_143052.bin)

**Matching Logic**
- **Duplicate detected**: Same registration number (e.g., "AB12345")
- **Searches**: All make folders, all subfolders
- **Matches**: Folders ending with _AB12345
- **Works even if**: Different date, mileage, ECU, or make/model
- **If no registration provided**: No duplicate check (creates new folder)

**Use Cases**
- **Same car, multiple dates**: Same registration read on different dates - choose to group or separate
- **Tuning progression**: Stock → Stage 1 → Stage 2 (same registration, different folders with dates)
- **Before/after comparison**: Keep both reads in same folder for easy comparison  
- **Multiple service visits**: Organize by date or keep all service history together
- **Same day reads**: Multiple reads of same car - your choice how to organize

**Technical Details**
- Matching criteria: Registration number only (unique vehicle identifier)
- Searches across all make folders (not limited to current make)
- Shows up to 5 existing folders in dialog (with "... and N more" for many)
- Folder list sorted by name (reverse, newest first typically)
- Custom QMessageBox with action buttons
- QDialog for folder selection if multiple matches
- Timestamp format: HHMMSS (e.g., 143052 for 14:30:52)

**Benefits**
- More accurate duplicate detection (registration = specific vehicle)
- Prevents accidental duplicate folders for same vehicle
- Flexible: You decide whether to group or separate
- Professional: Tracks tuning stages, service history, or comparisons
- Safe: No file overwrites (timestamp protection)
- Works across makes: Same registration even if make/model changes (rare but possible)

---

## Version 1.3.2 (January 24, 2026)

### Start Minimized to Tray

**New Feature**
- ✅ **Starts minimized to tray on Windows startup**: When app auto-starts with Windows, it now goes straight to system tray instead of opening the window
- ✅ **Command-line argument support**: `--minimized` or `--tray` argument to start minimized
- ✅ **Startup notification**: Small notification appears when starting minimized (2 seconds)
- ✅ **Updated startup message**: Checkbox notification now mentions "minimized to tray"

**Behavior Changes**
- **Windows startup**: App starts silently in tray (no window pop-up)
- **Manual start**: Window opens normally (unchanged)
- **Pop-ups**: Still appear automatically even when window is hidden
- **Tray icon**: Double-click to show window anytime

**Technical**
- Registry entry now includes `--minimized` argument: `"path\to\ECU_Organizer.exe" --minimized`
- main() checks for `--minimized` or `--tray` in sys.argv
- If argument present: window.hide() + notification
- If argument absent: window.show() (normal behavior)

**Why This Matters**
- Professional: App doesn't pop up window on every Windows boot
- Convenient: Starts silently, ready to work in background
- User-friendly: Double-click tray icon when you need the window
- Clean: No more manually minimizing after Windows starts

---

## Version 1.3.1 (January 23, 2025)

### Support Link in Main Window

**New Features**
- ✅ **Buy Me a Coffee link in main window**: Clickable link added below buttons
- ✅ **Your actual link updated**: https://buymeacoffee.com/autobyte
- ✅ **Yellow styling**: Matches Buy Me a Coffee branding
- ✅ **Always visible**: Non-intrusive but accessible

**Link Details**
- Location: Bottom of main window, centered
- Text: "If you like this app, you can support me on: ☕ Buy Me a Coffee"
- Color: Yellow (#FFDD00) for the link
- Behavior: Opens browser to your Buy Me a Coffee page
- Style: Professional, clean, non-intrusive

**Tray Icon Improvements**
- Application name set even earlier (before QApplication creation)
- Redundant setting after QApplication creation
- Best possible configuration for Python script
- Note: Complete fix requires building as EXE (see TRAY_ICON_FINAL_SOLUTION.md)

**UI Changes**
- Window height increased to 580px (from 550px) to accommodate support link
- Support link positioned below buttons with proper spacing
- Consistent styling across app

---

## Version 1.3 (January 23, 2025)

### Support & Build Improvements

**New Features**
- ✅ **Help Menu**: Added menu bar with Help menu
- ✅ **About Dialog**: Information about the application
- ✅ **Support Link**: "☕ Support the Developer" with Buy Me a Coffee integration
- ✅ **Interactive Build Script**: `build_interactive.py` for PyCharm users

**Support Features**
- Help → About: Application information and credits
- Help → Support the Developer: Buy Me a Coffee link with motivational message
- Customizable support link (update in code)
- Professional dialog with clickable link

**Build Script Features** (`build_interactive.py`)
- Interactive configuration prompts
- Auto-install PyInstaller if missing
- Clean build option
- One-file or one-folder build
- Console or windowed mode
- Custom icon detection
- Colored terminal output
- Auto-open dist folder
- Cross-platform support
- Perfect for PyCharm users

**UI Changes**
- Window height increased: 550px (to accommodate menu bar)
- Menu bar with Help menu at top of window
- Professional About and Support dialogs

---

## Version 1.2.1 (January 23, 2025)

### Tray Icon Tooltip Fix

**Fixed**
- ✅ **Tray Icon Tooltip**: Now explicitly shows "ECU File Organizer" when hovering over tray icon
- ✅ **Dynamic Tooltip**: Updates to show monitoring status ("Monitoring Active" / "Monitoring Stopped")

**Note**: When running as Python script, the process name in tray may still show "python" due to Windows using the Python interpreter. Build as EXE for complete professional appearance (see TRAY_ICON_INFO.md).

**Tooltip Behavior**:
- Monitoring Active: "ECU File Organizer - Monitoring Active"
- Monitoring Stopped: "ECU File Organizer - Monitoring Stopped"
- Initial: "ECU File Organizer"

---

## Version 1.2 (January 23, 2025)

### Critical Updates Based on User Feedback

**Major Changes**
- ✅ **File is MOVED instead of COPIED**: Original file is moved from source folder to organized location (no duplicates!)
- ✅ **Read Method Dropdown**: Added dropdown in pop-up form with options:
  - Normal Read-OBD
  - Virtual Read-OBD
  - Bench
  - Boot

**Folder Structure Updated**
- Now includes read method: `Make_Model_Date_ECU_ReadMethod_Mileage_Registration`
- Example: `Volkswagen_Golf_2008_VI_20250123_PCR2.1_OBD_45000km_AB12345`

**Parser Improvements**
- Automatically detects read method from filename (OBD, Bench, Boot)
- Distinguishes between Normal Read-OBD and Virtual Read-OBD
- Dropdown pre-selected based on detected method

**Why These Changes Matter**
- **Move vs Copy**: No duplicate files cluttering your source folder
- **Read Method**: Essential for tracking how ECU was accessed (important for documentation and troubleshooting)
- **Auto-detection**: Saves time by pre-selecting read method from filename

---

## Version 1.1 (January 23, 2025)

### Updates Based on User Feedback

**New Features**
- ✅ **Windows Startup Checkbox**: Enable/disable auto-start from main window
- ✅ **Exit Button**: Red exit button in main window to fully quit the app
- ✅ **Proper Application Name**: Fixed "python" showing in taskbar - now shows "ECU File Organizer"
- ✅ **Registration Number Field**: Added to pop-up form for vehicle registration

**UI Improvements**
- Startup checkbox in settings section (☑ Run on Windows startup)
- Exit button with clear red styling for easy identification
- Application name properly set in taskbar, tray, and notifications
- Window size increased to accommodate new controls (600x500)

**Technical**
- Added winreg import for Windows Registry operations
- Startup management methods integrated into main class
- Checkbox state syncs with actual Windows startup status
- Exit button properly stops monitoring and closes tray icon

---

## Version 1.0 (January 23, 2025)

### Initial Release

**Core Features**
- ✅ Automatic folder monitoring for .bin files
- ✅ Smart Autotuner filename parsing
- ✅ Pop-up form with pre-filled data (Make, Model, Date, ECU, Mileage, Registration)
- ✅ Organized folder structure by Make/Model/Date/ECU/Mileage/Registration
- ✅ System tray integration
- ✅ Windows startup support
- ✅ Real-time file detection
- ✅ Works with files from ANY tool (not just Autotuner)

**Parsing Support**
- Volkswagen, Opel, Peugeot, Citroen, DS formats
- Ford, Mercedes, BMW, Audi formats
- Bosch, Siemens, Delphi, Continental ECUs
- PCR2.1, EDC17, MED17, and other ECU types
- OBD, BENCH, BOOT read methods

**User Interface**
- Main settings window
- Pop-up form (always on top)
- System tray menu
- Keyboard shortcuts (Tab, Enter, Esc)
- Real-time destination preview

**Tools Included**
- Test file generator
- Windows startup configurator
- Executable builder
- Enhanced parser module

**Documentation**
- Complete README
- Quick start guide
- Installation guide
- Troubleshooting tips

---

## Tested Formats

### Autotuner Naming Conventions
```
Make_Model_Year__Generation__Engine_Power_ECU_Type_Method_Status.bin
```

**Examples**:
- Volkswagen_Golf_2008__VI__1_6_TDI_CR_105_hp_Siemens_PCR2_1_OBD_NR.bin
- Opel_Astra_2019__K__1_5_CDTI_122_hp_Bosch_EDC17_OBD_NR.bin
- Peugeot_308_2020__T9__1_5_BlueHDI_130_hp_Bosch_MED17_OBD_NR.bin

### Recognized ECU Brands
- Bosch (EDC17, MED17, MD1, etc.)
- Siemens (PCR2.1, etc.)
- Delphi (DCM series)
- Continental (SID, EMS series)
- Marelli, Valeo, Denso

---

## Known Limitations

1. **Filename Format**: Best with Autotuner standard naming
   - Workaround: Manual editing in pop-up form

2. **File Size**: No file size validation
   - Application trusts all .bin files

3. **Duplicate Detection**: Basic check only
   - Warns if similar folder exists

4. **Language**: Interface in English only
   - All documentation in English

---

## Planned Features (Future Versions)

### Version 1.1 (Planned)
- [ ] Customer name field
- [ ] VIN number support
- [ ] Multiple destination folders
- [ ] File history database
- [ ] Search organized files

### Version 1.2 (Planned)
- [ ] Integration with ULP Manager
- [ ] Custom folder structure templates
- [ ] Batch organization mode
- [ ] Export reports (CSV/Excel)

### Version 2.0 (Future)
- [ ] Multi-language support (Serbian, Norwegian)
- [ ] Cloud backup integration
- [ ] Mobile companion app
- [ ] Advanced file comparison

---

## Technical Specifications

**Framework**: PyQt6 6.7.0  
**Python**: 3.8+  
**Threading**: QThread for background monitoring (no external dependencies)  
**File Detection**: 2-second polling with size stability check (built-in, no watchdog library)  
**Settings Storage**: JSON file in user home directory  

**File Organization Logic**:
```
Base/
└── Make/
    └── Make_Model_Date_ECU_Mileage_Registration/
        └── original_file.bin
```

**Startup Integration**: Windows Registry (HKEY_CURRENT_USER\Software\Microsoft\Windows\CurrentVersion\Run)

---

## Development Notes

**Built for**: Uros @ Stellantis Norway  
**Use Case**: Automotive diagnostic specialist  
**Vehicles**: Stellantis brands (Opel, Peugeot, Citroen, DS)  
**Tools**: Autotuner ECU reading equipment  
**Workflow**: Read ECU → Auto-organize → Quick access  

**Design Philosophy**:
- Minimal user interaction
- Maximum automation
- Professional organization
- Background operation
- No disruption to diagnostic work

---

## Support & Feedback

**For Issues**:
1. Check documentation (README.md, INSTALLATION.md)
2. Test with test file generator
3. Verify folder paths and permissions
4. Check Windows Event Viewer

**For Feature Requests**:
- Consider integration with existing workflow
- Maintain simplicity and speed
- Preserve backward compatibility

---

## License

**Personal Use**: Free for Uros and Stellantis Norway  
**Distribution**: Contact developer  
**Modifications**: Allowed for personal use  
**Commercial**: Contact for licensing  

---

## Credits

**Developer**: Claude (Anthropic AI)  
**Requested by**: Uros (Autobyte Diagnostics) 
**Inspired by**: Real workflow needs in automotive diagnostics  
**Date**: January 23, 2025  

---

## Changelog

### v1.0 (January 23, 2025)
- Initial release
- All core features implemented
- Documentation complete
- Ready for production use

---

**Current Version: 1.0**  
**Status**: ✅ Production Ready  
**Last Updated**: January 23, 2025
