"""Small in-memory rate limiter for the recovery workflow."""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime, timedelta


@dataclass
class AttemptBucket:
    # store all attempts that still count for the current time window
    attempts: list[datetime] = field(default_factory=list)
    # if this is not None, user should wait until this time before trying again
    locked_until: datetime | None = None


class RateLimiter:
    # Sofya Grishkova - i6397764
    def __init__(self, max_attempts: int = 5, window_seconds: int = 60) -> None:
        # max attempts allowed inside one window
        self.max_attempts = max_attempts
        # how long the window lasts, in seconds
        self.window_seconds = window_seconds
        # key is usually email, value is the attempts for this user
        self._buckets: dict[str, AttemptBucket] = {}

    # Sofya Grishkova - i6397764
    def is_locked(self, key: str) -> bool:
        # if there is no bucket for this user, there is nothing to block
        bucket = self._buckets.get(key)
        if not bucket or bucket.locked_until is None:
            return False

        # if lockout time is still in the future, user is blocked
        if datetime.now() < bucket.locked_until:
            return True

        # lockout already ended, so clean the old record
        del self._buckets[key]
        return False

    # Sofya Grishkova - i6397764
    def record_failure(self, key: str) -> None:
        now = datetime.now()
        bucket = self._buckets.setdefault(key, AttemptBucket())

        # remove attempts that are older than the current window
        window_start = now - timedelta(seconds=self.window_seconds)
        bucket.attempts = [attempt for attempt in bucket.attempts if attempt >= window_start]

        # add the current failed attempt
        bucket.attempts.append(now)

        # lock the user if too many attempts happened in the same window
        if len(bucket.attempts) >= self.max_attempts:
            bucket.locked_until = now + timedelta(seconds=self.window_seconds)

    # Sofya Grishkova - i6397764
    def record_success(self, key: str) -> None:
        # on success we reset failed attempts, because user proved they had the right token
        self._buckets.pop(key, None)

    # Sofya Grishkova - i6397764
    def get_remaining_lockout_time(self, key: str) -> str | None:
        # used by UI to show a readable waiting time
        bucket = self._buckets.get(key)
        if not bucket or bucket.locked_until is None:
            return None

        remaining = bucket.locked_until - datetime.now()
        total_seconds = max(0, int(remaining.total_seconds()))
        minutes = total_seconds // 60
        seconds = total_seconds % 60
        return f"{minutes}m {seconds}s"

    # Sofya Grishkova - i6397764
    def reset(self) -> None:
        # mostly useful for tests, so old attempts do not affect the next test
        self._buckets.clear()


# separate limiters because requesting a token and guessing a token are different actions
validation_limiter = RateLimiter(max_attempts=5, window_seconds=60)
request_limiter = RateLimiter(max_attempts=3, window_seconds=60)

def get_validation_limiter():
    return validation_limiter

def get_request_limiter():
    return request_limiter

# Sofya Grishkova - i6397764
def configure_validation_limit(max_attempts: int, window_seconds: int) -> None:
    # small helper in case experiment config wants to change validation limits
    validation_limiter.max_attempts = max_attempts
    validation_limiter.window_seconds = window_seconds


# Sofya Grishkova - i6397764
def configure_request_limit(max_attempts: int, window_seconds: int) -> None:
    # small helper in case experiment config wants to change request limits
    request_limiter.max_attempts = max_attempts
    request_limiter.window_seconds = window_seconds


# Sofya Grishkova - i6397764
def is_locked(email: str) -> bool:
    # wrapper kept so the UI can still call the old function name
    return validation_limiter.is_locked(email)


# Sofya Grishkova - i6397764
def record_failure(email: str) -> None:
    # wrapper kept for the validation limiter
    validation_limiter.record_failure(email)


# Sofya Grishkova - i6397764
def record_success(email: str) -> None:
    # wrapper kept for the validation limiter
    validation_limiter.record_success(email)


# Sofya Grishkova - i6397764
def get_remaining_lockout_time(email: str) -> str | None:
    # wrapper kept so UI does not need to know about RateLimiter class
    return validation_limiter.get_remaining_lockout_time(email)
