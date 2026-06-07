"""Recovery token repository interface / in-memory adapter placeholder."""

from datetime import datetime
from typing import Optional
from ..domain.models import RecoveryToken

# Writer: Anna Kálmánczhelyi
class TokenRepository:
    def __init__(self):
        # Initialize an empty directory for storing tokens
        self.tokens = {}

# Writer: Anna Kálmánczhelyi
# Reviewer: Nadja Poltoracki - i6403661
    def store_token(self, token_hash: str, user_id: str, created_at: datetime, expires_at: datetime, used: bool = False) -> None:
        token_record = RecoveryToken(
            user_id=user_id, 
            token_value=token_hash, 
            created_at=created_at, 
            expires_at=expires_at, 
            used =used)
        
        # Store in the dictionary
        self.tokens[token_hash] = token_record
        
# Writer: Anna Kálmánczhelyi
# Reviewer: Nadja Poltoracki - i6403661
    def find_token(self, token_hash: str) -> Optional[RecoveryToken]:
        # Look up token
        return self.tokens.get(token_hash)

# Writer: Anna Kálmánczhelyi
    def mark_token_used(self, token_hash: str):
        # Once the token was used for reset, mark as used -> so lose its active status
        token = self.tokens.get(token_hash)
        if token:
            token.used = True
