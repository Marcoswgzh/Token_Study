"""User repository interface / in-memory adapter """

from typing import Optional
from ..domain.models import User

class UserRepository:
    def __init__(self):
        self.users = {}

    def create_user(self, user_id: str, email: str, password_hash: str):
        #create then store a new user based on models.User dataclass

        user = User(user_id=user_id, 
                    email=email, 
                    password_hash=password_hash, 
                    mfa_enabled=False)
        self.users[user_id] = user

    def find_user(self, user_id: str) -> Optional[User]:
        #if user is found (based on user_id), return it
        return self.users.get(user_id)

    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        user = self.users.get(user_id)
        if user:
            user.password_hash = new_password_hash
            return True
        return False