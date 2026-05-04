"""
Service Layer — Authentication Business Logic
Handles password hashing and JWT token management
"""

import hashlib
import hmac
import json
import base64
import time

SECRET_KEY = "shiftsaas-secret-key-2026"

def hash_password(password: str) -> str:
    """Hash a password using SHA-256 with a salt."""
    salt = "shiftsaas_salt_2026"
    return hashlib.sha256(f"{salt}{password}".encode()).hexdigest()

def verify_password(plain_password: str, hashed_password: str) -> bool:
    """Verify a password against its hash."""
    return hash_password(plain_password) == hashed_password

def create_token(payload: dict) -> str:
    """Create a simple JWT-like token."""
    payload['exp'] = time.time() + 86400  # 24h expiry
    encoded = base64.b64encode(json.dumps(payload).encode()).decode()
    signature = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).hexdigest()
    return f"{encoded}.{signature}"

def verify_token(token: str) -> dict:
    """Verify and decode a token."""
    try:
        parts = token.split('.')
        if len(parts) != 2:
            return None
        encoded, signature = parts
        expected_sig = hmac.new(SECRET_KEY.encode(), encoded.encode(), hashlib.sha256).hexdigest()
        if not hmac.compare_digest(signature, expected_sig):
            return None
        payload = json.loads(base64.b64decode(encoded).decode())
        if payload.get('exp', 0) < time.time():
            return None
        return payload
    except Exception:
        return None
