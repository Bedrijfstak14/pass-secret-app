import os, base64
from cryptography.hazmat.primitives.ciphers.aead import AESGCM

KEY = base64.urlsafe_b64decode(os.getenv('SECRET_KEY'))

def encrypt(data: bytes):
    aes = AESGCM(KEY)
    nonce = os.urandom(12)
    ct = aes.encrypt(nonce, data, None)
    return ct, nonce

def decrypt(ct: bytes, nonce: bytes):
    aes = AESGCM(KEY)
    return aes.decrypt(nonce, ct, None)
