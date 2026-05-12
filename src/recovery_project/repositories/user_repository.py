"""User repository interface / in-memory adapter """

from typing import Optional
from ..domain.models import User

class UserRepository:
    # Writer: Anna Kálmánczhelyi 
    def __init__(self):
        self.users = {}
    # Writer: Anna Kálmánczhelyi 
    def create_user(self, user_id: str, email: str, password_hash: str):
        #create then store a new user based on models.User dataclass

        user = User(user_id=user_id, 
                    email=email, 
                    password_hash=password_hash, 
                    mfa_enabled=False)
        self.users[user_id] = user

    # Writer: Anna Kálmánczhelyi 
    def find_user(self, user_id: str) -> Optional[User]:
        #if user is found (based on user_id), return it
        return self.users.get(user_id)

#function writer Erika Skodova
    def find_email(self, email: str) -> Optional[User]:
        # if user is found (based on email), return user ID
        for user in self.users.values():
            if user.email == email:
                return user
        return None

    # Writer: Anna Kálmánczhelyi 
    def update_password(self, user_id: str, new_password_hash: str) -> bool:
        user = self.users.get(user_id)
        if user:
            user.password_hash = new_password_hash
            return True
        return False