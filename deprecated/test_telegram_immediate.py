import asyncio
from telegram import Bot

async def main():
    try:
        bot = Bot(token="7860539648:AAFqr7eDxUQoCTtlUuISSZrdrF0gOxmA000")
        await bot.send_message(
            chat_id="6989072955",
            text="🔔 *Test Message* 🔔\nThis is a test from your heart rate monitor.",
            parse_mode='Markdown'
        )
        print("✅ Test message sent successfully!")
    except Exception as e:
        print(f"❌ Error: {e}")
    finally:
        if 'bot' in locals():
            await bot.close()

if __name__ == "__main__":
    asyncio.run(main())
    input("\nPress Enter to exit...")
