from hashlib import sha256


class HashService:
    @staticmethod
    def sha256(content: str) -> str:
        return sha256(content.encode("utf-8")).hexdigest()
