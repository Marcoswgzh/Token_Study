""" Handles User login and User data storage"""
# Refactored by: Nadja Poltoracki - i6403661
from __future__ import annotations

from pathlib import Path
from recovery_project.services.password_service import PasswordService

USER_FILE = Path(__file__).with_name("users.txt")

# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def _read_users() -> dict[str, str]:
    users: dict[str, str] = {}
    if not USER_FILE.exists():
        return users

    with USER_FILE.open("r", encoding="utf-8") as fh:
        for line in fh:
            line = line.strip()
            if not line:
                continue
            try:
                email, stored_hash = line.split(":", 1)
            except ValueError:
                continue
            users[email] = stored_hash

    return users


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def _write_users(users: dict[str, str]) -> None:
    USER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USER_FILE.open("w", encoding="utf-8") as fh:
        for email, stored_hash in sorted(users.items()):
            fh.write(f"{email}:{stored_hash}\n")


# Main writer: Timea Vojcikova - i6377033
# Email check to find user
def user_exists(email: str) -> bool:
    return email in _read_users()


# Main writer: Timea Vojcikova - i6377033
def register_user(email: str, password: str) -> bool:
    users = _read_users()
    if email in users:
        return False

    users[email] = PasswordService.hash_password(password)
    _write_users(users)
    return True


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def login_user(email: str, password: str) -> bool:
    users = _read_users()
    stored_hash = users.get(email)
    if stored_hash is None:
        return False
    return PasswordService.verify_password(password, stored_hash)

# Main writer: Timea Vojcikova - i6377033
def update_password(email: str, new_password: str) -> bool:
    users = _read_users()
    if email not in users:
        return False

    users[email] = PasswordService.hash_password(new_password)
    _write_users(users)
    return True

# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def logout_user(email: str) -> None:
    print(f"{email} logged out.")