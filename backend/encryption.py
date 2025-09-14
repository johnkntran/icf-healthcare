import os
import binascii

from Crypto.Cipher import AES


key_str = os.environ['LANGGRAPH_ENCRYPTION_KEY']
key = binascii.a2b_hex(key_str)


def encrypt(data: str) -> tuple[bytes, bytes]:
    cipher = AES.new(key=key, mode=AES.MODE_EAX)
    nonce = cipher.nonce
    encrypted_data, _ = cipher.encrypt_and_digest(data.encode())
    return encrypted_data, nonce


def decrypt(data: bytes, nonce: bytes) -> str:
    cipher = AES.new(key=key, mode=AES.MODE_EAX, nonce=nonce)
    decrypted_data = cipher.decrypt(data)
    return decrypted_data.decode()