def split_text(text: str, chunk_size: int = 500, overlap: int = 50) -> list[str]:
    chunks = []

    start = 0

    while start < len(text):
        end = start + chunk_size

        chunks.append(text[start:end])
        start = end - overlap

    return chunks


def estimate_token_count(text: str) -> int:
    """Approximate the number of model tokens in ``text``.

    Chunking is character-based, so this counts whitespace-separated words as
    a dependency-free proxy. It is intended for observability, not for billing
    or model limit enforcement.
    """
    return len(text.split())
