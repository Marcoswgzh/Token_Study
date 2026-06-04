"""Token generation/validation helpers"""
import secrets
import string
import hashlib

# TODO: Check if this is unused (I think it is) and delete
# Characters included in the token
# We can increase this by adding string.digits (digits from 0 to 9) and/or string.punctuation (special characters)
default_alphabet = string.ascii_letters

# Writer: Anna Kálmánczhelyi
# Reviewer: Nadja Poltoracki - i6403661
class TokenService:
    def __init__(self, alphabet: str = None, token_length: int=10):
        # TODO: remove the preset 10 limit
        self.alphabet = alphabet or string.ascii_letters + string.digits
        self.token_length = token_length

# Generates the token using a given length.
# secrets.choice takes a random character from a sequence then create the token hash with the hashlib library
# Writer: Anna Kálmánczhelyi
# Reviewer: Nadja Poltoracki - i6403661
    def generate_token(self) -> tuple:
        token = "".join(secrets.choice(self.alphabet) for _ in range(self.token_length))
        # TODO: Delete duplicate in recovery service?
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, token_hash

# Writer: Anna Kálmánczhelyi
    def verify_token(self, provided_token: str, stored_hash: str) -> bool:
        # Verifying the token based on the hash
        provided_hash = hashlib.sha256(provided_token.encode()).hexdigest()
        return provided_hash == stored_hash




