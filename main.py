from typing import Final
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import requests
import os
import logging
import re
from datetime import datetime, timedelta
from dotenv import load_dotenv
from collections import defaultdict, deque

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
GITHUB_TOKEN: Final[str] = os.getenv('GITHUB_TOKEN')

# Validate that required environment variables are set
if not TOKEN or not BOT_USERNAME:
    raise ValueError("Please ensure TELEGRAM_TOKEN and BOT_USERNAME are set in .env file")

# Change the constant name and value
USER_COOLDOWN_SECONDS = 15  # Changed from USER_COOLDOWN_MINUTES
user_last_request = defaultdict(datetime.now)

# Rate limiting constants
MESSAGE_WINDOW_SECONDS = 60  # Time window to track messages (1 minute)
MAX_MESSAGES = 3  # Maximum messages allowed in the window
TEMP_BLOCK_SECONDS = 30  # Temporary block duration
user_messages = defaultdict(lambda: deque(maxlen=MAX_MESSAGES))  # Track message timestamps
user_block_until = defaultdict(lambda: datetime.min)  # Track block expiry time

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
Message: {update.message.text}
Response Length: {response_length}
=================""")

# Commands
async def start_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "Merhaba! GitHub'da sizi takip etmeyen kişileri gösterebilen bir botum. Kullanıcı adınızı girerek kullanabilirsiniz. \n\nHello! This is a bot that can show you who doesn't follow you on GitHub. You can use your username to use it."
    await update.message.reply_text(response) 
    log_message(update, response)

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    response = "GitHub Kullanıcı Adınızı girerek kullanabilirsiniz.\n\nGitHub username can be entered to use it.\n\nExample: 'AhmetCanArslan'"
    await update.message.reply_text(response)
    log_message(update, response)


# Messages
async def handle_response(username: str) -> list[str]:
    try:
        username = sanitize_username(username)
        followers = set()
        following = set()
        
        # Add headers for authentication
        headers = {}
        if GITHUB_TOKEN:
            headers['Authorization'] = f'token {GITHUB_TOKEN}'
        
        # Get all followers with pagination
        page = 1
        while True:
            followers_url = f"https://api.github.com/users/{username}/followers"
            followers_response = requests.get(
                f"{followers_url}?page={page}&per_page=100",
                headers=headers,
                timeout=10
            )
            
            if followers_response.status_code != 200 or not followers_response.json():
                break
                
            followers.update(user['login'] for user in followers_response.json())
            page += 1
        
        # Get all following with pagination
        page = 1
        while True:
            following_url = f"https://api.github.com/users/{username}/following"
            following_response = requests.get(
                f"{following_url}?page={page}&per_page=100",
                headers=headers,
                timeout=10
            )
            
            if following_response.status_code != 200 or not following_response.json():
                break
                
            following.update(user['login'] for user in following_response.json())
            page += 1

        # Log remaining rate limit
        remaining = followers_response.headers.get('X-RateLimit-Remaining')
        limit = followers_response.headers.get('X-RateLimit-Limit')
        logger.info(f"GitHub API Rate Limit - Remaining: {remaining}/{limit}")

        # Check rate limit from first API response
        if followers_response.status_code == 403:
            rate_reset_time = datetime.fromtimestamp(int(followers_response.headers.get('X-RateLimit-Reset', 0)))
            minutes_to_reset = max(0, (rate_reset_time - datetime.now()).total_seconds() / 60)
            return [f"GitHub API sınırına ulaşıldı. Lütfen {round(minutes_to_reset)} dakika sonra tekrar deneyin.\n\nGitHub API rate limit reached. Please try again in {round(minutes_to_reset)} minutes."]

        if following_response.status_code == 403:
            rate_reset_time = datetime.fromtimestamp(int(following_response.headers.get('X-RateLimit-Reset', 0)))
            minutes_to_reset = max(0, (rate_reset_time - datetime.now()).total_seconds() / 60)
            return [f"GitHub API sınırına ulaşıldı. Lütfen {round(minutes_to_reset)} dakika sonra tekrar deneyin.\n\nGitHub API rate limit reached. Please try again in {round(minutes_to_reset)} minutes."]

        if followers_response.status_code == 404 or following_response.status_code == 404:
            return ["Kullanıcı adı bulunamadı. Lütfen geçerli bir GitHub kullanıcı adı girin. \n\nUser not found. Please enter a valid GitHub username."]
        
        # Find users who don't follow back
        unfollowers = following - followers
        not_following_back = followers - following
        
        responses = []
        current_response = ""
        
        if not unfollowers and not not_following_back:
            return [f"Harika! Takip ettiğiniz herkes sizi geri takip ediyor ve siz de sizi takip eden herkesi takip ediyorsunuz!\n\nCongratulations! Everyone you follow is following you back and you follow everyone who follows you!"]
        
        if not unfollowers:
            current_response += "Harika! Sizi takip etmeyen kimse yok!\n\nGreat! Everyone you follow is following you back!\n\n"
        else:
            current_response += f"Users not following you\n\nSizi takip etmeyen kullanıcılar ({len(unfollowers)}):\n\n"
            # Split unfollowers into chunks
            for user in sorted(unfollowers):
                user_line = f"• [{user}](https://github.com/{user})\n"
                if len(current_response) + len(user_line) > 3000:  # Telegram limit safety
                    responses.append(current_response)
                    current_response = user_line
                else:
                    current_response += user_line
        
        if current_response:
            responses.append(current_response)
            current_response = ""
        
        if not_following_back:
            header = f"\n─────────────────────\n\nUsers you don't follow back\n\nSizin takip etmediğiniz kullanıcılar ({len(not_following_back)}):\n\n"
            current_response = header
            
            for user in sorted(not_following_back):
                user_line = f"• [{user}](https://github.com/{user})\n"
                if len(current_response) + len(user_line) > 3000:
                    responses.append(current_response)
                    current_response = user_line
                else:
                    current_response += user_line
            
            if current_response:
                responses.append(current_response)
        
        return responses
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}")
        return ["Bir hata oluştu. Lütfen daha sonra tekrar deneyin. \n\nAn error occurred. Please try again later."]

async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    message_type: str = update.message.chat.type
    text: str = update.message.text
    user_id = update.message.from_user.id
    current_time = datetime.now()

    # Check if user is temporarily blocked
    if current_time < user_block_until[user_id]:
        remaining_seconds = (user_block_until[user_id] - current_time).seconds
        logger.warning(f"Blocked user attempt - User ID: {user_id}, Username: {update.message.from_user.username}")
        await update.message.reply_text(
            f"Çok fazla mesaj gönderdiniz. Lütfen {remaining_seconds} saniye bekleyin.\n\n"
            f"Too many messages. Please wait {remaining_seconds} seconds.",
            parse_mode='Markdown'
        )
        return

    # Add current message timestamp to user's history
    user_messages[user_id].append(current_time)
    
    # Check if user has sent too many messages in the time window
    if len(user_messages[user_id]) >= MAX_MESSAGES:
        oldest_message = user_messages[user_id][0]
        if (current_time - oldest_message).seconds < MESSAGE_WINDOW_SECONDS:
            # User exceeded rate limit, apply temporary block
            user_block_until[user_id] = current_time + timedelta(seconds=TEMP_BLOCK_SECONDS)
            logger.warning(f"Applied temp block - User ID: {user_id}, Username: {update.message.from_user.username}")
            await update.message.reply_text(
                f"Çok fazla mesaj gönderdiniz. Lütfen {TEMP_BLOCK_SECONDS} saniye bekleyin.\n\n"
                f"Too many messages. Please wait {TEMP_BLOCK_SECONDS} seconds.",
                parse_mode='Markdown'
            )
            return

    # Process the message if not blocked
    if message_type == 'group':
        if BOT_USERNAME in text:
            new_text = text.replace(BOT_USERNAME, '').strip()
            responses = await handle_response(new_text)
        else:
            return
    else:
        responses = await handle_response(text)
    
    # Send each response separately
    for response in responses:
        await update.message.reply_text(response, parse_mode='Markdown', disable_web_page_preview=True)
    
    log_message(update, responses[0])  # Log first response or modify logging as needed

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

