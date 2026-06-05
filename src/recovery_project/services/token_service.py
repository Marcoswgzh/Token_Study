"""Token generation/validation helpers"""
import secrets
import string
import hashlib
from datetime import datetime

from recovery_project.services.rate_limiter import validation_limiter
from recovery_project.repositories.token_repository import TokenRepository

# This token generation and validation is mainly for the first reasearch question, where we have to vary the entropy of the token

# Characters included in the token. We can increase this by adding string.digits (digits from 0 to 9) and/or string.punctuation (special characters)
default_alphabet = string.ascii_letters

# Writer: Anna Kálmánczhelyi
class TokenService:
    def __init__(self, alphabet: str = "0123456789ABCDEF", token_length: int=5):
        self.alphabet = alphabet
        self.token_length = token_length

# Generates the token using a given length. secrets.choice takes a random character from a sequence
# then create the token hash with the hashlib library
# Writer: Anna Kálmánczhelyi
    def generate_token(self) -> tuple:
        token = "".join(secrets.choice(self.alphabet) for _ in range(self.token_length))
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, token_hash
    
    #this is verifying the token based on the hash

token_repository = TokenRepository()
def get_token_repo() -> TokenRepository:
    return token_repository

# Writers: Anna Kálmánczhelyi, Sofya Grishkova - i6397764
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
    if record.user_id != email:
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