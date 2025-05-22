import os
import subprocess
import shutil
import xml.etree.ElementTree as ET


class GameXMLConverter:
    """Handles conversion of XML and .game.xml files between formats"""
    
    def __init__(self, tools_path="tools"):
        """Initialize the converter with paths to conversion tools"""
        self.tools_path = tools_path
        self.xml_converter_path = os.path.join(tools_path, "Gibbed.Dunia.ConvertXml.exe")
        
        # Excluded files that should not be converted
        self.excluded_files = [
            "_depload.xml",
            "moviedata.xml"
        ]
        
        # Check for tools and dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check if all required dependencies are available"""
        # Check main executable
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
    
    def should_exclude_file(self, file_path):
        """Check if a file should be excluded from conversion"""
        filename = os.path.basename(file_path)
        for excluded_file in self.excluded_files:
            if excluded_file in filename:
                return True
        return False
    
    def is_file_xml_format(self, file_path):
        """Check if a file is in readable XML format"""
        try:
            ET.parse(file_path)
            return True
        except ET.ParseError:
            return False
    
    def convert_to_readable(self, file_path):
        """Convert file to readable XML format"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        # Skip excluded files
        if self.should_exclude_file(file_path):
            return False, f"File {file_path} is excluded from conversion"
        
        try:
            # Check if already readable
            if self.is_file_xml_format(file_path):
                return True, "File is already in readable XML format"
            
            print(f"DEBUG: Converting file: {file_path}")
            
            # Determine conversion paths
            base, ext = os.path.splitext(file_path)
            print(f"DEBUG: Base: {base}, Extension: {ext}")
            
            if ext == '.rml':
                # For .rml files, create corresponding .xml file
                xml_path = base + '.xml'
                rml_path = file_path
            elif ext == '.game.xml':
                rml_path = base + '.rml'
                xml_path = file_path
            elif ext == '.xml':
                rml_path = base + '.rml'
                xml_path = file_path
            else:
                rml_path = file_path + '.rml'
                xml_path = file_path.replace(ext, '.xml')
            
            print(f"DEBUG: RML path: {rml_path}")
            print(f"DEBUG: XML path: {xml_path}")
            
            # For .rml files, we don't need to backup/move - just convert directly
            if ext == '.rml':
                # Use absolute paths with forward slashes
                abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
                abs_xml_path = os.path.abspath(xml_path).replace("\\", "/")
                
                print(f"DEBUG: Converting RML to XML")
                print(f"DEBUG: Command: {self.xml_converter_path} --xml {abs_rml_path} {abs_xml_path}")
                
                # Run conversion
                process = subprocess.run(
                    [self.xml_converter_path, "--xml", abs_rml_path, abs_xml_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )
                
                print(f"DEBUG: Return code: {process.returncode}")
                print(f"DEBUG: Stdout: {process.stdout}")
                print(f"DEBUG: Stderr: {process.stderr}")
                
                # Check conversion result
                if process.returncode != 0:
                    return False, f"Conversion failed: {process.stderr}"
                
                # Check if output file was created
                if not os.path.exists(xml_path):
                    return False, f"Conversion appeared to succeed but output file not found: {xml_path}"
                
                return True, f"Successfully converted RML to readable XML: {abs_xml_path}"
            
            else:
                # Original logic for .game.xml files
                # Backup original file
                if os.path.exists(rml_path):
                    os.remove(rml_path)
                shutil.move(file_path, rml_path)
                
                # Use absolute paths with forward slashes
                abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
                abs_xml_path = os.path.abspath(xml_path).replace("\\", "/")
                
                # Run conversion
                process = subprocess.run(
                    [self.xml_converter_path, "--xml", abs_rml_path, abs_xml_path],
                    stdout=subprocess.PIPE,
                    stderr=subprocess.PIPE,
                    text=True,
                    timeout=30
                )
                
                # Check conversion result
                if process.returncode != 0:
                    # Restore original file on failure
                    shutil.move(rml_path, file_path)
                    return False, f"Conversion failed: {process.stderr}"
                
                # Clean up intermediate file
                if os.path.exists(rml_path):
                    os.remove(rml_path)
                
                return True, f"Successfully converted to readable XML format: {abs_xml_path}"
                
        except subprocess.TimeoutExpired:
            return False, "Conversion timed out - file may be too large or corrupted"
        except FileNotFoundError as e:
            return False, f"File not found: {str(e)}"
        except PermissionError as e:
            return False, f"Permission denied: {str(e)}"
        except Exception as e:
            return False, f"Error during conversion: {str(e)}"
        
    def save_as_binary(self, file_path):
        """Convert readable XML back to binary format"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        # Skip excluded files
        if self.should_exclude_file(file_path):
            return False, f"File {file_path} is excluded from conversion"
        
        try:
            # Create backup of readable XML - REMOVED THIS PART
            # backup_path = file_path + ".readable.bak"
            # shutil.copy2(file_path, backup_path)
            
            # Determine conversion paths
            base, ext = os.path.splitext(file_path)
            if ext == '.game.xml':
                rml_path = base + '.rml'
            elif ext == '.xml':
                rml_path = base + '.rml'
            else:
                rml_path = file_path + '.rml'
            
            # Use absolute paths with forward slashes
            abs_xml_path = os.path.abspath(file_path).replace("\\", "/")
            abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
            
            # Run conversion
            process = subprocess.run(
                [self.xml_converter_path, "--rml", abs_xml_path, abs_rml_path],
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=30
            )
            
            # Check conversion result
            if process.returncode != 0:
                return False, f"Conversion to binary failed: {process.stderr}"
            
            # Replace original with binary version
            if os.path.exists(file_path):
                os.remove(file_path)
            shutil.move(rml_path, file_path)
            
            # Modified success message to not mention readable backup
            return True, f"Successfully saved as binary format."
            
        except Exception as e:
            return False, f"Error during save: {str(e)}"