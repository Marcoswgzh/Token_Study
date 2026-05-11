"""Password recovery flow

Core responsibilities:
- issue token
- validate token (entropy/TTL/single-use behavior)
- reset password on successful recovery
"""
import hashlib
from datetime import datetime, timedelta

from .rate_limiter import request_limiter, validation_limiter
from .token_service import TokenService
from ..repositories.token_repository import TokenRepository
from ..repositories.user_repository import UserRepository

user_repository = UserRepository()
service = TokenService()
token_repository = TokenRepository()

# Sofya Grishkova - i6397764
def issue_token(email: str) -> str | None:
    # do not issue endless tokens for the same account
    if request_limiter.is_locked(email):
        return None

    token, token_hash = service.generate_token()

    created_at = datetime.now()

    #TODO: this doesn't connect to the ui yet, the seconds are hardcoded, so if the user changes them on the interface, it won't have an effect
    expires_at = datetime.now() + timedelta(seconds=300)

    token_repository.store_token(token_hash, email, created_at, expires_at)

    # count token requests too, because requesting many reset emails is also abuse
    request_limiter.record_failure(email)

    # print statement for testing and to be able to see the token
    # In a real workflow, the token would be sent to the email provided
    print(f"Token issued for {email}: {token}")
    return token

# Sofya Grishkova - i6397764
def validate_token(email: str, provided_token: str) -> bool:
    # if the account is locked, even a correct token should not work yet
    if validation_limiter.is_locked(email):
        return False

    provided_hash = hashlib.sha256(provided_token.encode()).hexdigest()
    record = token_repository.find_token(provided_hash)

    # unknown token is a failed guess
    if not record:
        validation_limiter.record_failure(email)
        return False

     # token must belong to the same account that is trying to recover
    if user_repository.find_email(email).user_id != record.user_id:
        validation_limiter.record_failure(email)
        return False

    # used tokens should not be accepted again
    if record.used:
        validation_limiter.record_failure(email)
        return False

    # expired token also counts as a failed validation attempt
    if datetime.now() > record.expires_at:
        validation_limiter.record_failure(email)
        return False

    # token is correct, so mark it as used and clear previous failures
    token_repository.mark_token_used(provided_hash)
    validation_limiter.record_success(email)
    return True

# Sofya Grishkova - i6397764
def reset_password(user_id: str, new_password: str) -> bool:
    # password is stored as a hash, not as plain text
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    return user_repository.update_password(user_id, password_hash)

# For testing purposes
if __name__ == "__main__":
    #test password reset and token generation in 1 workflow:
    #create user and confirm it
    user_repository.create_user(user_id="test1", email="example@example.com", password_hash="some_hash")
    print(f"user created: {user_repository.find_user('test1')}")

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

        #verify that it was changed in repo too
        user = user_repository.find_email("example@example.com")
        print(f"the new password hash is: {user.password_hash}")

    #check if the same token can be validation (it should fail if all went well)
    is_valid_again = validate_token("example@example.com", token)
    print(f"is the token valid on a second use? {is_valid_again}")


    
