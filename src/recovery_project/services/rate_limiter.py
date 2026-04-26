"""Per-account rate-limiting placeholder for recovery attempts."""

from datetime import datetime, timedelta

# A dictionary with the form {email: {"count": int, "locked_until": datetime}}
failed_attempts = {}
MAX_ATTEMPTS = 5
LOCKOUT_TIME = 1

# Check if the workflow is locked for the desired email.
def is_locked(email: str) -> bool:
    # If the email is not in the dictionary, the workflow is not locked
    if email not in failed_attempts:
        return False
    
    locked_until = failed_attempts[email]["locked_until"]

    # If the locked_until field is empty, the workflow is not locked
    if locked_until is None:
        return False
    
    # If the locked_until field is not empty and it is larger than the current datetime, the workflow is locked
    if datetime.now() < locked_until:
        return True
    else:
        # Else, the locked_until field is "in the past", so it has already expired, so delete it
        del failed_attempts[email]
        return False

# Add a record to the failed attempts dictionary on failure
def record_failure(email: str) -> None:
    # Add the record set to 0
    if email not in failed_attempts:
        failed_attempts[email] = {"count": 0, "locked_until": None}
    
    # Increase it by 1
    failed_attempts[email]["count"] += 1

    # If the number of failed attempts has surpassed the max, lock the workflow
    if failed_attempts[email]["count"] >= MAX_ATTEMPTS:
        failed_attempts[email]["locked_until"] = datetime.now() + timedelta(minutes=LOCKOUT_TIME)

# Delete a record on success
def record_success(email: str) -> None:
    if email in failed_attempts:
        del failed_attempts[email]

# Get the remaining time
def get_remaining_lockout_time(email: str) -> str:
    # Check if the record exists
    if email not in failed_attempts:
        return None
    
    locked_until = failed_attempts[email]["locked_until"]

    if locked_until is None:
        return None
    
    # Calculate remaining time and return it
    remaining = locked_until - datetime.now()
    total_seconds = int(remaining.total_seconds())
    minutes = total_seconds // 60
    seconds = total_seconds % 60
    return f"{minutes}m {seconds}s"
