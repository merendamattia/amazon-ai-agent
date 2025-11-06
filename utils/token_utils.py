import logging

import tiktoken

logger = logging.getLogger(__name__)


def truncate_to_max_tokens(text, max_tokens=200000):
    """Truncate text to a maximum number of tokens"""
    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) > max_tokens:
        truncated_tokens = tokens[:max_tokens]
        truncated_text = encoding.decode(truncated_tokens)
        logger.warning(f"Content truncated from {len(tokens)} to {max_tokens} tokens")
        return truncated_text

    return text
