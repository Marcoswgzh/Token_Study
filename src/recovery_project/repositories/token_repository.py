"""Recovery token repository interface / in-memory adapter placeholder."""

from datetime import datetime
from typing import Optional
from ..domain.models import RecoveryToken

class TokenRepository:
    def __init__(self):
        # initialize an empty directory for storing tokens
        self.tokens = {}


    def store_token(self, token_hash: str, user_id: str, created_at: datetime, expires_at: datetime, used: bool = False) -> None:
        #takes parameters based on the recovery token dataclass
        token_record = RecoveryToken(
            user_id=user_id, 
            token_value=token_hash, 
            created_at=created_at, 
            expires_at=expires_at, 
            used =used)
        
        #store in the dictionary
        #key = hash; value = token object
        self.tokens[token_hash] = token_record
        
        
    def find_token(self, token_hash: str) -> Optional[RecoveryToken]:
        # based on hash, look up token
        # return RecoveryToken if found (or None if no valid token is found)
        return self.tokens.get(token_hash)

    def mark_token_used(self, token_hash: str):
        #once the token was used successfuly for reset, mark the token used -> so lose its active status 

        token = self.tokens.get(token_hash)
        if token:
            token.used = True
