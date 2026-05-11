import time

import pytest

from recovery_project.repositories.token_repository import TokenRepository
from recovery_project.services import recovery_service
from recovery_project.services.rate_limiter import request_limiter, validation_limiter


@pytest.fixture(autouse=True)
# Sofya Grishkova - i6397764
def reset_recovery_state():
    # each test should start with empty in-memory storage
    recovery_service.token_repository = TokenRepository()
    validation_limiter.max_attempts = 5
    validation_limiter.window_seconds = 60
    validation_limiter.reset()
    request_limiter.max_attempts = 3
    request_limiter.window_seconds = 60
    request_limiter.reset()
    yield
    validation_limiter.reset()
    request_limiter.reset()


# Sofya Grishkova - i6397764
def test_invalid_attempts_lock_account() -> None:
    # make the limit smaller so the test is short
    validation_limiter.max_attempts = 2

    assert recovery_service.validate_token("student@example.com", "bad-token") is False
    assert validation_limiter.is_locked("student@example.com") is False

    # second bad attempt reaches the limit
    assert recovery_service.validate_token("student@example.com", "bad-token-again") is False
    assert validation_limiter.is_locked("student@example.com") is True


# Sofya Grishkova - i6397764
def test_locked_account_rejects_correct_token() -> None:
    # even if user later enters the real token, lockout still has to apply
    validation_limiter.max_attempts = 2
    token = recovery_service.issue_token("student@example.com")

    recovery_service.validate_token("student@example.com", "bad-token")
    recovery_service.validate_token("student@example.com", "bad-token-again")

    assert token is not None
    assert recovery_service.validate_token("student@example.com", token) is False


# Sofya Grishkova - i6397764
def test_successful_validation_clears_failed_attempts() -> None:
    # if the token is correct, previous failed guesses should be cleared
    token = recovery_service.issue_token("student@example.com")

    recovery_service.validate_token("student@example.com", "bad-token")

    assert token is not None
    assert recovery_service.validate_token("student@example.com", token) is True
    assert validation_limiter.is_locked("student@example.com") is False


# Sofya Grishkova - i6397764
def test_token_is_bound_to_email() -> None:
    # a token issued for one account must not work for another account
    token = recovery_service.issue_token("first@example.com")

    assert token is not None
    assert recovery_service.validate_token("second@example.com", token) is False
    assert recovery_service.validate_token("first@example.com", token) is True


# Sofya Grishkova - i6397764
def test_attempt_window_expires_old_failures() -> None:
    # after the window passes, old bad attempts should not count anymore
    validation_limiter.max_attempts = 2
    validation_limiter.window_seconds = 1

    recovery_service.validate_token("student@example.com", "bad-token")
    time.sleep(1.1)
    recovery_service.validate_token("student@example.com", "another-bad-token")

    assert validation_limiter.is_locked("student@example.com") is False


# Sofya Grishkova - i6397764
def test_reset_token_requests_are_limited() -> None:
    # requesting reset tokens too often should also be limited
    request_limiter.max_attempts = 3

    assert recovery_service.issue_token("student@example.com") is not None
    assert recovery_service.issue_token("student@example.com") is not None
    assert recovery_service.issue_token("student@example.com") is not None
    assert recovery_service.issue_token("student@example.com") is None
