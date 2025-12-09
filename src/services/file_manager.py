"""
File Manager Service

Handles file operations for Claude credentials and profiles.
"""

import os
import shutil
import json
from pathlib import Path
from typing import List, Optional, Dict, Any
from models.credential import ClaudeCredential
from models.profile import Profile


class FileManager:
    """Manages file operations for Claude profiles."""

    def __init__(self):
        """Initialize FileManager with Claude directory path."""
        self.claude_dir = self._get_claude_directory()
        self.active_credentials_file = self.claude_dir / ".credentials.json"

    def _get_claude_directory(self) -> Path:
        """Get the Claude directory path."""
        # Default Claude directory location
        home_dir = Path.home()
        claude_dir = home_dir / ".claude"

        if not claude_dir.exists():
            # Try alternative locations
            if os.name == 'nt':  # Windows
                claude_dir = Path(os.environ.get('USERPROFILE', home_dir)) / ".claude"

        return claude_dir

    def ensure_claude_directory_exists(self) -> bool:
        """Ensure Claude directory exists."""
        try:
            self.claude_dir.mkdir(parents=True, exist_ok=True)
            return True
        except Exception as e:
            print(f"Error creating Claude directory: {e}")
            return False

    def get_profile_files(self) -> List[str]:
        """Get list of profile credential files."""
        if not self.claude_dir.exists():
            return []

        profile_files = []
        for file_path in self.claude_dir.glob("*.credentials.json"):
            # Skip the active credentials file
            if file_path.name != ".credentials.json":
                # Extract profile name from filename
                profile_name = file_path.stem.replace(".credentials", "")
                profile_files.append(profile_name)

        return sorted(profile_files)

    def read_credential_file(self, file_path: Path) -> Optional[ClaudeCredential]:
        """Read and parse a credential file."""
        try:
            if not file_path.exists():
                return None

            with open(file_path, 'r', encoding='utf-8') as file:
                content = file.read().strip()
                if not content:
                    return None

                return ClaudeCredential.from_json(content)

        except Exception as e:
            print(f"Error reading credential file {file_path}: {e}")
            return None

    def write_credential_file(self, file_path: Path, credential: ClaudeCredential) -> bool:
        """Write credential to file."""
        try:
            self.ensure_claude_directory_exists()

            with open(file_path, 'w', encoding='utf-8') as file:
                file.write(credential.to_json())

            return True

        except Exception as e:
            print(f"Error writing credential file {file_path}: {e}")
            return False

    def get_active_credentials(self) -> Optional[ClaudeCredential]:
        """Get the currently active credentials."""
        return self.read_credential_file(self.active_credentials_file)

    def set_active_credentials(self, credential: ClaudeCredential) -> bool:
        """Set the active credentials."""
        return self.write_credential_file(self.active_credentials_file, credential)

    def get_profile_credentials(self, profile_name: str) -> Optional[ClaudeCredential]:
        """Get credentials for a specific profile."""
        file_path = self.claude_dir / f"{profile_name}.credentials.json"
        return self.read_credential_file(file_path)

    def save_profile_credentials(self, profile_name: str, credential: ClaudeCredential) -> bool:
        """Save credentials for a specific profile."""
        file_path = self.claude_dir / f"{profile_name}.credentials.json"
        return self.write_credential_file(file_path, credential)

    def delete_profile_credentials(self, profile_name: str) -> bool:
        """Delete credentials for a specific profile."""
        try:
            file_path = self.claude_dir / f"{profile_name}.credentials.json"
            if file_path.exists():
                file_path.unlink()
            return True

        except Exception as e:
            print(f"Error deleting profile credentials: {e}")
            return False

    def backup_active_credentials(self, backup_name: str) -> bool:
        """Create a backup of current active credentials."""
        try:
            if not self.active_credentials_file.exists():
                return False

            active_credential = self.get_active_credentials()
            if active_credential is None:
                return False

            return self.save_profile_credentials(backup_name, active_credential)

        except Exception as e:
            print(f"Error backing up active credentials: {e}")
            return False

    def profile_exists(self, profile_name: str) -> bool:
        """Check if a profile exists."""
        file_path = self.claude_dir / f"{profile_name}.credentials.json"
        return file_path.exists()

    def get_claude_directory_info(self) -> Dict[str, Any]:
        """Get information about the Claude directory."""
        return {
            "path": str(self.claude_dir),
            "exists": self.claude_dir.exists(),
            "is_writable": os.access(self.claude_dir, os.W_OK) if self.claude_dir.exists() else False,
            "active_credentials_exists": self.active_credentials_file.exists()
        }