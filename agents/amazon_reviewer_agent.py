import logging

from datapizza.agents import Agent
from datapizza.clients.openai import OpenAIClient
from datapizza.tools.web_fetch import WebFetchTool

from utils.prompt_loader import load_prompt
from utils.token_utils import truncate_to_max_tokens

logger = logging.getLogger(__name__)


class TruncatedWebFetchTool:
    """Wrapper for WebFetchTool that truncates responses to max tokens"""

    def __init__(self, original_tool):
        self.original_tool = original_tool

    def __getattr__(self, name):
        """Delegate attribute access to original tool"""
        return getattr(self.original_tool, name)

    def __call__(self, url):
        """Call the tool and truncate the result"""
        logger.debug(f"Fetching content from: {url}")
        result = self.original_tool(url)
        result = truncate_to_max_tokens(result, max_tokens=200000)
        return result


class AmazonReviewerAgent:
    """Agent for generating Amazon product reviews"""

    def __init__(self, api_key, model):
        """
        Initialize the AmazonReviewerAgent

        Args:
            api_key: OpenAI API key
            model: OpenAI model name
        """
        self.api_key = api_key
        self.model = model
        self.agent = None
        self.run_prompt_template = None

        logger.info(f"Initializing AmazonReviewerAgent with model: {model}")
        self._initialize_agent()

    def _initialize_agent(self):
        """Initialize the internal agent"""
        # Load system prompt
        system_prompt = load_prompt("system_prompt.md")

        # Load run prompt template
        self.run_prompt_template = load_prompt("run_prompt.md")

        # Create wrapped web tool
        web_tool = WebFetchTool(timeout=15.0)
        wrapped_tool = TruncatedWebFetchTool(web_tool)

        # Create agent
        self.agent = Agent(
            name="AmazonReviewAgent",
            tools=[wrapped_tool],
            client=OpenAIClient(api_key=self.api_key, model=self.model),
            system_prompt=system_prompt,
        )

        logger.info("Agent initialized successfully")

    def generate_review(self, link):
        """
        Generate a review for the given Amazon product link

        Args:
            link: Amazon product URL

        Returns:
            str: Generated review text
        """
        if not self.agent:
            raise RuntimeError("Agent not initialized")

        logger.info(f"Generating review for: {link}")

        # Format the run prompt with the provided link
        run_prompt = self.run_prompt_template.format(link=link)

        # Run the agent
        response = self.agent.run(run_prompt, tool_choice="required_first")
        review = response.text

        logger.info("Review generated successfully")
        return review
