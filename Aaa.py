from telegram import Update
from telegram.ext import (
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    Application,
)
from typing import Dict
import asyncio

MAIN_BOT_TOKEN = "1220116092:AAGNF7PAqv5Q0YO0p_uF3aJwAUi6DFI74Fk"

user_bots: Dict[str, Application] = {}

async def anza(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Karibu! Tunafanya majalibio ya Clone.")

async def clone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("Tuma token ya bot: /clone <BOT_TOKEN>")
        return

    token = context.args[0]
    if token in user_bots:
        await update.message.reply_text("Bot hiyo tayari inaendeshwa.")
        return

    try:
        app = await start_user_bot(token)
        user_bots[token] = app
        await update.message.reply_text("Bot mpya imeanzishwa kwa mafanikio!")
    except Exception as e:
        await update.message.reply_text(f"Hitilafu: {e}")

async def start_user_bot(token: str) -> Application:
    app = ApplicationBuilder().token(token).build()

    async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
        await update.message.reply_text("Salamu kutoka kwa bot iliyozaliwa kwa clone.")

    app.add_handler(CommandHandler("start", start))

    # Endesha bot mpya kwa polling sambamba bila kukwama loop kuu
    loop = asyncio.get_running_loop()
    loop.create_task(app.run_polling())
    return app

def main():
    app = ApplicationBuilder().token(MAIN_BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", anza))
    app.add_handler(CommandHandler("clone", clone))

    print("Main bot is running...")
    app.run_polling()  # synchronous version ya run_polling()

if __name__ == "__main__":
    main()
