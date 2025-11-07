import argparse
import logging
import os

from dotenv import load_dotenv

from agents.amazon_reviewer_agent import AmazonReviewerAgent
from agents.amazon_sales_listing_agent import AmazonSalesListingAgent

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)


def _load_environment():
    """Load environment variables"""
    load_dotenv()
    openai_api_key = os.getenv("OPENAI_API_KEY")
    openai_model = os.getenv("OPENAI_MODEL")

    if not openai_api_key or not openai_model:
        raise ValueError("OPENAI_API_KEY and OPENAI_MODEL must be defined in .env")

    logger.info(f"Environment loaded with model: {openai_model}")
    return openai_api_key, openai_model


def _parse_arguments():
    """Parse command line arguments"""
    parser = argparse.ArgumentParser(
        description="Generate an Amazon product review or sales listing using an AI agent"
    )
    parser.add_argument("link", help="Amazon product link")
    parser.add_argument(
        "--type",
        choices=["review", "listing"],
        default="review",
        help="Output type: 'review' for product review or 'listing' for sales listing (default: review)",
    )
    return parser.parse_args()


def main():
    """Main function"""
    try:
        logger.info("Starting Amazon review/listing generator")

        # Parse arguments
        args = _parse_arguments()
        link = args.link
        output_type = args.type
        logger.info(f"Processing link: {link} (type: {output_type})")

        # Load environment
        api_key, model = _load_environment()

        # Initialize appropriate agent based on type
        if output_type == "listing":
            agent = AmazonSalesListingAgent(api_key, model)
            logger.info("Sales Listing Agent initialized")

            # Generate sales listing
            logger.info("Generating sales listing...")
            result = agent.generate_listing(link)
            logger.info("Sales listing generated successfully")
        else:
            agent = AmazonReviewerAgent(api_key, model)
            logger.info("Reviewer Agent initialized")

            # Generate review
            logger.info("Generating review...")
            result = agent.generate_review(link)
            logger.info("Review generated successfully")

        print(result)

    except FileNotFoundError as e:
        logger.error(f"File not found - {e}")
    except ValueError as e:
        logger.error(f"Configuration error: {e}")
    except Exception as e:
        logger.error(f"Error: {e}", exc_info=True)


if __name__ == "__main__":
    main()
