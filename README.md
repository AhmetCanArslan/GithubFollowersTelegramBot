# GitHub Followers Telegram Bot

A Telegram bot that helps you discover who doesn't follow you back on GitHub.

## Features

- Shows users who don't follow you back on GitHub
- Simple to use - just send your GitHub username
- Sanitizes inputs for security
- Detailed logging of bot usage
- Rate limiting protection

## Usage

1. Start a chat with the bot: [@github_follower_bot](https://t.me/github_follower_bot)
2. Send your GitHub username
3. The bot will analyze your followers and following lists
4. You'll receive a list of users who don't follow you back

## Setup Your Own Instance

### Prerequisites

- Python 3.7+
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- Your Telegram Bot's username

### Installation

1. Clone this repository:
2. Install dependencies (python-telegram-bot, requests, python-dotenv): pip install -r requirements.txt
3. Set up your environment variables: .env file -> TELEGRAM_BOT_TOKEN=your_bot_token, TELEGRAM_BOT_USERNAME=your_bot_username
4. Run the bot: python main.py
