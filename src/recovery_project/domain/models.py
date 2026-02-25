from dataclasses import dataclass
from datetime import datetime


@dataclass(slots=True)
class User:
    user_id: str
    email: str
    password_hash: str
    mfa_enabled: bool = False


@dataclass(slots=True)
class RecoveryToken:
    user_id: str
    token_value: str
    created_at: datetime
    expires_at: datetime
    used: bool = False


@dataclass(slots=True)
class RecoveryAttempt:
    user_id: str
    guessed_token: str
    timestamp: datetime
    success: bool
    blocked_by_rate_limit: bool = False
