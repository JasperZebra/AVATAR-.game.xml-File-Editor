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


class CloseableNotebook(ttk.Notebook):
    """A ttk.Notebook subclass with × close buttons on each tab."""

    __initialized = False
    _images = ()

    def __init__(self, *args, **kwargs):
        if not CloseableNotebook.__initialized:
            self._initialize_custom_style()
            CloseableNotebook.__initialized = True
        kwargs.setdefault("style", "CloseableNotebook")
        super().__init__(*args, **kwargs)
        self._active = None
        self._closed_tab = None
        self.bind("<ButtonPress-1>", self._on_btn_press, True)
        self.bind("<ButtonRelease-1>", self._on_btn_release)

    def _initialize_custom_style(self):
        style = ttk.Style()
        # Build close-button images programmatically (avoids tiny GIF issues)
        CloseableNotebook._images = (
            CloseableNotebook._draw_close_image(
                "img_nb_close", "#aaaaaa", "#484848"),         # dim × on subtle box
            CloseableNotebook._draw_close_image(
                "img_nb_close_active", "#ffffff", "#606060"),  # white × on lighter box
            CloseableNotebook._draw_close_image(
                "img_nb_close_pressed", "#ffffff", "#993333"), # white × on red box
        )

        style.element_create("close", "image", "img_nb_close",
                             ("active", "pressed", "!disabled", "img_nb_close_pressed"),
                             ("active", "!disabled", "img_nb_close_active"),
                             border=4, sticky='')

        style.layout("CloseableNotebook", [
            ("CloseableNotebook.client", {"sticky": "nswe"})
        ])
        style.layout("CloseableNotebook.Tab", [
            ("CloseableNotebook.tab", {
                "sticky": "nswe",
                "children": [
                    ("CloseableNotebook.padding", {
                        "side": "top",
                        "sticky": "nswe",
                        "children": [
                            ("CloseableNotebook.focus", {
                                "side": "top",
                                "sticky": "nswe",
                                "children": [
                                    ("CloseableNotebook.label", {"side": "left", "sticky": 'w'}),
                                    ("close", {"side": "left", "sticky": ''}),
                                ]
                            })
                        ]
                    })
                ]
            })
        ])

        style.configure("CloseableNotebook",
                        background=DarkTheme.BG_DARK,
                        borderwidth=1,
                        tabposition='nw')
        style.configure("CloseableNotebook.Tab",
                        background=DarkTheme.BG_LIGHT,
                        foreground=DarkTheme.FG_NORMAL,
                        padding=[8, 6],   # tight left padding so text sits left
                        anchor='w',       # left-align the label text
                        font=('Segoe UI', 9))
        style.map("CloseableNotebook.Tab",
                  background=[('selected', DarkTheme.BG_DARK),
                              ('active', DarkTheme.BUTTON_HOVER)],
                  foreground=[('selected', DarkTheme.ACCENT_BLUE)])

    @staticmethod
    def _draw_close_image(name, x_color, box_color, box_size=16, gap=10):
        """Draw a close-button PhotoImage.

        The image is (gap + box_size) pixels wide:
          - left `gap` columns are filled with DarkTheme.BG_DARK so they are
            invisible against the selected-tab background, creating space
            between the filename label and the × box.
          - the remaining `box_size` columns contain the coloured × button.
        """
        total_w = gap + box_size
        img = tk.PhotoImage(name=name, width=total_w, height=box_size)

        # Left gap strip — use the selected-tab background so it is invisible
        gap_row = '{' + ' '.join([DarkTheme.BG_DARK] * gap) + '}'
        for y in range(box_size):
            img.put(gap_row, (0, y))

        # Right box strip — coloured button background
        box_row = '{' + ' '.join([box_color] * box_size) + '}'
        for y in range(box_size):
            img.put(box_row, (gap, y))

        # Draw × diagonals inside the box (margin 3 px from box edges)
        m = 3
        for i in range(m, box_size - m):
            img.put(x_color, to=(gap + i, i))                    # main  (\)
            img.put(x_color, to=(gap + i, box_size - 1 - i))     # anti  (/)
        # Thicken each diagonal by one extra pixel
        for i in range(m, box_size - m - 1):
            img.put(x_color, to=(gap + i + 1, i))                # main  thicken
            img.put(x_color, to=(gap + i + 1, box_size - 1 - i)) # anti  thicken
        return img

    def _on_btn_press(self, event):
        x, y = event.x, event.y
        elem = self.identify(x, y)
        if "close" in elem:
            try:
                index = self.index("@%d,%d" % (x, y))
                self._active = index
            except tk.TclError:
                pass

    def _on_btn_release(self, event):
        x, y = event.x, event.y
        if self._active is not None:
            try:
                index = self.index("@%d,%d" % (x, y))
            except tk.TclError:
                self._active = None
                return

            elem = self.identify(x, y)
            if "close" in elem and self._active == index:
                tabs = self.tabs()
                if index < len(tabs):
                    self._closed_tab = tabs[index]
                    self.event_generate("<<NotebookTabClose>>")
        self._active = None


class GameXMLEditor:
    """Modern GUI Editor for .game.xml files with dark theme"""

    def __init__(self):
        self.root = tk.Tk()
        self.root.title("AVATAR XML File Editor | Made By: Jasper_Zebra | Version 2.5")
        self.root.geometry("1800x1100")

        # Apply dark theme
        self.setup_dark_theme()

        # Initialize converter with enhanced feedback
        print("Initializing Game XML Converter...")
        self.converter = GameXMLConverter()

        # Per-tab file management (replaces single-file variables)
        self.open_files = {}

        # Create GUI
        self.create_menu()
        self.create_toolbar()
        self.create_main_frame()
        self.create_status_bar()

        # Bind notebook events (after create_main_frame creates self.notebook)
        self.notebook.bind("<<NotebookTabClose>>", self.close_tab)
        self.notebook.bind("<<NotebookTabChanged>>", self.on_tab_changed)

        # Bind Ctrl+W to close active tab
        self.root.bind('<Control-w>', lambda e: self.close_active_tab())

        # Check converter status and show welcome
        self.show_welcome_message()

        # Enhanced converter status reporting
        if not self.converter.can_convert:
            # Detailed error reporting
            converter_info = self.converter.get_converter_info()

            if not converter_info["available_converters"]:
                missing_tools = [conv["exe"] for conv in self.converter.converter_definitions]
                status_msg = f"WARNING: No conversion tools found - Missing: {', '.join(missing_tools[:2])}"
                if len(missing_tools) > 2:
                    status_msg += f" and {len(missing_tools)-2} more"
            elif converter_info["missing_dlls"]:
                status_msg = f"WARNING: Missing DLLs - {', '.join(converter_info['missing_dlls'][:2])}"
                if len(converter_info["missing_dlls"]) > 2:
                    status_msg += f" and {len(converter_info['missing_dlls'])-2} more"
            else:
                status_msg = "WARNING: File conversion disabled - unknown issue"

            self.status_var.set(status_msg)

            # Show detailed setup instructions
            self.show_converter_setup_dialog()
        else:
            # Success - show available tools
            tool_info = self.converter.get_available_tools_info()
            avatar_ready = any("Avatar" in conv.get("games", []) for conv in self.converter.available_converters)

            if avatar_ready:
                self.status_var.set(f"🎮 AVATAR Ready - {tool_info}")
            else:
                self.status_var.set(f"Ready - {tool_info}")

            # Test conversion capability
            test_success, test_info = self.converter.test_conversion_capability()
            if test_success:
                print(f"Conversion test: {test_info}")

    def show_converter_setup_dialog(self):
        """Show setup instructions for missing conversion tools"""
        setup_window = tk.Toplevel(self.root)
        setup_window.title("Conversion Tools Setup Required")
        setup_window.geometry("700x600")
        setup_window.configure(bg=DarkTheme.BG_DARK)
        setup_window.resizable(True, True)
        setup_window.transient(self.root)
        setup_window.grab_set()

        # Center the window
        setup_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 300,
            self.root.winfo_rooty() + 200
        ))

        # Main frame
        main_frame = ttk.Frame(setup_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        # Title with icon
        title_frame = ttk.Frame(main_frame)
        title_frame.pack(fill=tk.X, pady=(0, 15))

        title_label = ttk.Label(title_frame,
                            text="⚙️ Setup Conversion Tools",
                            font=('Segoe UI', 16, 'bold'),
                            foreground=DarkTheme.ACCENT_ORANGE)
        title_label.pack()

        # Get converter info for detailed reporting
        converter_info = self.converter.get_converter_info()

        # Status section
        status_frame = ttk.LabelFrame(main_frame, text="Current Status", padding=15)
        status_frame.pack(fill=tk.X, pady=(0, 15))

        if not converter_info["available_converters"]:
            status_text = "❌ No conversion tools found"
            status_color = DarkTheme.ACCENT_RED
        elif converter_info["missing_dlls"]:
            status_text = f"⚠️ Tools found but missing {len(converter_info['missing_dlls'])} required DLLs"
            status_color = DarkTheme.ACCENT_ORANGE
        else:
            status_text = "❓ Unknown configuration issue"
            status_color = DarkTheme.ACCENT_YELLOW

        status_label = ttk.Label(status_frame, text=status_text,
                                font=('Segoe UI', 11, 'bold'),
                                foreground=status_color)
        status_label.pack(anchor=tk.W)

        # Tools path info
        path_label = ttk.Label(status_frame,
                            text=f"Looking for tools in: {os.path.abspath(converter_info['tools_path'])}",
                            font=('Consolas', 9))
        path_label.pack(anchor=tk.W, pady=(5, 0))

        # Required files section
        required_frame = ttk.LabelFrame(main_frame, text="Required Files", padding=15)
        required_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 15))

        # Create scrollable text for file list
        text_frame = ttk.Frame(required_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        files_text = tk.Text(text_frame, height=12, wrap=tk.WORD,
                            font=('Consolas', 9),
                            bg=DarkTheme.BG_LIGHT,
                            fg=DarkTheme.FG_NORMAL,
                            borderwidth=1,
                            relief='solid')

        files_scrolly = ttk.Scrollbar(text_frame, orient=tk.VERTICAL, command=files_text.yview)
        files_text.configure(yscrollcommand=files_scrolly.set)

        files_text.grid(row=0, column=0, sticky="nsew")
        files_scrolly.grid(row=0, column=1, sticky="ns")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # Build file list content
        files_content = "📋 Place these files in the tools/ folder:\n\n"

        files_content += "🔧 CONVERTER EXECUTABLES (need at least one):\n"
        for conv_def in self.converter.converter_definitions:
            found = any(conv["exe"] == conv_def["exe"] for conv in converter_info["available_converters"])
            status_icon = "✅" if found else "❌"
            games_list = ", ".join(conv_def["games"][:2])
            if len(conv_def["games"]) > 2:
                games_list += f" + {len(conv_def['games'])-2} more"

            files_content += f"  {status_icon} {conv_def['exe']}\n"
            files_content += f"      (For: {games_list})\n"

        files_content += "\n📚 REQUIRED DLL FILES:\n"
        required_dlls = [
            "Gibbed.Dunia.FileFormats.dll",
            "NDesk.Options.dll",
            "Gibbed.IO.dll",
            "Gibbed.ProjectData.dll"
        ]

        for dll in required_dlls:
            found = dll not in converter_info["missing_dlls"]
            status_icon = "✅" if found else "❌"
            files_content += f"  {status_icon} {dll}\n"

        files_content += "\n💡 SETUP INSTRUCTIONS:\n"
        files_content += "1. Create a 'tools' folder in your editor directory\n"
        files_content += "2. Download Gibbed's Far Cry 2 / Dunia tools\n"
        files_content += "3. Extract the files listed above into the tools folder\n"
        files_content += "4. Restart the editor\n\n"

        files_content += "🎮 FOR AVATAR FILES:\n"
        files_content += "• Gibbed.FarCry2.ConvertXMLResource.exe (recommended)\n"
        files_content += "• This tool specifically supports Avatar: The Game RML files\n\n"

        files_content += "🌟 DOWNLOAD LOCATIONS:\n"
        files_content += "• Search for 'Gibbed Far Cry 2 tools'\n"
        files_content += "• Check Rick's Game Stuff blog\n"
        files_content += "• Look for Far Cry modding communities\n"

        files_text.insert(1.0, files_content)
        files_text.config(state=tk.DISABLED)

        # Buttons
        button_frame = ttk.Frame(main_frame)
        button_frame.pack(fill=tk.X, pady=(15, 0))

        # Refresh button
        def refresh_status():
            setup_window.destroy()
            # Re-initialize converter
            self.converter = GameXMLConverter()
            if self.converter.can_convert:
                tool_info = self.converter.get_available_tools_info()
                self.status_var.set(f"🎮 Ready - {tool_info}")
                self.show_custom_messagebox("Setup Complete", "Conversion tools detected successfully!", "info")
            else:
                self.show_converter_setup_dialog()

        ttk.Button(button_frame, text="🔄 Check Again",
                command=refresh_status, width=15).pack(side=tk.LEFT, padx=(0, 10))

        # Open tools folder button (Windows only)
        def open_tools_folder():
            tools_path = os.path.abspath(converter_info['tools_path'])
            if not os.path.exists(tools_path):
                os.makedirs(tools_path)

            try:
                os.startfile(tools_path)
            except Exception as e:
                self.show_custom_messagebox("Error", f"Could not open folder: {str(e)}", "error")

        ttk.Button(button_frame, text="📁 Open Tools Folder",
                command=open_tools_folder, width=20).pack(side=tk.LEFT, padx=(0, 10))

        # Continue anyway button
        ttk.Button(button_frame, text="Continue Without Conversion",
                command=setup_window.destroy, width=25).pack(side=tk.RIGHT)

        # Focus and wait
        setup_window.focus_set()

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
                               font=('Segoe UI', 16, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 20))

        # Description
        desc_text = """A powerful XML editor designed for AVATAR game files.

        Key Features:
        - Open and edit .game.xml, .xml, and .rml files
        - Convert binary game files to readable XML format
        - Live XML source editing with syntax highlighting
        - Multi-file tab interface (VS Code-style)
        - Real-time XML validation and error checking
        - Search functionality with Ctrl+F support
        - Modern dark theme for comfortable editing
        - Integrated Gibbed Dunia conversion tools

        Perfect for modding and analyzing AVATAR game data files.

        Built with Python and tkinter for reliable performance."""

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

        # Edit menu — only Close Tab remains
        edit_menu = tk.Menu(menubar, tearoff=0,
                           bg=DarkTheme.MENU_BG,
                           fg=DarkTheme.MENU_FG,
                           selectcolor=DarkTheme.ACCENT_BLUE,
                           activebackground=DarkTheme.SELECTION_BG,
                           activeforeground=DarkTheme.SELECTION_FG,
                           font=('Segoe UI', 9))
        menubar.add_cascade(label="Edit", menu=edit_menu)
        edit_menu.add_command(label="Close Tab", command=self.close_active_tab,
                             accelerator="Ctrl+W")

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

    def create_toolbar(self):
        """Create the modern toolbar with dark theme"""
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)

        # File operations section
        file_frame = ttk.LabelFrame(toolbar_frame, text="File Operations", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        ttk.Button(file_frame, text="📁 Select XML File",
                  command=self.open_file, width=20).pack(side=tk.LEFT, padx=2)
        ttk.Button(file_frame, text="💾 Save",
                  command=self.save_file, width=20).pack(side=tk.LEFT, padx=2)

        # Conversion section
        conversion_frame = ttk.LabelFrame(toolbar_frame, text="Format Conversion", padding=10)
        conversion_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))

        self.convert_button = ttk.Button(conversion_frame, text="🔄 Convert To Readable",
                                        command=self.convert_to_readable, width=24)
        self.convert_button.pack(side=tk.LEFT, padx=2)

        self.save_binary_button = ttk.Button(conversion_frame, text="💽 Save To Binary",
                                            command=self.save_as_binary, width=24)
        self.save_binary_button.pack(side=tk.LEFT, padx=2)

        # Disable buttons if no converter
        if not self.converter.can_convert:
            self.convert_button.config(state=tk.DISABLED)
            self.save_binary_button.config(state=tk.DISABLED)

    def create_main_frame(self):
        """Create the main content area — full-width CloseableNotebook"""
        main_container = ttk.Frame(self.root)
        main_container.pack(fill=tk.BOTH, expand=True, padx=10, pady=5)

        self.notebook = CloseableNotebook(main_container)
        self.notebook.pack(fill=tk.BOTH, expand=True)

    # ------------------------------------------------------------------ #
    #  Tab management helpers
    # ------------------------------------------------------------------ #

    def get_active_tab(self):
        """Return the open_files dict for the currently selected tab, or None."""
        selected = self.notebook.select()
        if not selected:
            return None
        return self.open_files.get(selected)

    def close_tab(self, event=None):
        """Close the tab whose path is stored in notebook._closed_tab."""
        tab_frame_path = getattr(self.notebook, '_closed_tab', None)
        if not tab_frame_path:
            return
        self._close_tab_by_path(tab_frame_path)

    def close_active_tab(self, event=None):
        """Close whichever tab is currently selected."""
        selected = self.notebook.select()
        if selected:
            self._close_tab_by_path(selected)

    def _close_tab_by_path(self, tab_frame_path):
        """Internal: prompt-save if needed, then destroy the tab."""
        if not tab_frame_path or tab_frame_path not in self.open_files:
            return

        tab_data = self.open_files[tab_frame_path]

        if tab_data['modified'] or tab_data['source_modified']:
            result = self.show_custom_messagebox_with_yesnocancel(
                "Unsaved Changes",
                f"'{os.path.basename(tab_data['file'])}' has unsaved changes.\n"
                "Save before closing?",
                "warning"
            )
            if result == "yes":
                # Select this tab so save_file operates on it
                self.notebook.select(tab_data['frame'])
                self.save_file()
                # If save failed the flags are still set — abort close
                if tab_data['modified'] or tab_data['source_modified']:
                    return
            elif result == "cancel":
                return
            # "no" → close without saving

        self.notebook.forget(tab_data['frame'])
        del self.open_files[tab_frame_path]

        if not self.open_files:
            self.status_var.set("Ready - No file loaded")
            self.modified_indicator.config(text="")
            self.root.title("AVATAR XML File Editor | Made By: Jasper_Zebra | Version 2.2")

    # ------------------------------------------------------------------ #
    #  Per-tab UI builder
    # ------------------------------------------------------------------ #

    def create_file_tab(self, parent, tab_data):
        """Build the full XML source editor UI inside a tab frame."""
        source_frame = ttk.Frame(parent)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)

        # ---- Search bar ----
        search_frame = ttk.Frame(source_frame)
        search_frame.pack(fill=tk.X, pady=(0, 5))

        ttk.Label(search_frame, text="Search:").pack(side=tk.LEFT, padx=(0, 5))

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=30)
        search_entry.pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(search_frame, text="Find",
                   command=self.find_text, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Next",
                   command=self.find_next, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Previous",
                   command=self.find_previous, width=8).pack(side=tk.LEFT, padx=2)
        ttk.Button(search_frame, text="Clear",
                   command=self.clear_search, width=8).pack(side=tk.LEFT, padx=2)

        case_sensitive_var = tk.BooleanVar()
        ttk.Checkbutton(search_frame, text="Case sensitive",
                        variable=case_sensitive_var).pack(side=tk.LEFT, padx=(10, 0))

        search_result_label = ttk.Label(search_frame, text="",
                                        foreground=DarkTheme.ACCENT_BLUE)
        search_result_label.pack(side=tk.RIGHT)

        # ---- Text widget with scrollbars ----
        text_frame = ttk.Frame(source_frame)
        text_frame.pack(fill=tk.BOTH, expand=True)

        source_text = tk.Text(text_frame, wrap=tk.NONE,
                              font=('Consolas', 10),
                              bg=DarkTheme.BG_LIGHT,
                              fg=DarkTheme.FG_NORMAL,
                              insertbackground=DarkTheme.ACCENT_BLUE,
                              selectbackground=DarkTheme.SELECTION_BG,
                              selectforeground=DarkTheme.SELECTION_FG,
                              borderwidth=1,
                              relief='solid',
                              undo=True,
                              state=tk.NORMAL)

        # Configure search highlighting tags
        source_text.tag_configure("search_highlight",
                                  background="#ffff00",
                                  foreground="#000000")
        source_text.tag_configure("current_match",
                                  background="#ff8c00",
                                  foreground="#ffffff")

        # Key bindings on the text widget
        source_text.bind('<Double-Button-1>', self.on_source_double_click)
        source_text.bind('<<Modified>>', self.on_source_text_change)
        source_text.bind('<Control-z>', lambda e: self._safe_edit(source_text, 'undo'))
        source_text.bind('<Control-y>', lambda e: self._safe_edit(source_text, 'redo'))
        source_text.bind('<Control-Z>', lambda e: self._safe_edit(source_text, 'redo'))
        source_text.bind('<Control-f>', self.focus_search)
        source_text.bind('<F3>', lambda e: self.find_next())
        source_text.bind('<Shift-F3>', lambda e: self.find_previous())
        source_text.bind('<Escape>', self.clear_search)

        # Search-entry shortcuts
        search_entry.bind('<Return>', lambda e: self.find_next())
        search_entry.bind('<Escape>', self.clear_search)

        # Scrollbars
        source_scrolly = ttk.Scrollbar(text_frame, orient=tk.VERTICAL,
                                        command=source_text.yview)
        source_scrollx = ttk.Scrollbar(text_frame, orient=tk.HORIZONTAL,
                                        command=source_text.xview)
        source_text.configure(yscrollcommand=source_scrolly.set,
                               xscrollcommand=source_scrollx.set)

        source_text.grid(row=0, column=0, sticky="nsew")
        source_scrolly.grid(row=0, column=1, sticky="ns")
        source_scrollx.grid(row=1, column=0, sticky="ew")
        text_frame.grid_rowconfigure(0, weight=1)
        text_frame.grid_columnconfigure(0, weight=1)

        # ---- Bottom controls ----
        source_controls = ttk.Frame(source_frame)
        source_controls.pack(fill=tk.X, pady=(10, 0))

        ttk.Button(source_controls, text="📋 Copy All",
                   command=self.copy_source).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="✅ Apply Changes",
                   command=self.apply_source_changes).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="🔍 Validate XML",
                   command=self.validate_source_xml).pack(side=tk.LEFT, padx=(0, 5))

        # Store all widget refs into tab_data
        tab_data['source_text'] = source_text
        tab_data['search_entry'] = search_entry
        tab_data['search_var'] = search_var
        tab_data['search_result_label'] = search_result_label
        tab_data['case_sensitive_var'] = case_sensitive_var
        tab_data['search_matches'] = []
        tab_data['current_match_index'] = -1

    # ------------------------------------------------------------------ #
    #  Search methods (all operate on the active tab)
    # ------------------------------------------------------------------ #

    def focus_search(self, event=None):
        """Focus the search entry in the active tab."""
        tab = self.get_active_tab()
        if tab is None:
            return "break"
        tab['search_entry'].focus_set()
        tab['search_entry'].select_range(0, tk.END)
        return "break"

    def find_text(self):
        """Find all occurrences of the search term in the active tab."""
        tab = self.get_active_tab()
        if tab is None:
            return

        search_term = tab['search_var'].get()
        if not search_term:
            self.clear_search()
            return

        source_text = tab['source_text']
        source_text.tag_remove("search_highlight", "1.0", tk.END)
        source_text.tag_remove("current_match", "1.0", tk.END)

        content = source_text.get("1.0", tk.END)

        if not tab['case_sensitive_var'].get():
            content_lower = content.lower()
            search_term_lower = search_term.lower()
        else:
            content_lower = content
            search_term_lower = search_term

        tab['search_matches'] = []
        start = 0
        while True:
            pos = content_lower.find(search_term_lower, start)
            if pos == -1:
                break

            lines_before = content[:pos].count('\n')
            if lines_before == 0:
                col = pos
            else:
                last_newline = content.rfind('\n', 0, pos)
                col = pos - last_newline - 1

            start_pos = f"{lines_before + 1}.{col}"
            end_pos = f"{lines_before + 1}.{col + len(search_term)}"
            tab['search_matches'].append((start_pos, end_pos))
            start = pos + 1

        for s, e in tab['search_matches']:
            source_text.tag_add("search_highlight", s, e)

        if tab['search_matches']:
            tab['current_match_index'] = 0
            self.highlight_current_match()
            tab['search_result_label'].config(
                text=f"{len(tab['search_matches'])} matches found")
        else:
            tab['search_result_label'].config(text="No matches found")
            tab['current_match_index'] = -1

    def find_next(self):
        """Move to the next search match."""
        tab = self.get_active_tab()
        if tab is None:
            return
        if not tab['search_matches']:
            self.find_text()
            return
        tab['current_match_index'] = (tab['current_match_index'] + 1) % len(tab['search_matches'])
        self.highlight_current_match()

    def find_previous(self):
        """Move to the previous search match."""
        tab = self.get_active_tab()
        if tab is None:
            return
        if not tab['search_matches']:
            self.find_text()
            return
        tab['current_match_index'] = (tab['current_match_index'] - 1) % len(tab['search_matches'])
        self.highlight_current_match()

    def highlight_current_match(self):
        """Scroll to and highlight the current match."""
        tab = self.get_active_tab()
        if tab is None:
            return
        idx = tab['current_match_index']
        matches = tab['search_matches']
        if 0 <= idx < len(matches):
            source_text = tab['source_text']
            source_text.tag_remove("current_match", "1.0", tk.END)
            start_pos, end_pos = matches[idx]
            source_text.tag_add("current_match", start_pos, end_pos)
            source_text.see(start_pos)
            tab['search_result_label'].config(
                text=f"Match {idx + 1} of {len(matches)}")

    def clear_search(self, event=None):
        """Clear all search highlights and reset state."""
        tab = self.get_active_tab()
        if tab is None:
            return "break"
        tab['source_text'].tag_remove("search_highlight", "1.0", tk.END)
        tab['source_text'].tag_remove("current_match", "1.0", tk.END)
        tab['search_var'].set("")
        tab['search_result_label'].config(text="")
        tab['search_matches'] = []
        tab['current_match_index'] = -1
        return "break"

    # ------------------------------------------------------------------ #
    #  About / validation / messaging
    # ------------------------------------------------------------------ #

    def show_about(self):
        """Show about dialog with dark theme"""
        about_window = tk.Toplevel(self.root)
        about_window.title("About AVATAR XML File Editor")
        about_window.geometry("600x500")
        about_window.configure(bg=DarkTheme.BG_DARK)
        about_window.resizable(False, False)
        about_window.transient(self.root)
        about_window.grab_set()

        about_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 500,
            self.root.winfo_rooty() + 300
        ))

        main_frame = ttk.Frame(about_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        title_label = ttk.Label(main_frame,
                               text="🎮 AVATAR XML File Editor",
                               font=('Segoe UI', 16, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 10))

        version_label = ttk.Label(main_frame,
                                 text="Version 2.2",
                                 font=('Segoe UI', 10))
        version_label.pack(pady=(0, 20))

        desc_text = """Welcome to Jasper's XML Editor!

        🎮 Designed specifically for AVATAR game file editing

        What you can do:
        - Load .game.xml, .xml, and .rml game files
        - Convert binary formats to editable XML
        - Edit XML content directly in the source tab
        - Open multiple files in VS Code-style tabs
        - Search through large files with Ctrl+F
        - Validate XML syntax in real-time
        - Save back to binary format for the game

        ✨ Features a modern dark theme and intuitive interface
        🔧 Powered by Gibbed Dunia conversion tools

        Ready to start modding? Click 'Select XML File' to begin!"""

        desc_label = ttk.Label(main_frame,
                              text=desc_text,
                              font=('Segoe UI', 9),
                              justify=tk.CENTER)
        desc_label.pack(pady=(0, 20))

        ok_button = ttk.Button(main_frame, text="OK",
                              command=about_window.destroy, width=10)
        ok_button.pack()
        ok_button.focus_set()
        about_window.wait_window()

    def validate_xml(self):
        """Validate the active tab's XML structure."""
        tab = self.get_active_tab()
        if tab is None:
            self.show_custom_messagebox("No File", "No XML file is currently loaded.", "warning")
            return
        try:
            ET.tostring(tab['tree_data'].getroot())
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

        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)
        height = max(200, len(lines) * 30 + 150)
        msg_window.geometry(f"{width}x{height}")

        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))

        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))

        if msg_type == "error":
            icon = "❌"
            color = DarkTheme.ACCENT_RED
        elif msg_type == "warning":
            icon = "⚠️"
            color = DarkTheme.ACCENT_ORANGE
        else:
            icon = "ℹ️"
            color = DarkTheme.ACCENT_BLUE

        ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18)).pack(side=tk.LEFT)
        ttk.Label(icon_frame, text=title, font=('Segoe UI', 14, 'bold'),
                  foreground=color).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(main_frame, text=message, font=('Segoe UI', 11),
                  justify=tk.LEFT, wraplength=width-60).pack(pady=(0, 20))

        ok_button = ttk.Button(main_frame, text="OK",
                               command=msg_window.destroy, width=15)
        ok_button.pack()
        ok_button.focus_set()
        msg_window.wait_window()

    def show_autoclose_messagebox(self, title, message, delay_ms=2000):
        """Show a dark-themed info popup that automatically closes after delay_ms milliseconds."""
        popup = tk.Toplevel(self.root)
        popup.title(title)
        popup.configure(bg=DarkTheme.BG_DARK)
        popup.resizable(False, False)
        popup.transient(self.root)
        popup.grab_set()

        lines = message.split('\n')
        width = max(350, max(len(line) * 9 for line in lines) + 120)
        height = max(150, len(lines) * 30 + 100)
        popup.geometry(f"{width}x{height}+{self.root.winfo_rootx() + 200}+{self.root.winfo_rooty() + 200}")

        main_frame = ttk.Frame(popup)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 10))
        ttk.Label(icon_frame, text="✅", font=('Segoe UI', 18)).pack(side=tk.LEFT)
        ttk.Label(icon_frame, text=title, font=('Segoe UI', 14, 'bold'),
                  foreground=DarkTheme.ACCENT_GREEN).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(main_frame, text=message, font=('Segoe UI', 11),
                  justify=tk.LEFT, wraplength=width - 60).pack(pady=(0, 10))

        popup.after(delay_ms, popup.destroy)

    def open_file(self):
        """Select a binary .xml file to convert and make readable!"""
        filetypes = [
            ("All supported files", "*.game.xml;*.xml;*.rml"),
            ("Game XML files", "*.game.xml"),
            ("XML files", "*.xml"),
            ("RML files", "*.rml"),
            ("All files", "*.*")
        ]
        filename = filedialog.askopenfilename(
            title="Open Game XML/RML File",
            filetypes=filetypes
        )
        if filename:
            self.load_file(filename)

    def load_file(self, filename):
        """Load a file into a new tab (or switch to it if already open)."""
        try:
            # If already open, switch to that tab
            for path, td in self.open_files.items():
                if td['file'] == filename:
                    self.notebook.select(td['frame'])
                    return

            # Determine if conversion is needed
            needs_conversion = False
            base, ext = os.path.splitext(filename)

            if ext == '.rml':
                needs_conversion = True
            else:
                needs_conversion = not self.converter.is_file_xml_format(filename)

            if needs_conversion:
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
                    self.show_autoclose_messagebox("Conversion Successful", message, 2000)
                    if ext == '.rml':
                        xml_filename = base + '.xml'
                        if os.path.exists(xml_filename):
                            filename = xml_filename
                        else:
                            self.show_custom_messagebox("Error", "Converted XML file not found", "error")
                            return
                else:
                    self.show_custom_messagebox(
                        "Cannot Edit",
                        "Cannot edit binary format files. Please convert first.",
                        "warning")
                    return

            # Parse the XML
            tree_data = ET.parse(filename)

            # Create the tab frame and add it to the notebook
            tab_frame = ttk.Frame(self.notebook)
            self.notebook.add(tab_frame, text=os.path.basename(filename))

            # Build tab_data (widget refs filled in by create_file_tab)
            tab_data = {
                'file': filename,
                'frame': tab_frame,
                'tree_data': tree_data,
                'source_text': None,
                'search_entry': None,
                'search_var': None,
                'search_result_label': None,
                'case_sensitive_var': None,
                'search_matches': [],
                'current_match_index': -1,
                'source_modified': False,
                'modified': False,
                'updating_source': False,
            }

            # Build the UI inside the tab
            self.create_file_tab(tab_frame, tab_data)

            # Register the tab
            self.open_files[str(tab_frame)] = tab_data

            # Select it
            self.notebook.select(tab_frame)

            # Update title and status
            self.root.title(
                f"AVATAR XML File Editor | Made By: Jasper_Zebra | Version 2.2 | "
                f"Current XML File Loaded: - {os.path.basename(filename)}")
            self.status_var.set(f"Loaded: {filename}")

            # Populate the source view
            self.refresh_source_view()

            # Clear modified indicator
            self.modified_indicator.config(text="")

        except Exception as e:
            self.show_custom_messagebox("Error", f"Failed to load file:\n{str(e)}", "error")

    def create_status_bar(self):
        """Create modern status bar with dark theme"""
        status_frame = ttk.Frame(self.root)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X, padx=10, pady=5)

        self.status_var = tk.StringVar()
        status_label = ttk.Label(status_frame, textvariable=self.status_var,
                                relief=tk.SUNKEN, font=('Segoe UI', 9))
        status_label.pack(side=tk.LEFT, fill=tk.X, expand=True)

        self.modified_indicator = ttk.Label(status_frame, text="",
                                           font=('Segoe UI', 9, 'bold'))
        self.modified_indicator.pack(side=tk.RIGHT, padx=(10, 0))

    def on_tab_changed(self, event=None):
        """Update status bar when the active tab changes."""
        tab = self.get_active_tab()
        if tab is None:
            self.status_var.set("Ready")
            self.modified_indicator.config(text="")
            return
        self.status_var.set(f"Editing: {tab['file']}")
        if tab['modified'] or tab['source_modified']:
            self.modified_indicator.config(text="●", foreground=DarkTheme.ACCENT_ORANGE)
        else:
            self.modified_indicator.config(text="")

    def show_custom_messagebox_with_yesnocancel(self, title, message, msg_type="info"):
        """Show a custom dark-themed message box with Yes/No/Cancel buttons"""
        result = ["cancel"]

        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.configure(bg=DarkTheme.BG_DARK)
        msg_window.resizable(False, False)
        msg_window.transient(self.root)
        msg_window.grab_set()

        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)
        height = max(200, len(lines) * 30 + 150)
        msg_window.geometry(f"{width}x{height}")

        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))

        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))

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

        ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18)).pack(side=tk.LEFT)
        ttk.Label(icon_frame, text=title, font=('Segoe UI', 14, 'bold'),
                  foreground=color).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(main_frame, text=message, font=('Segoe UI', 11),
                  justify=tk.LEFT, wraplength=width-60).pack(pady=(0, 20))

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

        yes_button = ttk.Button(button_frame, text="Yes", command=on_yes, width=12)
        yes_button.pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="No", command=on_no, width=12).pack(side=tk.LEFT, padx=5)
        ttk.Button(button_frame, text="Cancel", command=on_cancel, width=12).pack(side=tk.LEFT, padx=5)

        yes_button.focus_set()
        msg_window.wait_window()

        return result[0]

    def on_source_double_click(self, event):
        """Select only the word under cursor using VS Code-style word chars (alphanumeric + underscore)."""
        import re
        widget = event.widget
        index = widget.index(f"@{event.x},{event.y}")
        line_num, col = map(int, index.split('.'))
        line_text = widget.get(f"{line_num}.0", f"{line_num}.end")
        word_char = re.compile(r'[A-Za-z0-9_]')
        if col < len(line_text) and word_char.match(line_text[col]):
            start = col
            end = col
            while start > 0 and word_char.match(line_text[start - 1]):
                start -= 1
            while end < len(line_text) and word_char.match(line_text[end]):
                end += 1
            widget.tag_remove('sel', '1.0', tk.END)
            widget.tag_add('sel', f"{line_num}.{start}", f"{line_num}.{end}")
            widget.mark_set('insert', f"{line_num}.{end}")
        return 'break'

    def on_source_text_change(self, event=None):
        """Handle changes to the source text widget."""
        tab = self.get_active_tab()
        if tab is None:
            return
        widget = event.widget if event else None
        if widget:
            widget.edit_modified(False)  # Reset so the event fires again on next change
        if not tab['updating_source'] and tab['tree_data']:
            tab['source_modified'] = True
            self.mark_modified()
            self.status_var.set("XML source modified - use 'Apply Changes' or save to apply")

    def apply_source_changes(self):
        """Apply source text edits back to the in-memory XML tree."""
        tab = self.get_active_tab()
        if tab is None:
            return False
        try:
            source_content = tab['source_text'].get(1.0, tk.END).strip()
            if not source_content:
                self.show_custom_messagebox("Error", "Source content is empty.", "error")
                return False

            try:
                new_root = ET.fromstring(source_content)
                new_tree = ET.ElementTree(new_root)
                tab['tree_data'] = new_tree
                tab['source_modified'] = False

                tab['updating_source'] = True
                try:
                    self.refresh_source_view()
                finally:
                    tab['updating_source'] = False

                self.status_var.set("XML source changes applied successfully")
                self.show_custom_messagebox(
                    "Success",
                    "XML source changes have been applied to the tree structure.",
                    "info")
                return True

            except ET.ParseError as e:
                self.show_custom_messagebox("Parse Error", f"XML Parse Error: {str(e)}", "error")
                self.status_var.set("XML parsing failed - check syntax")
                return False

        except Exception as e:
            self.show_custom_messagebox("Error", f"Error applying source changes: {str(e)}", "error")
            return False

    def validate_source_xml(self):
        """Validate the XML syntax in the active tab's source widget."""
        tab = self.get_active_tab()
        if tab is None:
            self.show_custom_messagebox("No File", "No file is currently loaded.", "warning")
            return
        try:
            source_content = tab['source_text'].get(1.0, tk.END).strip()
            if not source_content:
                self.show_custom_messagebox("Validation", "Source content is empty.", "warning")
                return
            try:
                ET.fromstring(source_content)
                self.show_custom_messagebox("Validation Result", "XML syntax is valid!", "info")
                self.status_var.set("XML validation successful")
            except ET.ParseError as e:
                error_info = str(e)
                if hasattr(e, 'lineno') and hasattr(e, 'offset'):
                    error_info += f"\nLine: {e.lineno}, Column: {e.offset}"
                self.show_custom_messagebox("Validation Error",
                                            f"XML Parse Error:\n{error_info}", "error")
                self.status_var.set("XML validation failed")
        except Exception as e:
            self.show_custom_messagebox("Validation Error",
                                        f"Error during validation: {str(e)}", "error")

    def save_file(self):
        """Save the active tab's file."""
        tab = self.get_active_tab()
        if tab is None:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return

        if not tab['tree_data']:
            self.show_custom_messagebox("No Data", "No data to save.", "warning")
            return

        # Auto-apply source changes before saving
        if tab['source_modified']:
            if not self.apply_source_changes():
                return

        try:
            from config import EDITOR_SETTINGS
            if os.path.exists(tab['file']) and EDITOR_SETTINGS.get("auto_backup", False):
                backup_path = tab['file'] + ".backup"
                import shutil
                shutil.copy2(tab['file'], backup_path)
                self.status_var.set(f"Backup created: {os.path.basename(backup_path)}")

            # Write with pretty formatting
            self.indent_xml(tab['tree_data'].getroot())
            tab['tree_data'].write(tab['file'], encoding="utf-8", xml_declaration=True)

            # Reset modification flags
            tab['modified'] = False
            tab['source_modified'] = False

            # Remove ● from tab title
            self.notebook.tab(tab['frame'], text=os.path.basename(tab['file']))

            self.modified_indicator.config(text="✓", foreground=DarkTheme.ACCENT_GREEN)

            # Refresh source view to reflect indentation normalisation
            self.refresh_source_view()

            self.status_var.set(f"Saved: {os.path.basename(tab['file'])}")

        except Exception as e:
            self.show_custom_messagebox("Save Error", f"Failed to save file:\n{str(e)}", "error")

    def _safe_edit(self, widget, action):
        try:
            widget.edit(action)
        except Exception:
            pass
        tab = self.get_active_tab()
        if tab and not widget.edit_modified():
            tab['source_modified'] = False
            tab['modified'] = False
            self.notebook.tab(tab['frame'], text=os.path.basename(tab['file']))
            self.modified_indicator.config(text="✓", foreground=DarkTheme.ACCENT_GREEN)
        return 'break'

    def _clear_source_modified(self, tab):
        """Reset all modified state after a programmatic source refresh."""
        tab['source_text'].edit_reset()
        tab['source_text'].edit_modified(False)
        tab['source_modified'] = False
        tab['modified'] = False
        self.notebook.tab(tab['frame'], text=os.path.basename(tab['file']))
        self.modified_indicator.config(text="✓", foreground=DarkTheme.ACCENT_GREEN)

    def refresh_source_view(self):
        """Repopulate the source text widget from the in-memory XML tree."""
        tab = self.get_active_tab()
        if tab is None:
            return

        if not tab['tree_data']:
            tab['source_text'].delete(1.0, tk.END)
            return

        try:
            tab['updating_source'] = True

            self.indent_xml(tab['tree_data'].getroot())
            xml_str = ET.tostring(tab['tree_data'].getroot(),
                                  encoding='unicode', method='xml')

            if not xml_str.startswith('<?xml'):
                xml_str = '<?xml version="1.0" encoding="utf-8"?>\n' + xml_str

            tab['source_text'].delete(1.0, tk.END)
            tab['source_text'].insert(1.0, xml_str)

            self.apply_dark_highlighting(tab['source_text'])

            tab['source_modified'] = False

        except Exception as e:
            tab['source_text'].delete(1.0, tk.END)
            tab['source_text'].insert(1.0, f"Error generating source view: {str(e)}")
        finally:
            tab['updating_source'] = False
            # Schedule reset after the event loop processes the queued <<Modified>> event
            self.root.after(0, lambda t=tab: self._clear_source_modified(t))

    def apply_dark_highlighting(self, source_text):
        """Apply dark-theme syntax highlighting to a source Text widget."""
        try:
            source_text.tag_configure("tag", foreground=DarkTheme.XML_TAG)
            source_text.tag_configure("attr", foreground=DarkTheme.XML_ATTR)
            source_text.tag_configure("string", foreground=DarkTheme.XML_STRING)
            source_text.tag_configure("comment", foreground=DarkTheme.XML_COMMENT)
            source_text.tag_configure("declaration", foreground=DarkTheme.ACCENT_PURPLE)

            content = source_text.get(1.0, tk.END)
            lines = content.split('\n')

            import re
            for i, line in enumerate(lines):
                for match in re.finditer(r'<\?xml.*?\?>', line):
                    source_text.tag_add("declaration",
                                        f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
                for match in re.finditer(r'<[^>]+>', line):
                    source_text.tag_add("tag",
                                        f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
                for match in re.finditer(r'="[^"]*"', line):
                    source_text.tag_add("string",
                                        f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
                for match in re.finditer(r'<!--.*?-->', line):
                    source_text.tag_add("comment",
                                        f"{i+1}.{match.start()}", f"{i+1}.{match.end()}")
        except Exception as e:
            print(f"Error applying highlighting: {e}")

    def copy_source(self):
        """Copy the active tab's source to the clipboard."""
        tab = self.get_active_tab()
        if tab is None:
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(tab['source_text'].get(1.0, tk.END))
        self.status_var.set("XML source copied to clipboard")

    def mark_modified(self):
        """Mark the active tab as modified (adds ● prefix to tab title)."""
        tab = self.get_active_tab()
        if tab is None:
            return
        tab['modified'] = True
        filename = os.path.basename(tab['file'])
        self.notebook.tab(tab['frame'], text=f"● {filename}")
        self.modified_indicator.config(text="●", foreground=DarkTheme.ACCENT_ORANGE)

    def save_as_binary(self):
        """Save the active tab's file in binary format."""
        tab = self.get_active_tab()
        if tab is None:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return

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

        self.save_file()

        success, message = self.converter.save_as_binary(tab['file'])
        if success:
            self.status_var.set("Saved in binary format")
            self.show_autoclose_messagebox("Saved as Binary", f"Successfully saved as binary:\n{os.path.basename(tab['file'])}", 2000)
        else:
            self.show_custom_messagebox("Save Error", message, "error")

    def show_custom_messagebox_with_result(self, title, message, msg_type="info"):
        """Show a custom dark-themed message box that returns True/False"""
        result = [False]

        msg_window = tk.Toplevel(self.root)
        msg_window.title(title)
        msg_window.configure(bg=DarkTheme.BG_DARK)
        msg_window.resizable(False, False)
        msg_window.transient(self.root)
        msg_window.grab_set()

        lines = message.split('\n')
        width = max(400, max(len(line) * 9 for line in lines) + 120)
        height = max(200, len(lines) * 30 + 150)
        msg_window.geometry(f"{width}x{height}")

        msg_window.geometry("+%d+%d" % (
            self.root.winfo_rootx() + 200,
            self.root.winfo_rooty() + 200
        ))

        main_frame = ttk.Frame(msg_window)
        main_frame.pack(fill=tk.BOTH, expand=True, padx=20, pady=20)

        icon_frame = ttk.Frame(main_frame)
        icon_frame.pack(fill=tk.X, pady=(0, 15))

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

        ttk.Label(icon_frame, text=icon, font=('Segoe UI', 18)).pack(side=tk.LEFT)
        ttk.Label(icon_frame, text=title, font=('Segoe UI', 14, 'bold'),
                  foreground=color).pack(side=tk.LEFT, padx=(10, 0))

        ttk.Label(main_frame, text=message, font=('Segoe UI', 11),
                  justify=tk.LEFT, wraplength=width-60).pack(pady=(0, 20))

        button_frame = ttk.Frame(main_frame)
        button_frame.pack()

        def on_yes():
            result[0] = True
            msg_window.destroy()

        def on_no():
            result[0] = False
            msg_window.destroy()

        yes_button = ttk.Button(button_frame, text="Yes", command=on_yes, width=15)
        yes_button.pack(side=tk.LEFT, padx=10)
        ttk.Button(button_frame, text="No", command=on_no, width=15).pack(side=tk.LEFT, padx=10)

        yes_button.focus_set()
        msg_window.wait_window()

        return result[0]

    def convert_to_readable(self):
        """Convert the active tab's file to readable XML format."""
        tab = self.get_active_tab()
        if tab is None:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return

        self.status_var.set("Converting to readable format...")
        self.root.update()

        success, message = self.converter.convert_to_readable(tab['file'])

        if success:
            self.load_file(tab['file'])
            self.show_custom_messagebox("Conversion Successful", message, "info")
        else:
            self.show_custom_messagebox("Conversion Failed", message, "error")
            self.status_var.set("Conversion failed")

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
        self.root.minsize(800, 600)
        self.root.configure(bg=DarkTheme.BG_DARK)

        self.root.update_idletasks()
        width = self.root.winfo_width()
        height = self.root.winfo_height()
        x = (self.root.winfo_screenwidth() // 2) - (width // 2)
        y = (self.root.winfo_screenheight() // 2) - (height // 2)
        self.root.geometry(f"{width}x{height}+{x}+{y}")

        self.root.protocol("WM_DELETE_WINDOW", self.on_closing)
        self.root.mainloop()

    def on_closing(self):
        """Handle application closing — prompt to save any modified tabs."""
        modified_tabs = [
            td for td in self.open_files.values()
            if td['modified'] or td['source_modified']
        ]

        if modified_tabs:
            filenames = ", ".join(
                os.path.basename(td['file']) for td in modified_tabs[:3])
            if len(modified_tabs) > 3:
                filenames += f" and {len(modified_tabs) - 3} more"

            result = self.show_custom_messagebox_with_yesnocancel(
                "Unsaved Changes",
                f"You have unsaved changes in:\n{filenames}\n\nSave all before closing?",
                "warning"
            )

            if result == "yes":
                for td in list(modified_tabs):
                    self.notebook.select(td['frame'])
                    self.save_file()
                # Only close if every tab was saved successfully
                still_modified = [
                    td for td in self.open_files.values()
                    if td['modified'] or td['source_modified']
                ]
                if not still_modified:
                    self.root.destroy()
            elif result == "no":
                self.root.destroy()
            # "cancel" → keep window open
        else:
            self.root.destroy()
