import logging

import requests

logger = logging.getLogger(__name__)


def expand_short_url(short_url: str) -> str:
    """
    Expand shortened Amazon URLs (amzn.to, amzn.eu, a.co, etc.)
    Follows HTTP redirects to get the final full URL

    Args:
        short_url: The shortened URL to expand

    Returns:
        str: The expanded full URL, or the original URL if expansion fails
    """
    try:
        # Use requests.get() with allow_redirects to follow all redirects
        response = requests.get(short_url, allow_redirects=True, timeout=5)

        # Log all redirect history
        for resp in response.history:
            logger.info(f"Redirect: status code {resp.status_code} -> {resp.url}")

        # Get the final URL
        final_url = response.url
        logger.info(f"Expanded short URL: {short_url} -> {final_url}")
        return final_url
    except Exception as e:
        logger.warning(f"Could not expand URL {short_url}: {e}. Using original.")
        return short_url
