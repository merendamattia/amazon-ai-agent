from agents.base_agent import BaseAmazonAgent


class AmazonSalesListingAgent(BaseAmazonAgent):
    """Agent for generating Amazon product sales listings"""

    def get_system_prompt_filename(self):
        """Return the filename of the system prompt"""
        return "sales_listing_system_prompt.md"

    def get_run_prompt_filename(self):
        """Return the filename of the run prompt template"""
        return "sales_listing_run_prompt.md"

    def get_agent_name(self):
        """Return the name of the agent"""
        return "AmazonSalesListingAgent"

    def generate_listing(self, link):
        """
        Generate a sales listing for the given Amazon product link

        Args:
            link: Amazon product URL

        Returns:
            str: Generated sales listing text
        """
        return self._generate(link, "sales listing")
