# ❓ Frequently Asked Questions (FAQ)

## General Questions

### Q: What is ECU File Organizer?
**A:** An automatic tool that watches a folder for new ECU `.bin` files, shows a pop-up form with pre-filled information, and organizes files into structured folders based on vehicle details.

### Q: Do I need to know programming to use it?
**A:** No! Just double-click `run_ecu_organizer.bat` and it works. No programming knowledge needed.

### Q: Does it work on Mac or Linux?
**A:** The Python script works on all platforms, but the batch files are Windows-only. On Mac/Linux, run: `python3 ecu_file_organizer.py`

---

## Installation & Setup

### Q: What do I need to install?
**A:** Just Python 3.8+ and PyQt6. The `run_ecu_organizer.bat` file installs everything automatically.

### Q: Do I need the watchdog library?
**A:** **No!** The application uses built-in file monitoring with PyQt6's QThread. No external file watching libraries are needed. Only PyQt6 is required.

### Q: How do I know what's installed?
**A:** Check `requirements.txt`:
```
PyQt6==6.7.0
PyQt6-Qt6==6.7.0
PyQt6-sip==13.8.0
```
That's it! Just PyQt6.

### Q: Can I create a standalone EXE?
**A:** Yes! Run `build_executable.bat`. This creates `dist\ECU_Organizer.exe` that works without Python installed.

### Q: How do I add it to Windows startup?
**A:** Run `python startup_config.py` and choose option 1, or manually add a shortcut to `shell:startup` folder.

---

## File Compatibility

### Q: Does it only work with Autotuner files?
**A:** **No!** It works with **ANY .bin file** from any tool:
- Autotuner ✅
- KESS ✅
- CMD ✅
- Alientech ✅
- K-TAG ✅
- FGTech ✅
- Or any other ECU tool ✅

### Q: What if my file isn't named in Autotuner format?
**A:** The pop-up will still appear, but fields might be empty. Just fill them in manually - works perfectly! The parsing is just a convenience feature.

**Examples**:
- `my_ecu_file.bin` → All fields empty, you fill manually
- `Golf_2020_ECU.bin` → Some fields detected, complete the rest
- `123456789.bin` → Fill everything manually

### Q: What filename formats are recognized?
**A:** The parser recognizes:
- **Autotuner format**: `Make_Model_Year__Generation__Engine_Power_ECU_Method_Status.bin`
- **Partial formats**: Anything with make/model/ECU keywords
- **Any format**: Manual entry always works!

### Q: Can I organize old files?
**A:** Yes! Just copy old .bin files to your monitored folder and they'll be detected.

---

## Pop-up Form

### Q: What fields are in the pop-up form?
**A:** 
1. **Make** (e.g., Volkswagen)
2. **Model** (e.g., Golf 2008 VI)
3. **Date** (YYYYMMDD format, default: today)
4. **ECU Type** (e.g., Siemens PCR2.1)
5. **Mileage** (in km, e.g., 45000)
6. **Registration No** (e.g., AB12345)

### Q: Do I have to fill all fields?
**A:** Only **Make** and **Model** are required. Everything else is optional (but recommended for better organization).

### Q: Can I edit pre-filled information?
**A:** Yes! All fields are editable. The parsing is just to save you time.

### Q: What if I don't know the mileage?
**A:** Leave it empty. The folder will be created without mileage in the name.

### Q: What format should the date be?
**A:** YYYYMMDD (e.g., 20250123 for January 23, 2025). Default is today's date.

### Q: Can I cancel without saving?
**A:** Yes! Click "Cancel" or press `Esc` and the file won't be organized.

---

## File Organization

### Q: Where are files organized?
**A:** Default location: `Desktop\ECU_files\` with structure:
```
ECU_files/
└── Make/
    └── Make_Model_Date_ECU_Mileage_Registration/
        └── original_file.bin
```

### Q: Can I change the destination folder?
**A:** Yes! In the main window, browse to select a different destination folder.

### Q: Are original files moved or copied?
**A:** **Copied!** Original files remain in the monitored folder. You can safely delete them after.

### Q: What if a folder already exists?
**A:** The file is copied to the existing folder. No duplicates or overwrites.

### Q: Can I organize files to different locations based on customer?
**A:** Currently no, but you can add customer name to the registration field or model field as a workaround.

### Q: Can I use a network drive?
**A:** Yes! Both monitor and destination folders can be on network drives (as long as they're mapped).

---

## Monitoring

### Q: How does the monitoring work?
**A:** The app uses **built-in PyQt6 QThread** to check the folder every 2 seconds for new .bin files. No external libraries needed!

### Q: Does it slow down my computer?
**A:** No! Very lightweight - uses ~50MB RAM and minimal CPU.

### Q: Can I monitor multiple folders?
**A:** Currently only one folder at a time. Run multiple instances to monitor multiple folders.

### Q: What if I add a file while the app is not running?
**A:** The file won't be detected. The app only detects files added while monitoring is active.

### Q: How do I know if monitoring is active?
**A:** Green status in the main window: "✅ Monitoring: [folder path]"

### Q: Can I pause monitoring?
**A:** Yes! Click "⏸️ Stop Monitoring" button in the main window.

---

## System Tray

### Q: Where does the app run after minimizing?
**A:** In the Windows system tray (bottom-right corner, near the clock).

### Q: How do I bring it back?
**A:** Double-click the tray icon or right-click and select "Show Window".

### Q: Can I close the app from the tray?
**A:** Yes! Right-click the tray icon and select "Quit".

### Q: Does closing the main window quit the app?
**A:** No! It minimizes to tray. Use "Quit" from the tray menu to fully exit.

---

## Troubleshooting

### Q: Pop-up doesn't appear when I add a file
**A:** Check:
- ✅ Monitoring is active (green status)
- ✅ Monitor folder path is correct
- ✅ File is .bin extension
- ✅ Wait 2-3 seconds after copying file
- ✅ File write is complete

### Q: Fields are empty in the pop-up
**A:** The filename wasn't in recognized format. Just fill fields manually - works fine!

### Q: "Python not found" error
**A:** 
1. Install Python 3.8+ from python.org
2. Make sure "Add Python to PATH" was checked during installation
3. Restart Command Prompt

### Q: "No module named PyQt6" error
**A:** Run: `pip install -r requirements.txt`

### Q: Application closes immediately
**A:** Run with console to see errors: `python ecu_file_organizer.py`

### Q: Files not organizing
**A:** Check:
- ✅ Destination folder has write permissions
- ✅ Enough disk space
- ✅ Make and Model fields are filled

### Q: Build executable fails
**A:**
1. Install PyInstaller: `pip install pyinstaller`
2. Delete `build` and `dist` folders
3. Run `build_executable.bat` again

---

## Advanced Usage

### Q: Can I change the folder naming structure?
**A:** Yes! Edit the `save_file()` function in `ecu_file_organizer.py` to customize folder naming.

### Q: Can I integrate with my existing database?
**A:** The code is open - you can add SQLite database logging in the `on_file_saved()` function.

### Q: Can I add more fields?
**A:** Yes! Edit the `ECUFormDialog` class to add more input fields (customer name, VIN, etc.).

### Q: Can I export a list of organized files?
**A:** Not built-in, but you could add this feature by modifying the code.

### Q: Does it work with other file extensions?
**A:** Currently only `.bin` and `.BIN`. You can modify the file extension check in `FileMonitor` class.

---

## Best Practices

### Q: Should I delete files from the monitored folder?
**A:** Yes! After organization, you can safely delete original files (they're copied, not moved).

### Q: What's the best workflow?
**A:**
```
1. Configure folders once
2. Start monitoring
3. Minimize to tray
4. Read ECU with your tool
5. Pop-up appears automatically
6. Fill mileage & registration
7. Press Enter
8. Continue working!
```

### Q: Should I always fill registration number?
**A:** Recommended! It helps identify specific vehicles, especially for fleet work.

### Q: How should I format registration numbers?
**A:** Any format works, but avoid spaces (use dashes or underscores):
- ✅ `AB12345`
- ✅ `AB-12345`
- ✅ `AB_12345`
- ❌ `AB 12345` (spaces become underscores in folder name)

---

## Compatibility

### Q: What Windows versions are supported?
**A:** Windows 10 and Windows 11 (tested). Should work on Windows 7/8 with Python 3.8+.

### Q: Does it work with Python 3.12?
**A:** Yes! Tested with Python 3.8 through 3.12.

### Q: Can I use it on a virtual machine?
**A:** Yes! Works perfectly in VMs.

### Q: Does it work with cloud storage (Dropbox, OneDrive)?
**A:** Yes! You can monitor and save to cloud-synced folders.

---

## Support

### Q: Where can I get help?
**A:** 
1. Read the documentation (README.md, INSTALLATION.md)
2. Check this FAQ
3. Test with `create_test_files.bat` first
4. Check Windows Event Viewer for Python errors

### Q: Can I request features?
**A:** The code is yours to modify! Add features as needed.

### Q: Is this free?
**A:** Yes, created specifically for Uros at Stellantis Norway.

---

## Quick Answers

**Q: Does it need watchdog library?**  
**A: No! Built-in monitoring only.**

**Q: Works with non-Autotuner files?**  
**A: Yes! Any .bin file works.**

**Q: Registration field added?**  
**A: Yes! New field for registration number.**

**Q: Difficult to install?**  
**A: No! Just double-click run_ecu_organizer.bat**

**Q: Can I use it daily?**  
**A: Yes! Built for daily professional use.**

---

**Still have questions? Check the full README.md for comprehensive documentation!**
