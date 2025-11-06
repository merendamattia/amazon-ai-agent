import logging
import os

import requests
from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import (
    Application,
    CommandHandler,
    ContextTypes,
    ConversationHandler,
    MessageHandler,
    filters,
)

from agents.amazon_reviewer_agent import AmazonReviewerAgent

# Load environment variables
load_dotenv()

# Configure logger
logging.basicConfig(
    level=logging.INFO, format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger(__name__)

# Conversation states
WAITING_FOR_LINK, GENERATING_REVIEW = range(2)

# Global agent instance
agent = None


# Main keyboard layout
def get_main_keyboard():
    """Get the main keyboard with persistent buttons"""
    return ReplyKeyboardMarkup(
        [["📝 Genera Recensione", "ℹ️ Aiuto"], ["❌ Stop"]],
        resize_keyboard=True,
        one_time_keyboard=False,
    )


def _initialize_agent():
    """Initialize the Amazon Reviewer Agent"""
    global agent
    try:
        openai_api_key = os.getenv("OPENAI_API_KEY")
        openai_model = os.getenv("OPENAI_MODEL")

        if not openai_api_key or not openai_model:
            logger.error("OPENAI_API_KEY and OPENAI_MODEL must be defined in .env")
            return False

        agent = AmazonReviewerAgent(openai_api_key, openai_model)
        logger.info("Amazon Reviewer Agent initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Failed to initialize agent: {e}")
        return False


def expand_short_url(short_url: str) -> str:
    """
    Expand shortened Amazon URLs (amzn.to, amzn.eu, a.co, etc.)
    Follows HTTP redirects to get the final full URL
    """
    try:
        # Use requests.get() with allow_redirects to follow all redirects
        response = requests.get(short_url, allow_redirects=True, timeout=5)

        # Log all redirect history
        for resp in response.history:
            logger.info(f"Redirect: {resp.status_code} -> {resp.url}")

        # Get the final URL
        final_url = response.url
        logger.info(f"Expanded short URL: {short_url} -> {final_url}")
        return final_url
    except Exception as e:
        logger.warning(f"Could not expand URL {short_url}: {e}. Using original.")
        return short_url


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")

    welcome_message = (
        f"👋 Ciao {user.first_name}!\n\n"
        "🤖 Sono il tuo Amazon Reviewer AI Agent Bot.\n\n"
        "✨ Posso aiutarti a generare recensioni dettagliate per prodotti Amazon in pochi click!\n\n"
        "📱 Usa i pulsanti qui sotto per iniziare:"
    )

    await update.message.reply_text(welcome_message, reply_markup=get_main_keyboard())
    return WAITING_FOR_LINK


async def handle_button_press(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle main menu button presses"""
    user_input = update.message.text.strip()

    # Remove extra spaces within the text as well
    user_input = " ".join(user_input.split())

    if user_input == "📝 Genera Recensione":
        message = (
            "📎 Per favore, inviami il link del prodotto Amazon\n\n"
            "⏳ La generazione della recensione potrebbe richiedere qualche minuto...\n\n"
            "Usa il pulsante ❌ Stop per annullare in qualsiasi momento."
        )
        await update.message.reply_text(message, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    elif user_input == "ℹ️ Aiuto":
        help_text = (
            "ℹ️ Guida Rapida\n\n"
            "Come usare il bot:\n"
            "1️⃣ Premi 📝 Genera Recensione\n"
            "2️⃣ Incolla il link del prodotto Amazon\n"
            "3️⃣ Aspetta la generazione (1-2 minuti)\n"
            "4️⃣ Ricevi la tua recensione!\n\n"
            "Comandi disponibili:\n"
            "• /start - Menu principale\n"
            "• /help - Questa guida\n\n"
            "Supporto:\n"
            "Se il link non funziona, assicurati che:\n"
            "• Sia un URL valido di Amazon\n"
            "• Inizi con `https://`\n\n"
        )
        await update.message.reply_text(help_text, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    elif user_input == "❌ Stop":
        goodbye_text = (
            "👋 Arrivederci!\n\n" "Usa /start quando vuoi generare una nuova recensione."
        )
        await update.message.reply_text(goodbye_text, reply_markup=get_main_keyboard())
        return WAITING_FOR_LINK

    else:
        # User sent something that's not a button - check if it's an Amazon link
        if user_input.startswith(("http://", "https://")):
            return await handle_amazon_link(update, context)

        # Invalid input
        await update.message.reply_text(
            "❌ Non ho capito. Usa i pulsanti per continuare.",
            reply_markup=get_main_keyboard(),
        )
        return WAITING_FOR_LINK


async def handle_amazon_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Amazon product link and generate review"""
    link = update.message.text.strip()

    # Remove extra spaces within the link as well
    link = " ".join(link.split())

    # Validate the link
    if not link.startswith(("http://", "https://")):
        await update.message.reply_text(
            "❌ Link non valido\n\n" "Assicurati che inizi con `http://` o `https://`",
            reply_markup=get_main_keyboard(),
        )
        return WAITING_FOR_LINK

    # Check if it's an Amazon link (accept various formats)
    amazon_identifiers = ["amazon", "amzn", "a.co", "dp/", "ASIN"]
    if not any(identifier in link.lower() for identifier in amazon_identifiers):
        await update.message.reply_text(
            "❌ Non sembra un link Amazon\n\n"
            "Per favore, inviami un link da amazon.com",
            reply_markup=get_main_keyboard(),
        )
        return WAITING_FOR_LINK

    logger.info(f"User {update.effective_user.id} requested review for: {link}")

    # Show loading message
    await update.message.reply_text(
        "⏳ Sto generando la tua recensione...\n\n"
        "Questo potrebbe richiedere qualche minuto... Per favore, aspetta.\n\n"
        "🔄 Analizzando il prodotto...",
        reply_markup=get_main_keyboard(),
    )

    try:
        # Expand short URLs (amzn.to, amzn.eu, a.co, etc.) to full Amazon URLs
        final_link = expand_short_url(link)
        logger.info(f"Using expanded link: {final_link}")

        # Generate review using the agent
        if agent is None:
            await update.message.reply_text(
                "❌ Errore: L'agente non è stato inizializzato.\n\n"
                "Usa /start per ricominciare.",
                reply_markup=get_main_keyboard(),
            )
            return WAITING_FOR_LINK

        review = agent.generate_review(final_link)

        # Send the review as a single message
        await update.message.reply_text(
            f"📝 RECENSIONE GENERATA\n\n{review}",
            reply_markup=get_main_keyboard(),
        )

        # Ask for another review
        await update.message.reply_text(
            "📝 Inviami un altro link per una nuova recensione, oppure usa i pulsanti.",
            reply_markup=get_main_keyboard(),
        )

        logger.info(
            f"Review generated successfully for user {update.effective_user.id}"
        )

    except Exception as e:
        logger.error(f"Error generating review: {e}")
        await update.message.reply_text(
            f"❌ Errore durante la generazione\n\n"
            f"`{str(e)}`\n\n"
            f"Per favore, riprova con un link diverso.",
            reply_markup=get_main_keyboard(),
        )

    return WAITING_FOR_LINK


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "ℹ️ Amazon Reviewer AI Agent Bot\n\n"
        "Come usare:\n"
        "1️⃣ Premi il pulsante 📝 Genera Recensione\n"
        "2️⃣ Incolla il link del prodotto Amazon\n"
        "3️⃣ Aspetta la generazione (1-2 minuti)\n"
        "4️⃣ Ricevi la tua recensione!\n\n"
        "Comandi disponibili:\n"
        "• /start - Menu principale\n"
        "• /help - Questa guida\n\n"
        "Note tecniche:\n"
        "• Alimentato da OpenAI GPT-4\n"
        "• Usa DataPizza AI Framework\n"
        "• Python Telegram Bot\n\n"
        "Supporto:\n"
        "Se hai problemi, assicurati che il link sia valido e da amazon.com"
    )
    await update.message.reply_text(help_text, reply_markup=get_main_keyboard())


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "👋 Operazione annullata\n\n" "Usa i pulsanti per continuare!",
        reply_markup=get_main_keyboard(),
    )
    return WAITING_FOR_LINK


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Log the error and send a telegram message to notify the developer."""
    logger.error(msg="Exception while handling an update:", exc_info=context.error)

    if isinstance(update, Update) and update.effective_message:
        await update.effective_message.reply_text(
            "❌ Si è verificato un errore. Per favore, riprova con /start"
        )


def main() -> None:
    """Start the bot"""
    # Initialize the agent
    if not _initialize_agent():
        logger.error("Failed to initialize agent. Exiting.")
        return

    # Get bot token
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN must be defined in .env")
        return

    # Create the Application
    application = Application.builder().token(token).build()

    # Add conversation handler
    conv_handler = ConversationHandler(
        entry_points=[
            CommandHandler("start", start),
            MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
        ],
        states={
            WAITING_FOR_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
            ],
            GENERATING_REVIEW: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_button_press),
            ],
        },
        fallbacks=[
            CommandHandler("start", start),
            CommandHandler("help", help_command),
            CommandHandler("cancel", cancel),
        ],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
