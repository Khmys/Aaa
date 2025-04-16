import os
import asyncio
import sqlite3
from telegram import Bot, Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from telegram.constants import ParseMode
from telegram.error import TelegramError
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route
import uvicorn

# Telegram & Server Info
URL = "https://superior-vinnie-huduma-2f8eb14f.koyeb.app"

PORT = int(os.environ.get("PORT", 10000))
TOKEN = "5861324474:AAH7zCxyQAiroqp74qTgipHlAikpqI0jDMQ"

# SQLite Database Connection
conn = sqlite3.connect("db.sqlite3", check_same_thread=False)
cursor = conn.cursor()

# Database Table Check
cursor.execute("""
    CREATE TABLE IF NOT EXISTS users (
        chat_id INTEGER PRIMARY KEY,
        blocked BOOLEAN DEFAULT FALSE
    );
""")
conn.commit()

# Save chat ID
def save_chat_id(chat_id: int):
    cursor.execute("""
        INSERT OR IGNORE INTO users (chat_id) VALUES (?);
    """, (chat_id,))
    conn.commit()

# Remove chat ID (if needed)
def remove_chat_id(chat_id: int):
    cursor.execute("DELETE FROM users WHERE chat_id = ?;", (chat_id,))
    conn.commit()

# Get all chat IDs
def get_all_chat_ids():
    cursor.execute("SELECT chat_id FROM users WHERE blocked = 0;")
    return [row[0] for row in cursor.fetchall()]

# Handle commands
async def amuli(update: Update, context: ContextTypes.DEFAULT_TYPE):
    msg = update.message
    if not msg:
        return

    try:
        user = update.effective_user
        chat_id = update.effective_chat.id
        command = msg.text.split()[0]

        if command == "/start":
            save_chat_id(chat_id)
            await update.message.reply_text(
                f"Karibu, {user.first_name}! Tuma post 📤 pia Utapokea 📥 post kutoka kwa watumiaji mbali mbali wa bot hii")

        elif command == "/off":
            cursor.execute("UPDATE users SET blocked = 1 WHERE chat_id = ?;", (chat_id,))
            conn.commit()
            await update.message.reply_text("⛔ Umejitoa kupokea matangazo. Unaweza kurudi kwa kutumia /start")

        elif command == "/on":
            cursor.execute("UPDATE users SET blocked = 0 WHERE chat_id = ?;", (chat_id,))
            conn.commit()
            await update.message.reply_text("✅ Umerudi kupokea matangazo. Karibu tena!")

        elif command == "takwimu":
            cursor.execute("SELECT COUNT(*) FROM users;")
            jumla = cursor.fetchone()[0]
            cursor.execute("SELECT COUNT(*) FROM users WHERE blocked = 1;")
            walioblock = cursor.fetchone()[0]
            active = jumla - walioblock

            msg = (
                f"**Takwimu za Watumiaji**\n\n"
                f"👥 Jumla ya waliojiunga: {jumla}\n"
                f"✅ Walio hai (hawajablock): {active}\n"
                f"🚫 Walioblock bot: {walioblock}"
            )
            await update.message.reply_text(msg, parse_mode="Markdown")

    except Exception as e:
        error_msg = f"Kuna hitilafu kwenye function ya Start: {str(e)}"
        await context.bot.send_message(chat_id=-1002158955567, text=error_msg)

# Handle message forwarding
async def forward(update: Update, context: ContextTypes.DEFAULT_TYPE):
    try:
        message = update.effective_message
        chat_type = update.effective_chat.type

        if chat_type != "private":
            return

        users = get_all_chat_ids()
        if not users:
            return

        full_name = update.effective_user.full_name if update.effective_user else "Mtu asiyejulikana"
        caption = message.caption or ""
        ujumbe = message.text or ""

        formatted_caption = f"<pre><code>{full_name}</code></pre>\n\n{caption}" if caption else f"<code>{full_name}</code>"
        formatted_message = f"<pre><code>{full_name}</code></pre>\n\n{ujumbe}" if ujumbe else None

        media_mapping = {
            "photo": context.bot.send_photo,
            "video": context.bot.send_video,
            "audio": context.bot.send_audio,
            "document": context.bot.send_document,
            "voice": context.bot.send_voice,
        }

        confirmation_message = await message.reply_text("✅ Ujumbe umetumwa!")
        tasks = []

        for user in users:
            if not user:
                continue

            sent = False
            for media_type, send_func in media_mapping.items():
                media = getattr(message, media_type, None)
                if media:
                    file_id = media[-1].file_id if media_type == "photo" else media.file_id
                    kwargs = {
                        "chat_id": user,
                        media_type: file_id,
                        "caption": formatted_caption,
                        "parse_mode": "HTML"
                    }
                    tasks.append(send_func(**kwargs))
                    sent = True
                    break

            if not sent and message.text:
                tasks.append(context.bot.send_message(
                    chat_id=user,
                    text=formatted_message,
                    parse_mode="HTML"
                ))

        await asyncio.gather(*tasks)
        await confirmation_message.delete()

    except Exception as e:
        await context.bot.send_message(
            chat_id=-1001334156926,
            text=f"Imeshindikana kutuma ujumbe: {e}"
        )

# Main Function
async def main() -> None:
    app = Application.builder().token(TOKEN).build()

    async def telegram(request: Request) -> Response:
        update = Update.de_json(data=await request.json(), bot=app.bot)
        await app.update_queue.put(update)
        return Response()

    starlette_app = Starlette(routes=[Route("/telegram", telegram, methods=["POST"])])

    app.add_handler(CommandHandler(["start", "off", "on", "takwimu"], amuli))
    app.add_handler(MessageHandler(filters.ALL, forward))

    async with app:
        await app.bot.set_webhook(url=f"{URL}/telegram")
        server = uvicorn.Server(config=uvicorn.Config(app=starlette_app, port=PORT, host="0.0.0.0"))
        await app.start()
        await server.serve()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
