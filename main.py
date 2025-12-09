#!/usr/bin/env python3
"""
Claude Profile Manager - Main Entry Point

A GUI application for managing Claude CLI profiles and switching between them.
Allows users to save, load, and switch between different Claude authentication profiles.
"""

import sys
import os
from pathlib import Path

# Add src directory to Python path
current_dir = Path(__file__).parent
src_dir = current_dir / "src"
sys.path.insert(0, str(src_dir))

def main():
    """Main entry point for the application."""
    try:
        from ui.main_window import ClaudeProfileManagerApp

        # Create and run the application
        app = ClaudeProfileManagerApp()
        app.run()

    except ImportError as e:
        print(f"Error importing modules: {e}")
        print("Please ensure all dependencies are installed.")
        sys.exit(1)
    except Exception as e:
        print(f"Unexpected error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()