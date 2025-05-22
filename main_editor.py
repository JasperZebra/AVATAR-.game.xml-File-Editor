import os
import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import xml.etree.ElementTree as ET

try:
    from converter import GameXMLConverter
except ImportError:
    print("Warning: converter module not found. Conversion features will be disabled.")
    class GameXMLConverter:
        def __init__(self, *args, **kwargs):
            self.can_convert = False
        def is_file_xml_format(self, file):
            return True
        def convert_to_readable(self, file):
            return False, "Converter not available"
        def save_as_binary(self, file):
            return False, "Converter not available"

try:
    from dialogs import AttributeEditDialog, FindDialog
except ImportError:
    print("Warning: dialogs module not found. Some features may be limited.")
    # Fallback implementations would go here


class DarkTheme:
    """Dark theme configuration for the XML Editor"""
    
    # Main colors
    BG_DARK = "#2b2b2b"
    BG_DARKER = "#1e1e1e"
    BG_LIGHT = "#3a3a3a"
    FG_LIGHT = "#ffffff"
    FG_NORMAL = "#cccccc"
    FG_DIM = "#888888"
    
    # Accent colors
    ACCENT_BLUE = "#007acc"
    ACCENT_GREEN = "#4ec9b0"
    ACCENT_ORANGE = "#ce9178"
    ACCENT_RED = "#f44747"
    ACCENT_PURPLE = "#c586c0"
    ACCENT_YELLOW = "#dcdcaa"
    
    # UI specific colors
    SELECTION_BG = "#264f78"
    SELECTION_FG = "#ffffff"
    BORDER_COLOR = "#454545"
    BUTTON_BG = "#414141"
    BUTTON_HOVER = "#4a4a4a"
    ENTRY_BG = "#3c3c3c"
    ENTRY_FG = "#ffffff"
    MENU_BG = "#2b2b2b"
    MENU_FG = "#cccccc"
    
    # Syntax highlighting colors
    XML_TAG = "#569cd6"
    XML_ATTR = "#9cdcfe"
    XML_STRING = "#ce9178"
    XML_COMMENT = "#6a9955"
    XML_TEXT = "#d4d4d4"


class GameXMLEditor:
    """Modern GUI Editor for .game.xml files with dark theme"""
    
    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AVATAR XML File Editor | Made By: Jasper_Zebra | version 2.0")
        self.root.geometry("1800x1100")
        
        # Apply dark theme
        self.setup_dark_theme()
        
        # Initialize converter
        self.converter = GameXMLConverter()
        
        # Current file
        self.current_file = None
        self.tree_data = None
        self.is_modified = False
        self.element_map = {}
        
        # NEW: Track source modifications separately
        self.source_modified = False
        self.updating_source = False  # Flag to prevent recursive updates
        
        # Create GUI
        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()
        self.create_status_bar()
        
        # Check converter status and show welcome
        self.show_welcome_message()
        
        if not self.converter.can_convert:
            self.status_var.set("WARNING: File conversion disabled - missing tools/dependencies")
        else:
            self.status_var.set("Ready - AVATAR XML File Editor | Made By: Jasper_Zebra | version 2.0")
    
    def setup_dark_theme(self):
        """Configure dark theme for the application"""
        self.root.configure(bg=DarkTheme.BG_DARK)
        
        # Configure ttk style
        style = ttk.Style()
        style.theme_use('clam')
        
        # Configure Frame styles
        style.configure('TFrame', 
                       background=DarkTheme.BG_DARK,
                       borderwidth=0)
        
        # Configure Label styles
        style.configure('TLabel', 
                       background=DarkTheme.BG_DARK, 
                       foreground=DarkTheme.FG_NORMAL,
                       font=('Segoe UI', 9))
        
        # Configure LabelFrame styles
        style.configure('TLabelframe',
                       background=DarkTheme.BG_DARK,
                       foreground=DarkTheme.FG_LIGHT,
                       borderwidth=1,
                       relief='solid')
        style.configure('TLabelframe.Label',
                       background=DarkTheme.BG_DARK,
                       foreground=DarkTheme.ACCENT_BLUE,
                       font=('Segoe UI', 9, 'bold'))
        
        # Configure Button styles
        style.configure('TButton',
                       background=DarkTheme.BUTTON_BG,
                       foreground=DarkTheme.FG_NORMAL,
                       borderwidth=1,
                       focuscolor='none',
                       font=('Segoe UI', 9),
                       relief='flat')
        style.map('TButton',
                 background=[('active', DarkTheme.BUTTON_HOVER),
                           ('pressed', DarkTheme.SELECTION_BG)],
                 foreground=[('active', DarkTheme.FG_LIGHT)])
        
        # Configure Entry styles
        style.configure('TEntry',
                       background=DarkTheme.ENTRY_BG,
                       foreground=DarkTheme.ENTRY_FG,
                       borderwidth=1,
                       insertcolor=DarkTheme.FG_LIGHT,
                       relief='solid',
                       fieldbackground=DarkTheme.ENTRY_BG)
        style.map('TEntry',
                 focuscolor=[('!focus', DarkTheme.BORDER_COLOR)],
                 bordercolor=[('focus', DarkTheme.ACCENT_BLUE)])
        
        # Configure Treeview styles
        style.configure('Treeview',
                       background=DarkTheme.BG_LIGHT,
                       foreground=DarkTheme.FG_NORMAL,
                       rowheight=25,
                       borderwidth=1,
                       font=('Consolas', 9),
                       fieldbackground=DarkTheme.BG_LIGHT)
        style.configure('Treeview.Heading',
                       background=DarkTheme.BG_DARKER,
                       foreground=DarkTheme.FG_LIGHT,
                       borderwidth=1,
                       relief='solid',
                       font=('Segoe UI', 9, 'bold'))
        style.map('Treeview',
                 background=[('selected', DarkTheme.SELECTION_BG)],
                 foreground=[('selected', DarkTheme.SELECTION_FG)])
        style.map('Treeview.Heading',
                 background=[('active', DarkTheme.BUTTON_HOVER)])
        
        # Configure Notebook styles
        style.configure('TNotebook',
                       background=DarkTheme.BG_DARK,
                       borderwidth=1,
                       tabposition='n')
        style.configure('TNotebook.Tab',
                       background=DarkTheme.BG_LIGHT,
                       foreground=DarkTheme.FG_NORMAL,
                       padding=[15, 8],
                       font=('Segoe UI', 9))
        style.map('TNotebook.Tab',
                 background=[('selected', DarkTheme.BG_DARK),
                           ('active', DarkTheme.BUTTON_HOVER)],
                 foreground=[('selected', DarkTheme.ACCENT_BLUE)])
        
        # Configure PanedWindow styles
        style.configure('TPanedwindow',
                       background=DarkTheme.BG_DARK,
                       borderwidth=1,
                       relief='solid')
        
        # Configure Scrollbar styles
        style.configure('Vertical.TScrollbar',
                       background=DarkTheme.BG_LIGHT,
                       troughcolor=DarkTheme.BG_DARKER,
                       borderwidth=1,
                       arrowcolor=DarkTheme.FG_NORMAL,
                       darkcolor=DarkTheme.BG_LIGHT,
                       lightcolor=DarkTheme.BG_LIGHT)
        style.configure('Horizontal.TScrollbar',
                       background=DarkTheme.BG_LIGHT,
                       troughcolor=DarkTheme.BG_DARKER,
                       borderwidth=1,
                       arrowcolor=DarkTheme.FG_NORMAL,
                       darkcolor=DarkTheme.BG_LIGHT,
                       lightcolor=DarkTheme.BG_LIGHT)
        
        # Configure readonly Entry style for tags
        style.configure('Readonly.TEntry',
                       background=DarkTheme.BG_DARKER,
                       foreground=DarkTheme.ACCENT_YELLOW,
                       borderwidth=1,
                       relief='solid',
                       fieldbackground=DarkTheme.BG_DARKER)
    
    def show_welcome_message(self):
        """Show welcome dialog similar to simplified map editor"""
        # Create a custom dark-themed message box
        welcome_window = tk.Toplevel(self.root)
        welcome_window.title("Welcome to AVATAR XML File Editor")
        welcome_window.geometry("600x500")
        welcome_window.configure(bg=DarkTheme.BG_DARK)
        welcome_window.resizable(False, False)
        welcome_window.transient(self.root)
        welcome_window.grab_set()
        
        # Center the window
        welcome_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 450,
            self.root.winfo_rooty() + 275
        ))
        
        # Main frame
        main_frame = ttk.Frame(welcome_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🎮 AVATAR XML File Editor",
                               font=('Segoe UI', 26, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """Welcome to Jasper's XML Editor!

        🎮 Designed specifically for AVATAR game file editing

        What you can do:
        - Load .game.xml, .xml, and .rml game files
        - Convert binary formats to editable XML
        - Browse file structure with the interactive tree view
        - Edit XML content directly in the source tab
        - Search through large files with Ctrl+F
        - Validate XML syntax in real-time
        - Save back to binary format for the game

        ✨ Features a modern dark theme and intuitive interface
        🔧 Powered by Gibbed Dunia conversion tools

        Ready to start modding? Click 'Select XML File' to begin!"""

        
        desc_label = ttk.Label(main_frame, 
                              text=desc_text,
                              font=('Segoe UI', 10),
                              justify=tk.LEFT)
        desc_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = ttk.Button(main_frame, 
                              text="Get Started",
                              command=welcome_window.destroy,
                              width=15)
        ok_button.pack(pady=10)
        
        # Focus and wait
        ok_button.focus_set()
        welcome_window.wait_window()
    
    def create_menu(self):
        """Create the menu bar with dark theme styling"""
        menubar = tk.Menu(self.root, 
                         bg=DarkTheme.MENU_BG, 
                         fg=DarkTheme.MENU_FG,
                         activebackground=DarkTheme.SELECTION_BG,
                         activeforeground=DarkTheme.SELECTION_FG,
                         font=('Segoe UI', 9))
        self.root.config(menu=menubar)
        
        # File menu
        file_menu = tk.Menu(menubar, tearoff=0, 
                           bg=DarkTheme.MENU_BG, 
                           fg=DarkTheme.MENU_FG,
                           selectcolor=DarkTheme.ACCENT_BLUE, 
                           activebackground=DarkTheme.SELECTION_BG,
                           activeforeground=DarkTheme.SELECTION_FG,
                           font=('Segoe UI', 9))
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Select XML File", command=self.open_file, 
                             accelerator="Ctrl+O")
        file_menu.add_separator()
        file_menu.add_command(label="Save", command=self.save_file, 
                             accelerator="Ctrl+S")
        file_menu.add_command(label="Save As Binary...", command=self.save_as_binary)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)
        
        # Edit menu
        edit_menu = tk.Menu(menubar, tearoff=0, 
                           bg=DarkTheme.MENU_BG, 
                           fg=DarkTheme.MENU_FG,
                           selectcolor=DarkTheme.ACCENT_BLUE, 
                           activebackground=DarkTheme.SELECTION_BG,
                           activeforeground=DarkTheme.SELECTION_FG,
                           font=('Segoe UI', 9))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Expand All", command=self.expand_all)
        edit_menu.add_command(label="Collapse All", command=self.collapse_all)
        edit_menu.add_separator()
        edit_menu.add_command(label="Find...", command=self.show_find_dialog, 
                             accelerator="Ctrl+F")
        
        # Tools menu
        tools_menu = tk.Menu(menubar, tearoff=0, 
                            bg=DarkTheme.MENU_BG, 
                            fg=DarkTheme.MENU_FG,
                            selectcolor=DarkTheme.ACCENT_BLUE, 
                            activebackground=DarkTheme.SELECTION_BG,
                            activeforeground=DarkTheme.SELECTION_FG,
                            font=('Segoe UI', 9))
        menubar.add_cascade(label="Tools", menu=tools_menu)
        tools_menu.add_command(label="Convert to Readable", command=self.convert_to_readable)
        tools_menu.add_command(label="Validate XML", command=self.validate_xml)
        
        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0, 
                           bg=DarkTheme.MENU_BG, 
                           fg=DarkTheme.MENU_FG,
                           selectcolor=DarkTheme.ACCENT_BLUE, 
                           activebackground=DarkTheme.SELECTION_BG,
                           activeforeground=DarkTheme.SELECTION_FG,
                           font=('Segoe UI', 9))
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self.show_about)
        
        # Bind keyboard shortcuts
        self.root.bind('<Control-o>', lambda e: self.open_file())
        self.root.bind('<Control-s>', lambda e: self.save_file())
        self.root.bind('<Control-f>', lambda e: self.show_find_dialog())

        # Update menu
        update_menu = tk.Menu(menubar, tearoff=0, 
                            bg=DarkTheme.MENU_BG, 
                            fg=DarkTheme.MENU_FG,
                            selectcolor=DarkTheme.ACCENT_BLUE, 
                            activebackground=DarkTheme.SELECTION_BG,
                            activeforeground=DarkTheme.SELECTION_FG,
                            font=('Segoe UI', 9))
        menubar.add_cascade(label="Update", menu=update_menu)
        update_menu.add_command(label="Check for Updates", command=self.check_for_updates)
        update_menu.add_command(label="View Changelog", command=self.view_changelog)
        update_menu.add_command(label="Download Latest", command=self.download_latest)
    
    def check_for_updates(self):
        """Check for updates and download if available"""
        try:
            import urllib.request
            import os
            import zipfile
            import shutil
            import subprocess
            import sys
            
            # Your current version
            current_version = "2.0"
            latest_version = "2.0"  # Update this manually when you release new versions
            
            if latest_version > current_version:
                message = f"""A new version is available!

    Current version: {current_version}
    Latest version: {latest_version}

    This will download and install the update automatically.
    The application will restart after the update.

    Would you like to download and install now?"""
                
                result = self.show_custom_messagebox_with_result(
                    "Update Available",
                    message,
                    "info"
                )
                
                if result:
                    self.download_and_install_update()
            else:
                self.show_custom_messagebox(
                    "Up to Date",
                    f"You're running the latest version ({current_version})!",
                    "info"
                )
                
        except Exception as e:
            self.show_custom_messagebox(
                "Update Error",
                f"Error checking for updates:\n{str(e)}",
                "error"
            )

    def download_and_install_update(self):
        """Download and install the update"""
        try:
            import urllib.request
            import os
            import zipfile
            import tempfile
            import shutil
            import subprocess
            import sys
            
            # Show downloading message
            self.status_var.set("Downloading update...")
            self.root.update()
            
            # Download URL - update this with each new release
            download_url = "https://github.com/JasperZebra/AVATAR-.game.xml-File-Editor/releases/download/V2.0/AVATAR_XML_File_Editor_V2.0.zip"
            
            # Create temp directory
            temp_dir = tempfile.mkdtemp()
            zip_path = os.path.join(temp_dir, "update.zip")
            
            # Download the file
            urllib.request.urlretrieve(download_url, zip_path)
            
            self.status_var.set("Extracting update...")
            self.root.update()
            
            # Extract the zip to temp directory
            extract_dir = os.path.join(temp_dir, "extracted")
            with zipfile.ZipFile(zip_path, 'r') as zip_ref:
                zip_ref.extractall(extract_dir)
            
            # Get current application directory
            if getattr(sys, 'frozen', False):
                # Running as exe
                current_dir = os.path.dirname(sys.executable)
                current_exe = sys.executable
            else:
                # Running as script
                current_dir = os.path.dirname(os.path.abspath(__file__))
                current_exe = __file__
            
            self.status_var.set("Preparing update...")
            self.root.update()
            
            # Create a batch file that will handle the update after app closes
            batch_script = f'''@echo off
            echo Waiting for application to close...
            timeout /t 5 /nobreak >nul

            echo Installing update...

            REM Copy all files from extracted directory to current directory
            xcopy "{extract_dir}" "{current_dir}" /E /Y /Q /I

            echo Cleaning up...
            REM Clean up temp directory
            rmdir /s /q "{temp_dir}"

            echo Update complete!

            REM Ask if user wants to open new version
            choice /c YN /m "Update installed successfully! Would you like to open the new version (Y/N)?"
            if errorlevel 2 goto end
            if errorlevel 1 goto start

            :start
            REM Find and start the main exe
            if exist "{current_dir}\\AVATAR_XML_File_Editor.exe" (
                start "" "{current_dir}\\AVATAR_XML_File_Editor.exe"
            ) else if exist "{current_dir}\\main.exe" (
                start "" "{current_dir}\\main.exe"
            ) else (
                for %%f in ("{current_dir}\\*.exe") do (
                    start "" "%%f"
                    goto end
                )
            )

            :end
            del "%~f0"
            '''
            
            # Save batch script
            batch_path = os.path.join(temp_dir, "update.bat")
            with open(batch_path, 'w') as f:
                f.write(batch_script)
            
            # Show success message
            self.show_custom_messagebox(
                "Download Complete",
                "Update downloaded successfully!\n\nThe application will now close and update automatically.",
                "info"
            )
            
            # Run batch script and close
            subprocess.Popen([batch_path], shell=True, creationflags=subprocess.CREATE_NEW_CONSOLE)
            
            # Give a moment for the batch to start, then quit
            self.root.after(1000, self.root.quit)
            
        except Exception as e:
            self.show_custom_messagebox(
                "Download Error",
                f"Failed to download update:\n{str(e)}",
                "error"
            )
            self.status_var.set("Update failed")

    def view_changelog(self):
        """Open changelog/releases page"""
        import webbrowser
        webbrowser.open("https://github.com/JasperZebra/AVATAR-.game.xml-File-Editor/releases")

    def download_latest(self):
        """Open download page for latest version"""
        import webbrowser
        webbrowser.open("https://github.com/JasperZebra/AVATAR-.game.xml-File-Editor/releases")

    def create_toolbar(self):
        """Create the modern toolbar with dark theme"""
        # Main toolbar frame with dark background
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # File operations section
        file_frame = ttk.LabelFrame(toolbar_frame, text="File Operations", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Open button with icon-like styling
        open_button = ttk.Button(file_frame, text="📁 Select XML File", 
                                command=self.open_file, width=20)
        open_button.pack(side=tk.LEFT, padx=2)
        
        # Save button
        save_button = ttk.Button(file_frame, text="💾 Save", 
                                command=self.save_file, width=20)
        save_button.pack(side=tk.LEFT, padx=2)
        
        # Conversion section
        conversion_frame = ttk.LabelFrame(toolbar_frame, text="Format Conversion", padding=10)
        conversion_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Convert to readable button
        self.convert_button = ttk.Button(conversion_frame, text="🔄 Convert To Readable", 
                                        command=self.convert_to_readable, width=24)
        self.convert_button.pack(side=tk.LEFT, padx=2)
        
        # Save as binary button
        self.save_binary_button = ttk.Button(conversion_frame, text="💽 Save To Binary", 
                                            command=self.save_as_binary, width=24)
        self.save_binary_button.pack(side=tk.LEFT, padx=2)
        
        # View operations section
        view_frame = ttk.LabelFrame(toolbar_frame, text="View Options", padding=10)
        view_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Expand/Collapse buttons
        ttk.Button(view_frame, text="➕ Expand All", 
                  command=self.expand_all, width=20).pack(side=tk.LEFT, padx=2)
        ttk.Button(view_frame, text="➖ Collapse All", 
                  command=self.collapse_all, width=20).pack(side=tk.LEFT, padx=2)
                
        # Disable buttons if no converter
        if not self.converter.can_convert:
            self.convert_button.config(state=tk.DISABLED)
            self.save_binary_button.config(state=tk.DISABLED)
    
    def create_main_frame(self):
        """Create the main content area with dark theme"""
        # Create main container with padding
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)
        
        # Left panel - XML Tree view with fixed width
        left_panel = ttk.LabelFrame(main_container, text="📁 XML Structure", padding=10, width=300)
        left_panel.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 5))
        left_panel.pack_propagate(False)  # Keep the fixed width
        
        # Tree controls frame
        tree_controls = ttk.Frame(left_panel)
        tree_controls.pack(fill=tk.X, pady=(0, 5))
        
        # File info label
        self.file_info_label = ttk.Label(tree_controls, text="No file loaded", 
                                        font=('Segoe UI', 9, 'italic'))
        self.file_info_label.pack(side=tk.LEFT)
        
        # Tree frame with scrollbars
        tree_frame = ttk.Frame(left_panel)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview with dark theme styling
        self.tree = ttk.Treeview(tree_frame, show='tree')
        
        # Scrollbars for tree
        tree_scrolly = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self.tree.yview)
        tree_scrollx = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=tree_scrolly.set, xscrollcommand=tree_scrollx.set)
        
        # Pack tree and scrollbars
        self.tree.grid(row=0, column=0, sticky="nsew")
        tree_scrolly.grid(row=0, column=1, sticky="ns")
        tree_scrollx.grid(row=1, column=0, sticky="ew")
        tree_frame.grid_rowconfigure(0, weight=1)
        tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind tree events
        self.tree.bind('<<TreeviewSelect>>', self.on_tree_select)
        
        # Right panel - Element details with tabs (takes remaining space)
        right_panel = ttk.LabelFrame(main_container, text="🔧 XML Details", padding=10)
        right_panel.pack(side=tk.RIGHT, fill=tk.BOTH, expand=True)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Bind tab change event to handle source sync
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)
                
        # XML Source tab
        source_frame = ttk.Frame(self.notebook)
        self.notebook.add(source_frame, text="XML Source")
        
        self.create_source_tab(source_frame)
        
        # Statistics tab
        stats_frame = ttk.Frame(self.notebook)
        self.notebook.add(stats_frame, text="Statistics")
        
        self.create_statistics_tab(stats_frame)

    def create_properties_tab(self, parent):
        """Create the properties tab for element editing"""
        # Element information section
        info_section = ttk.LabelFrame(parent, text="Element Information", padding=10)
        info_section.pack(fill=tk.X, pady=(0, 10))
        
        # Tag name
        tag_frame = ttk.Frame(info_section)
        tag_frame.pack(fill=tk.X, pady=2)
        ttk.Label(tag_frame, text="Tag:", width=12).pack(side=tk.LEFT)
        self.tag_var = tk.StringVar()
        tag_entry = ttk.Entry(tag_frame, textvariable=self.tag_var, state="readonly",
                             font=('Consolas', 10, 'bold'), style='Readonly.TEntry')
        tag_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Text content
        text_frame = ttk.Frame(info_section)
        text_frame.pack(fill=tk.X, pady=2)
        ttk.Label(text_frame, text="Text:", width=12).pack(side=tk.LEFT)
        self.text_var = tk.StringVar()
        text_entry = ttk.Entry(text_frame, textvariable=self.text_var, font=('Consolas', 10))
        text_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(5, 0))
        
        # Bind text change events
        text_entry.bind('<KeyRelease>', self.on_text_change)
        text_entry.bind('<FocusOut>', self.on_text_change)
        self.text_var.trace('w', self.on_text_var_change)
        
        # Attributes section
        attr_section = ttk.LabelFrame(parent, text="Attributes", padding=10)
        attr_section.pack(fill=tk.BOTH, expand=True)
        
        # Attributes toolbar
        attr_toolbar = ttk.Frame(attr_section)
        attr_toolbar.pack(fill=tk.X, pady=(0, 5))
        
        ttk.Button(attr_toolbar, text="➕ Add", 
                  command=self.add_attribute).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(attr_toolbar, text="✏️ Edit", 
                  command=self.edit_selected_attribute).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(attr_toolbar, text="🗑️ Delete", 
                  command=self.delete_attribute).pack(side=tk.LEFT, padx=(0, 5))
        
        # Attributes frame
        attr_tree_frame = ttk.Frame(attr_section)
        attr_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        # Attributes treeview with dark theme styling
        self.attr_tree = ttk.Treeview(attr_tree_frame, columns=("value",), height=12)
        self.attr_tree.heading("#0", text="Attribute Name")
        self.attr_tree.heading("value", text="Value")
        self.attr_tree.column("#0", width=180, minwidth=100)
        self.attr_tree.column("value", width=300, minwidth=150)
        
        # Attributes scrollbar
        attr_scrolly = ttk.Scrollbar(attr_tree_frame, orient=tk.VERTICAL, 
                                    command=self.attr_tree.yview)
        self.attr_tree.configure(yscrollcommand=attr_scrolly.set)
        
        self.attr_tree.grid(row=0, column=0, sticky="nsew")
        attr_scrolly.grid(row=0, column=1, sticky="ns")
        attr_tree_frame.grid_rowconfigure(0, weight=1)
        attr_tree_frame.grid_columnconfigure(0, weight=1)
        
        # Bind attribute editing
        self.attr_tree.bind('<Double-1>', self.edit_attribute)
    
    def create_source_tab(self, parent):
        """Create the XML source view tab with dark theme and editing capabilities"""
        source_frame = ttk.Frame(parent)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # NEW: Search bar frame
        search_frame = ttk.Frame(source_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))
        
        # Search controls
        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))
        
        self.search_var = tk.StringVar()
        self.search_entry = ttk.Entry(search_frame, textvariable=self.search_var, width=30)
        self.search_entry.pack(side=tk.LEFT, padx=(0, 5))
        
        # Search buttons
        ttk.Button(search_frame, text="Find", command=self.find_text, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Next", command=self.find_next, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Previous", command=self.find_previous, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Clear", command=self.clear_search, width=8).pack(side=tk.LEFT, padx=2)
        
        # Case sensitive checkbox
        self.case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="Case sensitive", 
                    variable=self.case_sensitive_var).pack(side=tk.LEFT, padx=(10, 0))
        
        # Search result label
        self.search_result_label = ttk.Label(search_frame, text="", foreground=DarkTheme.ACCENT_BLUE)
        self.search_result_label.pack(side=tk.RIGHT)
        
        # Source text widget with scrollbars and dark theme - MADE EDITABLE
        text_frame = ttk.Frame(source_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)
        
        self.source_text = tk.Text(text_frame, wrap=tk.NONE, 
                                font=('Consolas', 10),
                                bg=DarkTheme.BG_LIGHT, 
                                fg=DarkTheme.FG_NORMAL, 
                                insertbackground=DarkTheme.ACCENT_BLUE,
                                selectbackground=DarkTheme.SELECTION_BG,
                                selectforeground=DarkTheme.SELECTION_FG,
                                borderwidth=1,
                                relief='solid',
                                state=tk.NORMAL)
        
        # Configure search highlighting tag with more visible colors
        self.source_text.tag_configure("search_highlight", 
                                    background="#000000",  # Bright yellow
                                    foreground="#000000")  # Black text
        self.source_text.tag_configure("current_match", 
                                    background="#ffffff",  # Bright orange  
                                    foreground="#ffffff")  # White text
        
        # Bind text modification events
        self.source_text.bind('<KeyRelease>', self.on_source_text_change)
        self.source_text.bind('<Button-1>', self.on_source_text_change)
        self.source_text.bind('<Control-v>', self.on_source_text_change)
        
        # NEW: Bind Ctrl+F for search
        self.source_text.bind('<Control-f>', self.focus_search)
        self.source_text.bind('<F3>', lambda e: self.find_next())
        self.source_text.bind('<Shift-F3>', lambda e: self.find_previous())
        self.source_text.bind('<Escape>', self.clear_search)
        
        # Bind Enter in search box
        self.search_entry.bind('<Return>', lambda e: self.find_next())
        self.search_entry.bind('<Escape>', self.clear_search)
        
        # Scrollbars for source text
        source_scrolly = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, 
                                    command=self.source_text.yview)
        source_scrollx = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL, 
                                    command=self.source_text.xview)
        self.source_text.configure(yscrollcommand=source_scrolly.set, 
                                xscrollcommand=source_scrollx.set)
        
        self.source_text.grid(row=0, column=0, sticky="nsew")
        source_scrolly.grid(row=0, column=1, sticky="ns")
        source_scrollx.grid(row=1, column=0, sticky="ew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)
        
        # Source controls
        source_controls = ttk.Frame(source_frame)
        source_controls.pack(fill=tk.X, pady=(10, 0))
        
        ttk.Button(source_controls, text="🔄 Refresh from Tree", 
                command=self.refresh_source_view).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="📋 Copy All", 
                command=self.copy_source).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="✅ Apply Changes to Tree", 
                command=self.apply_source_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="🔍 Validate XML", 
                command=self.validate_source_xml).pack(side=tk.LEFT, padx=(0, 5))
        
        # Initialize search variables
        self.search_matches = []
        self.current_match_index = -1

    # NEW SEARCH METHODS - Add these to your GameXMLEditor class

    def focus_search(self, event=None):
        """Focus on the search entry box"""
        if hasattr(self, 'search_entry'):
            self.search_entry.focus_set()
            self.search_entry.select_range(0, tk.END)
        return "break"  # Prevent default Ctrl+F behavior

    def find_text(self):
        """Find all occurrences of search text"""
        search_term = self.search_var.get()
        if not search_term:
            self.clear_search()
            return
        
        # Clear previous highlights
        self.source_text.tag_remove("search_highlight", "1.0", tk.END)
        self.source_text.tag_remove("current_match", "1.0", tk.END)
        
        # Get all text content
        content = self.source_text.get("1.0", tk.END)
        
        # Search options
        if not self.case_sensitive_var.get():
            content_lower = content.lower()
            search_term_lower = search_term.lower()
        else:
            content_lower = content
            search_term_lower = search_term
        
        # Find all matches
        self.search_matches = []
        start = 0
        while True:
            pos = content_lower.find(search_term_lower, start)
            if pos == -1:
                break
            
            # Convert position to line.column format
            lines_before = content[:pos].count('\n')
            if lines_before == 0:
                col = pos
            else:
                last_newline = content.rfind('\n', 0, pos)
                col = pos - last_newline - 1
            
            start_pos = f"{lines_before + 1}.{col}"
            end_pos = f"{lines_before + 1}.{col + len(search_term)}"
            
            self.search_matches.append((start_pos, end_pos))
            start = pos + 1
        
        # Highlight all matches
        for start_pos, end_pos in self.search_matches:
            self.source_text.tag_add("search_highlight", start_pos, end_pos)
        
        # Update result display
        if self.search_matches:
            self.current_match_index = 0
            self.highlight_current_match()
            self.search_result_label.config(text=f"{len(self.search_matches)} matches found")
        else:
            self.search_result_label.config(text="No matches found")
            self.current_match_index = -1

    def find_next(self):
        """Find next occurrence"""
        if not self.search_matches:
            self.find_text()
            return
        
        if self.search_matches:
            self.current_match_index = (self.current_match_index + 1) % len(self.search_matches)
            self.highlight_current_match()

    def find_previous(self):
        """Find previous occurrence"""
        if not self.search_matches:
            self.find_text()
            return
        
        if self.search_matches:
            self.current_match_index = (self.current_match_index - 1) % len(self.search_matches)
            self.highlight_current_match()

    def highlight_current_match(self):
        """Highlight the current match and scroll to it"""
        if self.current_match_index >= 0 and self.current_match_index < len(self.search_matches):
            # Remove previous current match highlight
            self.source_text.tag_remove("current_match", "1.0", tk.END)
            
            # Get current match position
            start_pos, end_pos = self.search_matches[self.current_match_index]
            
            # Highlight current match
            self.source_text.tag_add("current_match", start_pos, end_pos)
            
            # Scroll to current match
            self.source_text.see(start_pos)
            
            # Update result label
            self.search_result_label.config(
                text=f"Match {self.current_match_index + 1} of {len(self.search_matches)}"
            )

    def clear_search(self, event=None):
        """Clear search highlights and results"""
        if hasattr(self, 'source_text'):
            self.source_text.tag_remove("search_highlight", "1.0", tk.END)
            self.source_text.tag_remove("current_match", "1.0", tk.END)
        
        if hasattr(self, 'search_var'):
            self.search_var.set("")
        
        if hasattr(self, 'search_result_label'):
            self.search_result_label.config(text="")
        
        self.search_matches = []
        self.current_match_index = -1
        
        return "break"  # Prevent default Escape behavior
    
    def create_statistics_tab(self, parent):
        """Create the statistics tab with dark theme"""
        stats_container = ttk.Frame(parent)
        stats_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # File statistics
        file_stats = ttk.LabelFrame(stats_container, text="File Statistics", padding=10)
        file_stats.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_file_size = ttk.Label(file_stats, text="File size: Not loaded")
        self.stats_file_size.pack(anchor=tk.W)
        
        self.stats_last_modified = ttk.Label(file_stats, text="Last modified: Not loaded")
        self.stats_last_modified.pack(anchor=tk.W)
        
        # Element statistics
        element_stats = ttk.LabelFrame(stats_container, text="Element Statistics", padding=10)
        element_stats.pack(fill=tk.X, pady=(0, 10))
        
        self.stats_total_elements = ttk.Label(element_stats, text="Total elements: 0")
        self.stats_total_elements.pack(anchor=tk.W)
        
        self.stats_total_attributes = ttk.Label(element_stats, text="Total attributes: 0")
        self.stats_total_attributes.pack(anchor=tk.W)
        
        self.stats_max_depth = ttk.Label(element_stats, text="Maximum depth: 0")
        self.stats_max_depth.pack(anchor=tk.W)
        
        # Element types
        types_frame = ttk.LabelFrame(stats_container, text="Element Types", padding=10)
        types_frame.pack(fill=tk.BOTH, expand=True)
        
        # Create treeview for element types with scrollbar frame
        stats_tree_frame = ttk.Frame(types_frame)
        stats_tree_frame.pack(fill=tk.BOTH, expand=True)
        
        self.stats_tree = ttk.Treeview(stats_tree_frame, columns=("count",), height=10)
        self.stats_tree.heading("#0", text="Element Type")
        self.stats_tree.heading("count", text="Count")
        self.stats_tree.column("#0", width=200)
        self.stats_tree.column("count", width=100)
        
        stats_scrolly = ttk.Scrollbar(stats_tree_frame, orient=tk.VERTICAL, 
                                     command=self.stats_tree.yview)
        self.stats_tree.configure(yscrollcommand=stats_scrolly.set)
        
        self.stats_tree.grid(row=0, column=0, sticky="nsew")
        stats_scrolly.grid(row=0, column=1, sticky="ns")
        stats_tree_frame.grid_rowconfigure(0, weight=1)
        stats_tree_frame.grid_columnconfigure(0, weight=1)
    
    def show_about(self):
        """Show about dialog with dark theme"""
        # Create a custom dark-themed about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("About AVATAR XML Editor")
        about_window.geometry("600x500")
        about_window.configure(bg=DarkTheme.BG_DARK)
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()
        
        # Center the window
        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 500,
            self.root.winfo_rooty() + 300
        ))
        
        # Main frame
        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Title
        title_label = ttk.Label(main_frame, 
                               text="🎮 AVATAR XML Editor",
                               font=('Segoe UI', 26, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(main_frame, 
                                 text="version 2.0",
                                 font=('Segoe UI', 10))
        version_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """A powerful XML editor designed for AVATAR game files.

        Key Features:
        - Open and edit .game.xml, .xml, and .rml files
        - Convert binary game files to readable XML format
        - Live XML source editing with syntax highlighting
        - Tree-based navigation and element management
        - Real-time XML validation and error checking
        - Search functionality with Ctrl+F support
        - Modern dark theme for comfortable editing
        - Integrated Gibbed Dunia conversion tools

        Perfect for modding and analyzing AVATAR game data files.

        Built with Python and tkinter for reliable performance."""        

        desc_label = ttk.Label(main_frame, 
                              text=desc_text,
                              font=('Segoe UI', 10),
                              justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = ttk.Button(main_frame, 
                              text="OK",
                              command=about_window.destroy,
                              width=10)
        ok_button.pack()
        
        # Focus and wait
        ok_button.focus_set()
        about_window.wait_window()
    
    def validate_xml(self):
        """Validate current XML structure"""
        if not self.tree_data:
            self.show_custom_messagebox("No File", "No XML file is currently loaded.", "warning")
            return
        
        try:
            # Basic validation - try to write to string
            ET.tostring(self.tree_data.getroot())
            self.show_custom_messagebox("Validation Result", "XML structure is valid!", "info")
        except Exception as e:
            self.show_custom_messagebox("Validation Error", f"XML validation failed:\n{str(e)}", "error")
    
    def show_custom_messagebox(self, title, message, msg_type="info"):
        """Show a custom dark-themed message box"""
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.configure(bg=DarkTheme.BG_DARK)
        msg_window.resizable(False, False)
        msg_window.transient(self.root)
        msg_window.grab_set()
        
        # Calculate size based on message length
        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)
        height = max(200, len(lines) * 30 + 150)
        msg_window.geometry(f"{width}x{height}")
        
        # Center the window
        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Main frame
        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and title
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Choose icon based on type
        if msg_type == "error":
            icon = "❌"
            color = DarkTheme.ACCENT_RED
        elif msg_type == "warning":
            icon = "⚠️"
            color = DarkTheme.ACCENT_ORANGE
        else:
            icon = "ℹ️"
            color = DarkTheme.ACCENT_BLUE
        
        icon_label = ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18))
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(icon_frame, text=title, 
                            font=('Segoe UI', 14, 'bold'),
                            foreground=color)
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Message
        msg_label = ttk.Label(main_frame, text=message,
                            font=('Segoe UI', 11),
                            justify=tk.LEFT,
                            wraplength=width-60)
        msg_label.pack(pady=(0, 20))
        
        # OK button
        ok_button = ttk.Button(main_frame, 
                            text="OK",
                            command=msg_window.destroy,
                            width=15)
        ok_button.pack()
        
        # Focus and wait
        ok_button.focus_set()
        msg_window.wait_window()

    def open_file(self):
        """Select a binary .xml file to convert and make readable!"""
        filetypes = [
            ("Game XML files", "*.game.xml"),
            ("XML files", "*.xml"),
            ("RML files", "*.rml"),
            ("All supported files", "*.game.xml;*.xml;*.rml"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Game XML/RML File",
            filetypes=filetypes
        )
        
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Load and display a .game.xml file with enhanced error handling"""
        try:
            # Reset modification flags
            self.source_modified = False
            
            # Determine if we need to convert based on file extension and format
            needs_conversion = False
            base, ext = os.path.splitext(filename)
            
            if ext == '.rml':
                # RML files always need conversion
                needs_conversion = True
            else:
                # Check if other files are in readable format
                needs_conversion = not self.converter.is_file_xml_format(filename)
            
            if needs_conversion:
                # Ask user if they want to convert using custom messagebox
                result = self.show_custom_messagebox_with_result(
                    "Binary Format Detected",
                    f"This {ext} file appears to be in binary format.\n\n"
                    "Would you like to convert it to readable XML format?",
                    "question"
                )
                
                if result:
                    success, message = self.converter.convert_to_readable(filename)
                    if not success:
                        self.show_custom_messagebox("Conversion Failed", message, "error")
                        return
                    self.show_custom_messagebox("Conversion Successful", message, "info")
                    
                    # For .rml files, we need to load the generated .xml file
                    if ext == '.rml':
                        xml_filename = base + '.xml'
                        if os.path.exists(xml_filename):
                            filename = xml_filename
                        else:
                            self.show_custom_messagebox("Error", "Converted XML file not found", "error")
                            return
                else:
                    self.show_custom_messagebox("Cannot Edit",
                                            "Cannot edit binary format files. Please convert first.",
                                            "warning")
                    return
            
            # Parse the XML file
            self.tree_data = ET.parse(filename)
            self.current_file = filename
            self.is_modified = False
            
            # Update tree display
            self.update_tree_display()
            
            # Update file info
            self.file_info_label.config(text=f"📄 {os.path.basename(filename)}")
            
            # Update window title
            self.root.title(f"AVATAR XML File Editor | Made By: Jasper_Zebra | version 2.0 | Current XML File Loaded: {os.path.basename(filename)}")
            self.status_var.set(f"Loaded: {filename}")
            
            # Update statistics
            self.update_statistics()
            
            # Update source view
            self.refresh_source_view()
            
            # Clear modified indicator
            self.modified_indicator.config(text="")
            
        except Exception as e:
            self.show_custom_messagebox("Error", f"Failed to load file:\n{str(e)}", "error")

    def create_status_bar(self):
        """Create modern status bar with dark theme"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)
        
        # Status text
        self.status_var = tk.StringVar()
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                relief=tk.SUNKEN, font=('Segoe UI', 9))
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)
        
        # Add file status indicators
        self.modified_indicator = ttk.Label(status_frame, text="", 
                                           font=('Segoe UI', 9, 'bold'))
        self.modified_indicator.pack(side=tk.RIGHT, padx=(10, 0))

    def on_tab_changed(self, event):
        """Handle tab change events to sync data between tabs"""
        try:
            current_tab = self.notebook.tab(self.notebook.select(), "text")
            
            # If switching TO the XML Source tab, refresh it with current tree data
            if current_tab == "XML Source" and not self.updating_source:
                self.refresh_source_view()
            
            # If switching FROM the XML Source tab and it was modified, ask to apply changes
            elif self.source_modified and hasattr(self, 'previous_tab') and self.previous_tab == "XML Source":
                result = self.show_custom_messagebox_with_yesnocancel(
                    "Source Modified", 
                    "The XML source has been modified. Do you want to apply the changes to the tree?",
                    "question"
                )
                
                if result == "yes":  # Yes - apply changes
                    if self.apply_source_changes():
                        self.source_modified = False
                elif result == "no":  # No - discard changes
                    self.source_modified = False
                    self.refresh_source_view()  # Reload from tree
                else:  # Cancel - go back to source tab
                    # Switch back to source tab
                    for i in range(self.notebook.index("end")):
                        if self.notebook.tab(i, "text") == "XML Source":
                            self.notebook.select(i)
                            break
                    return
            
            # Store current tab for next time
            self.previous_tab = current_tab
            
        except Exception as e:
            print(f"Error in tab change handler: {e}")

    def show_custom_messagebox_with_yesnocancel(self, title, message, msg_type="info"):
        """Show a custom dark-themed message box with Yes/No/Cancel buttons"""
        result = ["cancel"]  # Default to cancel
        
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.configure(bg=DarkTheme.BG_DARK)
        msg_window.resizable(False, False)
        msg_window.transient(self.root)
        msg_window.grab_set()
        
        # Calculate size based on message length
        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)
        height = max(200, len(lines) * 30 + 150)
        msg_window.geometry(f"{width}x{height}")
        
        # Center the window
        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Main frame
        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and title
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Choose icon based on type
        if msg_type == "error":
            icon = "❌"
            color = DarkTheme.ACCENT_RED
        elif msg_type == "warning":
            icon = "⚠️"
            color = DarkTheme.ACCENT_ORANGE
        elif msg_type == "question":
            icon = "❓"
            color = DarkTheme.ACCENT_BLUE
        else:
            icon = "ℹ️"
            color = DarkTheme.ACCENT_BLUE
        
        icon_label = ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18))
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(icon_frame, text=title, 
                            font=('Segoe UI', 14, 'bold'),
                            foreground=color)
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Message
        msg_label = ttk.Label(main_frame, text=message,
                            font=('Segoe UI', 11),
                            justify=tk.LEFT,
                            wraplength=width-60)
        msg_label.pack(pady=(0, 20))
        
        # Button frame for Yes/No/Cancel buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        def on_yes():
            result[0] = "yes"
            msg_window.destroy()
            
        def on_no():
            result[0] = "no"
            msg_window.destroy()
            
        def on_cancel():
            result[0] = "cancel"
            msg_window.destroy()
        
        # Yes/No/Cancel buttons
        yes_button = ttk.Button(button_frame, 
                            text="Yes",
                            command=on_yes,
                            width=12)
        yes_button.pack(side=tk.LEFT, padx=5)
        
        no_button = ttk.Button(button_frame, 
                            text="No",
                            command=on_no,
                            width=12)
        no_button.pack(side=tk.LEFT, padx=5)
        
        cancel_button = ttk.Button(button_frame, 
                                text="Cancel",
                                command=on_cancel,
                                width=12)
        cancel_button.pack(side=tk.LEFT, padx=5)
        
        # Focus and wait
        yes_button.focus_set()
        msg_window.wait_window()
        
        return result[0]

    def on_source_text_change(self, event=None):
        """Handle changes to the source text widget"""
        if not self.updating_source and self.tree_data:
            self.source_modified = True
            self.mark_modified()
            self.status_var.set("XML source modified - use 'Apply Changes to Tree' or save to apply")

    def apply_source_changes(self):
        """Apply changes from the source text widget back to the XML tree"""
        try:
            # Get the current source text
            source_content = self.source_text.get(1.0, tk.END).strip()
            
            if not source_content:
                self.show_custom_messagebox("Error", "Source content is empty.", "error")
                return False
            
            # Try to parse the XML
            try:
                # Parse the XML string
                new_root = ET.fromstring(source_content)
                
                # Create a new ElementTree
                new_tree = ET.ElementTree(new_root)
                
                # Replace the current tree data
                self.tree_data = new_tree
                self.source_modified = False
                
                # Update all displays
                self.updating_source = True  # Prevent recursive updates
                try:
                    self.update_tree_display()
                    self.update_statistics()
                    self.refresh_source_view()  # Reformat and re-highlight
                finally:
                    self.updating_source = False
                
                # Clear any selection and update details
                self.clear_element_details()
                
                self.status_var.set("XML source changes applied successfully")
                self.show_custom_messagebox("Success", "XML source changes have been applied to the tree structure.", "info")
                return True
                
            except ET.ParseError as e:
                error_msg = f"XML Parse Error: {str(e)}"
                self.show_custom_messagebox("Parse Error", error_msg, "error")
                self.status_var.set("XML parsing failed - check syntax")
                return False
                
        except Exception as e:
            error_msg = f"Error applying source changes: {str(e)}"
            self.show_custom_messagebox("Error", error_msg, "error")
            return False

    def validate_source_xml(self):
        """Validate the XML syntax in the source text widget"""
        try:
            source_content = self.source_text.get(1.0, tk.END).strip()
            
            if not source_content:
                self.show_custom_messagebox("Validation", "Source content is empty.", "warning")
                return
            
            # Try to parse the XML
            try:
                ET.fromstring(source_content)
                self.show_custom_messagebox("Validation Result", "XML syntax is valid!", "info")
                self.status_var.set("XML validation successful")
            except ET.ParseError as e:
                # Get line and column info if available
                error_info = str(e)
                if hasattr(e, 'lineno') and hasattr(e, 'offset'):
                    error_info += f"\nLine: {e.lineno}, Column: {e.offset}"
                
                self.show_custom_messagebox("Validation Error", f"XML Parse Error:\n{error_info}", "error")
                self.status_var.set("XML validation failed")
                
        except Exception as e:
            self.show_custom_messagebox("Validation Error", f"Error during validation: {str(e)}", "error")

    def save_file(self):
        """Save the current file with enhanced feedback and source sync"""
        if not self.current_file:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return
        
        if not self.tree_data:
            self.show_custom_messagebox("No Data", "No data to save.", "warning")
            return
        
        # If source was modified, apply changes first
        if self.source_modified:
            result = self.show_custom_messagebox_with_result(
                "Source Modified", 
                "The XML source has been modified. Apply changes before saving?",
                "question"
            )
            
            if result:
                if not self.apply_source_changes():
                    return  # Don't save if applying changes failed
            else:
                self.source_modified = False  # User chose to discard source changes
        
        try:
            from config import EDITOR_SETTINGS
            if os.path.exists(self.current_file) and EDITOR_SETTINGS.get("auto_backup", False):
                backup_path = self.current_file + ".backup"
                import shutil
                shutil.copy2(self.current_file, backup_path)
                self.status_var.set(f"Backup created: {os.path.basename(backup_path)}")   

            # Write XML file with pretty formatting
            self.indent_xml(self.tree_data.getroot())
            self.tree_data.write(self.current_file, encoding="utf-8", xml_declaration=True)
            
            # Reset modification status
            self.is_modified = False
            self.source_modified = False
            self.root.title(self.root.title().rstrip(" *"))
            self.modified_indicator.config(text="✓", foreground=DarkTheme.ACCENT_GREEN)
            self.file_info_label.config(text=f"📄 {os.path.basename(self.current_file)}")
            
            # Update statistics and source view
            self.update_statistics()
            self.refresh_source_view()
            
            # Show success message with custom messagebox
            self.show_custom_messagebox("File Saved", f"Successfully saved: {os.path.basename(self.current_file)}", "info")
                        
        except Exception as e:
            self.show_custom_messagebox("Save Error", f"Failed to save file:\n{str(e)}", "error")

    def refresh_source_view(self):
        """Refresh the XML source view with dark theme syntax highlighting"""
        if not self.tree_data:
            self.source_text.delete(1.0, tk.END)
            return
        
        try:
            self.updating_source = True  # Prevent modification detection during refresh
            
            # Pretty print the XML
            self.indent_xml(self.tree_data.getroot())
            xml_str = ET.tostring(self.tree_data.getroot(), 
                                 encoding='unicode', method='xml')
            
            # Add XML declaration
            if not xml_str.startswith('<?xml'):
                xml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str
            
            # Update text widget
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, xml_str)
            
            # Apply dark theme syntax highlighting
            self.apply_dark_highlighting()
            
            # Reset modification flag
            self.source_modified = False
            
        except Exception as e:
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, f"Error generating source view: {str(e)}")
        finally:
            self.updating_source = False

    def update_statistics(self):
        """Update file and element statistics"""
        if not self.tree_data or not self.current_file:
            return
        
        try:
            # File statistics
            if os.path.exists(self.current_file):
                file_size = os.path.getsize(self.current_file)
                size_str = f"{file_size:,} bytes"
                if file_size > 1024:
                    size_str += f" ({file_size/1024:.1f} KB)"
                if file_size > 1024*1024:
                    size_str += f" ({file_size/(1024*1024):.1f} MB)"
                
                self.stats_file_size.config(text=f"File size: {size_str}")
                
                import time
                mod_time = os.path.getmtime(self.current_file)
                mod_str = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(mod_time))
                self.stats_last_modified.config(text=f"Last modified: {mod_str}")
            
            # Element statistics
            root = self.tree_data.getroot()
            element_count = len(list(root.iter()))
            attr_count = sum(len(elem.attrib) for elem in root.iter())
            max_depth = self.calculate_max_depth(root)
            
            # Count element types
            element_types = {}
            for elem in root.iter():
                tag = elem.tag
                element_types[tag] = element_types.get(tag, 0) + 1
            
            # Update labels
            self.stats_total_elements.config(text=f"Total elements: {element_count:,}")
            self.stats_total_attributes.config(text=f"Total attributes: {attr_count:,}")
            self.stats_max_depth.config(text=f"Maximum depth: {max_depth}")
            
            # Update types tree
            self.stats_tree.delete(*self.stats_tree.get_children())
            for tag, count in sorted(element_types.items(), key=lambda x: x[1], reverse=True):
                self.stats_tree.insert("", "end", text=tag, values=(count,))
        
        except Exception as e:
            print(f"Error updating statistics: {e}")
    
    def calculate_max_depth(self, element, current_depth=0):
        """Calculate maximum depth of XML tree"""
        if not list(element):
            return current_depth
        return max(self.calculate_max_depth(child, current_depth + 1) 
                  for child in element)
    
    def apply_dark_highlighting(self):
        """Apply dark theme syntax highlighting to XML source"""
        try:
            # Configure text tags for dark theme highlighting
            self.source_text.tag_configure("tag", foreground=DarkTheme.XML_TAG)
            self.source_text.tag_configure("attr", foreground=DarkTheme.XML_ATTR)
            self.source_text.tag_configure("string", foreground=DarkTheme.XML_STRING)
            self.source_text.tag_configure("comment", foreground=DarkTheme.XML_COMMENT)
            self.source_text.tag_configure("declaration", foreground=DarkTheme.ACCENT_PURPLE)
            
            # Simple pattern matching for highlighting
            content = self.source_text.get(1.0, tk.END)
            lines = content.split('\n')
            
            for i, line in enumerate(lines):
                # Highlight XML declaration
                import re
                for match in re.finditer(r'<\?xml.*?\?>', line):
                    start_pos = f"{i+1}.{match.start()}"
                    end_pos = f"{i+1}.{match.end()}"
                    self.source_text.tag_add("declaration", start_pos, end_pos)
                
                # Highlight XML tags
                for match in re.finditer(r'<[^>]+>', line):
                    start_pos = f"{i+1}.{match.start()}"
                    end_pos = f"{i+1}.{match.end()}"
                    self.source_text.tag_add("tag", start_pos, end_pos)
                
                # Highlight attribute values
                for match in re.finditer(r'="[^"]*"', line):
                    start_pos = f"{i+1}.{match.start()}"
                    end_pos = f"{i+1}.{match.end()}"
                    self.source_text.tag_add("string", start_pos, end_pos)
                
                # Highlight comments
                for match in re.finditer(r'<!--.*?-->', line):
                    start_pos = f"{i+1}.{match.start()}"
                    end_pos = f"{i+1}.{match.end()}"
                    self.source_text.tag_add("comment", start_pos, end_pos)
        
        except Exception as e:
            print(f"Error applying highlighting: {e}")
    
    def copy_source(self):
        """Copy source to clipboard"""
        self.root.clipboard_clear()
        self.root.clipboard_append(self.source_text.get(1.0, tk.END))
        self.status_var.set("XML source copied to clipboard")
    
    def edit_selected_attribute(self):
        """Edit the currently selected attribute"""
        selection = self.attr_tree.selection()
        if not selection:
            self.show_custom_messagebox("No Selection", "Please select an attribute to edit.", "warning")
            return
        
        # Simulate double-click on selected item
        item = selection[0]
        self.edit_attribute(None, item=item)
    
    def update_tree_display(self):
        """Update the tree view with current XML data"""
        # Clear existing tree and element map
        self.tree.delete(*self.tree.get_children())
        self.element_map = {}
        
        if self.tree_data is None:
            return
        
        # Add root element
        root_element = self.tree_data.getroot()
        self.add_element_to_tree("", root_element)
        
        # Expand root by default
        children = self.tree.get_children()
        if children:
            self.tree.item(children[0], open=True)
            self.tree.selection_set(children[0])
            self.tree.focus(children[0])
    
    def add_element_to_tree(self, parent, element):
        """Recursively add elements to the tree view with improved display"""
        # Create display text with better formatting
        display_text = element.tag
        
        # Add attribute count if any
        if element.attrib:
            display_text += f" ({len(element.attrib)} attrs)"
        
        # Add text content preview if any
        if element.text and element.text.strip():
            text_preview = element.text.strip()
            if len(text_preview) > 30:
                text_preview = text_preview[:30] + "..."
            display_text += f" = '{text_preview}'"
        
        # Add child count if any
        child_count = len(list(element))
        if child_count > 0:
            display_text += f" [{child_count} children]"
        
        # Insert item with improved styling
        item_id = self.tree.insert(parent, "end", text=display_text)
        
        # Store element reference in the element map
        self.element_map[item_id] = element
        
        # Add children
        for child in element:
            self.add_element_to_tree(item_id, child)
        
        return item_id
    
    def on_tree_select(self, event):
        """Handle tree selection change with enhanced UI updates"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected element using the element map
        item = selection[0]
        if item in self.element_map:
            element = self.element_map[item]
            self.update_element_details(element)
        else:
            # Clear details if no element found
            self.clear_element_details()
    
    def update_element_details(self, element):
        """Update the element details panel with enhanced information"""
        # Since Properties tab was removed, we'll just update the status bar
        # Update status bar with element info
        attr_count = len(element.attrib)
        child_count = len(list(element))
        text_content = element.text.strip() if element.text else ""
        text_preview = f" | Text: '{text_content[:30]}...'" if text_content else ""
        
        self.status_var.set(f"Selected: {element.tag} | {attr_count} attributes | {child_count} children{text_preview}")

    def clear_element_details(self):
        """Clear the element details panel"""
        self.status_var.set("No element selected")

    def on_text_var_change(self, *args):
        """Handle StringVar changes for text content"""
        self.on_text_change(None)
    
    def on_text_change(self, event):
        """Handle text content change with improved feedback"""
        selection = self.tree.selection()
        if not selection:
            return
        
        # Get selected element and update its text
        item = selection[0]
        if item in self.element_map:
            element = self.element_map[item]
            new_text = self.text_var.get()
            
            # Only update if the text actually changed
            if element.text != new_text:
                element.text = new_text
                self.mark_modified()
                
                # Update tree display immediately
                self.update_tree_item_text(item, element)
                
                # Refresh source view if visible
                current_tab = self.notebook.tab(self.notebook.select(), "text")
                if current_tab == "XML Source":
                    self.refresh_source_view()
    
    def update_tree_item_text(self, item, element):
        """Update tree item display text with enhanced formatting"""
        display_text = element.tag
        
        # Add attribute count
        if element.attrib:
            display_text += f" ({len(element.attrib)} attrs)"
        
        # Add text content preview
        if element.text and element.text.strip():
            text_preview = element.text.strip()
            if len(text_preview) > 30:
                text_preview = text_preview[:30] + "..."
            display_text += f" = '{text_preview}'"
        
        # Add child count
        child_count = len(list(element))
        if child_count > 0:
            display_text += f" [{child_count} children]"
        
        self.tree.item(item, text=display_text)
        
    def refresh_attribute_display(self, element):
        """Refresh the attribute display with enhanced formatting"""
        # Clear and rebuild the attribute tree
        self.attr_tree.delete(*self.attr_tree.get_children())
        
        # Add all attributes with better formatting
        for attr_name, attr_value in sorted(element.attrib.items()):
            # Truncate long values for display
            display_value = str(attr_value)
            if len(display_value) > 50:
                display_value = display_value[:50] + "..."
            
            item_id = self.attr_tree.insert("", "end", text=attr_name, values=(display_value,))
            
            # Add tooltip for long values
            if len(str(attr_value)) > 50:
                self.attr_tree.set(item_id, "value", display_value + " [...]")
        
    def mark_modified(self):
        """Mark the document as modified with visual indicators"""
        if not self.is_modified:
            self.is_modified = True
            current_title = self.root.title()
            if not current_title.endswith("*"):
                self.root.title(current_title + " *")
            
            # Update modified indicator with themed colors
            self.modified_indicator.config(text="●", foreground=DarkTheme.ACCENT_ORANGE)
            
            # Update file info
            if self.current_file:
                self.file_info_label.config(text=f"📄 {os.path.basename(self.current_file)} (modified)")
    
    def save_as_binary(self):
        """Save the file in binary format with enhanced user experience"""
        if not self.current_file:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return
        
        # Show information about the process using custom messagebox instead of standard messagebox
        custom_result = self.show_custom_messagebox_with_result(
            "Save as Binary",
            "This will:\n\n"
            "1. Save the current XML file\n"
            "2. Convert it to binary format\n\n"
            "Continue?",
            "question"
        )
        
        if not custom_result:
            return
        
        # First save as readable XML
        self.save_file()
        
        # Then convert to binary
        success, message = self.converter.save_as_binary(self.current_file)
        
        if success:
            self.show_custom_messagebox("Saved as Binary", message, "info")
            self.status_var.set("Saved in binary format")
        else:
            self.show_custom_messagebox("Save Error", message, "error")

    def show_custom_messagebox_with_result(self, title, message, msg_type="info"):
        """Show a custom dark-themed message box that returns a result"""
        result = [False]  # Use a list to allow modification from inner function
        
        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.configure(bg=DarkTheme.BG_DARK)
        msg_window.resizable(False, False)
        msg_window.transient(self.root)
        msg_window.grab_set()
        
        # Calculate size based on message length - MODIFY THESE VALUES
        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)  # Increased from 300 to 400
        height = max(200, len(lines) * 30 + 150)  # Increased from 150 to 200 and multiplier from 25 to 30
        msg_window.geometry(f"{width}x{height}")
        
        # Center the window
        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))
        
        # Main frame
        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)
        
        # Icon and title
        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))
        
        # Choose icon based on type
        if msg_type == "error":
            icon = "❌"
            color = DarkTheme.ACCENT_RED
        elif msg_type == "warning":
            icon = "⚠️"
            color = DarkTheme.ACCENT_ORANGE
        elif msg_type == "question":
            icon = "❓"
            color = DarkTheme.ACCENT_BLUE
        else:
            icon = "ℹ️"
            color = DarkTheme.ACCENT_BLUE
        
        icon_label = ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18))  # Increased font size from 16 to 18
        icon_label.pack(side=tk.LEFT)
        
        title_label = ttk.Label(icon_frame, text=title, 
                            font=('Segoe UI', 14, 'bold'),  # Increased font size from 12 to 14
                            foreground=color)
        title_label.pack(side=tk.LEFT, padx=(10, 0))
        
        # Message
        msg_label = ttk.Label(main_frame, text=message,
                            font=('Segoe UI', 11),  # Increased font size from 10 to 11
                            justify=tk.LEFT,
                            wraplength=width-60)  # Increased wraplength from width-40 to width-60
        msg_label.pack(pady=(0, 20))
        
        # Button frame for Yes/No buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack()
        
        def on_yes():
            result[0] = True
            msg_window.destroy()
            
        def on_no():
            result[0] = False
            msg_window.destroy()
        
        # Yes/No buttons
        yes_button = ttk.Button(button_frame, 
                            text="Yes",
                            command=on_yes,
                            width=15)  # Increased width from 10 to 15
        yes_button.pack(side=tk.LEFT, padx=10)  # Increased padx from 5 to 10
        
        no_button = ttk.Button(button_frame, 
                            text="No",
                            command=on_no,
                            width=15)  # Increased width from 10 to 15
        no_button.pack(side=tk.LEFT, padx=10)  # Increased padx from 5 to 10
        
        # Focus and wait
        yes_button.focus_set()
        msg_window.wait_window()
        
        return result[0]

    def convert_to_readable(self):
        """Convert current file to readable format with enhanced feedback"""
        if not self.current_file:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return
        
        # Show progress
        self.status_var.set("Converting to readable format...")
        self.root.update()
        
        success, message = self.converter.convert_to_readable(self.current_file)
        
        if success:
            # Reload the file to show readable format
            self.load_file(self.current_file)
            self.show_custom_messagebox("Conversion Successful", message, "info")
        else:
            self.show_custom_messagebox("Conversion Failed", message, "error")
            self.status_var.set("Conversion failed")
    
    def expand_all(self):
        """Expand all tree items with progress indication"""
        self.status_var.set("Expanding all elements...")
        self.root.update()
        
        self.expand_all_recursive("")
        
        self.status_var.set("All elements expanded")
    
    def expand_all_recursive(self, item):
        """Recursively expand tree items"""
        if item:
            self.tree.item(item, open=True)
        
        for child in self.tree.get_children(item):
            self.expand_all_recursive(child)
    
    def collapse_all(self):
        """Collapse all tree items with progress indication"""
        self.status_var.set("Collapsing all elements...")
        self.root.update()
        
        self.collapse_all_recursive("")
        
        self.status_var.set("All elements collapsed")
    
    def collapse_all_recursive(self, item):
        """Recursively collapse tree items"""
        for child in self.tree.get_children(item):
            self.collapse_all_recursive(child)
            self.tree.item(child, open=False)
    
    def show_find_dialog(self):
        """Show find dialog with enhanced search capabilities"""
        if not self.tree_data:
            self.show_custom_messagebox("No File", "No file is currently loaded.", "warning")
            return
        
        dialog = FindDialog(self.root, self.tree)
        self.root.wait_window(dialog.dialog)
    
    def indent_xml(self, elem, level=0):
        """Add pretty-printing indentation to XML"""
        i = "\n" + level * "  "
        if len(elem):
            if not elem.text or not elem.text.strip():
                elem.text = i + "  "
            if not elem.tail or not elem.tail.strip():
                elem.tail = i
            for child in elem:
                self.indent_xml(child, level + 1)
            if not child.tail or not child.tail.strip():
                child.tail = i
        else:
            if level and (not elem.tail or not elem.tail.strip()):
                elem.tail = i
    
    def run(self):
        """Start the application with enhanced window management"""
        # Set minimum window size
        self.root.minsize(800, 600)
        
        # Apply additional dark theme styling to the root window
        self.root.configure(bg=DarkTheme.BG_DARK)
        
        # Center window on screen
        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")
        
        # Handle window closing
        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        
        # Start the main loop
        self.root.mainloop()
    
    def on_closing(self):
        """Handle application closing with unsaved changes check"""
        if self.is_modified or self.source_modified:
            if self.source_modified:
                message = "You have unsaved changes in the XML source. Do you want to save before closing?"
            else:
                message = "You have unsaved changes. Do you want to save before closing?"
            
            result = self.show_custom_messagebox_with_yesnocancel(
                "Unsaved Changes",
                message,
                "warning"
            )
            
            if result == "yes":  # Yes - save and close
                self.save_file()
                if not self.is_modified and not self.source_modified:  # Only close if save was successful
                    self.root.destroy()
            elif result == "no":  # No - close without saving
                self.root.destroy()
            # Cancel - do nothing, keep window open
        else:
            self.root.destroy()