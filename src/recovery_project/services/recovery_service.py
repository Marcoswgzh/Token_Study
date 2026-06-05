"""Password recovery flow

Core responsibilities:
- issue token
- validate token (entropy/TTL/single-use behavior)
- reset password on successful recovery
"""

# Writer: Anna Kálmánczhelyi
from datetime import datetime, timedelta

from recovery_project.services.token_service import TokenService, validate_token, get_token_repo
from recovery_project.services.rate_limiter import get_request_limiter, get_validation_limiter
from recovery_project.services.auth_service import update_password

request_limiter = get_request_limiter()
validation_limiter = get_validation_limiter()
token_service = TokenService()
# Writer: Anna Kálmánczhelyi
# Sofya Grishkova - i6397764
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

# Writer: Anna Kálmánczhelyi
# For testing purposes
if __name__ == "__main__":
    #test password reset and token generation in 1 workflow:
    #create user and confirm it
    #create token for user
    token = issue_token("example@example.com")
    print(f"generated token: {token}")

    #test if token is valid
    is_valid = validate_token("example@example.com", token)
    print(f"is the token valid? {is_valid}")

    #based on validity result, reset password and store it
    if is_valid:
        is_reset = reset_password("example@example.com", "new_password")
        print(f"is password reset? {is_reset}")

    #check if the same token can be validation (it should fail if all went well)
    is_valid_again = validate_token("example@example.com", token)
    print(f"is the token valid on a second use? {is_valid_again}")


    
