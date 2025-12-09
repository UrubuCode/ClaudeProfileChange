"""
Formatting utilities for Claude Profile Manager.
"""

from datetime import datetime, timezone
from typing import Optional


class TimeFormatter:
    """Formats time-related information."""

    @staticmethod
    def format_expires_at(expires_at_ms: int) -> str:
        """Format expiration timestamp to human-readable string."""
        try:
            # Convert milliseconds to seconds
            expires_at = datetime.fromtimestamp(expires_at_ms / 1000, tz=timezone.utc)
            now = datetime.now(tz=timezone.utc)

            if expires_at <= now:
                return "Expired"

            diff = expires_at - now
            days = diff.days
            hours = diff.seconds // 3600
            minutes = (diff.seconds % 3600) // 60

            if days > 0:
                return f"{days}d {hours}h"
            elif hours > 0:
                return f"{hours}h {minutes}m"
            else:
                return f"{minutes}m"

        except (ValueError, OSError):
            return "Unknown"

    @staticmethod
    def format_expires_in_hours(hours: float) -> str:
        """Format hours until expiration to human-readable string."""
        if hours <= 0:
            return "Expired"

        if hours < 1:
            minutes = int(hours * 60)
            return f"{minutes}m"
        elif hours < 24:
            return f"{hours:.1f}h"
        else:
            days = int(hours / 24)
            remaining_hours = int(hours % 24)
            if remaining_hours > 0:
                return f"{days}d {remaining_hours}h"
            else:
                return f"{days}d"

    @staticmethod
    def format_datetime(timestamp_ms: int) -> str:
        """Format timestamp to readable datetime string."""
        try:
            dt = datetime.fromtimestamp(timestamp_ms / 1000)
            return dt.strftime("%Y-%m-%d %H:%M")
        except (ValueError, OSError):
            return "Unknown"


class StatusFormatter:
    """Formats status information for display."""

    @staticmethod
    def format_subscription_type(subscription_type: str) -> str:
        """Format subscription type for display."""
        return subscription_type.replace('_', ' ').title()

    @staticmethod
    def format_rate_limit_tier(tier: str) -> str:
        """Format rate limit tier for display."""
        return tier.replace('_', ' ').title()

    @staticmethod
    def format_scopes(scopes: list) -> str:
        """Format scopes list for display."""
        if not scopes:
            return "No scopes"

        # Shorten common scope prefixes
        formatted_scopes = []
        for scope in scopes:
            if scope.startswith('user:'):
                formatted_scopes.append(scope[5:])  # Remove 'user:' prefix
            else:
                formatted_scopes.append(scope)

        return ", ".join(formatted_scopes)

    @staticmethod
    def format_profile_status(is_active: bool, is_valid: bool, hours_remaining: Optional[float] = None) -> str:
        """Format overall profile status."""
        if is_active:
            if not is_valid:
                return "🔴 Active (Expired)"
            else:
                time_str = ""
                if hours_remaining is not None:
                    time_str = f" ({TimeFormatter.format_expires_in_hours(hours_remaining)})"
                return f"🟢 Active{time_str}"
        else:
            if not is_valid:
                return "🔴 Expired"
            else:
                time_str = ""
                if hours_remaining is not None:
                    time_str = f" ({TimeFormatter.format_expires_in_hours(hours_remaining)})"
                return f"⚪ Available{time_str}"

    @staticmethod
    def get_status_color(is_active: bool, is_valid: bool) -> str:
        """Get color code for status display."""
        if is_active and is_valid:
            return "green"
        elif is_active and not is_valid:
            return "red"
        elif not is_active and is_valid:
            return "blue"
        else:
            return "gray"