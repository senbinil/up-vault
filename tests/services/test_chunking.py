from up_vault.services.chunking import estimate_token_count, split_text


def test_split_text_preserves_order_and_overlap() -> None:
    text = "0123456789" * 100  # 1000 characters

    chunks = split_text(text, chunk_size=500, overlap=50)

    assert chunks == [text[0:500], text[450:950], text[900:1000]]
    assert chunks[0][-50:] == chunks[1][:50]
    assert chunks[1][-50:] == chunks[2][:50]


def test_split_text_returns_a_single_chunk_for_short_content() -> None:
    assert split_text("hello", chunk_size=500, overlap=50) == ["hello"]


def test_split_text_returns_no_chunks_for_empty_content() -> None:
    assert split_text("") == []


def test_estimate_token_count_counts_words() -> None:
    assert estimate_token_count("hello world") == 2


def test_estimate_token_count_ignores_extra_whitespace() -> None:
    assert estimate_token_count("  hello\n\tworld  ") == 2


def test_estimate_token_count_of_empty_text_is_zero() -> None:
    assert estimate_token_count("") == 0
