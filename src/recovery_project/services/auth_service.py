from __future__ import annotations

import hashlib
import hmac
import secrets
from pathlib import Path

USER_FILE = Path(__file__).with_name("users.txt")
_PBKDF2_ITERATIONS = 120_000


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        _PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest}"


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def verify_password(password: str, stored_hash: str) -> bool:
    try:
        algorithm, iterations, salt, expected = stored_hash.split("$")
    except ValueError:
        return False

    if algorithm != "pbkdf2_sha256":
        return False

    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        int(iterations),
    ).hex()
    return hmac.compare_digest(digest, expected)


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


# Main writer: Sofya Grishkova - i6397764
def user_exists(email: str) -> bool:
    return email in _read_users()


# Main writer: Sofya Grishkova - i6397764
def register_user(email: str, password: str) -> bool:
    users = _read_users()
    if email in users:
        return False

    users[email] = hash_password(password)
    _write_users(users)
    return True


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def login_user(email: str, password: str) -> bool:
    users = _read_users()
    stored_hash = users.get(email)
    if stored_hash is None:
        return False
    return verify_password(password, stored_hash)


# Main writer: Sofya Grishkova - i6397764
def update_password(email: str, new_password: str) -> bool:
    users = _read_users()
    if email not in users:
        return False

    users[email] = hash_password(new_password)
    _write_users(users)
    return True


# Main writer: Timea Vojcikova - i6377033
# Reviewer: Sofya Grishkova - i6397764
def logout_user(email: str) -> None:
    print(f"{email} logged out.")