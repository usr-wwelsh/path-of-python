"""
Resource path helper for PyInstaller bundled executables.

This module provides utilities to correctly resolve file paths whether
running in development mode or as a bundled executable.
"""
import os
import sys


def get_base_path():
    """
    Get the base path for the application.

    Returns:
        str: Base directory path that works in both dev and bundled modes
    """
    if getattr(sys, 'frozen', False):
        # Running as bundled executable (PyInstaller)
        # PyInstaller creates a temp folder and stores path in _MEIPASS
        return sys._MEIPASS
    else:
        # Running in development mode
        # Go up one level from utility/ to get to project root
        return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def resource_path(relative_path):
    """
    Get absolute path to resource, works for dev and for PyInstaller.

    Args:
        relative_path (str): Path relative to project root

    Returns:
        str: Absolute path to the resource

    Example:
        >>> resource_path('graphics/gui/cursor.png')
        'C:/path/to/game/graphics/gui/cursor.png'  # in dev
        'C:/Users/.../Temp/_MEI12345/graphics/gui/cursor.png'  # bundled
    """
    base = get_base_path()
    return os.path.join(base, relative_path)


# For convenience, also export the base path
BASE_PATH = get_base_path()
