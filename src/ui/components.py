"""
UI Components for Claude Profile Manager

Contains reusable UI components and widgets.
"""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import List, Callable, Optional, Dict, Any
from models.profile import Profile
from utils.formatters import StatusFormatter, TimeFormatter
from .styles import StyleManager


class ProfileListFrame(ttk.Frame):
    """Frame containing the list of profiles."""

    def __init__(self, parent, on_selection_change: Optional[Callable] = None):
        """
        Initialize the profile list frame.

        Args:
            parent: Parent widget
            on_selection_change: Callback when selection changes
        """
        super().__init__(parent)
        self.on_selection_change = on_selection_change
        self.profiles: List[Profile] = []

        self._create_widgets()

    def _create_widgets(self):
        """Create the widgets for the profile list."""
        # Title
        title_label = ttk.Label(self, text="Claude Profiles", font=("Arial", 12, "bold"))
        title_label.pack(pady=(0, 10))

        # Profile list with scrollbar
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)

        # Create treeview for profiles
        columns = ("Name", "Status", "Subscription", "Expires")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", height=10)

        # Define column headers and widths
        self.tree.heading("Name", text="Profile Name")
        self.tree.heading("Status", text="Status")
        self.tree.heading("Subscription", text="Subscription")
        self.tree.heading("Expires", text="Expires In")

        self.tree.column("Name", width=120, anchor="w")
        self.tree.column("Status", width=100, anchor="center")
        self.tree.column("Subscription", width=80, anchor="center")
        self.tree.column("Expires", width=100, anchor="center")

        # Scrollbar
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)

        # Pack treeview and scrollbar
        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)

        # Bind selection event
        self.tree.bind("<<TreeviewSelect>>", self._on_tree_select)

        # Context menu for right-click
        self.context_menu = tk.Menu(self, tearoff=0)
        self.context_menu.add_command(label="Switch to Profile", command=self._switch_to_selected)
        self.context_menu.add_separator()
        self.context_menu.add_command(label="Rename Profile", command=self._rename_selected)
        self.context_menu.add_command(label="Delete Profile", command=self._delete_selected)

        self.tree.bind("<Button-3>", self._show_context_menu)  # Right click

    def _on_tree_select(self, event):
        """Handle tree selection change."""
        if self.on_selection_change:
            selected_profile = self.get_selected_profile()
            self.on_selection_change(selected_profile)

    def _show_context_menu(self, event):
        """Show context menu on right click."""
        # Select the item under cursor
        item = self.tree.identify_row(event.y)
        if item:
            self.tree.selection_set(item)
            self.context_menu.post(event.x_root, event.y_root)

    def _switch_to_selected(self):
        """Switch to selected profile."""
        profile = self.get_selected_profile()
        if profile and hasattr(self.master, 'switch_to_profile'):
            self.master.switch_to_profile(profile.name)

    def _rename_selected(self):
        """Rename selected profile."""
        profile = self.get_selected_profile()
        if profile and hasattr(self.master, 'rename_profile'):
            self.master.rename_profile(profile.name)

    def _delete_selected(self):
        """Delete selected profile."""
        profile = self.get_selected_profile()
        if profile and hasattr(self.master, 'delete_profile'):
            self.master.delete_profile(profile.name)

    def update_profiles(self, profiles: List[Profile]):
        """Update the profile list."""
        self.profiles = profiles

        # Clear existing items
        for item in self.tree.get_children():
            self.tree.delete(item)

        # Add profiles to tree
        for profile in profiles:
            status = "🟢 Active" if profile.is_active else ("🔴 Expired" if not profile.has_valid_credentials() else "⚪ Available")

            subscription = ""
            expires_text = ""

            if profile.credential:
                subscription = StatusFormatter.format_subscription_type(
                    profile.credential.claude_ai_oauth.subscription_type
                )
                expires_text = TimeFormatter.format_expires_in_hours(
                    profile.credential.claude_ai_oauth.expires_in_hours()
                )

            # Use tags for different row colors
            tags = []
            if profile.is_active:
                tags.append("active")
            elif not profile.has_valid_credentials():
                tags.append("expired")

            self.tree.insert("", "end", values=(
                profile.name,
                status,
                subscription,
                expires_text
            ), tags=tags)

        # Configure tags for styling
        self.tree.tag_configure("active", background="#e8f5e8")
        self.tree.tag_configure("expired", background="#ffe8e8")

    def get_selected_profile(self) -> Optional[Profile]:
        """Get the currently selected profile."""
        selection = self.tree.selection()
        if not selection:
            return None

        item = selection[0]
        values = self.tree.item(item, "values")
        if not values:
            return None

        profile_name = values[0]
        return next((p for p in self.profiles if p.name == profile_name), None)


class ProfileDetailFrame(ttk.Frame):
    """Frame showing detailed information about selected profile."""

    def __init__(self, parent):
        """Initialize the profile detail frame."""
        super().__init__(parent)
        self.current_profile: Optional[Profile] = None

        self._create_widgets()

    def _create_widgets(self):
        """Create the widgets for profile details."""
        # Title
        self.title_label = ttk.Label(self, text="Profile Details", font=("Arial", 12, "bold"))
        self.title_label.pack(pady=(0, 10))

        # Details frame with labels
        details_frame = ttk.Frame(self)
        details_frame.pack(fill=tk.BOTH, expand=True, padx=10)

        # Profile info labels
        self.name_var = tk.StringVar(value="No profile selected")
        self.status_var = tk.StringVar()
        self.subscription_var = tk.StringVar()
        self.expires_var = tk.StringVar()
        self.scopes_var = tk.StringVar()

        ttk.Label(details_frame, text="Profile Name:", font=("Arial", 9, "bold")).grid(
            row=0, column=0, sticky="w", padx=(0, 10), pady=2
        )
        ttk.Label(details_frame, textvariable=self.name_var).grid(
            row=0, column=1, sticky="w", pady=2
        )

        ttk.Label(details_frame, text="Status:", font=("Arial", 9, "bold")).grid(
            row=1, column=0, sticky="w", padx=(0, 10), pady=2
        )
        ttk.Label(details_frame, textvariable=self.status_var).grid(
            row=1, column=1, sticky="w", pady=2
        )

        ttk.Label(details_frame, text="Subscription:", font=("Arial", 9, "bold")).grid(
            row=2, column=0, sticky="w", padx=(0, 10), pady=2
        )
        ttk.Label(details_frame, textvariable=self.subscription_var).grid(
            row=2, column=1, sticky="w", pady=2
        )

        ttk.Label(details_frame, text="Expires:", font=("Arial", 9, "bold")).grid(
            row=3, column=0, sticky="w", padx=(0, 10), pady=2
        )
        ttk.Label(details_frame, textvariable=self.expires_var).grid(
            row=3, column=1, sticky="w", pady=2
        )

        ttk.Label(details_frame, text="Scopes:", font=("Arial", 9, "bold")).grid(
            row=4, column=0, sticky="nw", padx=(0, 10), pady=2
        )
        scopes_label = ttk.Label(details_frame, textvariable=self.scopes_var, wraplength=200)
        scopes_label.grid(row=4, column=1, sticky="w", pady=2)

    def update_profile(self, profile: Optional[Profile]):
        """Update the displayed profile information."""
        self.current_profile = profile

        if profile is None:
            self.name_var.set("No profile selected")
            self.status_var.set("")
            self.subscription_var.set("")
            self.expires_var.set("")
            self.scopes_var.set("")
            return

        # Update profile information
        self.name_var.set(profile.name)

        if profile.credential:
            # Status
            status = StatusFormatter.format_profile_status(
                profile.is_active,
                profile.has_valid_credentials(),
                profile.credential.claude_ai_oauth.expires_in_hours()
            )
            self.status_var.set(status)

            # Subscription
            subscription = StatusFormatter.format_subscription_type(
                profile.credential.claude_ai_oauth.subscription_type
            )
            self.subscription_var.set(subscription)

            # Expires
            expires = TimeFormatter.format_expires_in_hours(
                profile.credential.claude_ai_oauth.expires_in_hours()
            )
            self.expires_var.set(expires)

            # Scopes
            scopes = StatusFormatter.format_scopes(
                profile.credential.claude_ai_oauth.scopes
            )
            self.scopes_var.set(scopes)
        else:
            self.status_var.set("No credentials")
            self.subscription_var.set("Unknown")
            self.expires_var.set("Unknown")
            self.scopes_var.set("Unknown")


class ActionButtonsFrame(ttk.Frame):
    """Frame containing action buttons."""

    def __init__(self, parent, callbacks: Dict[str, Callable]):
        """
        Initialize the action buttons frame.

        Args:
            parent: Parent widget
            callbacks: Dictionary of callback functions
        """
        super().__init__(parent)
        self.callbacks = callbacks

        self._create_widgets()

    def _create_widgets(self):
        """Create action buttons."""
        # Main action buttons
        ttk.Button(
            self,
            text="Switch to Profile",
            command=self.callbacks.get('switch_profile', lambda: None)
        ).pack(side=tk.LEFT, padx=(0, 5))

        ttk.Button(
            self,
            text="Save Current as...",
            command=self.callbacks.get('save_current', lambda: None)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self,
            text="Refresh",
            command=self.callbacks.get('refresh', lambda: None)
        ).pack(side=tk.LEFT, padx=5)

        # Separator
        ttk.Separator(self, orient="vertical").pack(side=tk.LEFT, fill=tk.Y, padx=10)

        # Management buttons
        ttk.Button(
            self,
            text="Rename",
            command=self.callbacks.get('rename_profile', lambda: None)
        ).pack(side=tk.LEFT, padx=5)

        ttk.Button(
            self,
            text="Delete",
            command=self.callbacks.get('delete_profile', lambda: None)
        ).pack(side=tk.LEFT, padx=5)