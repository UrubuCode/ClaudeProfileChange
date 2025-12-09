"""
UI package for Claude Profile Manager

Contains all user interface components and windows.
"""

from .main_window import ClaudeProfileManagerApp
from .components import ProfileListFrame, ProfileDetailFrame, ActionButtonsFrame
from .styles import StyleManager, ModernTheme

__all__ = [
    "ClaudeProfileManagerApp",
    "ProfileListFrame",
    "ProfileDetailFrame",
    "ActionButtonsFrame",
    "StyleManager",
    "ModernTheme"
]