import logging
import os

from datapizza.tools import tool

from utils.token_utils import truncate_to_max_tokens

logger = logging.getLogger(__name__)


def create_web_fetch_tool():
    """
    Create a web fetch tool with truncation support

    Returns:
        A tool function that can be used with datapizza agents
    """
    from datapizza.tools.web_fetch import WebFetchTool

    # Get configuration from environment variables
    try:
        web_fetch_timeout = float(os.getenv("WEB_FETCH_TIMEOUT", "15"))
    except ValueError:
        raise ValueError(
            "Invalid WEB_FETCH_TIMEOUT value in environment: must be a number"
        )
    try:
        max_tokens = int(os.getenv("MAX_TOKENS", "150000"))
    except ValueError:
        raise ValueError("Invalid MAX_TOKENS value in environment: must be an integer")

    # Create the base web fetch tool
    web_fetch_tool = WebFetchTool(timeout=web_fetch_timeout)

    @tool
    def fetch_and_truncate(url: str) -> str:
        """
        Fetch content from a URL and truncate to max tokens

        Args:
            url: The URL to fetch from

        Returns:
            str: The fetched and truncated content
        """
        logger.debug(f"Fetching content from: {url}")
        result = web_fetch_tool(url)
        result = truncate_to_max_tokens(result, max_tokens=max_tokens)
        return result

    return fetch_and_truncate
