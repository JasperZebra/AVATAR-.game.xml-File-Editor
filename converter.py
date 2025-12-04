import os
import subprocess
import shutil
import xml.etree.ElementTree as ET


class GameXMLConverter:
    """Handles conversion of XML and .game.xml files between formats using multiple converter tools"""
    
    def __init__(self, tools_path="tools"):
        """Initialize the converter with paths to conversion tools"""
        self.tools_path = tools_path
        
        # Define available converter tools
        self.converter_definitions = [
            {
                "name": "Gibbed Far Cry 2 Converter", 
                "exe": "Gibbed.FarCry2.ConvertXMLResource.exe",
                "syntax": "simple",  # input.rml output.xml
                "games": ["Avatar: The Game", "Far Cry 2"],
                "priority": 1  # Higher priority for Avatar files
            },
            {
                "name": "Gibbed Dunia Converter",
                "exe": "Gibbed.Dunia.ConvertXml.exe", 
                "syntax": "flags",   # --xml input.rml output.xml
                "games": ["Far Cry 3", "Far Cry 4", "Far Cry 5", "Far Cry 6", "Other Dunia games"],
                "priority": 2
            }
        ]
        
        # Excluded files that should not be converted
        self.excluded_files = [
            "_depload.xml",
            "moviedata.xml",
            "_deploadnewparticles_",  # Prefix for particle files
            ".preload.xml"
        ]
        
        # Check for tools and dependencies
        self.check_dependencies()
    
    def check_dependencies(self):
        """Check if conversion tools and dependencies are available"""
        self.available_converters = []
        
        # Check each converter tool
        for converter_info in self.converter_definitions:
            exe_path = os.path.join(self.tools_path, converter_info["exe"])
            if os.path.exists(exe_path):
                converter_copy = converter_info.copy()
                converter_copy["path"] = exe_path
                self.available_converters.append(converter_copy)
                print(f"Found converter: {converter_info['name']}")
            else:
                print(f"Missing converter: {converter_info['name']} ({converter_info['exe']})")
        
        # Sort by priority (lower number = higher priority)
        self.available_converters.sort(key=lambda x: x["priority"])
        
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
        self.can_convert = len(self.available_converters) > 0 and not self.missing_dlls
        
        # Report status
        if not self.can_convert:
            print(f"WARNING: Conversion disabled due to missing dependencies")
            if not self.available_converters:
                print(f"  - No converter executables found in: {self.tools_path}")
                for conv_def in self.converter_definitions:
                    print(f"    Missing: {conv_def['exe']}")
            if self.missing_dlls:
                print(f"  - Missing DLLs: {', '.join(self.missing_dlls)}")
        else:
            print(f"Conversion enabled with {len(self.available_converters)} tool(s):")
            for conv in self.available_converters:
                games_str = ", ".join(conv["games"][:2])  # Show first 2 games
                if len(conv["games"]) > 2:
                    games_str += f" and {len(conv['games'])-2} more"
                print(f"  - {conv['name']} (supports: {games_str})")
    
    def get_available_tools_info(self):
        """Get information about available conversion tools"""
        if not self.can_convert:
            return "No conversion tools available"
        
        tool_names = [conv["name"] for conv in self.available_converters]
        return f"Available: {', '.join(tool_names)}"
    
    def should_exclude_file(self, file_path):
        """Check if a file should be excluded from conversion"""
        filename = os.path.basename(file_path).lower()
        for excluded_file in self.excluded_files:
            if excluded_file.lower() in filename:
                return True
        return False
    
    def is_file_xml_format(self, file_path):
        """Check if a file is in readable XML format"""
        try:
            with open(file_path, 'rb') as f:
                # Read first few bytes to check for XML declaration or tags
                header = f.read(100)
                
                # Check for XML declaration or opening tag
                if b'<?xml' in header or b'<' in header[:10]:
                    # Try to parse as XML
                    try:
                        ET.parse(file_path)
                        return True
                    except ET.ParseError:
                        return False
                else:
                    # Likely binary format
                    return False
        except Exception:
            return False
    
    def detect_file_type(self, file_path):
        """Detect the type of file and suggest best converter"""
        filename = os.path.basename(file_path).lower()
        
        # Check file extension and content
        if filename.endswith('.rml'):
            return "rml_binary"
        elif filename.endswith('.game.xml'):
            if self.is_file_xml_format(file_path):
                return "game_xml_readable"
            else:
                return "game_xml_binary"
        elif filename.endswith('.xml'):
            if self.is_file_xml_format(file_path):
                return "xml_readable"
            else:
                return "xml_binary"
        else:
            return "unknown"
    
    def convert_to_readable(self, file_path):
        """Convert file to readable XML format using available tools"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        # Skip excluded files
        if self.should_exclude_file(file_path):
            return False, f"File {os.path.basename(file_path)} is excluded from conversion"
        
        # Check if already readable
        if self.is_file_xml_format(file_path):
            return True, "File is already in readable XML format"
        
        print(f"DEBUG: Converting file: {file_path}")
        file_type = self.detect_file_type(file_path)
        print(f"DEBUG: Detected file type: {file_type}")
        
        # Determine conversion paths
        base, ext = os.path.splitext(file_path)
        print(f"DEBUG: Base: {base}, Extension: {ext}")
        
        if ext.lower() == '.rml':
            # For .rml files, create corresponding .xml file
            xml_path = base + '.xml'
            rml_path = file_path
            conversion_mode = "rml_to_xml"
        elif ext.lower() in ['.game.xml', '.xml']:
            # For XML files that are actually binary, backup and convert
            rml_path = base + '.rml'
            xml_path = file_path
            conversion_mode = "binary_xml_to_readable"
        else:
            rml_path = file_path + '.rml'
            xml_path = file_path.replace(ext, '.xml')
            conversion_mode = "unknown_to_xml"
        
        print(f"DEBUG: Conversion mode: {conversion_mode}")
        print(f"DEBUG: RML path: {rml_path}")
        print(f"DEBUG: XML path: {xml_path}")
        
        # Try conversion with available tools
        last_error = None
        for converter in self.available_converters:
            print(f"DEBUG: Trying conversion with {converter['name']}...")
            
            try:
                success, message = self._try_converter_conversion(
                    rml_path, xml_path, converter, conversion_mode, file_path
                )
                
                if success:
                    print(f"DEBUG: Conversion successful with {converter['name']}")
                    return True, f"Successfully converted using {converter['name']}: {message}"
                else:
                    print(f"DEBUG: Conversion failed with {converter['name']}: {message}")
                    last_error = message
                    
            except Exception as e:
                error_msg = f"Error with {converter['name']}: {str(e)}"
                print(f"DEBUG: {error_msg}")
                last_error = error_msg
        
        # All converters failed
        return False, f"All conversion attempts failed. Last error: {last_error}"
    
    def _try_converter_conversion(self, rml_path, xml_path, converter, conversion_mode, original_file):
        """Try conversion with a specific converter"""
        try:
            # Handle different conversion modes
            if conversion_mode == "rml_to_xml":
                input_path = rml_path
                output_path = xml_path
            elif conversion_mode == "binary_xml_to_readable":
                # Backup original file first
                if os.path.exists(rml_path):
                    os.remove(rml_path)
                shutil.move(original_file, rml_path)
                input_path = rml_path
                output_path = xml_path
            else:
                input_path = rml_path
                output_path = xml_path
            
            # Use absolute paths with forward slashes for better compatibility
            abs_input_path = os.path.abspath(input_path).replace("\\", "/")
            abs_output_path = os.path.abspath(output_path).replace("\\", "/")
            
            # Build command based on converter syntax
            if converter["syntax"] == "simple":
                # Far Cry 2 style: exe input.rml output.xml
                cmd = [converter["path"], abs_input_path, abs_output_path]
            else:
                # Dunia style: exe --xml input.rml output.xml  
                cmd = [converter["path"], "--xml", abs_input_path, abs_output_path]
            
            print(f"DEBUG: Running command: {' '.join(cmd)}")
            
            # Run conversion process
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,  # Increased timeout for large files
                cwd=self.tools_path  # Run from tools directory
            )
            
            print(f"DEBUG: Return code: {process.returncode}")
            print(f"DEBUG: Stdout: {process.stdout}")
            print(f"DEBUG: Stderr: {process.stderr}")
            
            # Check conversion result
            if process.returncode != 0:
                # Restore original file if we moved it
                if conversion_mode == "binary_xml_to_readable" and os.path.exists(rml_path):
                    shutil.move(rml_path, original_file)
                return False, f"Converter returned error code {process.returncode}: {process.stderr}"
            
            # Verify output file was created and is valid
            if not os.path.exists(output_path):
                if conversion_mode == "binary_xml_to_readable" and os.path.exists(rml_path):
                    shutil.move(rml_path, original_file)
                return False, f"Output file was not created: {output_path}"
            
            # Verify the output is valid XML
            try:
                ET.parse(output_path)
            except ET.ParseError as e:
                if conversion_mode == "binary_xml_to_readable" and os.path.exists(rml_path):
                    shutil.move(rml_path, original_file)
                return False, f"Generated XML is invalid: {str(e)}"
            
            # Clean up intermediate files for binary XML conversion
            if conversion_mode == "binary_xml_to_readable" and os.path.exists(rml_path):
                os.remove(rml_path)
            
            return True, f"Successfully converted to readable XML: {abs_output_path}"
            
        except subprocess.TimeoutExpired:
            return False, "Conversion timed out - file may be too large or corrupted"
        except FileNotFoundError as e:
            return False, f"File not found during conversion: {str(e)}"
        except PermissionError as e:
            return False, f"Permission denied during conversion: {str(e)}"
        except Exception as e:
            return False, f"Unexpected error during conversion: {str(e)}"
    
    def save_as_binary(self, file_path):
        """Convert readable XML back to binary format using available tools"""
        if not self.can_convert:
            return False, "Conversion tools not available"
        
        # Skip excluded files
        if self.should_exclude_file(file_path):
            return False, f"File {os.path.basename(file_path)} is excluded from conversion"
        
        print(f"DEBUG: Converting XML to binary: {file_path}")
        
        # Check if this is the special oasisstrings case
        filename = os.path.basename(file_path).lower()
        is_oasisstrings = filename == 'oasisstrings.xml'
        
        # Determine conversion paths
        base, ext = os.path.splitext(file_path)
        if ext.lower() == '.game.xml':
            rml_path = base + '.rml'
        elif ext.lower() == '.xml':
            rml_path = base + '.rml'
        else:
            rml_path = file_path + '.rml'
        
        # Try conversion with available tools
        last_error = None
        for converter in self.available_converters:
            print(f"DEBUG: Trying binary conversion with {converter['name']}...")
            
            try:
                success, message = self._try_converter_to_binary(
                    file_path, rml_path, converter, is_oasisstrings
                )
                
                if success:
                    print(f"DEBUG: Binary conversion successful with {converter['name']}")
                    return True, f"Successfully saved as binary using {converter['name']}"
                else:
                    print(f"DEBUG: Binary conversion failed with {converter['name']}: {message}")
                    last_error = message
                    
            except Exception as e:
                error_msg = f"Error during binary conversion with {converter['name']}: {str(e)}"
                print(f"DEBUG: {error_msg}")
                last_error = error_msg
        
        return False, f"All binary conversion attempts failed. Last error: {last_error}"
    
    def _try_converter_to_binary(self, xml_path, rml_path, converter, is_oasisstrings=False):
        """Try converting XML to binary with a specific converter"""
        try:
            # Use absolute paths with forward slashes
            abs_xml_path = os.path.abspath(xml_path).replace("\\", "/")
            abs_rml_path = os.path.abspath(rml_path).replace("\\", "/")
            
            # Build command based on converter syntax
            if converter["syntax"] == "simple":
                # Far Cry 2 style might not support reverse conversion easily
                # Try the command anyway, but this might fail
                cmd = [converter["path"], abs_xml_path, abs_rml_path]
            else:
                # Dunia style: exe --rml input.xml output.rml
                cmd = [converter["path"], "--rml", abs_xml_path, abs_rml_path]
            
            print(f"DEBUG: Running binary conversion command: {' '.join(cmd)}")
            
            # Run conversion process
            process = subprocess.run(
                cmd,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                timeout=60,
                cwd=self.tools_path
            )
            
            print(f"DEBUG: Binary conversion return code: {process.returncode}")
            print(f"DEBUG: Binary conversion stdout: {process.stdout}")
            print(f"DEBUG: Binary conversion stderr: {process.stderr}")
            
            # Check conversion result
            if process.returncode != 0:
                return False, f"Binary converter returned error code {process.returncode}: {process.stderr}"
            
            # Check if output file was created
            if not os.path.exists(rml_path):
                return False, f"Binary output file was not created: {rml_path}"
            
            # Special handling for oasisstrings file
            if is_oasisstrings:
                # For oasisstrings: keep binary as .rml, delete the .xml
                if os.path.exists(xml_path):
                    os.remove(xml_path)
                # rml_path already has the binary file, no need to move/rename
                print(f"DEBUG: oasisstrings special case - kept as .rml")
                return True, f"Successfully converted oasisstrings to binary .rml format."
            else:
                # Normal behavior: replace XML with binary version
                if os.path.exists(xml_path):
                    # Keep a backup of the original XML
                    backup_path = xml_path + ".xml_backup"
                    if os.path.exists(backup_path):
                        os.remove(backup_path)
                    shutil.copy2(xml_path, backup_path)
                    
                    # Replace with binary version
                    os.remove(xml_path)
                    shutil.move(rml_path, xml_path)
                
                return True, f"Successfully converted to binary format."
            
        except subprocess.TimeoutExpired:
            return False, "Binary conversion timed out"
        except Exception as e:
            return False, f"Error during binary conversion: {str(e)}"

    def get_converter_info(self):
        """Get detailed information about available converters"""
        info = {
            "can_convert": self.can_convert,
            "tools_path": self.tools_path,
            "available_converters": self.available_converters,
            "missing_dlls": self.missing_dlls,
            "excluded_files": self.excluded_files
        }
        return info
    
    def test_conversion_capability(self, test_file_path=None):
        """Test conversion capability with a sample file or general availability"""
        if not self.can_convert:
            return False, "No conversion tools available"
        
        if test_file_path and os.path.exists(test_file_path):
            # Test with specific file
            file_type = self.detect_file_type(test_file_path)
            is_readable = self.is_file_xml_format(test_file_path)
            
            return True, f"File type: {file_type}, Readable: {is_readable}, Tools available: {len(self.available_converters)}"
        else:
            # General capability test
            tool_names = [conv["name"] for conv in self.available_converters]
            return True, f"Conversion ready with tools: {', '.join(tool_names)}"