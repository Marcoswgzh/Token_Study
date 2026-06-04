""" Handles Password hashing and verification logic for User"""
# Refactored by: Nadja Poltoracki - i6403661
from __future__ import annotations

import hashlib
import hmac
import secrets

_PBKDF2_ITERATIONS = 120_000

class PasswordService:
    # Main writer: Timea Vojcikova - i6377033
    # Reviewer: Sofya Grishkova - i6397764
    @staticmethod
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
    @staticmethod
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

