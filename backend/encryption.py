from cryptography.fernet import Fernet
import os

_KEY_PATH = os.environ.get('PFMS_FERNET_KEY_PATH', None)

def get_key():
    key = os.environ.get('PFMS_FERNET_KEY')
    if key:
        return key.encode()
    if _KEY_PATH and os.path.exists(_KEY_PATH):
        with open(_KEY_PATH, 'rb') as f:
            return f.read()
    # development fallback
    return Fernet.generate_key()


def encrypt(value: str):
    if value is None:
        return None
    key = get_key()
    f = Fernet(key)
    return f.encrypt(value.encode()).decode()


def decrypt(value: str):
    if value is None:
        return None
    key = get_key()
    f = Fernet(key)
    return f.decrypt(value.encode()).decode()
