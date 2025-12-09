"""
Main Window for Claude Profile Manager

Contains the main application window and coordinates all UI components.
"""

import tkinter as tk
from tkinter import ttk, messagebox, simpledialog
import threading
from typing import Optional, List
from models.profile import Profile
from services.profile_manager import ProfileManager
from utils.validators import ProfileValidator
from .components import ProfileListFrame, ProfileDetailFrame, ActionButtonsFrame


class ClaudeProfileManagerApp:
    """Main application class for Claude Profile Manager."""

    def __init__(self):
        """Initialize the application."""
        self.root = tk.Tk()
        self.profile_manager = ProfileManager()
        self.selected_profile: Optional[Profile] = None

        self._setup_window()
        self._create_widgets()
        self._setup_layout()
        self._load_profiles()

    def _setup_window(self):
        """Setup the main window properties."""
        self.root.title("Claude Profile Manager")
        self.root.geometry("800x600")
        self.root.minsize(600, 400)

        # Configure grid weights for responsive layout
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)

        # Set window icon (if available)
        try:
            # You can add an icon file here
            # self.root.iconbitmap('icon.ico')
            pass
        except:
            pass

        # Center window on screen
        self.root.update_idletasks()
        x = (self.root.winfo_screenwidth() // 2) - (800 // 2)
        y = (self.root.winfo_screenheight() // 2) - (600 // 2)
        self.root.geometry(f"800x600+{x}+{y}")

    def _create_widgets(self):
        """Create all UI widgets."""
        # Main container
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky="nsew")
        main_frame.columnconfigure(0, weight=1)
        main_frame.rowconfigure(1, weight=1)

        # Title
        title_label = ttk.Label(
            main_frame,
            text="Claude Profile Manager",
            font=("Arial", 16, "bold")
        )
        title_label.grid(row=0, column=0, pady=(0, 20))

        # Content area
        content_frame = ttk.Frame(main_frame)
        content_frame.grid(row=1, column=0, sticky="nsew")
        content_frame.columnconfigure(0, weight=1)
        content_frame.columnconfigure(1, weight=1)
        content_frame.rowconfigure(0, weight=1)

        # Profile list (left side)
        self.profile_list_frame = ProfileListFrame(
            content_frame,
            on_selection_change=self._on_profile_selection_change
        )
        self.profile_list_frame.grid(row=0, column=0, sticky="nsew", padx=(0, 10))

        # Profile details (right side)
        self.profile_detail_frame = ProfileDetailFrame(content_frame)
        self.profile_detail_frame.grid(row=0, column=1, sticky="nsew")

        # Action buttons (bottom)
        callbacks = {
            'switch_profile': self._switch_to_selected_profile,
            'save_current': self._save_current_as_profile,
            'refresh': self._refresh_profiles,
            'rename_profile': self._rename_selected_profile,
            'delete_profile': self._delete_selected_profile
        }

        self.action_buttons_frame = ActionButtonsFrame(main_frame, callbacks)
        self.action_buttons_frame.grid(row=2, column=0, pady=(20, 0))

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        self.status_bar = ttk.Label(main_frame, textvariable=self.status_var, relief="sunken")
        self.status_bar.grid(row=3, column=0, sticky="ew", pady=(10, 0))

        # Menu bar
        self._create_menu()

    def _create_menu(self):
        """Create the application menu bar."""
        menubar = tk.Menu(self.root)
        self.root.config(menu=menubar)

        # File menu
        file_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="File", menu=file_menu)
        file_menu.add_command(label="Refresh Profiles", command=self._refresh_profiles)
        file_menu.add_separator()
        file_menu.add_command(label="Exit", command=self.root.quit)

        # Profile menu
        profile_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Profile", menu=profile_menu)
        profile_menu.add_command(label="Switch to Profile", command=self._switch_to_selected_profile)
        profile_menu.add_command(label="Save Current as...", command=self._save_current_as_profile)
        profile_menu.add_separator()
        profile_menu.add_command(label="Rename Profile", command=self._rename_selected_profile)
        profile_menu.add_command(label="Delete Profile", command=self._delete_selected_profile)

        # Help menu
        help_menu = tk.Menu(menubar, tearoff=0)
        menubar.add_cascade(label="Help", menu=help_menu)
        help_menu.add_command(label="About", command=self._show_about)

    def _setup_layout(self):
        """Setup the layout and configure grid weights."""
        pass  # Already handled in _create_widgets

    def _load_profiles(self):
        """Load all profiles from disk."""
        try:
            self._update_status("Loading profiles...")
            profiles = self.profile_manager.get_all_profiles()
            self.profile_list_frame.update_profiles(profiles)
            self._update_status(f"Loaded {len(profiles)} profiles")
        except Exception as e:
            self._update_status(f"Error loading profiles: {str(e)}")
            messagebox.showerror("Error", f"Failed to load profiles: {str(e)}")

    def _refresh_profiles(self):
        """Refresh the profile list."""
        self._load_profiles()

    def _on_profile_selection_change(self, profile: Optional[Profile]):
        """Handle profile selection change."""
        self.selected_profile = profile
        self.profile_detail_frame.update_profile(profile)

        if profile:
            self._update_status(f"Selected profile: {profile.name}")
        else:
            self._update_status("No profile selected")

    def _switch_to_selected_profile(self):
        """Switch to the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile to switch to.")
            return

        if not self.selected_profile.has_valid_credentials():
            result = messagebox.askyesno(
                "Expired Credentials",
                f"Profile '{self.selected_profile.name}' has expired credentials. "
                "Do you want to switch anyway?"
            )
            if not result:
                return

        try:
            self._update_status(f"Switching to profile: {self.selected_profile.name}")

            success = self.profile_manager.switch_to_profile(self.selected_profile.name)

            if success:
                self._update_status(f"Successfully switched to profile: {self.selected_profile.name}")
                messagebox.showinfo(
                    "Success",
                    f"Successfully switched to profile '{self.selected_profile.name}'"
                )
                # Refresh to show updated active status
                self._refresh_profiles()
            else:
                self._update_status("Failed to switch profile")
                messagebox.showerror(
                    "Error",
                    f"Failed to switch to profile '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Error switching profile: {str(e)}")
            messagebox.showerror("Error", f"Error switching profile: {str(e)}")

    def _save_current_as_profile(self):
        """Save current active credentials as a new profile."""
        # Get profile name from user
        profile_name = simpledialog.askstring(
            "Save Current Profile",
            "Enter a name for the new profile:"
        )

        if not profile_name:
            return

        # Validate profile name
        is_valid, error_msg = ProfileValidator.validate_profile_name(profile_name)
        if not is_valid:
            messagebox.showerror("Invalid Profile Name", error_msg)
            return

        # Check if profile already exists
        existing_profiles = [p.name for p in self.profile_manager.get_all_profiles()]
        if profile_name in existing_profiles:
            result = messagebox.askyesno(
                "Profile Exists",
                f"Profile '{profile_name}' already exists. Do you want to overwrite it?"
            )
            if not result:
                return

        try:
            self._update_status(f"Saving current credentials as profile: {profile_name}")

            success = self.profile_manager.save_current_as_profile(
                profile_name,
                overwrite=True
            )

            if success:
                self._update_status(f"Successfully saved profile: {profile_name}")
                messagebox.showinfo(
                    "Success",
                    f"Successfully saved current credentials as profile '{profile_name}'"
                )
                self._refresh_profiles()
            else:
                self._update_status("Failed to save profile")
                messagebox.showerror(
                    "Error",
                    f"Failed to save profile '{profile_name}'"
                )

        except Exception as e:
            self._update_status(f"Error saving profile: {str(e)}")
            messagebox.showerror("Error", f"Error saving profile: {str(e)}")

    def _rename_selected_profile(self):
        """Rename the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile to rename.")
            return

        # Get new name from user
        new_name = simpledialog.askstring(
            "Rename Profile",
            f"Enter new name for profile '{self.selected_profile.name}':",
            initialvalue=self.selected_profile.name
        )

        if not new_name or new_name == self.selected_profile.name:
            return

        # Validate new name
        is_valid, error_msg = ProfileValidator.validate_profile_name(new_name)
        if not is_valid:
            messagebox.showerror("Invalid Profile Name", error_msg)
            return

        try:
            self._update_status(f"Renaming profile: {self.selected_profile.name} -> {new_name}")

            success = self.profile_manager.rename_profile(self.selected_profile.name, new_name)

            if success:
                self._update_status(f"Successfully renamed profile to: {new_name}")
                messagebox.showinfo(
                    "Success",
                    f"Successfully renamed profile to '{new_name}'"
                )
                self._refresh_profiles()
            else:
                self._update_status("Failed to rename profile")
                messagebox.showerror(
                    "Error",
                    f"Failed to rename profile '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Error renaming profile: {str(e)}")
            messagebox.showerror("Error", f"Error renaming profile: {str(e)}")

    def _delete_selected_profile(self):
        """Delete the currently selected profile."""
        if not self.selected_profile:
            messagebox.showwarning("Warning", "Please select a profile to delete.")
            return

        # Confirm deletion
        result = messagebox.askyesno(
            "Confirm Deletion",
            f"Are you sure you want to delete profile '{self.selected_profile.name}'?\n\n"
            "This action cannot be undone."
        )

        if not result:
            return

        try:
            self._update_status(f"Deleting profile: {self.selected_profile.name}")

            success = self.profile_manager.delete_profile(self.selected_profile.name)

            if success:
                self._update_status(f"Successfully deleted profile: {self.selected_profile.name}")
                messagebox.showinfo(
                    "Success",
                    f"Successfully deleted profile '{self.selected_profile.name}'"
                )
                self.selected_profile = None
                self.profile_detail_frame.update_profile(None)
                self._refresh_profiles()
            else:
                self._update_status("Failed to delete profile")
                messagebox.showerror(
                    "Error",
                    f"Failed to delete profile '{self.selected_profile.name}'"
                )

        except Exception as e:
            self._update_status(f"Error deleting profile: {str(e)}")
            messagebox.showerror("Error", f"Error deleting profile: {str(e)}")

    def _show_about(self):
        """Show the about dialog."""
        about_text = (
            "Claude Profile Manager\n"
            "Version 1.0.0\n\n"
            "A tool for managing Claude CLI authentication profiles.\n"
            "Easily switch between different Claude accounts and sessions.\n\n"
            "Features:\n"
            "• Switch between profiles quickly\n"
            "• Save current credentials as new profiles\n"
            "• Manage profile names and credentials\n"
            "• Visual status indicators\n\n"
            "Built with Python and tkinter."
        )

        messagebox.showinfo("About Claude Profile Manager", about_text)

    def _update_status(self, message: str):
        """Update the status bar message."""
        self.status_var.set(message)
        self.root.update_idletasks()

    def switch_to_profile(self, profile_name: str):
        """Public method to switch to a profile (called from components)."""
        # Find the profile
        profiles = self.profile_manager.get_all_profiles()
        profile = next((p for p in profiles if p.name == profile_name), None)

        if profile:
            self.selected_profile = profile
            self._switch_to_selected_profile()

    def rename_profile(self, profile_name: str):
        """Public method to rename a profile (called from components)."""
        # Find the profile
        profiles = self.profile_manager.get_all_profiles()
        profile = next((p for p in profiles if p.name == profile_name), None)

        if profile:
            self.selected_profile = profile
            self._rename_selected_profile()

    def delete_profile(self, profile_name: str):
        """Public method to delete a profile (called from components)."""
        # Find the profile
        profiles = self.profile_manager.get_all_profiles()
        profile = next((p for p in profiles if p.name == profile_name), None)

        if profile:
            self.selected_profile = profile
            self._delete_selected_profile()

    def run(self):
        """Run the application main loop."""
        try:
            # Validate environment
            env_info = self.profile_manager.validate_environment()
            if not env_info['exists']:
                messagebox.showwarning(
                    "Claude Directory Not Found",
                    f"Claude directory not found at: {env_info['path']}\n\n"
                    "Please ensure Claude CLI is installed and has been used at least once."
                )

            self.root.mainloop()

        except KeyboardInterrupt:
            # Handle Ctrl+C gracefully
            self.root.quit()
        except Exception as e:
            messagebox.showerror("Application Error", f"An unexpected error occurred: {str(e)}")
        finally:
            try:
                self.root.destroy()
            except:
                pass