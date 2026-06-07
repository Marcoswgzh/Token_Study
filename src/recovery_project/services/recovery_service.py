"""Password recovery flow

Core responsibilities:
- issue token
- validate token (entropy/TTL/single-use behavior)
- reset password on successful recovery
"""
from __future__ import annotations

# Writer: Anna Kálmánczhelyi
from datetime import datetime, timedelta

from recovery_project.services.token_service import TokenService, validate_token, get_token_repo
from recovery_project.services.rate_limiter import get_request_limiter, get_validation_limiter
from recovery_project.services.auth_service import update_password

request_limiter = get_request_limiter()
validation_limiter = get_validation_limiter()
token_service = TokenService()
# Writer: Anna Kálmánczhelyi
# Reviwer: Sofya Grishkova - i6397764
def issue_token(email: str) -> str | None:
    # do not issue endless tokens for the same account
    if request_limiter.is_locked(email):
        return None

    token, token_hash = token_service.generate_token()

    created_at = datetime.now()
    expires_at = created_at + timedelta(seconds=300)

    # The demo backend binds recovery tokens directly to the account email.
    get_token_repo().store_token(token_hash, email, created_at, expires_at)

    # count token requests too, because requesting many reset emails is also abuse
    request_limiter.record_failure(email)

    # print statement for testing and to be able to see the token
    # In a real workflow, the token would be sent to the email provided
    print(f"Token issued for {email}: {token}")
    return token

# Writer: Anna Kálmánczhelyi
# Sofya Grishkova - i6397764
def reset_password(email: str, new_password: str) -> bool:
    return update_password(email, new_password)


    
