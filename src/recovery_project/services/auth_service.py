"""Authentication service placeholder (login checks, password updates)."""
import bcrypt
import os

USER_FILE = "users.txt"


# Password utilities

def hash_password(password: str) -> bytes:
    return bcrypt.hashpw(password.encode(), bcrypt.gensalt())


def verify_password(password: str, hashed: bytes) -> bool:
    return bcrypt.checkpw(password.encode(), hashed)


# File utilities

def _read_users():
    users = {}

    if not os.path.exists(USER_FILE):
        return users

    with open(USER_FILE, "r") as f:
        for line in f:
            username, hashed = line.strip().split(":")
            users[username] = hashed.encode()

    return users


def _write_user(username: str, hashed: bytes):
    with open(USER_FILE, "a") as f:
        f.write(f"{username}:{hashed.decode()}\n")


# Authentication related methods

def register_user(username: str, password: str) -> bool:
    users = _read_users()

    if username in users:
        return False  # user already exists

    hashed = hash_password(password)
    _write_user(username, hashed)

    return True


def login_user(username: str, password: str) -> bool:
    users = _read_users()

    if username not in users:
        return False

    return verify_password(password, users[username])


def logout_user(username: str):
    # For file-based auth, there's no real session tracking yet
    # So for now this is just a placeholder for future session/token logic
    print(f"{username} logged out.")