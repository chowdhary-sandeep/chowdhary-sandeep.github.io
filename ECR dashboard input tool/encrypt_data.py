import os
import json
import base64
import getpass
from typing import Tuple

from hashlib import pbkdf2_hmac

try:
    from cryptography.hazmat.primitives.ciphers.aead import AESGCM
except Exception as e:  # pragma: no cover
    AESGCM = None


DATA_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'data'))
FILES = [
    'ecr_records.json',
    'staff_records.json',
    'card_vectors.json',
    'staff_card_vectors.json',
    'token_vectors.json',
]


def _derive_key(password: str, salt: bytes, iterations: int = 200_000) -> bytes:
    return pbkdf2_hmac('sha256', password.encode('utf-8'), salt, iterations, dklen=32)


def _encrypt_bytes(key: bytes, plaintext: bytes) -> Tuple[bytes, bytes, bytes]:
    if AESGCM is None:
        raise RuntimeError('cryptography is not installed. Please install with: python -m pip install cryptography')
    import os as _os
    aes = AESGCM(key)
    iv = _os.urandom(12)
    ct = aes.encrypt(iv, plaintext, None)
    return iv, ct, b''


def encrypt_file(path: str, password: str) -> str:
    with open(path, 'rb') as f:
        data = f.read()
    salt = os.urandom(16)
    key = _derive_key(password, salt)
    iv, ct, _ = _encrypt_bytes(key, data)
    out = {
        'alg': 'AES-GCM',
        'kdf': 'PBKDF2-HMAC-SHA256',
        'iter': 200000,
        'salt': base64.b64encode(salt).decode('utf-8'),
        'iv': base64.b64encode(iv).decode('utf-8'),
        'ct': base64.b64encode(ct).decode('utf-8'),
    }
    out_path = path + '.enc'
    with open(out_path, 'w', encoding='utf-8') as f:
        json.dump(out, f, separators=(',', ':'))
    return out_path


def main():
    password = os.environ.get('ECR_ENCRYPT_PASSWORD') or 'lalaland'
    print('Encrypting data in', DATA_DIR)
    if AESGCM is None:
        print('cryptography not available. Attempting to install...')
        raise RuntimeError('cryptography not installed')
    for name in FILES:
        p = os.path.join(DATA_DIR, name)
        if not os.path.exists(p):
            continue
        try:
            out = encrypt_file(p, password)
            print('Encrypted', name, '->', os.path.basename(out))
        except Exception as e:
            print('Failed to encrypt', name, e)
    # Optionally delete plaintext files after encryption
    # Comment out next block if you prefer to keep local copies
    for name in FILES:
        p = os.path.join(DATA_DIR, name)
        if os.path.exists(p):
            try:
                os.remove(p)
                print('Removed plaintext', name)
            except Exception as e:
                print('Could not remove', name, e)


if __name__ == '__main__':
    main()



