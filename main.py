from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from transformers import AutoModelForCausalLM, AutoTokenizer
import torch
import os

load_dotenv()

# Global variables
_TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
_MODEL_PATH = os.getenv("MODEL_PATH")
_ALLOWED_ROLES = os.getenv("ALLOWED_ROLES").split(",")  # Fetch allowed roles from environment variable
_DEFAULT_ROLE = os.getenv("DEFAULT_ROLE")
# LLM chat model setup
model = AutoModelForCausalLM.from_pretrained(_MODEL_PATH)
tokenizer = AutoTokenizer.from_pretrained(_MODEL_PATH)

# Global variable to store the current role, default role is the first in the allowed list
current_role = "@ZoneTwelve"

if isinstance(_DEFAULT_ROLE, str) and _DEFAULT_ROLE in _ALLOWED_ROLES:
    current_role = _DEFAULT_ROLE

def chat_with_ncueatingai(
    prompt: str = "What's for lunch?",
    system_prompt: str = "You act like a @ZoneTwelve.",
    max_tokens: int = 128,
):
    """Generate a response from the NCUEatingAI model based on the user input."""
    # Prepare the chat messages
    messages = [
        {"role": "system", "content": system_prompt},
        {"role": "user", "content": prompt}
    ]

    # Apply chat template
    input_text = tokenizer.apply_chat_template(messages, tokenize=False, add_generation_prompt=True)

    # Tokenize inputs
    inputs = tokenizer(input_text, return_tensors="pt")

    # Generate response
    try:
      with torch.no_grad():
          outputs = model.generate(
              inputs.input_ids,
              max_length=max_tokens,
              pad_token_id=tokenizer.eos_token_id,
              do_sample=True,
              temperature=1.15,
          )

      # Decode the response
      response = tokenizer.decode(outputs[0][:-1], skip_special_tokens=False)
    except ValueError as e:
      response = "Oops, I can not process that."
    return response.replace(input_text, "")

# Define a command handler for the /start command
async def start(update: Update, context) -> None:
    """Send a message when the command /start is issued."""
    await update.message.reply_text('Hello! I am your friendly bot. How can I help you today?')

# Define a command handler for the /help command
async def help_command(update: Update, context) -> None:
    """Send a message when the command /help is issued."""
    await update.message.reply_text(
        'You can use the following commands:\n'
        '/start - Start the bot\n'
        '/help - Get help\n'
        '/role - Change the AI role\n'
    )

# Define a command handler for the /role command
async def role_command(update: Update, context) -> None:
    """Change the role of the AI if the role is in the allowed list."""
    global current_role

    if len(context.args) == 0:
        await update.message.reply_text(f'Please provide a role. Allowed roles: {", ".join(_ALLOWED_ROLES)}')
        return

    requested_role = context.args[0].lower()

    if requested_role in _ALLOWED_ROLES:
        current_role = requested_role
        await update.message.reply_text(f'Role has been changed to: {current_role}')
    else:
        await update.message.reply_text(f'Invalid role. Allowed roles are: {", ".join(_ALLOWED_ROLES)}')

# Define a message handler to generate an AI-based response
async def ai_response(update: Update, context) -> None:
    """Generate AI-based response for the user message."""
    user_message = update.message.text
    print("User message", user_message)

    # Use the current role to adjust the system prompt
    system_prompt = f"You act like a {current_role}."

    # Generate the response using the chat_with_ncueatingai function
    ai_reply = chat_with_ncueatingai(prompt=user_message, system_prompt=system_prompt)

    # Send the AI-generated reply back to the user
    await update.message.reply_text(f"[{current_role.replace('@', '')}]\n{ai_reply}")

async def reply_command(update: Update, context):
    if update.message.reply_to_message:
        original_message = update.message.reply_to_message.text

        # Use the current role to adjust the system prompt
        system_prompt = f"You act like a {current_role}."

        # Generate the response using the chat_with_ncueatingai function
        ai_reply = chat_with_ncueatingai(prompt=original_message, system_prompt=system_prompt)

        # Send the AI-generated reply back to the user
        await update.message.reply_text(f"[{current_role.replace('@', '')}]\n{ai_reply}")

# Main function to set up the bot
def main():
    """Start the bot."""
    # Create an Application instance
    application = Application.builder().token(_TELEGRAM_BOT_TOKEN).build()

    # Add handlers for commands
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("role", role_command))  # Handler for /role command
    application.add_handler(CommandHandler("reply", reply_command))

    # Add a handler for text messages and AI response
    #application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, ai_response))
    application.add_handler(MessageHandler(filters.TEXT, ai_response))

    # Start the bot
    application.run_polling()

if __name__ == '__main__':
    main()
