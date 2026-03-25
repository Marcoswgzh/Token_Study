"""Password recovery flow

Core responsibilities:
- issue token
- validate token (entropy/TTL/single-use behavior)
- reset password on successful recovery
"""
import hashlib
from datetime import datetime, timedelta

#i don't know about issues with import, i'll look into it later. for now, if you have trouble running the code because of the invalid imports, run from terminal with:
# python -m src.recovery_project.services.recovery_service

from .token_service import TokenService
from ..repositories.token_repository import TokenRepository

service = TokenService()
token_repository = TokenRepository()

# Use tokenRepository for database purposes
def issue_token(email: str, ) -> str:
    token, token_hash = service.generate_token()

    created_at = datetime.now()

    #TODO: this doesn't connect to the ui yet, the seconds are hardcoded, so if the user changes them on the interface, it won't have an effect
    expires_at = datetime.now() + timedelta(seconds=300)

    token_repository.store_token(token_hash, email, created_at, expires_at)
    # print statement for testing and to be able to see the token
    # In a real workflow, the token would be sent to the email provided
    print(f"Token issued for {email}: {token}")
    return token

# Validate the token
def validate_token(email: str, provided_token: str) -> bool:
    
    #hash the provided_token
    provided_hash = hashlib.sha256(provided_token.encode()).hexdigest()

    #try to find this provided_hash in the repo
    record = token_repository.find_token(provided_hash)

    # If the user is not in the database, return false
    if not record:
        return False
    
    # If the token have been used already, return false
    if record.used:
        return False
    
    # If the token is expired, return false
    if datetime.now() > record.expires_at:
        return False
    
    # If any of the previous conditions happen, the provided token is correct, so return true
    #we also mark the token used (so it cannot be reused infinite times)
    token_repository.mark_token_used(provided_hash)
    return True

# For testing purposes
if __name__ == "__main__":
    token = issue_token("hello")
    print(f"generated token: {token}")

    is_valid = validate_token("hello", token)
    print(f"is the token valid? {is_valid}")

    print(f"tokens in the repository: {token_repository.tokens}")


