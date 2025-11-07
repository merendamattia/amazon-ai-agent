from agents.base_agent import BaseAmazonAgent


class AmazonReviewerAgent(BaseAmazonAgent):
    """Agent for generating Amazon product reviews"""

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "review_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "review_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "AmazonReviewAgent"

    def generate_review(self, link):
        """
        Generate a review for the given Amazon product link

        Args:
            link: Amazon product URL

        Returns:
            str: Generated review text
        """
        return self._generate(link, "review")
