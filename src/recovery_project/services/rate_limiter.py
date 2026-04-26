"""Per-account rate-limiting placeholder for recovery attempts."""

from datetime import datetime, timedelta

failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 1

def is_locked(email: str) -> bool:
    if email not in failed_attempts:
        return False
    
    locked_until = failed_attempts[email]["locked_until"]

    if locked_until is None:
        return False
    
    if datetime.now() < locked_until:
        return True
    else:
        failed_attempts[email] = {"count": 0, "locked_until": None}
        return False
    
def record_failure(email: str) -> None:
    if email not in failed_attempts:
        failed_attempts[email] = {"count": 0, "locked_until": None}
    
    failed_attempts[email]["count"] += 1

    if failed_attempts[email]["count"] >= MAX_ATTEMPTS:
        failed_attempts[email]["locked_until"] = datetime.now() + timedelta(minutes=LOCKOUT_TIME)

def record_success(email: str) -> None:
    if email in failed_attempts:
        del failed_attempts[email]

def get_remaining_lockout_time(email: str) -> int:
    if email not in failed_attempts:
        return None
    
    locked_until = failed_attempts[email]["locked_until"]

    if locked_until is None:
        return None
    
    remaining_time_raw = locked_until - datetime.now()
    remaining_time_minutes = int(remaining_time_raw.total_seconds() / 60) + 1
    return remaining_time_minutes

