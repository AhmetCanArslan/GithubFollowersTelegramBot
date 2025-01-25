from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import logging
import re
from datetime import datetime
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
# Disable httpx logging
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger("httpcore").setLevel(logging.WARNING)
# Get our logger
logger = logging.getLogger(__name__)

# Load environment variables
load_dotenv()

# Get token from environment variables
TOKEN: Final[str] = os.getenv('TELEGRAM_TOKEN')
BOT_USERNAME: Final[str] = os.getenv('BOT_USERNAME')

# Validate that required environment variables are set
if not TOKEN or not BOT_USERNAME:
    raise ValueError("Please ensure TELEGRAM_TOKEN and BOT_USERNAME are set in .env file")

def sanitize_username(username: str) -> str:
    """Sanitize GitHub username to prevent injection attacks"""
    # Remove any characters that aren't alphanumeric, dash, or underscore
    sanitized = re.sub(r'[^a-zA-Z0-9\-_]', '', username)
    return sanitized

def log_message(update: Update, response: str):
    """Log message details to console"""
    user = update.message.from_user
    current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    
    # Extract number from response if it contains unfollowers count
    response_length = "0"
    if "takip etmeyen kullanıcılar" in response:
        try:
            # Extract number between parentheses
            response_length = re.search(r'\((\d+)\)', response).group(1)
        except:
            response_length = "Error"
    elif "Harika!" in response:
        response_length = "0"
    elif "hata" in response.lower():
        response_length = "Error"
    
    logger.info(f"""
=== New Message ===
Time: {current_time}
From User: {user.first_name} {user.last_name if user.last_name else ''} (@{user.username if user.username else 'No username'})
User ID: {user.id}
IP/User ID: {user.id}
Message: {update.message.text}
Response Length: {response_length}
=================""")

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Merhaba! GitHub'da sizi takip etmeyen kişileri gösterebilen bir botum."
    await update.message.reply_text(response)
    log_message(update, response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "GitHub Kullanıcı Adınızı girerek kullanabilirsiniz. \nÖrnek: 'AhmetCanArslan'"
    await update.message.reply_text(response)
    log_message(update, response)

async def custom_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Custom command executed."
    await update.message.reply_text(response)
    log_message(update, response)

# Messages
async def handle_response(username: str) -> str:
    try:
        # Sanitize input
        clean_username = sanitize_username(username)
        
        if not clean_username:
            return "Geçersiz kullanıcı adı. Lütfen geçerli bir GitHub kullanıcı adı girin."
        
        # Add delay protection
        if len(clean_username) > 39:  # GitHub username max length is 39
            return "Kullanıcı adı çok uzun. Lütfen geçerli bir GitHub kullanıcı adı girin."

        # GitHub API endpoints
        followers_url = f"https://api.github.com/users/{clean_username}/followers"
        following_url = f"https://api.github.com/users/{clean_username}/following"
        
        try:
            # Fetch followers and following with timeout
            followers_response = requests.get(followers_url, timeout=10)
            following_response = requests.get(following_url, timeout=10)
        except requests.Timeout:
            return "GitHub API yanıt vermedi. Lütfen daha sonra tekrar deneyin."
        except requests.RequestException:
            return "Bağlantı hatası oluştu. Lütfen daha sonra tekrar deneyin."
        
        if followers_response.status_code == 404 or following_response.status_code == 404:
            return "Kullanıcı adı bulunamadı. Lütfen geçerli bir GitHub kullanıcı adı girin."
        
        if followers_response.status_code != 200 or following_response.status_code != 200:
            return "GitHub API'sine erişimde bir sorun oluştu. Lütfen daha sonra tekrar deneyin."
        
        # Extract usernames from responses
        followers = set(user['login'] for user in followers_response.json())
        following = set(user['login'] for user in following_response.json())
        
        # Find users who don't follow back
        unfollowers = following - followers
        
        if not unfollowers:
            return f"Harika! Takip ettiğiniz herkes sizi geri takip ediyor!"
        
        # Create response message
        response = f"Sizi takip etmeyen kullanıcılar ({len(unfollowers)}):\n\n"
        for user in sorted(unfollowers):
            response += f"• {user}\n"
        
        return response
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return "Bir hata oluştu. Lütfen daha sonra tekrar deneyin."

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    
    # Process only private messages
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            response = await handle_response(new_text)
        else:
            return
    else:
        response = await handle_response(text)
    
    await update.message.reply_text(response)
    log_message(update, response)

# Error Handler
async def error(update: Update, context: ContextTypes.DEFAULT_TYPE):
    logger.error(f'Update {update} caused error {context.error}')

# Main Function
def main() -> None:
    logger.info('Starting bot...')
    
    try:
        app = Application.builder().token(TOKEN).build()

        # Commands
        app.add_handler(CommandHandler('start', start_command))
        app.add_handler(CommandHandler('help', help_command))
        app.add_handler(CommandHandler('custom', custom_command))

        # Messages
        app.add_handler(MessageHandler(filters.TEXT, handle_message))

        # Errors
        app.add_error_handler(error)

        # Polls the bot
        logger.info('Bot is running...')
        app.run_polling(poll_interval=3)
        
    except Exception as e:
        logger.error(f'Critical error: {str(e)}')

if __name__ == '__main__':
    main()

