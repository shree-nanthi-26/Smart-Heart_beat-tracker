# Telegram Bot Setup for SmartHeartBeat

This guide will help you set up the Telegram bot for receiving heart rate alerts.

## Prerequisites
1. Python 3.7 or higher
2. `python-telegram-bot` package (already added to requirements.txt)
3. A Telegram account

## Setup Instructions

### 1. Create a Telegram Bot
1. Open Telegram and search for `@BotFather`
2. Start a chat with BotFather and send `/newbot`
3. Follow the instructions to create a new bot
4. Save the API token provided by BotFather

### 2. Get Your Chat ID
1. Search for `@userinfobot` on Telegram
2. Start a chat with the bot
3. It will reply with your chat ID

### 3. Configure the Bot
1. Open `telegram_bot.py`
2. Replace `YOUR_TELEGRAM_BOT_TOKEN` with your bot token
3. Replace `YOUR_CHAT_ID` with your chat ID

### 4. Test the Bot
Run the example script to test the bot:
```bash
python telegram_bot.py
```

### 5. Integrate with SmartHeartBeat
1. Import the `TelegramBot` class in your main script:
   ```python
   from telegram_bot import TelegramBot
   ```

2. Initialize the bot at the start of your script:
   ```python
   # Initialize Telegram bot
telegram_bot = TelegramBot(
    token="YOUR_TELEGRAM_BOT_TOKEN",
    chat_id="YOUR_CHAT_ID"
)
   ```

3. Send alerts when high heart rate is detected:
   ```python
   # Inside your main loop where you detect high heart rate
   if heart_rate > 90:  # Your threshold
       await telegram_bot.send_alert(
           heart_rate=heart_rate,
           timestamp=datetime_str
       )
   ```

## Troubleshooting
- Make sure your bot has been started with BotFather
- Verify your chat ID is correct
- Check that your bot has been added to the chat where you want to receive messages
- Ensure your internet connection is stable

## Security Notes
- Never commit your bot token or chat ID to version control
- Consider using environment variables for sensitive information
- Keep your bot token private to prevent unauthorized access
