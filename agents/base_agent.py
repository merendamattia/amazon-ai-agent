import logging
import os
from abc import ABC, abstractmethod

from datapizza.agents import Agent
from dotenv import load_dotenv

from utils.prompt_loader import load_prompt
from utils.url_utils import expand_short_url
from utils.client_utils import get_client
from tools.web_fetch import create_web_fetch_tool

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class BaseAmazonAgent(ABC):
    """Base class for Amazon agents with common functionality"""

    def __init__(self, api_key, model, provider="google"):
        """
        Initialize the BaseAmazonAgent

        Args:
            api_key: API key for the provider
            model: Model name
            provider: Provider name ('openai' or 'google', default: 'google')
        """
        self.api_key = api_key
        self.model = model
        self.provider = provider
        self.agent = None
        self.run_prompt_template = None

        logger.info(
            f"Initializing {self.__class__.__name__} with model: {model} (provider: {provider})"
        )
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the internal agent"""
        # Load prompts (subclasses define which prompts to load)
        system_prompt = load_prompt(self.get_system_prompt_filename())
        self.run_prompt_template = load_prompt(self.get_run_prompt_filename())

        logger.info("Creating web fetch tool with truncation support")

        # Create the web fetch tool with truncation
        web_fetch_tool = create_web_fetch_tool()

        # Get the appropriate client based on provider
        client = get_client(self.provider, self.api_key, self.model)

        # Create agent with the tool
        self.agent = Agent(
            name=self.get_agent_name(),
            tools=[web_fetch_tool],
            client=client,
            system_prompt=system_prompt,
        )

        logger.info("Agent initialized successfully")

    def _generate(self, link, output_type):
        """
        Generate output for the given Amazon product link

        Args:
            link: Amazon product URL
            output_type: Type of output being generated (for logging)

        Returns:
            str: Generated output text
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")

        logger.info(f"Generating {output_type} for: {link}")

        # Expand the URL if it's shortened
        expanded_link = expand_short_url(link)
        logger.info(f"Using link: {expanded_link}")

        # Format the run prompt with the provided link
        run_prompt = self.run_prompt_template.format(link=expanded_link)

        # Run the agent
        response = self.agent.run(run_prompt, tool_choice="required_first")
        result = response.text

        logger.info(f"{output_type.capitalize()} generated successfully")
        return result

    @abstractmethod
    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        pass

    @abstractmethod
    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        pass

    @abstractmethod
    def get_agent_name(self):
        """Return the name of the agent"""
        pass
