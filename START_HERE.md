# 🚀 START HERE - ECU File Organizer

## What Is This?

**ECU File Organizer** automatically organizes your ECU `.bin` files from Autotuner into a structured folder system with minimal effort.

## Quick Start (3 Steps)

### 1️⃣ Install & Run (Pick One)

**EASIEST** - Double-click: `run_ecu_organizer.bat`
- Installs everything automatically
- Starts the app
- Done in 30 seconds!

**OR** - Build standalone EXE: `build_executable.bat`
- Creates `dist\ECU_Organizer.exe`
- No Python needed on other computers

### 2️⃣ Configure

When app opens:
- Set **Monitor Folder** (where Autotuner saves files)
- Set **Destination** (default: Desktop\ECU_files)
- Click **"Start Monitoring"**

### 3️⃣ Test It

**Double-click**: `create_test_files.bat`
- Creates test .bin file
- Pop-up appears automatically
- Fill in mileage → Save
- Check Desktop\ECU_files for organized file

---

## How It Works

```
1. You read ECU with Autotuner
   ↓
2. File saved to monitor folder
   ↓
3. Pop-up appears (auto-filled from filename)
   ↓
4. You add mileage → Press Enter
   ↓
5. File organized into:
   Desktop/ECU_files/Make/Make_Model_Date_ECU_Mileage/
```

---

## What's Included

### Core Files
- **ecu_file_organizer.py** - Main application
- **requirements.txt** - Python dependencies

### Helper Scripts
- **startup_config.py** - Add/remove from Windows startup
- **test_file_generator.py** - Create test files
- **build_exe.py** - Build standalone executable
- **enhanced_parser.py** - Advanced filename parsing

### Windows Quick Start (Batch Files)
- **run_ecu_organizer.bat** ⭐ EASIEST WAY TO START
- **build_executable.bat** - Create EXE
- **create_test_files.bat** - Generate test files

### Documentation
- **INSTALLATION.md** - Full installation guide
- **README.md** - Complete documentation
- **QUICK_START.md** - 5-minute guide

---

## Features

✅ **Auto-monitoring** - Watches folder for new files  
✅ **Smart parsing** - Extracts Make, Model, ECU from filename  
✅ **Pop-up form** - Pre-filled data, just add mileage & registration  
✅ **System tray** - Runs in background  
✅ **Windows startup** - Auto-start option  
✅ **Organized folders** - Structured by Make/Model/Date/ECU/Mileage/Registration  
✅ **Works with ANY tool** - Not just Autotuner! KESS, CMD, Alientech, etc.

**Note**: If filename is not Autotuner format, just fill fields manually - works perfectly!  

---

## Example

**Input**: `Volkswagen_Golf_2008__VI__1_6_TDI_CR_105_hp_Siemens_PCR2_1_OBD_NR.bin`

**Pop-up shows**:
- Make: Volkswagen ✅
- Model: Golf 2008 VI ✅
- Date: 20250123 ✅
- ECU: Siemens PCR2.1 ✅
- Mileage: ➡️ **YOU ADD: 45000**
- Registration: ➡️ **YOU ADD: AB12345**

**Result**:
```
Desktop/ECU_files/Volkswagen/Volkswagen_Golf_2008_VI_20250123_PCR2.1_45000km_AB12345/
└── Volkswagen_Golf_2008__VI__1_6_TDI_CR_105_hp_Siemens_PCR2_1_OBD_NR.bin
```

---

## Requirements

- Windows 10/11
- Python 3.8+ (installed automatically by run_ecu_organizer.bat)
- 50MB disk space

---

## Getting Help

1. **Quick Guide**: Read `QUICK_START.md` (5 min)
2. **Full Docs**: Read `README.md` (detailed)
3. **Installation Issues**: Read `INSTALLATION.md`
4. **Test First**: Use `create_test_files.bat` before real files

---

## Next Steps

1. ✅ **Run**: `run_ecu_organizer.bat` (or build EXE)
2. ✅ **Configure**: Set your Autotuner folder
3. ✅ **Test**: Use test file generator
4. ✅ **Use**: Read real ECU files from Autotuner
5. ✅ **Automate**: Add to Windows startup (optional)

---

**Ready to organize your ECU files automatically! 🚗💾**

**Questions?** Check README.md for comprehensive documentation.
