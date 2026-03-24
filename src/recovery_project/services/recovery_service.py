"""Password recovery flow placeholder.

Core responsibilities:
- issue token
- validate token (entropy/TTL/single-use behavior)
- reset password on successful recovery
"""
from src.recovery_project.services.token_service import TokenService

service = TokenService()

# Use a dictionary for now, then change to an actual database
def issue_token(email: str, database: dict) -> str:
    token, token_hash = service.generate_token()
    database[email] = {
        "hash": token_hash,
        "used": False  
    }
    # print statement for testing and to be able to see the token
    # In a real workflow, the token would be sent to the email provided
    print(f"Token issued for {email}: {token}")
    return token

# Validate the token
def validate_token(email: str, provided_token: str, database: dict) -> bool:
    record = database.get(email)

    # If the user is not in the database, return false
    if not record:
        return False
    
    # If the token have been used already, return false
    if record["used"]:
        return False
    
    # If the provided token hash is not the same as the the hash stored in the database, return false
    if not service.verify_token(provided_token, record["hash"]):
        return False
    
    # If any of the previous conditions happen, the provided token is correct, so return true
    return True

# For testing purposes
if __name__ == "__main__":
    database = {}
    token = issue_token("hello", database)
    print(database)
    print(validate_token("hello", token, database))


