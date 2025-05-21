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
        self.root.title("AVATAR .game.xml File Editor | Made By: Jasper_Zebra | Version 1.0")
        self.root.geometry("1400x900")
        
        # Apply dark theme
        self.setup_dark_theme()
        
        # Initialize converter
        self.converter = GameXMLConverter()
        
        # Current file
        self.current_file = None
        self.tree_data = None
        self.is_modified = False
        self.element_map = {}
        
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
            self.status_var.set("Ready - Game XML Editor")
    
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
        welcome_window.title("Welcome to Game XML Editor")
        welcome_window.geometry("500x400")
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
                               text="🎮 Game XML Editor",
                               font=('Segoe UI', 16, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """Welcome to the Game XML Editor!

This editor allows you to:

• Open and edit .game.xml files
• Convert between binary and readable XML formats
• Navigate XML structure with tree view
• Edit elements, attributes, and text content
• Search and find elements
• Pretty-print XML output

Use 'Open Game XML...' to get started!"""
        
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
        file_menu.add_command(label="Open Game XML...", command=self.open_file, 
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
    
    def create_toolbar(self):
        """Create the modern toolbar with dark theme"""
        # Main toolbar frame with dark background
        toolbar_frame = ttk.Frame(self.root)
        toolbar_frame.pack(side=tk.TOP, fill=tk.X, padx=10, pady=5)
        
        # File operations section
        file_frame = ttk.LabelFrame(toolbar_frame, text="File Operations", padding=10)
        file_frame.pack(side=tk.LEFT, fill=tk.Y, padx=(0, 10))
        
        # Open button with icon-like styling
        open_button = ttk.Button(file_frame, text="📁 Open Game XML", 
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
        
        # Create horizontal paned window for resizable layout
        paned = ttk.PanedWindow(main_container, orient=tk.HORIZONTAL)
        paned.pack(fill=tk.BOTH, expand=True)
        
        # Left panel - XML Tree view
        left_panel = ttk.LabelFrame(paned, text="📁 XML Structure", padding=10)
        paned.add(left_panel, weight=1)
        
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
        
        # Right panel - Element details with tabs
        right_panel = ttk.LabelFrame(paned, text="🔧 Element Details", padding=10)
        paned.add(right_panel, weight=1)
        
        # Create notebook for tabbed interface
        self.notebook = ttk.Notebook(right_panel)
        self.notebook.pack(fill=tk.BOTH, expand=True)
        
        # Properties tab
        properties_frame = ttk.Frame(self.notebook)
        self.notebook.add(properties_frame, text="Properties")
        
        self.create_properties_tab(properties_frame)
        
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
        """Create the XML source view tab with dark theme"""
        source_frame = ttk.Frame(parent)
        source_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=10)
        
        # Source text widget with scrollbars and dark theme
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
                                  relief='solid')
        
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
        
        ttk.Button(source_controls, text="🔄 Refresh", 
                  command=self.refresh_source_view).pack(side=tk.LEFT, padx=(0, 5))
        ttk.Button(source_controls, text="📋 Copy All", 
                  command=self.copy_source).pack(side=tk.LEFT, padx=(0, 5))
    
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
    
    def show_about(self):
        """Show about dialog with dark theme"""
        # Create a custom dark-themed about dialog
        about_window = tk.Toplevel(self.root)
        about_window.title("About Game XML Editor")
        about_window.geometry("500x400")
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
                               text="🎮 Game XML Editor",
                               font=('Segoe UI', 16, 'bold'),
                               foreground=DarkTheme.ACCENT_BLUE)
        title_label.pack(pady=(0, 10))
        
        # Version
        version_label = ttk.Label(main_frame, 
                                 text="Version 1.0",
                                 font=('Segoe UI', 10))
        version_label.pack(pady=(0, 20))
        
        # Description
        desc_text = """A modern tool for editing .game.xml files.

Features:
• Binary to XML conversion
• Tree-based XML editing
• Real-time validation
• Modern dark theme interface

Built with Python and tkinter"""
        
        desc_label = ttk.Label(main_frame, 
                              text=desc_text,
                              font=('Segoe UI', 9),
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
        
        # OK button
        ok_button = ttk.Button(main_frame, 
                            text="OK",
                            command=msg_window.destroy,
                            width=15)  # Increased width from 10 to 15
        ok_button.pack()
        
        # Focus and wait
        ok_button.focus_set()
        msg_window.wait_window()

    def open_file(self):
        """Open a .game.xml file with better file handling"""
        filetypes = [
            ("Game XML files", "*.game.xml"),
            ("XML files", "*.xml"),
            ("All files", "*.*")
        ]
        
        filename = filedialog.askopenfilename(
            title="Open Game XML File",
            filetypes=filetypes
        )
        
        if filename:
            self.load_file(filename)
    
    def load_file(self, filename):
        """Load and display a .game.xml file with enhanced error handling"""
        try:
            # Check if file is in readable format
            if not self.converter.is_file_xml_format(filename):
                # Ask user if they want to convert using custom messagebox
                result = self.show_custom_messagebox_with_result(
                    "Binary Format Detected",
                    "This .game.xml file appears to be in binary format.\n\n"
                    "Would you like to convert it to readable XML format?\n\n"
                    "Note: You can enable `auto_backup` to create backups.",
                    "question"
                )
                
                if result:
                    success, message = self.converter.convert_to_readable(filename)
                    if not success:
                        self.show_custom_messagebox("Conversion Failed", message, "error")
                        return
                    self.show_custom_messagebox("Conversion Successful", message, "info")
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
            self.root.title(f"Game XML Editor - {os.path.basename(filename)}")
            self.status_var.set(f"Loaded: {filename}")
            
            # Update statistics
            self.update_statistics()
            
            # Update source view
            self.refresh_source_view()
            
            # Clear modified indicator
            self.modified_indicator.config(text="")
            
        except Exception as e:
            self.show_custom_messagebox("Error", f"Failed to load file:\n{str(e)}", "error")

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
    
    def refresh_source_view(self):
        """Refresh the XML source view with dark theme syntax highlighting"""
        if not self.tree_data:
            self.source_text.delete(1.0, tk.END)
            return
        
        try:
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
            
        except Exception as e:
            self.source_text.delete(1.0, tk.END)
            self.source_text.insert(1.0, f"Error generating source view: {str(e)}")
    
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
        # Update tag name
        self.tag_var.set(element.tag)
        
        # Update text content
        self.text_var.set(element.text or "")
        
        # Update attributes using the refresh method
        self.refresh_attribute_display(element)
        
        # Update status bar with element info
        attr_count = len(element.attrib)
        child_count = len(list(element))
        self.status_var.set(f"Selected: {element.tag} | {attr_count} attributes | {child_count} children")
    
    def clear_element_details(self):
        """Clear the element details panel"""
        self.tag_var.set("")
        self.text_var.set("")
        self.attr_tree.delete(*self.attr_tree.get_children())
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
    
    def edit_attribute(self, event, item=None):
        """Edit selected attribute with improved handling"""
        if item is None:
            selection = self.attr_tree.selection()
            if not selection:
                return
            item = selection[0]
        
        attr_name = self.attr_tree.item(item, "text")
        attr_values = self.attr_tree.item(item, "values")
        
        # Handle case where value might be empty
        attr_value = attr_values[0] if attr_values else ""
        
        # Create edit dialog
        dialog = AttributeEditDialog(self.root, attr_name, attr_value)
        
        # Wait for dialog to complete
        self.root.wait_window(dialog.dialog)
        
        # Check if we have a result
        if hasattr(dialog, 'result') and dialog.result:
            new_name, new_value = dialog.result
            
            # Update in XML
            tree_selection = self.tree.selection()
            if tree_selection:
                tree_item = tree_selection[0]
                if tree_item in self.element_map:
                    element = self.element_map[tree_item]
                    
                    # Remove old attribute if name changed
                    if new_name != attr_name and attr_name in element.attrib:
                        del element.attrib[attr_name]
                    
                    # Set new attribute
                    element.attrib[new_name] = new_value
                    
                    # Update displays
                    self.refresh_attribute_display(element)
                    self.update_tree_item_text(tree_item, element)
                    self.mark_modified()
                    
                    # Refresh source view if visible
                    current_tab = self.notebook.tab(self.notebook.select(), "text")
                    if current_tab == "XML Source":
                        self.refresh_source_view()
    
    def add_attribute(self):
        """Add new attribute to selected element with improved UX"""
        tree_selection = self.tree.selection()
        if not tree_selection:
            self.show_custom_messagebox("No Selection", "Please select an element first.", "warning")
            return
        
        # Create edit dialog for new attribute
        dialog = AttributeEditDialog(self.root, "", "")
        
        # Wait for dialog to complete
        self.root.wait_window(dialog.dialog)
        
        # Check if we have a result
        if hasattr(dialog, 'result') and dialog.result:
            attr_name, attr_value = dialog.result
            
            # Check if attribute already exists
            tree_item = tree_selection[0]
            if tree_item in self.element_map:
                element = self.element_map[tree_item]
                
                if attr_name in element.attrib:
                    result = messagebox.askyesno("Attribute Exists", 
                                               f"Attribute '{attr_name}' already exists. Replace it?")
                    if not result:
                        return
                
                # Add to XML
                element.attrib[attr_name] = attr_value
                
                # Update displays
                self.refresh_attribute_display(element)
                self.update_tree_item_text(tree_item, element)
                self.mark_modified()
                
                # Select the new attribute
                for item_id in self.attr_tree.get_children():
                    if self.attr_tree.item(item_id, "text") == attr_name:
                        self.attr_tree.selection_set(item_id)
                        self.attr_tree.focus(item_id)
                        break
                
                self.status_var.set(f"Added attribute: {attr_name}")
    
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
    
    def delete_attribute(self):
        """Delete selected attribute with enhanced confirmation"""
        selection = self.attr_tree.selection()
        if not selection:
            self.show_custom_messagebox("No Selection", "Please select an attribute to delete.", "warning")
            return
        
        item = selection[0]
        attr_name = self.attr_tree.item(item, "text")
        
        # Enhanced confirmation dialog
        result = messagebox.askyesno("Confirm Delete", 
                                   f"Are you sure you want to delete attribute '{attr_name}'?\n\n"
                                   f"This action cannot be undone.")
        if result:
            # Remove from XML
            tree_selection = self.tree.selection()
            if tree_selection:
                tree_item = tree_selection[0]
                if tree_item in self.element_map:
                    element = self.element_map[tree_item]
                    if attr_name in element.attrib:
                        del element.attrib[attr_name]
                    
                    # Update displays
                    self.refresh_attribute_display(element)
                    self.update_tree_item_text(tree_item, element)
                    self.mark_modified()
                    
                    self.status_var.set(f"Deleted attribute: {attr_name}")
    
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
    
    def save_file(self):
        """Save the current file with enhanced feedback"""
        if not self.current_file:
            self.show_custom_messagebox("No File", "No file is currently open.", "warning")
            return
        
        if not self.tree_data:
            self.show_custom_messagebox("No Data", "No data to save.", "warning")
            return
        
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
            self.root.title(self.root.title().rstrip(" *"))
            self.modified_indicator.config(text="✓", foreground=DarkTheme.ACCENT_GREEN)
            self.file_info_label.config(text=f"📄 {os.path.basename(self.current_file)}")
            
            # Update statistics and source view
            self.update_statistics()
            self.refresh_source_view()
                        
        except Exception as e:
            self.show_custom_messagebox("Save Error", f"Failed to save file:\n{str(e)}", "error")
    
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
        if self.is_modified:
            result = messagebox.askyesnocancel(
                "Unsaved Changes",
                "You have unsaved changes. Do you want to save before closing?",
                icon='warning'
            )
            
            if result is True:  # Yes - save and close
                self.save_file()
                if not self.is_modified:  # Only close if save was successful
                    self.root.destroy()
            elif result is False:  # No - close without saving
                self.root.destroy()
            # Cancel - do nothing, keep window open
        else:
            self.root.destroy()