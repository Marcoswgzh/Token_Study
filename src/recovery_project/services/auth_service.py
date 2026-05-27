"""Small file-backed authentication service for the demo UI."""

from __future__ import annotations

import hashlib
import hmac
import secrets
from pathlib import Path

USER_FILE = Path(__file__).with_name("users.txt")
DEMO_EMAIL = "student@university.edu"
DEMO_PASSWORD = "Password123!"
_PBKDF2_ITERATIONS = 120_000
_DEMO_PASSWORD_HASH = (
    "pbkdf2_sha256$120000$9537145d3b3e2e520c29a297a4a6e6fb"
    "$27fc6ce7ae7b435b0f8ed38d8725905780670c2a484a4bf0604180f198cf3095"
)


# Sofya Grishkova - i6397764
def hash_password(password: str) -> str:
    salt = secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac(
        "sha256",
        password.encode("utf-8"),
        bytes.fromhex(salt),
        _PBKDF2_ITERATIONS,
    ).hex()
    return f"pbkdf2_sha256${_PBKDF2_ITERATIONS}${salt}${digest}"


# Sofya Grishkova - i6397764
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


# Sofya Grishkova - i6397764
def _read_users() -> dict[str, str]:
    users: dict[str, str] = {}
    if USER_FILE.exists():
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

    if DEMO_EMAIL not in users:
        users[DEMO_EMAIL] = _DEMO_PASSWORD_HASH

    return users


# Sofya Grishkova - i6397764
def _read_persisted_users() -> dict[str, str]:
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


# Sofya Grishkova - i6397764
def _write_users(users: dict[str, str]) -> None:
    USER_FILE.parent.mkdir(parents=True, exist_ok=True)
    with USER_FILE.open("w", encoding="utf-8") as fh:
        for email, stored_hash in sorted(users.items()):
            fh.write(f"{email}:{stored_hash}\n")


# Sofya Grishkova - i6397764
def ensure_demo_user() -> None:
    _read_users()


# Sofya Grishkova - i6397764
def user_exists(email: str) -> bool:
    return email in _read_users()


# Sofya Grishkova - i6397764
def register_user(email: str, password: str) -> bool:
    users = _read_persisted_users()
    if email in users:
        return False

    users[email] = hash_password(password)
    _write_users(users)
    return True


# Sofya Grishkova - i6397764
def login_user(email: str, password: str) -> bool:
    users = _read_users()
    stored_hash = users.get(email)
    if stored_hash is None:
        return False
    return verify_password(password, stored_hash)


# Sofya Grishkova - i6397764
def update_password(email: str, new_password: str) -> bool:
    users = _read_users()
    if email not in users:
        return False

    users[email] = hash_password(new_password)
    _write_users(users)
    return True


# Sofya Grishkova - i6397764
def logout_user(email: str) -> None:
    print(f"{email} logged out.")
