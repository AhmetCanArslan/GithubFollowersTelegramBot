# GitHub Followers Telegram Bot

[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)

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

<img src="https://github.com/user-attachments/assets/d8ba14c1-fab0-49f2-a231-d3e932ba79f9" width="600" alt="image">
<img src="https://github.com/user-attachments/assets/275d903f-dd8e-4938-96be-71c34aa8924f" width="600" alt="image">
<img src="https://github.com/user-attachments/assets/241d0d89-e8b5-46a0-a832-8c4a8af66e8c" width="600" alt="image">


## Setup Your Own Instance

### Prerequisites

- Python 3.7+
- A Telegram Bot Token (get it from [@BotFather](https://t.me/botfather))
- Your Telegram Bot's username
- (Optional) GitHub Personal Access Token for higher API rate limits
  - Required scopes: `user:follow` and `read:user`

### Installation

1. Clone this repository
2. Install dependencies: `pip install -r requirements.txt`
3. Set up your environment variables in `.env` file:
   ```
   TELEGRAM_TOKEN=your_bot_token
   BOT_USERNAME=your_bot_username
   GITHUB_TOKEN=your_github_token (optional)
   ```
   To create a GitHub token:
   - Go to GitHub Settings → Developer Settings → Personal Access Tokens
   - Generate a new token with `user:follow` and `read:user` scopes
   - Copy the token and add it to your `.env` file
4. Run the bot: `python main.py`
