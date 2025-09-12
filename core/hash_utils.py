#algoritmo hash (FNV-1a o hashlib)
import hashlib
import fnvhash
import os

class HashUtils:
    @staticmethod
    def fnv1a_hash(data: bytes) -> int:
        """Genera un hash FNV-1a para los datos proporcionados."""
        return fnvhash.fnv1a_32(data)

    @staticmethod
    def sha256_hash(data: bytes) -> str:
        """Genera un hash SHA-256 para los datos proporcionados."""
        sha256 = hashlib.sha256()
        sha256.update(data)
        return sha256.hexdigest()

    @staticmethod
    def generate_salt(length: int = 16) -> bytes:
        """Genera una sal aleatoria de la longitud especificada."""
        return os.urandom(length)

    @staticmethod
    def hash_with_salt(data: bytes, salt: bytes) -> str:
        """Genera un hash SHA-256 para los datos proporcionados con una sal."""
        return HashUtils.sha256_hash(salt + data)