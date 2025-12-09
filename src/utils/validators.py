"""
Validation utilities for Claude Profile Manager.
"""

import re
from typing import List, Optional


class ProfileValidator:
    """Validates profile names and other input data."""

    # Valid profile name pattern: alphanumeric, hyphens, underscores
    VALID_NAME_PATTERN = re.compile(r'^[a-zA-Z0-9_-]+$')

    # Reserved names that cannot be used as profile names
    RESERVED_NAMES = {
        'con', 'prn', 'aux', 'nul',  # Windows reserved
        'com1', 'com2', 'com3', 'com4', 'com5', 'com6', 'com7', 'com8', 'com9',
        'lpt1', 'lpt2', 'lpt3', 'lpt4', 'lpt5', 'lpt6', 'lpt7', 'lpt8', 'lpt9',
        'credentials', 'config', 'settings'  # Claude reserved
    }

    @classmethod
    def validate_profile_name(cls, name: str) -> tuple[bool, Optional[str]]:
        """
        Validate a profile name.

        Returns:
            tuple: (is_valid, error_message)
        """
        if not name:
            return False, "Profile name cannot be empty"

        if len(name) < 1:
            return False, "Profile name must be at least 1 character long"

        if len(name) > 50:
            return False, "Profile name must be 50 characters or less"

        if not cls.VALID_NAME_PATTERN.match(name):
            return False, "Profile name can only contain letters, numbers, hyphens, and underscores"

        if name.lower() in cls.RESERVED_NAMES:
            return False, f"'{name}' is a reserved name and cannot be used"

        if name.startswith('.'):
            return False, "Profile name cannot start with a dot"

        if name.endswith('.'):
            return False, "Profile name cannot end with a dot"

        # Check for consecutive special characters
        if '--' in name or '__' in name or '-_' in name or '_-' in name:
            return False, "Profile name cannot contain consecutive special characters"

        return True, None

    @classmethod
    def sanitize_profile_name(cls, name: str) -> str:
        """
        Sanitize a profile name by removing invalid characters.

        Args:
            name: Raw profile name

        Returns:
            Sanitized profile name
        """
        if not name:
            return ""

        # Remove invalid characters
        sanitized = re.sub(r'[^a-zA-Z0-9_-]', '_', name)

        # Remove leading/trailing dots and special characters
        sanitized = sanitized.strip('._-')

        # Replace consecutive special characters
        sanitized = re.sub(r'[-_]{2,}', '_', sanitized)

        # Ensure it doesn't exceed max length
        if len(sanitized) > 50:
            sanitized = sanitized[:50]

        # Ensure it's not a reserved name
        if sanitized.lower() in cls.RESERVED_NAMES:
            sanitized += "_profile"

        return sanitized

    @classmethod
    def suggest_profile_names(cls, base_name: str, existing_names: List[str]) -> List[str]:
        """
        Suggest available profile names based on a base name.

        Args:
            base_name: The desired base name
            existing_names: List of existing profile names

        Returns:
            List of suggested available names
        """
        suggestions = []
        sanitized_base = cls.sanitize_profile_name(base_name)

        if not sanitized_base:
            sanitized_base = "profile"

        # First, try the sanitized base name
        if sanitized_base not in existing_names:
            suggestions.append(sanitized_base)

        # Generate numbered variations
        for i in range(1, 10):
            candidate = f"{sanitized_base}_{i}"
            if candidate not in existing_names:
                suggestions.append(candidate)

        # Generate suffix variations
        suffixes = ['new', 'alt', 'backup', 'copy']
        for suffix in suffixes:
            candidate = f"{sanitized_base}_{suffix}"
            if candidate not in existing_names and candidate not in suggestions:
                suggestions.append(candidate)

        return suggestions[:5]  # Return up to 5 suggestions