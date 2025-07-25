#!/usr/bin/env python3
"""
Rock Paper Scissors GUI Client Launcher
Run this script to start the GUI version of the game client.
"""

import sys
import os

# Add current directory to path
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

from gui_client import main

if __name__ == "__main__":
    print("🎮 Starting Rock Paper Scissors GUI Client...")
    main()
