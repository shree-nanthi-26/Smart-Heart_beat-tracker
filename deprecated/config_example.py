# Google Fit API Configuration
SCOPES = ["https://www.googleapis.com/auth/fitness.heart_rate.read"]
CLIENT_SECRET_FILE = "client_secret.json"  # Download from Google Cloud Console
TOKEN_FILE = "token.json"  # Will be generated on first run

# Telegram Configuration (Optional)
TELEGRAM_BOT_TOKEN = "your_telegram_bot_token"  # Get from @BotFather
TELEGRAM_CHAT_ID = "your_telegram_chat_id"  # Get from @userinfobot

# Heart Rate Settings
HEART_RATE_THRESHOLD = 90  # BPM - Adjust as needed
CHECK_INTERVAL = 300  # 5 minutes between checks

# Logging Configuration
LOG_FILE = "heart_monitor.log"
LOG_LEVEL = "INFO"  # DEBUG, INFO, WARNING, ERROR, CRITICAL
