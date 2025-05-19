#!/usr/bin/env python3
"""
Game XML Editor - Main Entry Point

A dedicated editor for .game.xml files with conversion capabilities between
binary and readable XML formats.

Author: Generated for Level Editor Project
"""

from main_editor import GameXMLEditor


def main():
    """Main function to run the Game XML Editor"""
    try:
        editor = GameXMLEditor()
        editor.run()
    except KeyboardInterrupt:
        print("\nEditor closed by user.")
    except Exception as e:
        print(f"Error starting editor: {str(e)}")
        input("Press Enter to exit...")


if __name__ == "__main__":
    main()