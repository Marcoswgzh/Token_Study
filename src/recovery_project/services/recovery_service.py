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
from ..repositories.user_repository import UserRepository

user_repository = UserRepository()
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

def reset_password(user_id: str, new_password: str) -> bool:
    password_hash = hashlib.sha256(new_password.encode()).hexdigest()
    return user_repository.update_password(user_id, password_hash)

# For testing purposes
if __name__ == "__main__":
    #test password reset and token generation in 1 workflow:
    #create user and confirm it
    user_repository.create_user(user_id="test1", email="example@example.com", password_hash="some_hash")
    print(f"user created: {user_repository.find_user('test1')}")

    #create token for user
    token = issue_token("test1")
    print(f"generated token: {token}")

    #test if token is valid
    is_valid = validate_token("test1", token)
    print(f"is the token valid? {is_valid}")

    #based on validity result, reset password and store it
    if is_valid:
        is_reset = reset_password("test1", "new_password")
        print(f"is password reset? {is_reset}")

        #verify that it was changed in repo too
        user = user_repository.find_user("test1")
        print(f"the new password hash is: {user.password_hash}")

    #check if the same token can be validation (it should fail if all went well)
    is_valid_again = validate_token("test1", token)
    print(f"is the token valid on a second use? {is_valid_again}")


    


