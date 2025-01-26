# GitHub Followers Telegram Bot

A Telegram bot that helps you discover who doesn't follow you back on GitHub and who follows you that you don't follow back.

## Features

- Shows users who don't follow you back on GitHub
- Shows users who follow you that you don't follow back
- Clickable usernames that link to GitHub profiles
- Simple to use - just send your GitHub username
- Sanitizes inputs for security
- Detailed logging of bot usage
- Rate limiting protection:
  - GitHub API rate limiting with remaining limit display
  - User message rate limiting (3 messages per minute)
  - Temporary blocks (30 seconds) for excessive usage
- Support for GitHub API authentication for higher rate limits

## Usage

1. Start a chat with the bot: [@github_follower_bot](https://t.me/github_follower_bot)
2. Send your GitHub username
3. The bot will analyze your followers and following lists
4. You'll receive:
   - A list of users who don't follow you back
   - A list of users who follow you that you don't follow back

Note: To prevent abuse, there's a limit of 3 messages per minute. Exceeding this will result in a 30-second temporary block.

## Setup Your Own Instance

### Prerequisites

- Python 3.7+
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- Your Telegram Bot's username
- (Optional) GitHub Personal Access Token for higher API rate limits

### Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in `.env` file:
   ```
   TELEGRAM_TOKEN=your_bot_token
   BOT_USERNAME=your_bot_username
   GITHUB_TOKEN=your_github_token (optional)
   ```
4. Run the bot: `python main.py`
