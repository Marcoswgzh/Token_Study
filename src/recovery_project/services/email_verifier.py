import re

def email_verifier(email: str) -> bool:
    if not re.match(r"^[^@\s]+@[^@\s]+\.[^@\s]+$", email):
        return False
    return True

 #Writer: Erika Skodova