from pyrogram import Client, filters
from pyrogram.types import Message

# Ingiza token yako ya bot
API_ID = 979271       #  https://my.telegram.org
API_HASH = "ba5c79822456d986a855b1bb1e4aafaf"
BOT_TOKEN = "848672959:AAGmoUTO0xGhybDm8hMVk3TkSlJ7UHbTMdI"  # Badilisha na token ya bot yako

# Tengeneza instance ya bot
app = Client("my_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

# Function ya /start
@app.on_message(filters.command("start") & filters.private)
async def start(client: Client, message: Message):
    await message.reply_text("Karibu kwenye echo bot! Tuma ujumbe wowote nikuurudishie.")

# Function ya echo – inashika meseji zote ambazo si command
@app.on_message(filters.text & filters.private & ~filters.command(["start"]))
async def messageHandle(client: Client, message: Message):
    await message.reply_text(f"Umesema: {message.text}")

# Endesha bot
app.run()
