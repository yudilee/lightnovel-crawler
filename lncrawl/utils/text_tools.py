import base64
import hashlib
import unicodedata
import uuid
from typing import Union

import zstd
from cryptography.fernet import Fernet

__key_cache = {}


def normalize(text: str) -> str:
    return unicodedata.normalize("NFKD", text).casefold()


def is_compressed(data: bytes) -> bool:
    # checks if the data is compressed with zstd
    return data.startswith(b'\x28\xB5\x2F\xFD')


def text_compress(plain: bytes) -> bytes:
    return zstd.compress(plain, 10)


def text_decompress(compressed: bytes) -> bytes:
    return zstd.decompress(compressed)


def text_encrypt(plain: bytes, secret: Union[str, bytes]) -> bytes:
    fernet = Fernet(generate_key(secret))
    result = fernet.encrypt(plain)
    return base64.urlsafe_b64decode(result)


def text_decrypt(cipher: bytes, secret: Union[str, bytes]) -> bytes:
    fernet = Fernet(generate_key(secret))
    cipher = base64.urlsafe_b64encode(cipher)
    return fernet.decrypt(cipher)


def text_compress_encrypt(plain: bytes, secret: Union[str, bytes]) -> bytes:
    return text_encrypt(text_compress(plain), secret)


def text_decrypt_decompress(cipher: bytes, secret: Union[str, bytes]) -> bytes:
    return text_decompress(text_decrypt(cipher, secret))


def generate_md5(*texts) -> str:
    md5 = hashlib.md5()
    for text in texts:
        md5.update(str(text or '').encode())
    return md5.hexdigest()


def generate_key(secret: Union[str, bytes]) -> bytes:
    if isinstance(secret, str):
        secret = secret.encode()
    if secret not in __key_cache:
        hash = hashlib.sha3_256(secret).digest()
        key = base64.urlsafe_b64encode(hash)
        __key_cache[secret] = key
    return __key_cache[secret]


def generate_uuid() -> str:
    return str(uuid.uuid4())
