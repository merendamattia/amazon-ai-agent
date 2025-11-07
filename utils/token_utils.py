import logging
import os

import tiktoken
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


def truncate_to_max_tokens(text, max_tokens=None):
    """
    Truncate text to a maximum number of tokens

    Args:
        text: Text to truncate
        max_tokens: Maximum tokens allowed. If None, uses MAX_TOKENS from .env (default: 200000)

    Returns:
        str: Truncated text
    """
    # Use provided max_tokens or read from environment variable
    if max_tokens is None:
        max_tokens = int(os.getenv("MAX_TOKENS", "200000"))

    encoding = tiktoken.get_encoding("cl100k_base")
    tokens = encoding.encode(text)

    if len(tokens) > max_tokens:
        truncated_tokens = tokens[:max_tokens]
        truncated_text = encoding.decode(truncated_tokens)
        logger.warning(f"Content truncated from {len(tokens)} to {max_tokens} tokens")
        return truncated_text

    return text
