"""
Claude Credential Model

Represents a Claude authentication credential with OAuth information.
"""

import json
from dataclasses import dataclass, asdict
from typing import List, Dict, Any, Optional
from datetime import datetime


@dataclass
class ClaudeOAuthInfo:
    """OAuth information for Claude authentication."""
    access_token: str
    refresh_token: str
    expires_at: int
    scopes: List[str]
    subscription_type: str
    rate_limit_tier: str

    def is_expired(self) -> bool:
        """Check if the token is expired."""
        current_time = int(datetime.now().timestamp() * 1000)
        return current_time >= self.expires_at

    def expires_in_hours(self) -> float:
        """Return hours until token expires."""
        current_time = int(datetime.now().timestamp() * 1000)
        diff_ms = self.expires_at - current_time
        return max(0, diff_ms / (1000 * 60 * 60))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format matching Claude's credentials file."""
        return {
            "accessToken": self.access_token,
            "refreshToken": self.refresh_token,
            "expiresAt": self.expires_at,
            "scopes": self.scopes,
            "subscriptionType": self.subscription_type,
            "rateLimitTier": self.rate_limit_tier
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClaudeOAuthInfo':
        """Create instance from dictionary."""
        return cls(
            access_token=data["accessToken"],
            refresh_token=data["refreshToken"],
            expires_at=data["expiresAt"],
            scopes=data["scopes"],
            subscription_type=data["subscriptionType"],
            rate_limit_tier=data["rateLimitTier"]
        )


@dataclass
class ClaudeCredential:
    """Complete Claude credential information."""
    claude_ai_oauth: ClaudeOAuthInfo

    def to_json(self) -> str:
        """Convert to JSON string matching Claude's credentials format."""
        data = {
            "claudeAiOauth": self.claude_ai_oauth.to_dict()
        }
        return json.dumps(data, separators=(',', ':'))

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary format."""
        return {
            "claudeAiOauth": self.claude_ai_oauth.to_dict()
        }

    @classmethod
    def from_json(cls, json_str: str) -> 'ClaudeCredential':
        """Create instance from JSON string."""
        try:
            data = json.loads(json_str)
            return cls.from_dict(data)
        except (json.JSONDecodeError, KeyError) as e:
            raise ValueError(f"Invalid credential JSON format: {e}")

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'ClaudeCredential':
        """Create instance from dictionary."""
        oauth_data = data["claudeAiOauth"]
        oauth_info = ClaudeOAuthInfo.from_dict(oauth_data)
        return cls(claude_ai_oauth=oauth_info)

    def is_valid(self) -> bool:
        """Check if the credential is valid (not expired and has required fields)."""
        return (
            self.claude_ai_oauth.access_token and
            self.claude_ai_oauth.refresh_token and
            not self.claude_ai_oauth.is_expired()
        )

    def get_user_info(self) -> str:
        """Get user-friendly information about the credential."""
        status = "Valid" if self.is_valid() else "Expired"
        hours_left = self.claude_ai_oauth.expires_in_hours()
        subscription = self.claude_ai_oauth.subscription_type.title()

        return f"{subscription} • {status} • {hours_left:.1f}h remaining"