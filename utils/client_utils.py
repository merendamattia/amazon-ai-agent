import logging

from datapizza.clients.openai import OpenAIClient
from datapizza.clients.google import GoogleClient

logger = logging.getLogger(__name__)


def get_client(provider: str, api_key: str, model: str):
    """
    Create and return a client based on the provider

    Args:
        provider: The provider name ('openai' or 'google')
        api_key: The API key for the provider
        model: The model name

    Returns:
        The client instance

    Raises:
        ValueError: If the provider is not supported
    """
    provider = provider.lower()

    if provider == "openai":
        logger.info(f"Using OpenAI provider with model: {model}")
        return OpenAIClient(api_key=api_key, model=model)
    elif provider == "google":
        logger.info(f"Using Google provider with model: {model}")
        return GoogleClient(api_key=api_key, model=model)
    else:
        raise ValueError(
            f"Unsupported provider: {provider}. Available providers: openai, google"
        )
