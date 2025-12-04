from cx_Freeze import setup, Executable
import os
import sys
from PIL import Image

def convert_png_to_ico(png_path, ico_path):
    # Open the PNG image
    img = Image.open(png_path)
    
    # Resize to standard icon sizes (16x16, 32x32, 48x48, 256x256)
    icon_sizes = [(16, 16), (32, 32), (48, 48), (256, 256)]
    
    # Save as ICO
    img.save(ico_path, format='ICO', sizes=icon_sizes)
    print(f"Converted {png_path} to {ico_path}")

# Convert xml_editor_icon.png to xml_editor_icon.ico
convert_png_to_ico('assets/xml_editor_icon.png', 'xml_editor_icon.ico')

# Define the base directory
base_dir = os.path.abspath(os.path.dirname(__file__))

# Build options
build_options = {
    'include_files': [
        # Add any assets or icon files here
        ('assets/xml_editor_icon.png', 'assets/xml_editor_icon.png'),
        ('main.py', 'main.py'),
        ('main_editor.py', 'main_editor.py'),
        ('converter.py', 'converter.py'),
        ('dialogs.py', 'dialogs.py'),
        ('config.py', 'config.py'),
        ('tools', 'tools'),  # Include entire tools folder with all files
        ('assets', 'assets'),  # Include entire assets folder
    ],
    'packages': [
        # Standard libraries
        'os', 'sys', 'logging', 'tkinter', 'pathlib', 're',
        
        # Tkinter related
        'tkinter.ttk', 'tkinter.filedialog', 'tkinter.messagebox',
        
        # XML processing
        'xml.etree.ElementTree',
        
        # Image handling
        'PIL',  # Pillow for image processing
    ],
    'excludes': [
        # Packages you want to exclude to reduce size
        'test', 'unittest', 'matplotlib', 'numpy', 'scipy'
    ],
    'include_msvcr': True,  # Include Microsoft Visual C Runtime
}

# Set up the executable
executables = [
    Executable(
        'main.py',  # Your main script
        base='Win32GUI' if sys.platform == 'win32' else None,  # GUI application
        target_name='AVATAR_XML_File_Editor.exe',  # Name of the final executable
        icon='xml_editor_icon.ico',  # Converted icon file
    )
]

# Setup
setup(
    name='AVATAR XML Editor',
    version='2.0',
    description='XML Editor for binary xml files',
    author='Jasper_Zebra',
    options={'build_exe': build_options},
    executables=executables  # python setup.py build 
)