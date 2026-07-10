"""密码哈希与 Token 工具"""
import hashlib
import secrets


def hash_password(password: str, salt: str | None = None) -> str:
    real_salt = salt or secrets.token_hex(16)
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), real_salt.encode(), 120_000)
    return f"{real_salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$", 1)
    except ValueError:
        return False
    return secrets.compare_digest(hash_password(password, salt), stored)


def generate_token() -> str:
    return secrets.token_urlsafe(32)
