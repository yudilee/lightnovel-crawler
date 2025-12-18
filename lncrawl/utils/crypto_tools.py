from typing import Tuple

from cryptography.hazmat.primitives import serialization
from cryptography.hazmat.primitives.asymmetric import padding, rsa


def generate_rsa_pair() -> Tuple[str, str]:
    """Generate RSA key pair"""
    private_key = rsa.generate_private_key(
        public_exponent=65537,
        key_size=4096,
    )
    private_key_pem = private_key.private_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PrivateFormat.PKCS8,
        encryption_algorithm=serialization.NoEncryption()
    ).decode()
    public_key_pem = private_key.public_key().public_bytes(
        encoding=serialization.Encoding.PEM,
        format=serialization.PublicFormat.SubjectPublicKeyInfo
    ).decode()
    return private_key_pem, public_key_pem


def rsa_encrypt(data: bytes, public_key_pem: str) -> bytes:
    """Encrypt data using RSA public key"""
    public_key = serialization.load_pem_public_key(
        public_key_pem.encode()
    )
    padding_scheme = padding.PKCS1v15()
    return public_key.encrypt(data, padding_scheme)


def rsa_decrypt(data: bytes, private_key_pem: str) -> bytes:
    """Decrypt data using RSA private key"""
    private_key = serialization.load_pem_private_key(
        private_key_pem.encode(),
        password=None,
    )
    padding_scheme = padding.PKCS1v15()
    return private_key.decrypt(data, padding_scheme)
