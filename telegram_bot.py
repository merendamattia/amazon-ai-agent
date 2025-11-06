import logging
import os

from dotenv import load_dotenv
from telegram import ReplyKeyboardMarkup, ReplyKeyboardRemove, Update
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
SELECTING_ACTION, WAITING_FOR_LINK = range(2)

# Global agent instance
agent = None


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


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Start the conversation and show main menu"""
    user = update.effective_user
    logger.info(f"User {user.id} started the bot")

    welcome_message = (
        f"👋 Ciao {user.first_name}!\n\n"
        "Sono il tuo **Amazon Reviewer AI Agent Bot**.\n\n"
        "Posso aiutarti a generare recensioni dettagliate per prodotti Amazon.\n\n"
        "Cosa vuoi fare?"
    )

    keyboard = [["📝 Genera Recensione", "❌ Esci"]]
    reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)

    await update.message.reply_text(welcome_message, reply_markup=reply_markup)
    return SELECTING_ACTION


async def handle_menu_selection(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> int:
    """Handle menu selection"""
    user_input = update.message.text

    if user_input == "📝 Genera Recensione":
        message = (
            "📎 Per favore, inviami il link del prodotto Amazon.\n\n"
            "Esempio: `https://www.amazon.com/your-product-link`\n\n"
            "⏳ La generazione della recensione potrebbe richiedere qualche minuto..."
        )
        await update.message.reply_text(
            message,
            reply_markup=ReplyKeyboardRemove(),
        )
        return WAITING_FOR_LINK

    elif user_input == "❌ Esci":
        await update.message.reply_text(
            "👋 Arrivederci! Usa /start per ricominciare.",
            reply_markup=ReplyKeyboardRemove(),
        )
        return ConversationHandler.END

    else:
        await update.message.reply_text(
            "❌ Opzione non riconosciuta. Usa i pulsanti sottostanti.",
            reply_markup=ReplyKeyboardMarkup(
                [["📝 Genera Recensione", "❌ Esci"]], one_time_keyboard=True
            ),
        )
        return SELECTING_ACTION


async def handle_amazon_link(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Handle Amazon product link and generate review"""
    link = update.message.text.strip()

    # Validate the link
    if not link.startswith(("http://", "https://")):
        await update.message.reply_text(
            "❌ Il link non è valido. Assicurati che inizi con `http://` o `https://`"
        )
        return WAITING_FOR_LINK

    if "amazon" not in link.lower():
        await update.message.reply_text(
            "❌ Il link non sembra essere un link Amazon. Per favore, inviami un link valido."
        )
        return WAITING_FOR_LINK

    logger.info(f"User {update.effective_user.id} requested review for: {link}")

    # Show loading message
    loading_message = await update.message.reply_text(
        "⏳ Sto generando la tua recensione...\n\n"
        "Questo potrebbe richiedere un minuto o due. Per favore, aspetta..."
    )

    try:
        # Generate review using the agent
        if agent is None:
            await loading_message.edit_text(
                "❌ Errore: L'agente non è stato inizializzato. Riprova con /start"
            )
            return SELECTING_ACTION

        review = agent.generate_review(link)

        # Check if review is too long for a single message (max 4096 chars)
        if len(review) > 4000:
            # Split the review into multiple messages
            await loading_message.delete()
            messages = [review[i : i + 4000] for i in range(0, len(review), 4000)]
            for idx, msg in enumerate(messages):
                await update.message.reply_text(msg)
            # Add final message with link
            await update.message.reply_text(
                f"✅ Recensione completata!\n\nLink prodotto: {link}"
            )
        else:
            await loading_message.edit_text(review)

        logger.info(
            f"Review generated successfully for user {update.effective_user.id}"
        )

        # Show menu to generate another review
        keyboard = [["📝 Genera Altra Recensione", "❌ Esci"]]
        reply_markup = ReplyKeyboardMarkup(keyboard, one_time_keyboard=True)
        await update.message.reply_text(
            "🎉 Vuoi generare un'altra recensione?", reply_markup=reply_markup
        )
        return SELECTING_ACTION

    except Exception as e:
        logger.error(f"Error generating review: {e}")
        await loading_message.edit_text(
            f"❌ Errore durante la generazione della recensione:\n\n`{str(e)}`\n\n"
            "Per favore, riprova con /start"
        )
        return SELECTING_ACTION


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Send help message"""
    help_text = (
        "🤖 **Amazon Reviewer AI Agent Bot**\n\n"
        "**Comandi disponibili:**\n"
        "• /start - Avvia il bot\n"
        "• /help - Mostra questo messaggio\n\n"
        "**Come usare:**\n"
        "1️⃣ Fai clic su 'Genera Recensione'\n"
        "2️⃣ Invia il link del prodotto Amazon\n"
        "3️⃣ Aspetta che l'IA generi la recensione\n"
        "4️⃣ Ricevi la tua recensione dettagliata!\n\n"
        "⚙️ **Tecnologie utilizzate:**\n"
        "• OpenAI GPT-4\n"
        "• DataPizza AI Framework\n"
        "• Python Telegram Bot"
    )
    await update.message.reply_text(help_text)


async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    """Cancel the conversation"""
    await update.message.reply_text(
        "❌ Operazione annullata. Usa /start per ricominciare.",
        reply_markup=ReplyKeyboardRemove(),
    )
    return ConversationHandler.END


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
        entry_points=[CommandHandler("start", start)],
        states={
            SELECTING_ACTION: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_menu_selection)
            ],
            WAITING_FOR_LINK: [
                MessageHandler(filters.TEXT & ~filters.COMMAND, handle_amazon_link)
            ],
        },
        fallbacks=[CommandHandler("start", start), CommandHandler("cancel", cancel)],
    )

    application.add_handler(conv_handler)
    application.add_handler(CommandHandler("help", help_command))
    application.add_error_handler(error_handler)

    # Start the Bot
    logger.info("Starting Telegram bot...")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
