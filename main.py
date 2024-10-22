from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
import os

load_dotenv()

# Global variables
_TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# Define a command handler for the /start command
async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! I am your friendly bot. How can I help you today?')

# Define a command handler for the /help command
async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text('You can use the following commands:\n/start - Start the bot\n/help - Get help')

# Define a message handler to echo all text messages
async def echo(update: Update, context) -> None:
    """Echo the user message."""
    await update.message.reply_text(f'You said: {update.message.text}')

# Main function to set up the bot
def main():
    """Start the bot."""
    # Use your own bot token here

    # Create an Application instance
    application = Application.builder().token(_TELEGRAM_BOT_TOKEN).build()

    # Add handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))

    # Add a handler for normal text messages
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()

