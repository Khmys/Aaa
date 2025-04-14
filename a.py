import os
import asyncio
import uvicorn
from telegram import Update
from telegram.ext import (
    ApplicationBuilder, CommandHandler, MessageHandler, ContextTypes, filters
)
from starlette.applications import Starlette
from starlette.requests import Request
from starlette.responses import Response
from starlette.routing import Route

# Define configuration constants
URL = "https://translate-3oi0.onrender.com"
PORT = int(os.environ.get("PORT", 10000))

# Function ya /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("Karibu! Tuma ujumbe wowote nitaukirudisha (echo).")

# Function ya echo - kurudisha ujumbe ule ule
async def echo(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(update.message.text)

# Main function
async def main():
    app = ApplicationBuilder().token("848672959:AAGmoUTO0xGhybDm8hMVk3TkSlJ7UHbTMdI").build()

    # Telegram webhook endpoint
    async def telegram(request: Request) -> Response:
        await app.update_queue.put(
            Update.de_json(data=await request.json(), bot=app.bot)
        )
        return Response()

    # Starlette app
    starlette_app = Starlette(
        routes=[
            Route("/telegram", telegram, methods=["POST"]),
        ]
    )

    # Ongeza handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, echo))

    # Set webhook
    await app.bot.set_webhook(url=f"{URL}/telegram")

    async with app:
        await app.start()
        config = uvicorn.Config(app=starlette_app, host="0.0.0.0", port=PORT, log_level="info")
        server = uvicorn.Server(config)
        await server.serve()
        await app.stop()

if __name__ == "__main__":
    asyncio.run(main())
