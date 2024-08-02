import os
import asyncio
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from dotenv import load_dotenv
from handlers import start, handle_message, handle_location, cancel, handle_count
from reminders_handlers import handle_reminder, reschedule_reminders

async def on_startup(application: Application) -> None:
    await reschedule_reminders(application.context)

def main() -> None:
    load_dotenv()

    bot_token = os.getenv("TELEGRAM_TOKEN")

    if not bot_token:
        raise ValueError("No se ha encontrado el TELEGRAM_TOKEN en el archivo .env")
    application = Application.builder().token(bot_token).build()


    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    application.add_handler(MessageHandler(filters.Regex("(?i)¡Quiero saber el clima!"), handle_location))
    application.add_handler(MessageHandler(filters.Regex("(?i)¡Quiero contar!"), handle_count))
    application.add_handler(MessageHandler(filters.Regex("(?i)Agregar Recordatorio"), handle_reminder))
    application.add_handler(MessageHandler(filters.Regex("(?i)Cancelar"), cancel))

    application.run_polling()

if __name__ == "__main__":
    asyncio.run(main())