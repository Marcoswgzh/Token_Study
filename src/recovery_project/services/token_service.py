"""Token generation/validation helpers"""
import math
import multiprocessing
import secrets
import string
import itertools
import time
import hashlib

# This token generation and validation is mainly for the first reasearch question, where we have to vary the entropy of the token

# Characters included in the token. We can increase this by adding string.digits (digits from 0 to 9) and/or string.punctuation (special characters)
default_alphabet = string.ascii_letters

class TokenService:
    def __init__(self, alphabet: str = None, token_length: int=10):
        self.alphabet = alphabet or string.ascii_letters + string.digits
        self.token_length = token_length

# Generates the token using a given length. secrets.choice takes a random character from a sequence
# then create the token hash with the hashlib library
    def generate_token(self) -> tuple:
        token = "".join(secrets.choice(self.alphabet) for _ in range(self.token_length))
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        return token, token_hash
    
    #this is verifying the token based on the hash
    def verify_token(self, provided_token: str, stored_hash: str) -> bool:
        provided_hash = hashlib.sha256(provided_token.encode()).hexdigest()
        return provided_hash == stored_hash




