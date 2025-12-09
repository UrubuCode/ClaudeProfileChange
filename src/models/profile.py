"""
Profile Model

Represents a Claude user profile with name and credentials.
"""

import os
from pathlib import Path
from typing import Optional
from .credential import ClaudeCredential


class Profile:
    """Represents a Claude user profile."""

    def __init__(self, name: str, credential: Optional[ClaudeCredential] = None):
        """
        Initialize a profile.

        Args:
            name: Profile name (used for filename)
            credential: Claude credential information
        """
        self.name = name
        self.credential = credential

    @property
    def filename(self) -> str:
        """Get the filename for this profile."""
        return f"{self.name}.credentials.json"

    @property
    def is_active(self) -> bool:
        """Check if this profile is currently active."""
        from services.profile_manager import ProfileManager
        try:
            active_profile = ProfileManager.get_active_profile()
            return (
                active_profile is not None and
                active_profile.name == self.name and
                active_profile.credential is not None and
                self.credential is not None and
                active_profile.credential.to_json() == self.credential.to_json()
            )
        except Exception:
            return False

    def has_valid_credentials(self) -> bool:
        """Check if the profile has valid credentials."""
        return self.credential is not None and self.credential.is_valid()

    def get_status_text(self) -> str:
        """Get a status text for UI display."""
        if not self.credential:
            return "No credentials"

        if self.is_active:
            return "Active • " + self.credential.get_user_info()
        else:
            return self.credential.get_user_info()

    def get_display_name(self) -> str:
        """Get display name for UI."""
        if self.is_active:
            return f"● {self.name}"
        return self.name

    def __str__(self) -> str:
        """String representation."""
        return f"Profile({self.name}, valid={self.has_valid_credentials()})"

    def __repr__(self) -> str:
        """Detailed string representation."""
        return f"Profile(name='{self.name}', credential={self.credential is not None})"