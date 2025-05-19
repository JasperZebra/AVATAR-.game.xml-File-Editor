import os
import subprocess
import shutil
import xml.etree.ElementTree as ET


class GameXMLConverter:
    """Handles conversion of .game.xml files between binary and XML formats"""
    
    def __init__(self, tools_path="tools"):
        """Initialize the converter with paths to conversion tools"""
        self.tools_path = tools_path
        self.xml_converter_path = os.path.join(tools_path, "Gibbed.Dunia.ConvertXml.exe")
        
        # Check for tools and dependencies
        self.check_dependencies()
        
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        self.xml_converter_exists = os.path.exists(self.xml_converter_path)
        
        # Check required DLLs
        required_dlls = [
            "Gibbed.Dunia.FileFormats.dll",
            "NDesk.Options.dll",
            "Gibbed.IO.dll",
            "Gibbed.ProjectData.dll"
        ]
        
        self.missing_dlls = []
        for dll in required_dlls:
            dll_path = os.path.join(self.tools_path, dll)
            if not os.path.exists(dll_path):
                self.missing_dlls.append(dll)
        
        # Determine if conversion is possible
        self.can_convert = self.xml_converter_exists and not self.missing_dlls
        
        if not self.can_convert:
            print(f"WARNING: Conversion disabled due to missing dependencies")
            if not self.xml_converter_exists:
                print(f"  - Missing: {self.xml_converter_path}")
            if self.missing_dlls:
                print(f"  - Missing DLLs: {', '.join(self.missing_dlls)}")
    
    def is_file_xml_format(self, file_path):
        """Check if a .game.xml file is in readable XML format"""
        try:
            ET.parse(file_path)
            return True
        except ET.ParseError:
            return False
    
    def convert_to_readable(self, game_xml_path):
        """Convert binary .game.xml to readable XML format"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        try:
            # Check if already readable
            if self.is_file_xml_format(game_xml_path):
                return True, "File is already in readable XML format"
            
            # Rename .game.xml to .game.rml (it's actually binary)
            rml_path = game_xml_path.replace(".game.xml", ".game.rml")
            
            # Backup original file
            if os.path.exists(rml_path):
                os.remove(rml_path)
            shutil.move(game_xml_path, rml_path)
            
            # Convert RML to readable XML
            abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
            abs_xml_path = os.path.abspath(game_xml_path).replace("\\", "/")
            
            process = subprocess.run(
                [self.xml_converter_path, "--xml", abs_rml_path, abs_xml_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=10
            )
            
            if process.returncode != 0:
                # Restore original file on failure
                shutil.move(rml_path, game_xml_path)
                return False, f"Conversion failed: {process.stderr}"
            
            # Clean up intermediate file
            if os.path.exists(rml_path):
                os.remove(rml_path)
            
            return True, "Successfully converted to readable XML format"
            
        except Exception as e:
            return False, f"Error during conversion: {str(e)}"
    
    def save_as_binary(self, game_xml_path):
        """Convert readable XML back to binary .game.xml format"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        try:
            # Create backup of readable XML
            backup_path = game_xml_path + ".readable.bak"
            shutil.copy2(game_xml_path, backup_path)
            
            # Convert XML to RML
            rml_path = game_xml_path.replace(".game.xml", ".game.rml")
            
            abs_xml_path = os.path.abspath(game_xml_path).replace("\\", "/")
            abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
            
            process = subprocess.run(
                [self.xml_converter_path, "--rml", abs_xml_path, abs_rml_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            if process.returncode != 0:
                return False, f"Conversion to binary failed: {process.stderr}"
            
            # Replace original with binary version
            if os.path.exists(game_xml_path):
                os.remove(game_xml_path)
            shutil.move(rml_path, game_xml_path)
            
            return True, f"Successfully saved as binary format. Readable backup: {backup_path}"
            
        except Exception as e:
            return False, f"Error during save: {str(e)}"