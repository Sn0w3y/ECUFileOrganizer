"""
ECU File Organizer
Monitors folder for new ECU files, parses filename, and organizes with pop-up form
"""

import sys
import os
import re
import shutil
from datetime import datetime
from pathlib import Path
from PyQt6.QtWidgets import (QApplication, QMainWindow, QWidget, QVBoxLayout, 
                              QHBoxLayout, QLabel, QLineEdit, QPushButton, 
                              QSystemTrayIcon, QMenu, QMessageBox, QFileDialog,
                              QGroupBox, QFormLayout, QCheckBox, QComboBox, QMenuBar,
                              QDialog, QListWidget, QListWidgetItem, QDialogButtonBox)
from PyQt6.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt6.QtGui import QIcon, QFont, QAction
import json
import winreg


class FileMonitor(QThread):
    """Background thread for monitoring folder"""
    file_detected = pyqtSignal(str)
    
    def __init__(self, monitor_folder):
        super().__init__()
        self.monitor_folder = monitor_folder
        self.running = True
        self.processed_files = set()
        
    def run(self):
        """Monitor folder for new .bin files"""
        while self.running:
            if os.path.exists(self.monitor_folder):
                try:
                    files = [f for f in os.listdir(self.monitor_folder) 
                            if f.lower().endswith('.bin')]
                    
                    for file in files:
                        file_path = os.path.join(self.monitor_folder, file)
                        if file_path not in self.processed_files:
                            # Check if file is fully written (size stable)
                            try:
                                size1 = os.path.getsize(file_path)
                                self.msleep(500)
                                size2 = os.path.getsize(file_path)
                                
                                if size1 == size2:
                                    self.processed_files.add(file_path)
                                    self.file_detected.emit(file_path)
                            except:
                                pass
                except:
                    pass
            
            self.msleep(2000)  # Check every 2 seconds
    
    def stop(self):
        self.running = False


class FileParser:
    """Parse Autotuner filename format"""
    
    @staticmethod
    def parse_filename(filename):
        """
        Parse filename like: Volkswagen_Golf_2008__VI__1_6_TDI_CR_105_hp_Siemens_PCR2_1_OBD_NR.bin
        Returns dict with parsed fields
        """
        # Remove .bin extension
        name = filename.replace('.bin', '').replace('.BIN', '')
        
        # Split by underscores
        parts = name.split('_')
        
        parsed = {
            'make': '',
            'model': '',
            'engine': '',
            'ecu': '',
            'date': datetime.now().strftime('%Y%m%d'),
            'mileage': '',
            'registration': '',
            'read_method': ''
        }
        
        # Try to extract make (usually first part)
        if len(parts) > 0:
            parsed['make'] = parts[0]
        
        # Try to extract model (parts after make until double underscore or numbers)
        model_parts = []
        ecu_parts = []
        found_ecu = False
        
        for i, part in enumerate(parts[1:], 1):
            # Skip empty parts
            if not part:
                continue
                
            # Look for ECU indicators (Bosch, Siemens, Delphi, Continental, etc.)
            if any(ecu_brand in part for ecu_brand in ['Bosch', 'Siemens', 'Delphi', 
                   'Continental', 'Marelli', 'Valeo', 'Denso', 'PCR', 'EDC', 'MED']):
                found_ecu = True
                ecu_parts.append(part)
            elif found_ecu:
                ecu_parts.append(part)
            elif not any(x in part for x in ['OBD', 'BENCH', 'BOOT', 'NR', 'OR', 'hp', 'ps', 'kW']):
                model_parts.append(part)
        
        parsed['model'] = ' '.join(model_parts) if model_parts else ''
        parsed['ecu'] = ' '.join(ecu_parts) if ecu_parts else ''
        
        # Detect read method from filename
        name_upper = name.upper()
        if 'BENCH' in name_upper:
            parsed['read_method'] = 'Bench'
        elif 'BOOT' in name_upper:
            parsed['read_method'] = 'Boot'
        elif 'OBD' in name_upper:
            # Check if it might be virtual read
            if 'VIRTUAL' in name_upper or 'VR' in name_upper:
                parsed['read_method'] = 'Virtual Read-OBD'
            else:
                parsed['read_method'] = 'Normal Read-OBD'
        
        # Clean up ECU name
        parsed['ecu'] = parsed['ecu'].replace('  ', ' ').strip()
        
        return parsed


class ECUFormDialog(QWidget):
    """Pop-up form for ECU file information"""
    file_saved = pyqtSignal(str)
    
    def __init__(self, file_path, parsed_data, destination_base, parent_window=None):
        super().__init__()
        self.file_path = file_path
        self.destination_base = destination_base
        self.parent_window = parent_window
        self.init_ui(parsed_data)
        
    def init_ui(self, parsed_data):
        """Initialize the form UI"""
        self.setWindowTitle("New ECU File Detected")
        self.setWindowFlags(Qt.WindowType.WindowStaysOnTopHint | Qt.WindowType.Dialog)
        self.setMinimumWidth(500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("📁 New ECU File Detected")
        title_font = QFont()
        title_font.setPointSize(12)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # File info
        file_label = QLabel(f"File: {os.path.basename(self.file_path)}")
        file_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(file_label)
        
        # Form group
        form_group = QGroupBox("ECU Information")
        form_layout = QFormLayout()
        
        # Make
        self.make_input = QLineEdit()
        self.make_input.setText(parsed_data['make'])
        self.make_input.textChanged.connect(self.update_preview)
        form_layout.addRow("Make:", self.make_input)
        
        # Model
        self.model_input = QLineEdit()
        self.model_input.setText(parsed_data['model'])
        self.model_input.textChanged.connect(self.update_preview)
        form_layout.addRow("Model:", self.model_input)
        
        # Date
        self.date_input = QLineEdit()
        self.date_input.setText(parsed_data['date'])
        self.date_input.setPlaceholderText("YYYYMMDD")
        self.date_input.textChanged.connect(self.update_preview)
        form_layout.addRow("Date:", self.date_input)
        
        # ECU
        self.ecu_input = QLineEdit()
        self.ecu_input.setText(parsed_data['ecu'])
        self.ecu_input.textChanged.connect(self.update_preview)
        form_layout.addRow("ECU Type:", self.ecu_input)
        
        # Read Method dropdown
        self.read_method_combo = QComboBox()
        self.read_method_combo.addItems([
            "Normal Read-OBD",
            "Virtual Read-OBD",
            "Bench",
            "Boot"
        ])
        # Set from parsed data if available
        if parsed_data['read_method']:
            index = self.read_method_combo.findText(parsed_data['read_method'])
            if index >= 0:
                self.read_method_combo.setCurrentIndex(index)
        self.read_method_combo.currentTextChanged.connect(self.update_preview)
        form_layout.addRow("Read Method:", self.read_method_combo)
        
        # Mileage
        self.mileage_input = QLineEdit()
        self.mileage_input.setText(parsed_data['mileage'])
        self.mileage_input.setPlaceholderText("e.g., 45000")
        self.mileage_input.textChanged.connect(self.update_preview)
        form_layout.addRow("Mileage (km):", self.mileage_input)
        
        # Registration number
        self.registration_input = QLineEdit()
        self.registration_input.setText(parsed_data['registration'])
        self.registration_input.setPlaceholderText("e.g., AB12345")
        self.registration_input.textChanged.connect(self.update_preview)
        form_layout.addRow("Registration No:", self.registration_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Preview
        preview_group = QGroupBox("Destination Preview")
        preview_layout = QVBoxLayout()
        self.preview_label = QLabel()
        self.preview_label.setWordWrap(True)
        self.preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        preview_layout.addWidget(self.preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(self.reject)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save && Organize")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(self.save_file)
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
        
        # Set focus to mileage input (first empty field)
        self.mileage_input.setFocus()
        
        # Update preview
        self.update_preview()
        
        # Center on screen
        self.center_on_screen()
        
    def center_on_screen(self):
        """Center the window on screen"""
        screen = QApplication.primaryScreen().geometry()
        size = self.geometry()
        self.move(
            (screen.width() - size.width()) // 2,
            (screen.height() - size.height()) // 2
        )
    
    def update_preview(self):
        """Update destination path preview"""
        make = self.make_input.text().strip()
        model = self.model_input.text().strip().replace(' ', '_')
        date = self.date_input.text().strip()
        ecu = self.ecu_input.text().strip().replace(' ', '_')
        read_method = self.read_method_combo.currentText()
        mileage = self.mileage_input.text().strip()
        registration = self.registration_input.text().strip().replace(' ', '_')
        
        # Shorten read method for folder name
        read_method_short = read_method.replace('Normal Read-', '').replace('Virtual Read-', 'Virtual')
        
        if make and model:
            folder_name = f"{make}_{model}_{date}_{ecu}_{read_method_short}"
            if mileage:
                folder_name += f"_{mileage}km"
            if registration:
                folder_name += f"_{registration}"
            
            dest_path = os.path.join(self.destination_base, make, folder_name)
            self.preview_label.setText(f"📂 {dest_path}")
        else:
            self.preview_label.setText("⚠️ Please fill in Make and Model")
    
    def check_existing_folders(self, registration):
        """Check if folders exist for this registration number"""
        existing_folders = []
        
        if not registration or not os.path.exists(self.destination_base):
            return existing_folders
        
        # Clean registration for matching
        registration_clean = registration.strip().replace(' ', '_')
        
        # Search through all make folders
        try:
            for make_name in os.listdir(self.destination_base):
                make_folder = os.path.join(self.destination_base, make_name)
                if not os.path.isdir(make_folder):
                    continue
                
                # Look through all folders in this make
                for folder_name in os.listdir(make_folder):
                    folder_path = os.path.join(make_folder, folder_name)
                    if os.path.isdir(folder_path):
                        # Check if folder name ends with this registration number
                        if folder_name.endswith(f"_{registration_clean}"):
                            existing_folders.append({
                                'path': folder_path,
                                'name': folder_name
                            })
        except Exception as e:
            print(f"Error checking existing folders: {e}")
        
        # Sort by name (newest first usually)
        existing_folders.sort(key=lambda x: x['name'], reverse=True)
        
        return existing_folders
    
    def show_duplicate_dialog(self, existing_folders):
        """Show dialog to choose between existing folder or creating new one"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Duplicate Detected")
        msg.setIcon(QMessageBox.Icon.Question)
        
        # Extract registration from first folder name
        first_folder = existing_folders[0]['name']
        registration = first_folder.split('_')[-1] if '_' in first_folder else "this registration"
        
        # Build message
        text = f"<h3>🔍 Found {len(existing_folders)} existing folder(s) for registration: <b>{registration}</b></h3>"
        text += "<p><b>Existing folders:</b></p><ul>"
        for folder in existing_folders[:5]:  # Show max 5
            text += f"<li><small>{folder['name']}</small></li>"
        if len(existing_folders) > 5:
            text += f"<li><i>... and {len(existing_folders) - 5} more</i></li>"
        text += "</ul>"
        text += "<p><b>What do you want to do?</b></p>"
        text += "<p><i>Add to existing: Keep all files together<br>"
        text += "Create new: Separate by date/service</i></p>"
        
        msg.setText(text)
        msg.setTextFormat(Qt.TextFormat.RichText)
        
        # Add custom buttons
        add_existing_btn = msg.addButton("📁 Add to Existing Folder", QMessageBox.ButtonRole.ActionRole)
        create_new_btn = msg.addButton("✨ Create New Folder", QMessageBox.ButtonRole.ActionRole)
        cancel_btn = msg.addButton("❌ Cancel", QMessageBox.ButtonRole.RejectRole)
        
        msg.exec()
        
        clicked_button = msg.clickedButton()
        
        if clicked_button == add_existing_btn:
            # If multiple folders, let user choose which one
            if len(existing_folders) > 1:
                return self.choose_existing_folder(existing_folders)
            else:
                return ('existing', existing_folders[0]['path'])
        elif clicked_button == create_new_btn:
            return ('new', None)
        else:
            return ('cancel', None)
    
    def choose_existing_folder(self, existing_folders):
        """Let user choose which existing folder to use"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Choose Existing Folder")
        dialog.setMinimumWidth(600)
        dialog.setMinimumHeight(400)
        
        layout = QVBoxLayout()
        
        label = QLabel("<h3>Select folder to add file to:</h3>")
        label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(label)
        
        list_widget = QListWidget()
        for folder in existing_folders:
            list_widget.addItem(folder['name'])
        list_widget.setCurrentRow(0)  # Select first by default
        layout.addWidget(list_widget)
        
        button_box = QDialogButtonBox(
            QDialogButtonBox.StandardButton.Ok | QDialogButtonBox.StandardButton.Cancel
        )
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)
        
        dialog.setLayout(layout)
        
        if dialog.exec() == QDialog.DialogCode.Accepted:
            selected_index = list_widget.currentRow()
            if selected_index >= 0:
                return ('existing', existing_folders[selected_index]['path'])
        
        return ('cancel', None)
    
    def save_file(self):
        """Save and organize the file"""
        make = self.make_input.text().strip()
        model = self.model_input.text().strip().replace(' ', '_')
        date = self.date_input.text().strip()
        ecu = self.ecu_input.text().strip().replace(' ', '_')
        read_method = self.read_method_combo.currentText()
        mileage = self.mileage_input.text().strip()
        registration = self.registration_input.text().strip().replace(' ', '_')
        
        # Validation
        if not make or not model:
            QMessageBox.warning(self, "Missing Information", 
                              "Please fill in at least Make and Model!")
            return
        
        # Check for existing folders with same registration number
        existing_folders = []
        if registration:  # Only check if registration is provided
            existing_folders = self.check_existing_folders(registration)
        
        dest_folder = None
        
        if existing_folders:
            # Show duplicate dialog
            choice, folder_path = self.show_duplicate_dialog(existing_folders)
            
            if choice == 'cancel':
                return  # User cancelled
            elif choice == 'existing':
                # Use existing folder
                dest_folder = folder_path
            elif choice == 'new':
                # Create new folder (continue with normal flow)
                pass
        
        # If not using existing folder, create new one
        if dest_folder is None:
            # Shorten read method for folder name
            read_method_short = read_method.replace('Normal Read-', '').replace('Virtual Read-', 'Virtual')
            
            # Build destination path
            folder_name = f"{make}_{model}_{date}_{ecu}_{read_method_short}"
            if mileage:
                folder_name += f"_{mileage}km"
            if registration:
                folder_name += f"_{registration}"
            
            dest_folder = os.path.join(self.destination_base, make, folder_name)
        
        try:
            # Create destination folder (if it doesn't exist)
            os.makedirs(dest_folder, exist_ok=True)
            
            # Move file (not copy)
            filename = os.path.basename(self.file_path)
            dest_path = os.path.join(dest_folder, filename)
            
            # Check if file already exists in destination
            if os.path.exists(dest_path):
                # Add timestamp to avoid overwriting
                base_name, ext = os.path.splitext(filename)
                timestamp = datetime.now().strftime("%H%M%S")
                filename = f"{base_name}_{timestamp}{ext}"
                dest_path = os.path.join(dest_folder, filename)
            
            shutil.move(self.file_path, dest_path)
            
            # Create Log.txt file
            self.create_log_file(dest_folder, make, model, date, ecu, read_method, 
                               mileage, registration, filename, dest_path)
            
            # Open folder if setting is enabled
            if self.parent_window and self.parent_window.settings.get('open_folder_on_save', False):
                try:
                    # Open folder in Windows Explorer
                    os.startfile(dest_folder)
                except Exception as e:
                    print(f"Could not open folder: {e}")
            
            # Emit signal and close
            self.file_saved.emit(dest_path)
            self.close()
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Failed to save file:\n{str(e)}")
    
    def create_log_file(self, dest_folder, make, model, date, ecu, read_method, 
                       mileage, registration, filename, dest_path):
        """Create or append to Log.txt file with session information"""
        try:
            log_path = os.path.join(dest_folder, "Log.txt")
            
            # Get file size
            file_size = os.path.getsize(dest_path)
            file_size_mb = file_size / (1024 * 1024)
            
            # Get current timestamp
            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            
            # Check if log file already exists
            is_new_log = not os.path.exists(log_path)
            
            # Build log entry
            if is_new_log:
                # First entry - create header
                log_entry = f"""ECU File Organization Log
{'=' * 70}

Vehicle: {make} {model} | Registration: {registration}
Folder: {os.path.basename(dest_folder)}

{'=' * 70}

"""
            else:
                # Subsequent entry - add separator
                log_entry = f"\n{'=' * 70}\n\n"
            
            # Add session entry
            log_entry += f"""SESSION {timestamp}
{'-' * 70}

File: {filename}
Size: {file_size_mb:.2f} MB ({file_size:,} bytes)

Vehicle Information:
  Make:           {make}
  Model:          {model}
  Date:           {date}
  ECU Type:       {ecu}
  Read Method:    {read_method}
  Mileage:        {mileage} km
  Registration:   {registration}

Full Path: {dest_path}

Organized by ECU File Organizer v1.7
https://buymeacoffee.com/autobyte
"""
            
            # Append to log file (or create if new)
            mode = 'w' if is_new_log else 'a'
            with open(log_path, mode, encoding='utf-8') as f:
                f.write(log_entry)
            
            session_text = "first session" if is_new_log else "new session"
            print(f"Log file updated: {log_path} ({session_text})")
            
        except Exception as e:
            print(f"Error creating/updating log file: {e}")
            # Don't show error to user - log creation is not critical
    
    def reject(self):
        """Cancel and close"""
        self.close()


class ECUOrganizerMain(QMainWindow):
    """Main application window"""
    
    def __init__(self):
        super().__init__()
        self.settings_file = os.path.join(os.path.expanduser('~'), '.ecu_organizer_settings.json')
        self.load_settings()
        self.init_ui()
        self.setup_tray()
        self.start_monitoring()
    
    def is_in_startup(self):
        """Check if application is in Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_READ)
            winreg.QueryValueEx(key, "ECUFileOrganizer")
            winreg.CloseKey(key)
            return True
        except (FileNotFoundError, OSError):
            return False
    
    def add_to_startup(self):
        """Add application to Windows startup"""
        try:
            # Get the path to the executable (or python script)
            if getattr(sys, 'frozen', False):
                # Running as compiled executable
                app_path = f'"{sys.executable}" --minimized'
            else:
                # Running as script - use pythonw to avoid console
                script_path = os.path.abspath(__file__)
                app_path = f'pythonw.exe "{script_path}" --minimized'
            
            # Registry key for startup
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            winreg.SetValueEx(key, "ECUFileOrganizer", 0, winreg.REG_SZ, app_path)
            winreg.CloseKey(key)
            
            self.settings['run_on_startup'] = True
            self.save_settings()
            return True
            
        except Exception as e:
            QMessageBox.warning(self, "Startup Error", f"Failed to add to startup:\n{str(e)}")
            return False
    
    def remove_from_startup(self):
        """Remove application from Windows startup"""
        try:
            key_path = r"Software\Microsoft\Windows\CurrentVersion\Run"
            key = winreg.OpenKey(winreg.HKEY_CURRENT_USER, key_path, 0, winreg.KEY_SET_VALUE)
            
            winreg.DeleteValue(key, "ECUFileOrganizer")
            winreg.CloseKey(key)
            
            self.settings['run_on_startup'] = False
            self.save_settings()
            return True
            
        except FileNotFoundError:
            # Already not in startup
            self.settings['run_on_startup'] = False
            self.save_settings()
            return True
        except Exception as e:
            QMessageBox.warning(self, "Startup Error", f"Failed to remove from startup:\n{str(e)}")
            return False
        
    def load_settings(self):
        """Load saved settings"""
        defaults = {
            'monitor_folder': os.path.join(os.path.expanduser('~'), 'Desktop', 'AutotunerFiles'),
            'destination_base': os.path.join(os.path.expanduser('~'), 'Desktop', 'ECU_files'),
            'run_on_startup': True,
            'open_folder_on_save': True,
            'recent_files': []  # Track recent organized files
        }
        
        if os.path.exists(self.settings_file):
            try:
                with open(self.settings_file, 'r') as f:
                    self.settings = json.load(f)
                # Merge with defaults for any missing keys
                for key, value in defaults.items():
                    if key not in self.settings:
                        self.settings[key] = value
            except:
                self.settings = defaults
        else:
            self.settings = defaults
            
    def save_settings(self):
        """Save settings to file"""
        try:
            with open(self.settings_file, 'w') as f:
                json.dump(self.settings, f, indent=4)
        except:
            pass
    
    def init_ui(self):
        """Initialize main window UI"""
        self.setWindowTitle("")  # Empty so only app name shows: "ECU File Organizer v1.7"
        self.setGeometry(100, 100, 600, 580)
        
        # Create menu bar
        menubar = self.menuBar()
        
        # Help menu
        help_menu = menubar.addMenu("Help")
        
        # Search action
        search_action = QAction("🔍 Search Files", self)
        search_action.triggered.connect(self.show_search_dialog)
        help_menu.addAction(search_action)
        
        # Recent Files action
        recent_action = QAction("📋 Recent Files", self)
        recent_action.triggered.connect(self.show_recent_files)
        help_menu.addAction(recent_action)
        
        # History action
        history_action = QAction("📜 History", self)
        history_action.triggered.connect(self.show_edit_history)
        help_menu.addAction(history_action)
        
        help_menu.addSeparator()
        
        # About action
        about_action = QAction("About", self)
        about_action.triggered.connect(self.show_about)
        help_menu.addAction(about_action)
        
        help_menu.addSeparator()
        
        # Support action
        support_action = QAction("☕ Support the Developer", self)
        support_action.triggered.connect(self.show_support)
        help_menu.addAction(support_action)
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("🔧 ECU File Organizer")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Settings group
        settings_group = QGroupBox("Settings")
        settings_layout = QFormLayout()
        
        # Monitor folder
        monitor_layout = QHBoxLayout()
        self.monitor_folder_input = QLineEdit()
        self.monitor_folder_input.setText(self.settings['monitor_folder'])
        self.monitor_folder_input.setReadOnly(True)
        monitor_layout.addWidget(self.monitor_folder_input)
        
        browse_monitor_btn = QPushButton("Browse")
        browse_monitor_btn.clicked.connect(self.browse_monitor_folder)
        monitor_layout.addWidget(browse_monitor_btn)
        
        settings_layout.addRow("Monitor Folder:", monitor_layout)
        
        # Destination folder
        dest_layout = QHBoxLayout()
        self.dest_folder_input = QLineEdit()
        self.dest_folder_input.setText(self.settings['destination_base'])
        self.dest_folder_input.setReadOnly(True)
        dest_layout.addWidget(self.dest_folder_input)
        
        browse_dest_btn = QPushButton("Browse")
        browse_dest_btn.clicked.connect(self.browse_dest_folder)
        dest_layout.addWidget(browse_dest_btn)
        
        settings_layout.addRow("Destination Folder:", dest_layout)
        
        # Windows startup checkbox
        self.startup_checkbox = QCheckBox("Run on Windows startup")
        self.startup_checkbox.setChecked(self.is_in_startup())
        self.startup_checkbox.stateChanged.connect(self.toggle_startup)
        settings_layout.addRow("", self.startup_checkbox)
        
        # Open folder checkbox
        self.open_folder_checkbox = QCheckBox("Open folder when file is saved")
        self.open_folder_checkbox.setChecked(self.settings.get('open_folder_on_save', True))
        self.open_folder_checkbox.stateChanged.connect(self.toggle_open_folder)
        settings_layout.addRow("", self.open_folder_checkbox)
        
        settings_group.setLayout(settings_layout)
        layout.addWidget(settings_group)
        
        # Status
        status_group = QGroupBox("Status")
        status_layout = QVBoxLayout()
        self.status_label = QLabel("⏸️ Monitoring not started")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        status_layout.addWidget(self.status_label)
        status_group.setLayout(status_layout)
        layout.addWidget(status_group)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        self.start_stop_btn = QPushButton("▶️ Start Monitoring")
        self.start_stop_btn.clicked.connect(self.toggle_monitoring)
        button_layout.addWidget(self.start_stop_btn)
        
        minimize_btn = QPushButton("Minimize to Tray")
        minimize_btn.clicked.connect(self.hide)
        button_layout.addWidget(minimize_btn)
        
        # History button
        history_btn = QPushButton("📜 History")
        history_btn.clicked.connect(self.show_edit_history)
        history_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        button_layout.addWidget(history_btn)
        
        exit_btn = QPushButton("❌ Exit")
        exit_btn.setStyleSheet("""
            QPushButton {
                background-color: #f44336;
                color: white;
                padding: 5px 15px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #da190b;
            }
        """)
        exit_btn.clicked.connect(self.quit_application)
        button_layout.addWidget(exit_btn)
        
        layout.addLayout(button_layout)
        
        # Support link
        support_layout = QHBoxLayout()
        support_layout.addStretch()
        
        support_label = QLabel(
            "If you like this app, you can support me on: "
            "<a href='https://buymeacoffee.com/autobyte' style='color: #FFDD00; text-decoration: none;'>"
            "☕ <b>Buy Me a Coffee</b></a>"
        )
        support_label.setTextFormat(Qt.TextFormat.RichText)
        support_label.setOpenExternalLinks(True)
        support_label.setStyleSheet("""
            QLabel {
                padding: 10px;
                color: #666;
                font-size: 11px;
            }
        """)
        support_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        support_layout.addWidget(support_label)
        
        support_layout.addStretch()
        layout.addLayout(support_layout)
        
        layout.addStretch()
        
        central_widget.setLayout(layout)
        
    def setup_tray(self):
        """Setup system tray icon"""
        self.tray_icon = QSystemTrayIcon(self)
        
        # Set tooltip to show proper application name
        self.tray_icon.setToolTip("ECU File Organizer")
        
        # Create icon (using text as placeholder)
        icon = QIcon()  # You can add a proper icon file here
        self.tray_icon.setIcon(QApplication.style().standardIcon(
            QApplication.style().StandardPixmap.SP_ComputerIcon))
        
        # Create menu
        tray_menu = QMenu()
        
        show_action = QAction("Show Window", self)
        show_action.triggered.connect(self.show)
        tray_menu.addAction(show_action)
        
        tray_menu.addSeparator()
        
        quit_action = QAction("Quit", self)
        quit_action.triggered.connect(self.quit_application)
        tray_menu.addAction(quit_action)
        
        self.tray_icon.setContextMenu(tray_menu)
        self.tray_icon.activated.connect(self.tray_icon_activated)
        
        self.tray_icon.show()
        
    def tray_icon_activated(self, reason):
        """Handle tray icon activation"""
        if reason == QSystemTrayIcon.ActivationReason.DoubleClick:
            self.show()
    
    def browse_monitor_folder(self):
        """Browse for monitor folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Monitor Folder",
                                                  self.settings['monitor_folder'])
        if folder:
            self.monitor_folder_input.setText(folder)
            self.settings['monitor_folder'] = folder
            self.save_settings()
            
            # Restart monitoring if active
            if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
                self.stop_monitoring()
                self.start_monitoring()
    
    def browse_dest_folder(self):
        """Browse for destination folder"""
        folder = QFileDialog.getExistingDirectory(self, "Select Destination Folder",
                                                  self.settings['destination_base'])
        if folder:
            self.dest_folder_input.setText(folder)
            self.settings['destination_base'] = folder
            self.save_settings()
    
    def toggle_startup(self, state):
        """Toggle Windows startup based on checkbox state"""
        if state == Qt.CheckState.Checked.value:
            # Add to startup
            if self.add_to_startup():
                self.tray_icon.showMessage(
                    "Startup Enabled",
                    "ECU Organizer will start with Windows (minimized to tray)",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
        else:
            # Remove from startup
            if self.remove_from_startup():
                self.tray_icon.showMessage(
                    "Startup Disabled",
                    "ECU Organizer will not start with Windows",
                    QSystemTrayIcon.MessageIcon.Information,
                    2000
                )
    
    def toggle_open_folder(self, state):
        """Toggle open folder on save setting"""
        self.settings['open_folder_on_save'] = (state == Qt.CheckState.Checked.value)
        self.save_settings()
    
    def start_monitoring(self):
        """Start folder monitoring"""
        # Create destination folder if it doesn't exist
        os.makedirs(self.settings['destination_base'], exist_ok=True)
        
        # Start monitor thread
        self.monitor_thread = FileMonitor(self.settings['monitor_folder'])
        self.monitor_thread.file_detected.connect(self.handle_new_file)
        self.monitor_thread.start()
        
        self.status_label.setText(f"✅ Monitoring: {self.settings['monitor_folder']}")
        self.status_label.setStyleSheet("padding: 10px; background-color: #d4edda; border-radius: 5px; color: #155724;")
        self.start_stop_btn.setText("⏸️ Stop Monitoring")
        
        # Update tray tooltip
        self.tray_icon.setToolTip("ECU File Organizer - Monitoring Active")
        
        # Show tray notification
        self.tray_icon.showMessage(
            "ECU Organizer",
            "Monitoring started",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    def stop_monitoring(self):
        """Stop folder monitoring"""
        if hasattr(self, 'monitor_thread'):
            self.monitor_thread.stop()
            self.monitor_thread.wait()
        
        self.status_label.setText("⏸️ Monitoring stopped")
        self.status_label.setStyleSheet("padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        self.start_stop_btn.setText("▶️ Start Monitoring")
        
        # Update tray tooltip
        self.tray_icon.setToolTip("ECU File Organizer - Monitoring Stopped")
    
    def toggle_monitoring(self):
        """Toggle monitoring on/off"""
        if hasattr(self, 'monitor_thread') and self.monitor_thread.isRunning():
            self.stop_monitoring()
        else:
            self.start_monitoring()
    
    def handle_new_file(self, file_path):
        """Handle newly detected file"""
        # Parse filename
        filename = os.path.basename(file_path)
        parsed_data = FileParser.parse_filename(filename)
        
        # Show pop-up form
        self.show_file_form(file_path, parsed_data)
        
        # Show tray notification
        self.tray_icon.showMessage(
            "New ECU File",
            f"File detected: {filename}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def show_file_form(self, file_path, parsed_data):
        """Show the pop-up form dialog"""
        dialog = ECUFormDialog(file_path, parsed_data, self.settings['destination_base'], parent_window=self)
        dialog.file_saved.connect(self.on_file_saved)
        dialog.show()
        
        # Keep reference to prevent garbage collection
        if not hasattr(self, 'active_dialogs'):
            self.active_dialogs = []
        self.active_dialogs.append(dialog)
        dialog.destroyed.connect(lambda: self.active_dialogs.remove(dialog) 
                                if dialog in self.active_dialogs else None)
    
    def on_file_saved(self, dest_path):
        """Handle file successfully saved"""
        # Add to recent files
        self.add_to_recent_files(dest_path)
        
        self.tray_icon.showMessage(
            "File Organized",
            f"File saved to:\n{dest_path}",
            QSystemTrayIcon.MessageIcon.Information,
            3000
        )
    
    def add_to_recent_files(self, dest_path):
        """Add file to recent files list"""
        try:
            # Extract folder information
            folder_path = os.path.dirname(dest_path)
            folder_name = os.path.basename(folder_path)
            filename = os.path.basename(dest_path)
            
            # Get parent folder (make)
            parent_folder = os.path.basename(os.path.dirname(folder_path))
            
            # Create recent file entry
            recent_entry = {
                'folder_path': folder_path,
                'folder_name': folder_name,
                'filename': filename,
                'make': parent_folder,
                'timestamp': datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            }
            
            # Get current recent files
            recent_files = self.settings.get('recent_files', [])
            
            # Add new entry at the beginning
            recent_files.insert(0, recent_entry)
            
            # Keep only last 20 entries
            recent_files = recent_files[:20]
            
            # Save to settings
            self.settings['recent_files'] = recent_files
            self.save_settings()
            
        except Exception as e:
            print(f"Error adding to recent files: {e}")
    
    def closeEvent(self, event):
        """Handle window close event"""
        event.ignore()
        self.hide()
        self.tray_icon.showMessage(
            "ECU Organizer",
            "Application minimized to tray",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    
    
    def show_recent_files(self):
        """Show recent files dialog"""
        recent_files = self.settings.get('recent_files', [])
        
        if not recent_files:
            QMessageBox.information(
                self,
                "No Recent Files",
                "No files have been organized yet.\n\n"
                "Organize some files first, then they will appear here."
            )
            return
        
        # Create recent files dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Recent Files")
        dialog.setMinimumWidth(700)
        dialog.setMinimumHeight(500)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>📋 Recent Files</h2>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        info_label = QLabel(
            f"<i>Showing last {len(recent_files)} organized files</i>"
        )
        info_label.setTextFormat(Qt.TextFormat.RichText)
        info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        info_label.setStyleSheet("color: #666; padding: 5px;")
        layout.addWidget(info_label)
        
        # Files list
        files_list = QListWidget()
        
        for entry in recent_files:
            # Parse folder name for display
            folder_name = entry.get('folder_name', '')
            timestamp = entry.get('timestamp', '')
            make = entry.get('make', '')
            
            # Create display text
            display_text = f"🕐 {timestamp} - {make} / {folder_name}"
            
            # Add to list
            item = QListWidgetItem(display_text)
            item.setData(Qt.ItemDataRole.UserRole, entry)  # Store full entry
            files_list.addItem(item)
        
        files_list.setCurrentRow(0)  # Select first
        layout.addWidget(files_list)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_folder_btn = QPushButton("📂 Open Folder")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        open_folder_btn.clicked.connect(lambda: self.open_recent_folder(files_list))
        button_layout.addWidget(open_folder_btn)
        
        view_log_btn = QPushButton("📄 View Log")
        view_log_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        view_log_btn.clicked.connect(lambda: self.view_recent_log(files_list))
        button_layout.addWidget(view_log_btn)
        
        button_layout.addStretch()
        
        clear_btn = QPushButton("🗑️ Clear History")
        clear_btn.clicked.connect(lambda: self.clear_recent_files(dialog))
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def open_recent_folder(self, files_list):
        """Open folder for selected recent file"""
        current_item = files_list.currentItem()
        if not current_item:
            return
        
        entry = current_item.data(Qt.ItemDataRole.UserRole)
        folder_path = entry.get('folder_path', '')
        
        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not open folder:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Folder Not Found",
                f"The folder no longer exists:\n\n{folder_path}"
            )
    
    def view_recent_log(self, files_list):
        """View Log.txt for selected recent file"""
        current_item = files_list.currentItem()
        if not current_item:
            return
        
        entry = current_item.data(Qt.ItemDataRole.UserRole)
        folder_path = entry.get('folder_path', '')
        log_path = os.path.join(folder_path, "Log.txt")
        
        if os.path.exists(log_path):
            try:
                os.startfile(log_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not open log file:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Log Not Found",
                f"Log.txt not found in:\n\n{folder_path}"
            )
    
    def clear_recent_files(self, parent_dialog):
        """Clear recent files history"""
        reply = QMessageBox.question(
            parent_dialog,
            "Clear History",
            "Are you sure you want to clear all recent files history?",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply == QMessageBox.StandardButton.Yes:
            self.settings['recent_files'] = []
            self.save_settings()
            parent_dialog.close()
            QMessageBox.information(
                self,
                "History Cleared",
                "Recent files history has been cleared."
            )
    
    
    def show_search_dialog(self):
        """Show search and filter dialog"""
        destination_base = self.settings.get('destination_base', '')
        
        if not destination_base or not os.path.exists(destination_base):
            QMessageBox.warning(
                self,
                "No Destination Set",
                "Please set the destination folder in Settings first."
            )
            return
        
        # Create search dialog
        dialog = QDialog(self)
        dialog.setWindowTitle("Search & Filter Files")
        dialog.setMinimumWidth(800)
        dialog.setMinimumHeight(600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel("<h2>🔍 Search & Filter Files</h2>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Search fields
        search_group = QGroupBox("Search Filters")
        search_layout = QFormLayout()
        
        registration_input = QLineEdit()
        registration_input.setPlaceholderText("e.g., AB12345")
        search_layout.addRow("Registration:", registration_input)
        
        make_input = QLineEdit()
        make_input.setPlaceholderText("e.g., Volkswagen")
        search_layout.addRow("Make:", make_input)
        
        model_input = QLineEdit()
        model_input.setPlaceholderText("e.g., Golf")
        search_layout.addRow("Model:", model_input)
        
        ecu_input = QLineEdit()
        ecu_input.setPlaceholderText("e.g., PCR2.1")
        search_layout.addRow("ECU Type:", ecu_input)
        
        search_group.setLayout(search_layout)
        layout.addWidget(search_group)
        
        # Search button
        search_btn = QPushButton("🔍 Search")
        search_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 10px 20px;
                font-weight: bold;
                font-size: 14px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        layout.addWidget(search_btn)
        
        # Results label
        results_label = QLabel("<b>Search Results:</b>")
        results_label.setTextFormat(Qt.TextFormat.RichText)
        layout.addWidget(results_label)
        
        # Results list
        results_list = QListWidget()
        layout.addWidget(results_list)
        
        # Results count
        count_label = QLabel("Enter search criteria and click Search")
        count_label.setStyleSheet("color: #666; font-style: italic; padding: 5px;")
        layout.addWidget(count_label)
        
        # Buttons
        button_layout = QHBoxLayout()
        
        open_folder_btn = QPushButton("📂 Open Folder")
        open_folder_btn.setStyleSheet("""
            QPushButton {
                background-color: #2196F3;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #1976D2;
            }
        """)
        open_folder_btn.clicked.connect(lambda: self.open_search_result(results_list))
        button_layout.addWidget(open_folder_btn)
        
        view_log_btn = QPushButton("📄 View Log")
        view_log_btn.clicked.connect(lambda: self.view_search_log(results_list))
        button_layout.addWidget(view_log_btn)
        
        button_layout.addStretch()
        
        close_btn = QPushButton("Close")
        close_btn.clicked.connect(dialog.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        # Connect search button
        search_btn.clicked.connect(lambda: self.perform_search(
            registration_input.text(),
            make_input.text(),
            model_input.text(),
            ecu_input.text(),
            results_list,
            count_label
        ))
        
        dialog.setLayout(layout)
        dialog.exec()
    
    def perform_search(self, registration, make, model, ecu, results_list, count_label):
        """Perform search with given criteria"""
        destination_base = self.settings.get('destination_base', '')
        
        # Clear previous results
        results_list.clear()
        
        # Get search criteria (lowercase for case-insensitive search)
        search_reg = registration.strip().lower()
        search_make = make.strip().lower()
        search_model = model.strip().lower()
        search_ecu = ecu.strip().lower()
        
        # Check if at least one criteria is provided
        if not any([search_reg, search_make, search_model, search_ecu]):
            count_label.setText("⚠️ Please enter at least one search criterion")
            count_label.setStyleSheet("color: #ff9800; font-style: italic;")
            return
        
        count_label.setText("🔍 Searching...")
        count_label.setStyleSheet("color: #2196F3; font-style: italic;")
        QApplication.processEvents()  # Update UI
        
        results = []
        
        try:
            # Scan all make folders
            for make_name in os.listdir(destination_base):
                make_folder = os.path.join(destination_base, make_name)
                if not os.path.isdir(make_folder):
                    continue
                
                # Scan all folders in this make
                for folder_name in os.listdir(make_folder):
                    folder_path = os.path.join(make_folder, folder_name)
                    if not os.path.isdir(folder_path):
                        continue
                    
                    # Convert folder name to lowercase for comparison
                    folder_lower = folder_name.lower()
                    
                    # Check if folder matches search criteria
                    match = True
                    
                    if search_reg and search_reg not in folder_lower:
                        match = False
                    if search_make and search_make not in folder_lower:
                        match = False
                    if search_model and search_model not in folder_lower:
                        match = False
                    if search_ecu and search_ecu not in folder_lower:
                        match = False
                    
                    if match:
                        results.append({
                            'folder_path': folder_path,
                            'folder_name': folder_name,
                            'make': make_name
                        })
        
        except Exception as e:
            count_label.setText(f"❌ Search error: {str(e)}")
            count_label.setStyleSheet("color: #f44336; font-style: italic;")
            return
        
        # Display results
        if results:
            for result in results:
                display_text = f"{result['make']} / {result['folder_name']}"
                item = QListWidgetItem(display_text)
                item.setData(Qt.ItemDataRole.UserRole, result)
                results_list.addItem(item)
            
            count_label.setText(f"✅ Found {len(results)} matching folder(s)")
            count_label.setStyleSheet("color: #4CAF50; font-style: italic;")
            results_list.setCurrentRow(0)
        else:
            count_label.setText("❌ No folders found matching your criteria")
            count_label.setStyleSheet("color: #f44336; font-style: italic;")
    
    def open_search_result(self, results_list):
        """Open folder for selected search result"""
        current_item = results_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a folder from the search results first."
            )
            return
        
        result = current_item.data(Qt.ItemDataRole.UserRole)
        folder_path = result.get('folder_path', '')
        
        if os.path.exists(folder_path):
            try:
                os.startfile(folder_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not open folder:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Folder Not Found",
                f"The folder no longer exists:\n\n{folder_path}"
            )
    
    def view_search_log(self, results_list):
        """View Log.txt for selected search result"""
        current_item = results_list.currentItem()
        if not current_item:
            QMessageBox.information(
                self,
                "No Selection",
                "Please select a folder from the search results first."
            )
            return
        
        result = current_item.data(Qt.ItemDataRole.UserRole)
        folder_path = result.get('folder_path', '')
        log_path = os.path.join(folder_path, "Log.txt")
        
        if os.path.exists(log_path):
            try:
                os.startfile(log_path)
            except Exception as e:
                QMessageBox.warning(
                    self,
                    "Error",
                    f"Could not open log file:\n{str(e)}"
                )
        else:
            QMessageBox.warning(
                self,
                "Log Not Found",
                f"Log.txt not found in:\n\n{folder_path}"
            )
    
    def show_about(self):
        """Show about dialog"""
        QMessageBox.about(self, "About ECU File Organizer",
            "<h3>ECU File Organizer v1.7</h3>"
            "<p>Automatic ECU file organization tool for automotive diagnostics.</p>"
            "<p><b>Features:</b></p>"
            "<ul>"
            "<li>Automatic file monitoring</li>"
            "<li>Smart filename parsing</li>"
            "<li>Read method tracking (OBD, Bench, Boot)</li>"
            "<li>Duplicate detection & intelligent handling</li>"
            "<li>Edit History - Fix mistakes after organizing</li>"
            "<li>Auto-open folder on save</li>"
            "<li>Automatic session Log.txt creation</li>"
            "<li>🔍 Search & Filter files (NEW in v1.7)</li>"
            "<li>📋 Recent Files list (NEW in v1.7)</li>"
            "<li>Professional file organization</li>"
            "</ul>"
            "<p><b>Developer:</b> Autobyte Diagnostics</p>"
            "<p><b>Year:</b> 2026</p>"
            "<p>Made with ❤️ for automotive professionals</p>"
        )
    
    def show_support(self):
        """Show support dialog with Buy Me a Coffee link"""
        msg = QMessageBox(self)
        msg.setWindowTitle("Support the Developer")
        msg.setTextFormat(Qt.TextFormat.RichText)
        msg.setText(
            "<h3>☕ Support This Project</h3>"
            "<p>If you find this app useful and it makes your work easier, "
            "consider supporting its development!</p>"
            "<p><b>Your support helps:</b></p>"
            "<ul>"
            "<li>Keep the app free and updated</li>"
            "<li>Add new features you request</li>"
            "<li>Improve documentation</li>"
            "<li>Develop more professional tools</li>"
            "</ul>"
            "<p><b>Support me on:</b></p>"
            "<p><a href='https://buymeacoffee.com/autobyte'>"
            "☕ Buy Me a Coffee</a></p>"
            "<p><i>Thank you for your support! 🙏</i></p>"
        )
        msg.setIcon(QMessageBox.Icon.Information)
        msg.setStandardButtons(QMessageBox.StandardButton.Ok)
        msg.exec()
    
    def get_organized_folders(self):
        """Get list of all organized folders"""
        folders = []
        
        try:
            destination_base = self.settings.get('destination_base', '')
            print(f"DEBUG get_organized_folders: destination_base = {destination_base}")
            
            if not destination_base:
                print("DEBUG: destination_base is None or empty")
                return folders
            
            if not os.path.exists(destination_base):
                print(f"DEBUG: destination_base does not exist: {destination_base}")
                return folders
            
            print(f"DEBUG: Scanning {destination_base}")
            
            # Go through all make folders
            for make_name in os.listdir(destination_base):
                make_folder = os.path.join(destination_base, make_name)
                print(f"DEBUG: Checking {make_name}")
                
                if not os.path.isdir(make_folder):
                    print(f"DEBUG: {make_name} is not a directory, skipping")
                    continue
                
                # Get all folders in this make
                for folder_name in os.listdir(make_folder):
                    folder_path = os.path.join(make_folder, folder_name)
                    if os.path.isdir(folder_path):
                        # Get folder modification time
                        mod_time = os.path.getmtime(folder_path)
                        folders.append({
                            'path': folder_path,
                            'name': folder_name,
                            'make': make_name,
                            'modified': mod_time
                        })
                        print(f"DEBUG: Added folder {folder_name}")
                        
        except Exception as e:
            print(f"ERROR in get_organized_folders: {e}")
            import traceback
            traceback.print_exc()
        
        # Sort by modification time (newest first)
        folders.sort(key=lambda x: x['modified'], reverse=True)
        
        print(f"DEBUG: Total folders found: {len(folders)}")
        return folders
    
    def parse_folder_name(self, folder_name):
        """Parse folder name back to individual components"""
        parts = folder_name.split('_')
        
        # Try to extract components
        # Expected format: Make_Model_Date_ECU_ReadMethod_Mileage_Registration
        data = {
            'make': '',
            'model': '',
            'date': '',
            'ecu': '',
            'read_method': '',
            'mileage': '',
            'registration': ''
        }
        
        if len(parts) < 3:
            return data
        
        # Make (first part)
        data['make'] = parts[0]
        
        # Registration (last part, if doesn't end with km)
        if parts[-1] and not parts[-1].endswith('km'):
            data['registration'] = parts[-1]
            end_index = -1
        else:
            end_index = None
        
        # Mileage (part ending with 'km')
        for i in range(len(parts)-1, -1, -1):
            if parts[i].endswith('km'):
                data['mileage'] = parts[i].replace('km', '')
                mileage_index = i
                break
        
        # Read method (OBD, Bench, Boot, Virtual) - before mileage
        read_methods = ['OBD', 'Bench', 'Boot', 'Virtual']
        for method in read_methods:
            if method in parts:
                data['read_method'] = method if method != 'OBD' else 'Normal Read-OBD'
                read_method_index = parts.index(method)
                break
        
        # ECU (before read method or mileage)
        # Date (8 digits YYYYMMDD)
        # Model (between make and date)
        model_parts = []
        for i, part in enumerate(parts[1:], 1):
            if len(part) == 8 and part.isdigit():
                data['date'] = part
                data['model'] = '_'.join(model_parts)
                # Rest is ECU until read method
                ecu_parts = []
                for j in range(i+1, len(parts)):
                    if parts[j] in read_methods or parts[j].endswith('km'):
                        break
                    ecu_parts.append(parts[j])
                data['ecu'] = '_'.join(ecu_parts)
                break
            else:
                model_parts.append(part)
        
        return data
    
    def show_edit_history(self):
        """Show dialog to edit previously organized folders"""
        try:
            print("DEBUG: show_edit_history called")
            
            # Check if destination base is set
            destination_base = self.settings.get('destination_base', '')
            if not destination_base:
                print("DEBUG: destination_base is not set")
                QMessageBox.warning(
                    self,
                    "No Destination Set",
                    "Please set the destination folder in Settings first.\n\n"
                    "The destination folder is where your organized files are stored."
                )
                return
            
            print(f"DEBUG: destination_base = {destination_base}")
            print(f"DEBUG: destination_base exists = {os.path.exists(destination_base)}")
            
            folders = self.get_organized_folders()
            print(f"DEBUG: Found {len(folders)} folders")
            
            if not folders:
                QMessageBox.information(
                    self,
                    "No History",
                    "No organized folders found.\n\n"
                    "Organize some files first, then you can edit them here."
                )
                return
            
            # Create edit history dialog
            dialog = QDialog(self)
            dialog.setWindowTitle("Edit Folder History")
            dialog.setMinimumWidth(800)
            dialog.setMinimumHeight(600)
            
            layout = QVBoxLayout()
            
            # Title
            title = QLabel("<h2>📝 Edit Organized Folders</h2>")
            title.setTextFormat(Qt.TextFormat.RichText)
            title.setAlignment(Qt.AlignmentFlag.AlignCenter)
            layout.addWidget(title)
            
            info_label = QLabel(
                "<i>Select a folder from the list below to edit its information.<br>"
                "The folder will be renamed based on your changes.</i>"
            )
            info_label.setTextFormat(Qt.TextFormat.RichText)
            info_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
            info_label.setStyleSheet("color: #666; padding: 10px;")
            layout.addWidget(info_label)
            
            # Folder list
            list_label = QLabel("<b>Recent Folders (max 50):</b>")
            list_label.setTextFormat(Qt.TextFormat.RichText)
            layout.addWidget(list_label)
            
            folder_list = QListWidget()
            for folder in folders[:50]:  # Show max 50 recent folders
                item_text = f"{folder['make']} / {folder['name']}"
                folder_list.addItem(item_text)
            folder_list.setCurrentRow(0)  # Select first
            layout.addWidget(folder_list)
            
            # Buttons
            button_layout = QHBoxLayout()
            
            edit_btn = QPushButton("📝 Edit Selected Folder")
            edit_btn.setStyleSheet("""
                QPushButton {
                    background-color: #2196F3;
                    color: white;
                    padding: 8px 16px;
                    font-weight: bold;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #1976D2;
                }
            """)
            edit_btn.clicked.connect(lambda: self.edit_selected_folder(folders, folder_list.currentRow(), dialog))
            button_layout.addWidget(edit_btn)
            
            button_layout.addStretch()
            
            close_btn = QPushButton("Close")
            close_btn.clicked.connect(dialog.close)
            button_layout.addWidget(close_btn)
            
            layout.addLayout(button_layout)
            
            dialog.setLayout(layout)
            
            print("DEBUG: About to show dialog")
            dialog.exec()
            print("DEBUG: Dialog closed")
            
        except Exception as e:
            print(f"ERROR in show_edit_history: {e}")
            import traceback
            traceback.print_exc()
            QMessageBox.critical(
                self,
                "Error",
                f"Failed to show history:\n\n{str(e)}\n\n"
                f"Error type: {type(e).__name__}\n\n"
                "Please check the console for more details."
            )
    
    def edit_selected_folder(self, folders, index, parent_dialog):
        """Edit the selected folder"""
        if index < 0 or index >= len(folders):
            return
        
        folder_info = folders[index]
        folder_path = folder_info['path']
        folder_name = folder_info['name']
        
        # Parse folder name to get components
        data = self.parse_folder_name(folder_name)
        
        # Create edit dialog
        edit_dialog = QDialog(parent_dialog)
        edit_dialog.setWindowTitle(f"Edit Folder: {folder_name}")
        edit_dialog.setMinimumWidth(600)
        
        layout = QVBoxLayout()
        
        # Title
        title = QLabel(f"<h3>📝 Edit Folder Information</h3>")
        title.setTextFormat(Qt.TextFormat.RichText)
        title.setAlignment(Qt.AlignmentFlag.AlignCenter)
        layout.addWidget(title)
        
        # Current path
        path_label = QLabel(f"<b>Current location:</b><br><small>{folder_path}</small>")
        path_label.setTextFormat(Qt.TextFormat.RichText)
        path_label.setStyleSheet("color: #666; padding: 10px; background-color: #f0f0f0; border-radius: 5px;")
        path_label.setWordWrap(True)
        layout.addWidget(path_label)
        
        # Form
        form_group = QGroupBox("Edit Information")
        form_layout = QFormLayout()
        
        make_input = QLineEdit(data['make'])
        form_layout.addRow("Make:", make_input)
        
        model_input = QLineEdit(data['model'])
        form_layout.addRow("Model:", model_input)
        
        date_input = QLineEdit(data['date'])
        date_input.setPlaceholderText("YYYYMMDD")
        form_layout.addRow("Date:", date_input)
        
        ecu_input = QLineEdit(data['ecu'])
        form_layout.addRow("ECU Type:", ecu_input)
        
        read_method_combo = QComboBox()
        read_method_combo.addItems([
            "Normal Read-OBD",
            "Virtual Read-OBD",
            "Bench",
            "Boot"
        ])
        if data['read_method']:
            index = read_method_combo.findText(data['read_method'])
            if index >= 0:
                read_method_combo.setCurrentIndex(index)
        form_layout.addRow("Read Method:", read_method_combo)
        
        mileage_input = QLineEdit(data['mileage'])
        mileage_input.setPlaceholderText("e.g., 45000")
        form_layout.addRow("Mileage (km):", mileage_input)
        
        registration_input = QLineEdit(data['registration'])
        registration_input.setPlaceholderText("e.g., AB12345")
        form_layout.addRow("Registration No:", registration_input)
        
        form_group.setLayout(form_layout)
        layout.addWidget(form_group)
        
        # Preview
        preview_group = QGroupBox("New Folder Name Preview")
        preview_layout = QVBoxLayout()
        preview_label = QLabel()
        preview_label.setWordWrap(True)
        preview_label.setStyleSheet("background-color: #f0f0f0; padding: 10px; border-radius: 5px;")
        preview_layout.addWidget(preview_label)
        preview_group.setLayout(preview_layout)
        layout.addWidget(preview_group)
        
        # Update preview function
        def update_preview():
            make = make_input.text().strip()
            model = model_input.text().strip().replace(' ', '_')
            date = date_input.text().strip()
            ecu = ecu_input.text().strip().replace(' ', '_')
            read_method = read_method_combo.currentText()
            mileage = mileage_input.text().strip()
            registration = registration_input.text().strip().replace(' ', '_')
            
            read_method_short = read_method.replace('Normal Read-', '').replace('Virtual Read-', 'Virtual')
            
            if make and model:
                new_name = f"{make}_{model}_{date}_{ecu}_{read_method_short}"
                if mileage:
                    new_name += f"_{mileage}km"
                if registration:
                    new_name += f"_{registration}"
                
                preview_label.setText(f"📂 {new_name}")
            else:
                preview_label.setText("⚠️ Please fill in Make and Model")
        
        # Connect all inputs to update preview
        make_input.textChanged.connect(update_preview)
        model_input.textChanged.connect(update_preview)
        date_input.textChanged.connect(update_preview)
        ecu_input.textChanged.connect(update_preview)
        read_method_combo.currentTextChanged.connect(update_preview)
        mileage_input.textChanged.connect(update_preview)
        registration_input.textChanged.connect(update_preview)
        
        # Initial preview
        update_preview()
        
        # Buttons
        button_layout = QHBoxLayout()
        
        cancel_btn = QPushButton("Cancel")
        cancel_btn.clicked.connect(edit_dialog.close)
        button_layout.addWidget(cancel_btn)
        
        button_layout.addStretch()
        
        save_btn = QPushButton("💾 Save Changes")
        save_btn.setStyleSheet("""
            QPushButton {
                background-color: #4CAF50;
                color: white;
                padding: 8px 16px;
                font-weight: bold;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #45a049;
            }
        """)
        save_btn.clicked.connect(lambda: self.save_folder_edit(
            folder_path,
            folder_info['make'],
            make_input.text().strip(),
            model_input.text().strip(),
            date_input.text().strip(),
            ecu_input.text().strip(),
            read_method_combo.currentText(),
            mileage_input.text().strip(),
            registration_input.text().strip(),
            edit_dialog,
            parent_dialog
        ))
        button_layout.addWidget(save_btn)
        
        layout.addLayout(button_layout)
        
        edit_dialog.setLayout(layout)
        edit_dialog.exec()
    
    def save_folder_edit(self, old_path, old_make, make, model, date, ecu, read_method, 
                        mileage, registration, edit_dialog, parent_dialog):
        """Save the edited folder information by renaming"""
        # Validation
        if not make or not model:
            QMessageBox.warning(edit_dialog, "Missing Information",
                              "Please fill in at least Make and Model!")
            return
        
        # Build new folder name
        model = model.replace(' ', '_')
        ecu = ecu.replace(' ', '_')
        registration = registration.replace(' ', '_')
        read_method_short = read_method.replace('Normal Read-', '').replace('Virtual Read-', 'Virtual')
        
        new_folder_name = f"{make}_{model}_{date}_{ecu}_{read_method_short}"
        if mileage:
            new_folder_name += f"_{mileage}km"
        if registration:
            new_folder_name += f"_{registration}"
        
        # Build new path
        destination_base = self.settings.get('destination_base', '')
        new_path = os.path.join(destination_base, make, new_folder_name)
        
        # Check if path is the same
        if old_path == new_path:
            QMessageBox.information(edit_dialog, "No Changes",
                                  "No changes detected. Folder name is the same.")
            return
        
        # Check if new path already exists
        if os.path.exists(new_path):
            QMessageBox.warning(edit_dialog, "Folder Exists",
                              f"A folder with this name already exists:\n\n{new_folder_name}\n\n"
                              "Please use different values.")
            return
        
        # Confirm with user
        reply = QMessageBox.question(
            edit_dialog,
            "Confirm Changes",
            f"Rename folder?\n\n"
            f"From: {os.path.basename(old_path)}\n"
            f"To: {new_folder_name}\n\n"
            "This will rename the folder and may move it to a different make folder if you changed the make.",
            QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No
        )
        
        if reply != QMessageBox.StandardButton.Yes:
            return
        
        try:
            # Create new make folder if needed
            new_make_folder = os.path.join(destination_base, make)
            os.makedirs(new_make_folder, exist_ok=True)
            
            # Rename/move folder
            shutil.move(old_path, new_path)
            
            # Clean up old make folder if empty
            old_make_folder = os.path.dirname(old_path)
            try:
                if not os.listdir(old_make_folder):
                    os.rmdir(old_make_folder)
            except:
                pass  # Ignore if can't remove
            
            QMessageBox.information(
                edit_dialog,
                "Success",
                f"Folder renamed successfully!\n\n"
                f"New location:\n{new_path}"
            )
            
            # Close both dialogs
            edit_dialog.close()
            parent_dialog.close()
            
        except Exception as e:
            QMessageBox.critical(
                edit_dialog,
                "Error",
                f"Failed to rename folder:\n\n{str(e)}"
            )
    
    def quit_application(self):
        """Quit the application completely"""
        # Stop monitoring
        self.stop_monitoring()
        
        # Hide tray icon
        self.tray_icon.hide()
        
        # Quit application
        QApplication.quit()


def main():
    # Set application properties BEFORE creating QApplication
    QApplication.setApplicationName("ECU File Organizer v1.7")
    QApplication.setOrganizationName("Stellantis")
    QApplication.setApplicationDisplayName("ECU File Organizer v1.7")
    
    app = QApplication(sys.argv)
    
    # Set again after QApplication creation for redundancy
    app.setApplicationName("ECU File Organizer v1.7")
    app.setOrganizationName("Stellantis")
    app.setApplicationDisplayName("ECU File Organizer v1.7")
    app.setQuitOnLastWindowClosed(False)
    
    window = ECUOrganizerMain()
    
    # Check for --minimized or --tray command-line argument
    if "--minimized" in sys.argv or "--tray" in sys.argv:
        # Start minimized to tray (don't show window)
        window.hide()
        window.tray_icon.showMessage(
            "ECU File Organizer",
            "Running in system tray. Double-click icon to show window.",
            QSystemTrayIcon.MessageIcon.Information,
            2000
        )
    else:
        # Normal startup - show window
        window.show()
    
    sys.exit(app.exec())


if __name__ == '__main__':
    main()
