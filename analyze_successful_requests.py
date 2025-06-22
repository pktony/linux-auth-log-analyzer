#!/usr/bin/env python3
"""
Simple runner script for successful request analysis
"""
import sys
from pathlib import Path

# Add src to path
src_path = Path(__file__).parent / "src"
sys.path.insert(0, str(src_path))

from successful_request_analyzer_main import main

if __name__ == "__main__":
    main() 