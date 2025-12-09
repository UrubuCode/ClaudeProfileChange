"""
Profile Manager Service

Main service for managing Claude profiles and switching between them.
"""

from typing import List, Optional, Dict, Any
from models.credential import ClaudeCredential
from models.profile import Profile
from .file_manager import FileManager


class ProfileManager:
    """Manages Claude profiles and credentials."""

    def __init__(self):
        """Initialize ProfileManager."""
        self.file_manager = FileManager()

    def get_all_profiles(self) -> List[Profile]:
        """Get all available profiles."""
        profiles = []
        profile_names = self.file_manager.get_profile_files()

        for name in profile_names:
            credential = self.file_manager.get_profile_credentials(name)
            profile = Profile(name, credential)
            profiles.append(profile)

        return profiles

    @staticmethod
    def get_active_profile() -> Optional[Profile]:
        """Get the currently active profile."""
        file_manager = FileManager()
        active_credential = file_manager.get_active_credentials()

        if active_credential is None:
            return None

        # Try to find which profile matches the active credentials
        profile_names = file_manager.get_profile_files()

        for name in profile_names:
            profile_credential = file_manager.get_profile_credentials(name)
            if (profile_credential is not None and
                profile_credential.to_json() == active_credential.to_json()):
                return Profile(name, profile_credential)

        # If no profile matches, create a temporary profile
        return Profile("unknown", active_credential)

    def switch_to_profile(self, profile_name: str) -> bool:
        """Switch to a specific profile."""
        try:
            # Get the profile credentials
            credential = self.file_manager.get_profile_credentials(profile_name)
            if credential is None:
                print(f"Profile '{profile_name}' not found")
                return False

            # Validate the credential
            if not credential.is_valid():
                print(f"Profile '{profile_name}' has expired credentials")
                return False

            # Set as active
            success = self.file_manager.set_active_credentials(credential)
            if success:
                print(f"Successfully switched to profile '{profile_name}'")
            else:
                print(f"Failed to switch to profile '{profile_name}'")

            return success

        except Exception as e:
            print(f"Error switching to profile '{profile_name}': {e}")
            return False

    def save_current_as_profile(self, profile_name: str, overwrite: bool = False) -> bool:
        """Save current active credentials as a new profile."""
        try:
            # Check if profile already exists
            if self.file_manager.profile_exists(profile_name) and not overwrite:
                print(f"Profile '{profile_name}' already exists")
                return False

            # Get current active credentials
            active_credential = self.file_manager.get_active_credentials()
            if active_credential is None:
                print("No active credentials found")
                return False

            # Save as profile
            success = self.file_manager.save_profile_credentials(profile_name, active_credential)
            if success:
                print(f"Successfully saved current credentials as profile '{profile_name}'")
            else:
                print(f"Failed to save profile '{profile_name}'")

            return success

        except Exception as e:
            print(f"Error saving profile '{profile_name}': {e}")
            return False

    def delete_profile(self, profile_name: str) -> bool:
        """Delete a profile."""
        try:
            if not self.file_manager.profile_exists(profile_name):
                print(f"Profile '{profile_name}' does not exist")
                return False

            success = self.file_manager.delete_profile_credentials(profile_name)
            if success:
                print(f"Successfully deleted profile '{profile_name}'")
            else:
                print(f"Failed to delete profile '{profile_name}'")

            return success

        except Exception as e:
            print(f"Error deleting profile '{profile_name}': {e}")
            return False

    def rename_profile(self, old_name: str, new_name: str) -> bool:
        """Rename a profile."""
        try:
            # Check if old profile exists
            if not self.file_manager.profile_exists(old_name):
                print(f"Profile '{old_name}' does not exist")
                return False

            # Check if new name already exists
            if self.file_manager.profile_exists(new_name):
                print(f"Profile '{new_name}' already exists")
                return False

            # Get credentials from old profile
            credential = self.file_manager.get_profile_credentials(old_name)
            if credential is None:
                print(f"Could not read credentials from profile '{old_name}'")
                return False

            # Save with new name
            if not self.file_manager.save_profile_credentials(new_name, credential):
                print(f"Failed to save profile '{new_name}'")
                return False

            # Delete old profile
            if not self.file_manager.delete_profile_credentials(old_name):
                print(f"Failed to delete old profile '{old_name}'")
                # Try to clean up the new profile
                self.file_manager.delete_profile_credentials(new_name)
                return False

            print(f"Successfully renamed profile '{old_name}' to '{new_name}'")
            return True

        except Exception as e:
            print(f"Error renaming profile '{old_name}' to '{new_name}': {e}")
            return False

    def get_profile_info(self, profile_name: str) -> Optional[Dict[str, Any]]:
        """Get detailed information about a profile."""
        try:
            credential = self.file_manager.get_profile_credentials(profile_name)
            if credential is None:
                return None

            profile = Profile(profile_name, credential)

            return {
                "name": profile_name,
                "is_active": profile.is_active,
                "is_valid": credential.is_valid(),
                "subscription_type": credential.claude_ai_oauth.subscription_type,
                "expires_at": credential.claude_ai_oauth.expires_at,
                "expires_in_hours": credential.claude_ai_oauth.expires_in_hours(),
                "scopes": credential.claude_ai_oauth.scopes,
                "rate_limit_tier": credential.claude_ai_oauth.rate_limit_tier,
                "status_text": profile.get_status_text()
            }

        except Exception as e:
            print(f"Error getting profile info for '{profile_name}': {e}")
            return None

    def validate_environment(self) -> Dict[str, Any]:
        """Validate the environment and Claude directory setup."""
        return self.file_manager.get_claude_directory_info()