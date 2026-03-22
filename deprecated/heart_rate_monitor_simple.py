import asyncio
import time
from telegram import Bot
from datetime import datetime
import random

# Telegram configuration
TELEGRAM_BOT_TOKEN = "7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000"
TELEGRAM_CHAT_ID = "6989072955"

# Initialize Telegram bot
telegram_bot = Bot(token=TELEGRAM_BOT_TOKEN)

async def send_telegram_alert(bpm):
    """Send a Telegram alert for high heart rate"""
    try:
        current_time = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        message = (
            f"🚨 *High Heart Rate Alert!* 🚨\n\n"
            f"• *Heart Rate:* `{bpm} BPM`\n"
            f"• *Time:* `{current_time}`\n"
            f"• *Status:* `Above 85 BPM`\n\n"
            "_Please check your vitals and consider taking a break._"
        )
        
        await telegram_bot.send_message(
            chat_id=TELEGRAM_CHAT_ID,
            text=message,
            parse_mode='Markdown'
        )
        print(f"✅ Alert sent for {bpm} BPM at {current_time}")
        return True
    except Exception as e:
        print(f"❌ Error sending Telegram alert: {e}")
        return False

async def simulate_heart_rate():
    """Simulate heart rate monitoring"""
    print("Starting heart rate monitoring...")
    print("Press Ctrl+C to stop")
    
    try:
        while True:
            # Simulate heart rate between 70-100 BPM with more frequent high readings
            current_bpm = random.choice(
                list(range(70, 86)) +  # 70-85 BPM (normal)
                list(range(85, 101)) * 2  # 85-100 BPM (high) - twice as likely
            )
            current_time = datetime.now().strftime("%H:%M:%S")
            
            print(f"\n[{current_time}] Current heart rate: {current_bpm} BPM", end="")
            
            if current_bpm > 85:
                print(" (High! Sending alert...)", end="")
                await send_telegram_alert(current_bpm)
            else:
                print(" (Normal)", end="")
            
            # Wait for 1 second before next reading for faster alerts
            await asyncio.sleep(1)
            
    except KeyboardInterrupt:
        print("\n\nStopping heart rate monitor...")
    except Exception as e:
        print(f"\nAn error occurred: {e}")

if __name__ == "__main__":
    try:
        asyncio.run(simulate_heart_rate())
    except KeyboardInterrupt:
        print("\nHeart rate monitor stopped by user.")
    except Exception as e:
        print(f"\nAn error occurred: {e}")
    finally:
        print("Thank you for using Heart Rate Monitor!")
