import hashlib

class HashUtils:
    @staticmethod
    def fnv1a_hash(data: bytes) -> int:
        """Genera un hash FNV-1a de 32 bits para los datos introducidos"""
        fnv_prime = 0x01000193
        hash_value = 0x811c9dc5
        for byte in data:
            hash_value ^= byte
            hash_value = (hash_value * fnv_prime) % (2**32)
        return hash_value

    @staticmethod
    def sha256_hash(data: bytes) -> str:
        """Genera un hash SHA-256 (alternativa)."""
        sha256 = hashlib.sha256()
        sha256.update(data)
        return sha256.hexdigest()

    @staticmethod
    def hash_file(filepath: str, use_fnv: bool = True) -> str:
        """Genera un hash del archivo especificado"""
        with open(filepath, "rb") as f:
            data = f.read()
        if use_fnv:
            return str(HashUtils.fnv1a_hash(data))  # lo devolvemos como string
        else:
            return HashUtils.sha256_hash(data)

    @staticmethod
    def hash_text(text: str, use_fnv: bool = True) -> str:
        """Genera un hash de un texto (string)"""
        data = text.encode("utf-8")
        if use_fnv:
            return str(HashUtils.fnv1a_hash(data))
        else:
            return HashUtils.sha256_hash(data)