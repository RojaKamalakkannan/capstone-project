"""Encryption utilities for sensitive data"""
from cryptography.fernet import Fernet
import os
from dotenv import load_dotenv
import base64

load_dotenv()

# Get or generate encryption key
ENCRYPTION_KEY = os.getenv("ENCRYPTION_KEY")

if not ENCRYPTION_KEY or ENCRYPTION_KEY.startswith("gAAAAAB"):
    # Generate a new key if not provided or using placeholder
    new_key = Fernet.generate_key()
    ENCRYPTION_KEY = new_key.decode()
    print(f"Generated new encryption key: {ENCRYPTION_KEY}")

# Ensure key is in the correct format
try:
    if isinstance(ENCRYPTION_KEY, str):
        # Try to decode as base64 URL-safe.env
        key_bytes = base64.urlsafe_b64decode(ENCRYPTION_KEY.encode())
        if len(key_bytes) != 32:
            raise ValueError("Key must be 32 bytes")
        cipher_suite = Fernet(ENCRYPTION_KEY.encode())
    else:
        cipher_suite = Fernet(ENCRYPTION_KEY)
except Exception as e:
    # If key is invalid, generate a new one
    new_key = Fernet.generate_key()
    ENCRYPTION_KEY = new_key.decode()
    cipher_suite = Fernet(new_key)
    print(f"Invalid key, generated new: {ENCRYPTION_KEY}")


def encrypt_data(data: str) -> str:
    """Encrypt sensitive data"""
    if not data:
        return ""
    try:
        return cipher_suite.encrypt(data.encode()).decode()
    except Exception as e:
        raise ValueError(f"Failed to encrypt data: {str(e)}")


def decrypt_data(encrypted_data: str) -> str:
    """Decrypt sensitive data"""
    if not encrypted_data:
        return ""
    try:
        return cipher_suite.decrypt(encrypted_data.encode()).decode()
    except Exception as e:
        raise ValueError(f"Failed to decrypt data: {str(e)}")
