"""Executable entry point for NEXUS Smart Resource Monitor."""
import sys
import os

# Ensure the root directory is on Python's module search path
sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from src.nexus.app import run

if __name__ == "__main__":
    sys.exit(run())
