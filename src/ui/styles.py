"""
Styles and themes for Claude Profile Manager UI

Modern color schemes and styling configurations.
"""

import tkinter as tk
from tkinter import ttk


class ModernTheme:
    """Ultra-modern design theme with enhanced visual appeal."""

    # Enhanced Color Palette - More sophisticated and modern
    COLORS = {
        # Primary brand colors - Modern blue with depth
        'primary': '#4f46e5',       # Indigo 600 - More sophisticated
        'primary_hover': '#4338ca',  # Indigo 700
        'primary_light': '#e0e7ff',  # Indigo 100
        'primary_dark': '#312e81',   # Indigo 800

        # Background hierarchy - Cleaner gradients
        'bg_primary': '#fefefe',     # Almost white with warmth
        'bg_secondary': '#f9fafb',   # Gray 50 - Subtle
        'bg_tertiary': '#f3f4f6',    # Gray 100 - Card backgrounds
        'bg_quaternary': '#e5e7eb',  # Gray 200 - Borders
        'bg_sidebar': '#f8fafc',     # Dedicated sidebar color

        # Text hierarchy - Better contrast and readability
        'text_primary': '#111827',   # Gray 900 - Main text
        'text_secondary': '#374151', # Gray 700 - Secondary text
        'text_tertiary': '#6b7280',  # Gray 500 - Muted text
        'text_quaternary': '#9ca3af', # Gray 400 - Placeholder
        'text_light': '#ffffff',     # White text on dark backgrounds

        # Status colors - More vibrant and clear
        'success': '#10b981',        # Emerald 500 - Brighter
        'success_bg': '#d1fae5',     # Emerald 100
        'success_border': '#a7f3d0', # Emerald 200

        'warning': '#f59e0b',        # Amber 500
        'warning_bg': '#fef3c7',     # Amber 100
        'warning_border': '#fde68a', # Amber 200

        'error': '#ef4444',          # Red 500
        'error_bg': '#fee2e2',       # Red 100
        'error_border': '#fecaca',   # Red 200

        'info': '#3b82f6',           # Blue 500
        'info_bg': '#dbeafe',        # Blue 100
        'info_border': '#bfdbfe',    # Blue 200

        # Interactive elements
        'interactive': '#6366f1',    # Indigo 500
        'interactive_hover': '#5b21b6', # Purple 800
        'interactive_light': '#f3f4f6', # Light interaction

        # Border system
        'border_light': '#f3f4f6',   # Light borders
        'border_medium': '#e5e7eb',  # Medium borders
        'border_strong': '#d1d5db',  # Strong borders
        'border_focus': '#4f46e5',   # Focus state
        'border_accent': '#a78bfa',  # Accent borders

        # Shadow system
        'shadow_light': '#0000000a',  # Light shadow
        'shadow_medium': '#0000001a', # Medium shadow
        'shadow_strong': '#0000002a', # Strong shadow

        # Card system
        'card_bg': '#ffffff',        # Pure white cards
        'card_hover': '#fefefe',     # Subtle hover
        'card_border': '#f3f4f6',    # Card borders
        'card_shadow': '#00000008',  # Card shadows
    }

    # Enhanced Typography System
    FONTS = {
        'display': ('Segoe UI', 18, 'bold'),     # Large titles
        'heading': ('Segoe UI', 16, 'bold'),     # Section headings
        'title': ('Segoe UI', 14, 'bold'),       # Component titles
        'subheading': ('Segoe UI', 12, 'bold'),  # Subsections
        'body': ('Segoe UI', 11),                # Main text (slightly larger)
        'body_medium': ('Segoe UI', 10),         # Secondary text
        'caption': ('Segoe UI', 9),              # Small text
        'micro': ('Segoe UI', 8),                # Micro text
        'button': ('Segoe UI', 10, '500'),       # Medium weight buttons
        'button_large': ('Segoe UI', 11, '500'), # Large buttons
    }

    # Enhanced Spacing System - More nuanced
    SPACING = {
        'none': 0,
        'xs': 4,     # Tight spacing
        'sm': 8,     # Small spacing
        'md': 12,    # Medium spacing
        'lg': 16,    # Large spacing
        'xl': 24,    # Extra large
        'xxl': 32,   # Double extra large
        'xxxl': 48,  # Triple extra large
        'huge': 64,  # Huge spacing
    }

    # Enhanced Component Sizing
    SIZES = {
        # Buttons
        'button_height_sm': 28,
        'button_height_md': 36,
        'button_height_lg': 44,
        'button_padding_x': 16,
        'button_padding_y': 8,

        # Inputs
        'input_height': 32,
        'input_padding': 12,

        # Cards and containers
        'card_padding': 20,
        'card_radius': 8,
        'sidebar_width': 280,

        # List items
        'row_height': 32,
        'row_padding': 12,

        # Icons and visual elements
        'icon_sm': 16,
        'icon_md': 20,
        'icon_lg': 24,

        # Borders
        'border_width': 1,
        'border_radius_sm': 4,
        'border_radius_md': 6,
        'border_radius_lg': 8,
    }


class StyleManager:
    """Manages application styling and themes."""

    def __init__(self, root: tk.Tk):
        """Initialize the style manager."""
        self.root = root
        self.style = ttk.Style()
        self.theme = ModernTheme()

        self._configure_root()
        self._setup_ttk_styles()

    def _configure_root(self):
        """Configure root window styling."""
        self.root.configure(
            bg=self.theme.COLORS['bg_primary']
        )

    def _setup_ttk_styles(self):
        """Setup TTK widget styles with modern, elegant design."""
        # Use a more modern base theme
        self.style.theme_use('clam')

        # Modern Treeview - Clean and elegant
        self.style.configure(
            'Modern.Treeview',
            background=self.theme.COLORS['card_bg'],
            foreground=self.theme.COLORS['text_primary'],
            fieldbackground=self.theme.COLORS['card_bg'],
            borderwidth=0,
            relief='flat',
            rowheight=self.theme.SIZES['row_height'] + 8,  # More spacious rows
            font=self.theme.FONTS['body'],
            indent=20  # Better indentation
        )

        # Treeview headers - Clean and modern
        self.style.configure(
            'Modern.Treeview.Heading',
            background=self.theme.COLORS['bg_tertiary'],
            foreground=self.theme.COLORS['text_secondary'],
            relief='flat',
            borderwidth=0,
            font=self.theme.FONTS['subheading'],
            padding=(12, 8)
        )

        # Primary Button - Modern gradient-like appearance
        self.style.configure(
            'Primary.TButton',
            background=self.theme.COLORS['primary'],
            foreground=self.theme.COLORS['text_light'],
            borderwidth=0,
            focuscolor='none',
            relief='flat',
            padding=(self.theme.SIZES['button_padding_x'], self.theme.SIZES['button_padding_y']),
            font=self.theme.FONTS['button_large'],
            borderradius=self.theme.SIZES['border_radius_md']
        )

        # Primary button hover states
        self.style.map(
            'Primary.TButton',
            background=[
                ('active', self.theme.COLORS['primary_hover']),
                ('pressed', self.theme.COLORS['primary_dark']),
                ('disabled', self.theme.COLORS['text_quaternary'])
            ],
            foreground=[
                ('disabled', self.theme.COLORS['text_tertiary'])
            ],
            relief=[('pressed', 'flat')]
        )

        # Secondary Button - Clean outline style
        self.style.configure(
            'Secondary.TButton',
            background=self.theme.COLORS['card_bg'],
            foreground=self.theme.COLORS['text_secondary'],
            borderwidth=1,
            relief='flat',
            focuscolor='none',
            padding=(self.theme.SIZES['button_padding_x'], self.theme.SIZES['button_padding_y']),
            font=self.theme.FONTS['button'],
            bordercolor=self.theme.COLORS['border_medium']
        )

        # Secondary button hover states
        self.style.map(
            'Secondary.TButton',
            background=[
                ('active', self.theme.COLORS['bg_tertiary']),
                ('pressed', self.theme.COLORS['bg_quaternary']),
                ('disabled', self.theme.COLORS['bg_secondary'])
            ],
            bordercolor=[
                ('active', self.theme.COLORS['border_strong']),
                ('pressed', self.theme.COLORS['primary']),
                ('disabled', self.theme.COLORS['border_light'])
            ],
            foreground=[
                ('active', self.theme.COLORS['text_primary']),
                ('disabled', self.theme.COLORS['text_quaternary'])
            ]
        )

        # Enhanced Card Frame with subtle shadow effect
        self.style.configure(
            'Card.TFrame',
            background=self.theme.COLORS['card_bg'],
            relief='flat',
            borderwidth=1,
            bordercolor=self.theme.COLORS['card_border']
        )

        # Elevated Card Frame for special sections
        self.style.configure(
            'ElevatedCard.TFrame',
            background=self.theme.COLORS['card_bg'],
            relief='raised',
            borderwidth=0,
            padding=self.theme.SIZES['card_padding']
        )

        # Modern Sidebar with gradient-like effect
        self.style.configure(
            'Sidebar.TFrame',
            background=self.theme.COLORS['bg_sidebar'],
            relief='flat',
            borderwidth=0
        )

        # Typography styles - More sophisticated
        self.style.configure(
            'Display.TLabel',
            background=self.theme.COLORS['bg_primary'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['display']
        )

        self.style.configure(
            'Heading.TLabel',
            background=self.theme.COLORS['bg_primary'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['heading']
        )

        self.style.configure(
            'Title.TLabel',
            background=self.theme.COLORS['bg_primary'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['title']
        )

        self.style.configure(
            'Subheading.TLabel',
            background=self.theme.COLORS['bg_primary'],
            foreground=self.theme.COLORS['text_secondary'],
            font=self.theme.FONTS['subheading']
        )

        self.style.configure(
            'Caption.TLabel',
            background=self.theme.COLORS['bg_primary'],
            foreground=self.theme.COLORS['text_tertiary'],
            font=self.theme.FONTS['caption']
        )

        # Status Labels with color coding
        self.style.configure(
            'Success.TLabel',
            background=self.theme.COLORS['success_bg'],
            foreground=self.theme.COLORS['success'],
            font=self.theme.FONTS['caption'],
            padding=(8, 4),
            relief='flat'
        )

        self.style.configure(
            'Warning.TLabel',
            background=self.theme.COLORS['warning_bg'],
            foreground=self.theme.COLORS['warning'],
            font=self.theme.FONTS['caption'],
            padding=(8, 4),
            relief='flat'
        )

        self.style.configure(
            'Error.TLabel',
            background=self.theme.COLORS['error_bg'],
            foreground=self.theme.COLORS['error'],
            font=self.theme.FONTS['caption'],
            padding=(8, 4),
            relief='flat'
        )

        # Modern Separator - Subtle and clean
        self.style.configure(
            'Modern.TSeparator',
            background=self.theme.COLORS['border_light']
        )

        # Accent Separator for sections
        self.style.configure(
            'Accent.TSeparator',
            background=self.theme.COLORS['primary'],
            thickness=2
        )

    def create_status_tag_colors(self, treeview: ttk.Treeview):
        """Configure status-based row colors for treeview with enhanced visual feedback."""
        # Active profile - Vibrant green highlight
        treeview.tag_configure(
            'active',
            background=self.theme.COLORS['success_bg'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['body']
        )

        # Expired profile - Subtle red highlight
        treeview.tag_configure(
            'expired',
            background=self.theme.COLORS['error_bg'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['body']
        )

        # Available profile - Clean default
        treeview.tag_configure(
            'available',
            background=self.theme.COLORS['card_bg'],
            foreground=self.theme.COLORS['text_primary'],
            font=self.theme.FONTS['body']
        )

        # Hover effect (when supported)
        treeview.tag_configure(
            'hover',
            background=self.theme.COLORS['bg_tertiary'],
            foreground=self.theme.COLORS['text_primary']
        )

    def create_card_frame(self, parent, elevated=False, **kwargs) -> ttk.Frame:
        """Create a styled card frame with optional elevation."""
        style = 'ElevatedCard.TFrame' if elevated else 'Card.TFrame'
        return ttk.Frame(parent, style=style, **kwargs)

    def create_sidebar_frame(self, parent, **kwargs) -> ttk.Frame:
        """Create a styled sidebar frame."""
        return ttk.Frame(parent, style='Sidebar.TFrame', **kwargs)

    def create_header_frame(self, parent, **kwargs) -> ttk.Frame:
        """Create a header frame with enhanced styling."""
        frame = ttk.Frame(parent, **kwargs)
        frame.configure(style='Card.TFrame')
        return frame

    def create_primary_button(self, parent, text: str, command=None, **kwargs) -> ttk.Button:
        """Create a primary styled button."""
        return ttk.Button(
            parent,
            text=text,
            command=command,
            style='Primary.TButton',
            **kwargs
        )

    def create_secondary_button(self, parent, text: str, command=None, **kwargs) -> ttk.Button:
        """Create a secondary styled button."""
        return ttk.Button(
            parent,
            text=text,
            command=command,
            style='Secondary.TButton',
            **kwargs
        )

    def create_heading_label(self, parent, text: str = None, **kwargs) -> ttk.Label:
        """Create a heading label."""
        label_kwargs = {'style': 'Heading.TLabel'}
        if text is not None:
            label_kwargs['text'] = text
        label_kwargs.update(kwargs)

        return ttk.Label(parent, **label_kwargs)

    def create_subheading_label(self, parent, text: str = None, **kwargs) -> ttk.Label:
        """Create a subheading label."""
        label_kwargs = {'style': 'Subheading.TLabel'}
        if text is not None:
            label_kwargs['text'] = text
        label_kwargs.update(kwargs)

        return ttk.Label(parent, **label_kwargs)

    def create_caption_label(self, parent, text: str = None, **kwargs) -> ttk.Label:
        """Create a caption label."""
        label_kwargs = {'style': 'Caption.TLabel'}
        if text is not None:
            label_kwargs['text'] = text
        label_kwargs.update(kwargs)

        return ttk.Label(parent, **label_kwargs)

    def create_modern_treeview(self, parent, **kwargs) -> ttk.Treeview:
        """Create a modern styled treeview."""
        tree = ttk.Treeview(parent, style='Modern.Treeview', **kwargs)
        self.create_status_tag_colors(tree)
        return tree

    def add_shadow_effect(self, widget, color='#00000020'):
        """Add a subtle shadow effect to a widget (simulation)."""
        # This is a basic shadow simulation - for real shadows you'd need a canvas
        pass

    @property
    def colors(self):
        """Get color palette."""
        return self.theme.COLORS

    @property
    def fonts(self):
        """Get font configuration."""
        return self.theme.FONTS

    @property
    def spacing(self):
        """Get spacing configuration."""
        return self.theme.SPACING

    @property
    def sizes(self):
        """Get size configuration."""
        return self.theme.SIZES