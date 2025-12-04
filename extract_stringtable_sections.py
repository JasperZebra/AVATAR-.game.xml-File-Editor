#!/usr/bin/env python3
"""
Extract and group stringtable sections from an XML file into separate XML files.
Each section will be saved as a separate XML file with proper structure.
"""

import xml.etree.ElementTree as ET
import os
from pathlib import Path


def sanitize_filename(name):
    """
    Convert section name to a safe filename.
    
    Args:
        name: Section name
        
    Returns:
        Sanitized filename
    """
    # Replace spaces and special characters
    safe_name = name.replace(" ", "_").replace("/", "_")
    return f"{safe_name}.xml"


def extract_sections(input_file, output_dir="extract_strings"):
    """
    Extract sections from a stringtable XML file and save each to a separate file.
    
    Args:
        input_file: Path to the input XML file
        output_dir: Directory where output files will be saved
    """
    # Create output directory if it doesn't exist
    Path(output_dir).mkdir(parents=True, exist_ok=True)
    
    # Parse the XML file
    try:
        tree = ET.parse(input_file)
        root = tree.getroot()
    except ET.ParseError as e:
        print(f"Error parsing XML file: {e}")
        return
    except FileNotFoundError:
        print(f"Error: File '{input_file}' not found")
        return
    
    # Find all section elements
    sections = root.findall('.//section')
    
    if not sections:
        print("No sections found in the XML file")
        return
    
    print(f"Found {len(sections)} sections")
    
    # Process each section
    for section in sections:
        section_name = section.get('name')
        
        if not section_name:
            print("Warning: Found section without name attribute, skipping...")
            continue
        
        # Count strings in this section
        strings = section.findall('string')
        string_count = len(strings)
        
        print(f"Processing section: '{section_name}' ({string_count} strings)")
        
        # Create a new XML structure for this section
        new_root = ET.Element('stringtable')
        new_section = ET.SubElement(new_root, 'section')
        new_section.set('name', section_name)
        
        # Copy all string elements to the new section
        for string_elem in strings:
            # Create a copy of the string element
            new_string = ET.SubElement(new_section, 'string')
            
            # Copy attributes
            if string_elem.get('enum'):
                new_string.set('enum', string_elem.get('enum'))
            if string_elem.get('value'):
                new_string.set('value', string_elem.get('value'))
            
            # Copy any other attributes
            for attr_name, attr_value in string_elem.attrib.items():
                if attr_name not in ['enum', 'value']:
                    new_string.set(attr_name, attr_value)
        
        # Create the output filename
        output_filename = sanitize_filename(section_name)
        output_path = os.path.join(output_dir, output_filename)
        
        # Create the tree and write to file
        new_tree = ET.ElementTree(new_root)
        ET.indent(new_tree, space="    ")  # Pretty print with 4-space indentation
        
        try:
            new_tree.write(output_path, encoding='utf-8', xml_declaration=True)
            print(f"  ✓ Saved to: {output_path}")
        except Exception as e:
            print(f"  ✗ Error saving {output_path}: {e}")
    
    print(f"\nExtraction complete! Files saved to '{output_dir}' directory")


def main():
    """Main function to handle command line usage and drag-and-drop."""
    import sys
    
    # Check if a file was provided (drag-and-drop or command line)
    if len(sys.argv) < 2:
        # No file provided - prompt user
        print("=" * 60)
        print("STRING TABLE SECTION EXTRACTOR")
        print("=" * 60)
        print("\nNo file provided!")
        print("\nTo use this script:")
        print("1. Drag and drop an XML file onto this script")
        print("2. Or run: python extract_stringtable_sections.py <file.xml>")
        print("\nPress Enter to exit...")
        input()
        return
    
    input_file = sys.argv[1]
    output_dir = sys.argv[2] if len(sys.argv) > 2 else "extract_strings"
    
    print("=" * 60)
    print("STRING TABLE SECTION EXTRACTOR")
    print("=" * 60)
    print(f"\nInput file: {input_file}")
    print(f"Output directory: {output_dir}")
    print("-" * 60)
    
    extract_sections(input_file, output_dir)
    
    print("\n" + "=" * 60)
    print("Press Enter to exit...")
    input()


if __name__ == "__main__":
    main()