import logging
import os
from abc import ABC, abstractmethod

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from datapizza.tools.web_fetch import WebFetchTool
from dotenv import load_dotenv

from utils.prompt_loader import load_prompt
from utils.token_utils import truncate_to_max_tokens

# Load environment variables
load_dotenv()

logger = logging.getLogger(__name__)


class TruncatedWebFetchTool:
    """Wrapper for WebFetchTool that truncates responses to max tokens"""

    def __init__(self, original_tool, max_tokens=None):
        self.original_tool = original_tool
        # Use env var if provided, otherwise use default
        self.max_tokens = max_tokens or int(os.getenv("MAX_TOKENS", "200000"))

    def __getattr__(self, name):
        """Delegate attribute access to original tool"""
        return getattr(self.original_tool, name)

    def __call__(self, url):
        """Call the tool and truncate the result"""
        logger.debug(f"Fetching content from: {url}")
        result = self.original_tool(url)
        result = truncate_to_max_tokens(result, max_tokens=self.max_tokens)
        return result


class BaseAmazonAgent(ABC):
    """Base class for Amazon agents with common functionality"""

    def __init__(self, api_key, model):
        """
        Initialize the BaseAmazonAgent

        Args:
            api_key: OpenAI API key
            model: OpenAI model name
        """
        self.api_key = api_key
        self.model = model
        self.agent = None
        self.run_prompt_template = None

        logger.info(f"Initializing {self.__class__.__name__} with model: {model}")
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the internal agent"""
        # Load prompts (subclasses define which prompts to load)
        system_prompt = load_prompt(self.get_system_prompt_filename())
        self.run_prompt_template = load_prompt(self.get_run_prompt_filename())

        # Get configuration from environment variables
        max_tokens = int(os.getenv("MAX_TOKENS", "200000"))
        web_fetch_timeout = float(os.getenv("WEB_FETCH_TIMEOUT", "15"))

        logger.info(
            f"Using MAX_TOKENS={max_tokens}, WEB_FETCH_TIMEOUT={web_fetch_timeout}"
        )

        # Create wrapped web tool with configuration
        web_tool = WebFetchTool(timeout=web_fetch_timeout)
        wrapped_tool = TruncatedWebFetchTool(web_tool, max_tokens=max_tokens)

        # Create agent
        self.agent = Agent(
            name=self.get_agent_name(),
            tools=[wrapped_tool],
            client=OpenAIClient(api_key=self.api_key, model=self.model),
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

        # Format the run prompt with the provided link
        run_prompt = self.run_prompt_template.format(link=link)

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
