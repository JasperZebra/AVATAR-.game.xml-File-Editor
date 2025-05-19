"""
Configuration settings for the Game XML Editor
"""

import os

# Default paths
DEFAULT_TOOLS_PATH = "tools"
DEFAULT_WINDOW_WIDTH = 1200
DEFAULT_WINDOW_HEIGHT = 800

# File extensions
SUPPORTED_EXTENSIONS = [".game.xml", ".xml"]

# Conversion tool filenames
CONVERTER_EXECUTABLE = "Gibbed.Dunia.ConvertXml.exe"
REQUIRED_DLLS = [
    "Gibbed.Dunia.FileFormats.dll",
    "NDesk.Options.dll", 
    "Gibbed.IO.dll",
    "Gibbed.ProjectData.dll"
]

# UI Settings
TREE_DEFAULT_WIDTH = 300
DETAILS_DEFAULT_WIDTH = 400
ATTRIBUTE_COLUMN_WIDTH = 150
VALUE_COLUMN_WIDTH = 250

# Colors (for potential theming)
COLORS = {
    "background": "#ffffff",
    "foreground": "#000000",
    "selected": "#0078d4",
    "error": "#d13438",
    "warning": "#ff8c00",
    "success": "#107c10"
}

# Editor settings
EDITOR_SETTINGS = {
    "auto_expand_root": True,
    "auto_backup": True,
    "confirm_deletes": True,
    "pretty_print_xml": True,
    "xml_encoding": "utf-8",
    "xml_declaration": True
}

# Search settings
SEARCH_SETTINGS = {
    "case_sensitive_default": False,
    "highlight_all_matches": True,
    "wrap_around": True
}

def get_tools_path():
    """Get the path to the conversion tools directory"""
    # Check if tools path exists relative to script
    script_dir = os.path.dirname(os.path.abspath(__file__))
    tools_path = os.path.join(script_dir, DEFAULT_TOOLS_PATH)
    
    if os.path.exists(tools_path):
        return tools_path
    
    # Check in current working directory
    if os.path.exists(DEFAULT_TOOLS_PATH):
        return DEFAULT_TOOLS_PATH
    
    # Return default even if it doesn't exist (will be handled by converter)
    return DEFAULT_TOOLS_PATH

def validate_tools_directory(tools_path):
    """Validate that the tools directory contains required files"""
    if not os.path.exists(tools_path):
        return False, f"Tools directory not found: {tools_path}"
    
    # Check for converter executable
    converter_path = os.path.join(tools_path, CONVERTER_EXECUTABLE)
    if not os.path.exists(converter_path):
        return False, f"Converter executable not found: {converter_path}"
    
    # Check for required DLLs
    missing_dlls = []
    for dll in REQUIRED_DLLS:
        dll_path = os.path.join(tools_path, dll)
        if not os.path.exists(dll_path):
            missing_dlls.append(dll)
    
    if missing_dlls:
        return False, f"Missing required DLLs: {', '.join(missing_dlls)}"
    
    return True, "All required tools found"