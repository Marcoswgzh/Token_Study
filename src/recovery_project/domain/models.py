#class written by

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

#written by Erika Škodová
@dataclass(slots=True)
class TrialResult:
    trial_id: int
    experiment_name: str
    token_length: int
    alphabet_size: int
    ttl_seconds: int
    rate_limit_enabled: bool
    rate_limit_max_attempts: int
    rate_limit_window_seconds: int
    success: bool
    attempts_made: int
    attempts_blocked: int
    time_elapsed_ms: float
    token_expired: bool
    timestamp: str
