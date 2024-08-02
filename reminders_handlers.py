import json
import os
from datetime import datetime, timedelta
import asyncio
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes
from dotenv import load_dotenv

load_dotenv()

REMINDERS_FILE = 'reminders.json'
reminders = {}

def get_main_menu_keyboard():
    keyboard = [
        ["Agregar Recordatorio"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {}

def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f, indent=4)

async def handle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = str(update.message.from_user.id)
    reminder_text = update.message.text

    try:
        if "en" in reminder_text:
            task, minutes = reminder_text.split("en")
            minutes = int(minutes.split()[0])
            reminder_time = datetime.now() + timedelta(minutes=minutes)
        elif "a las" in reminder_text:
            task, time_str = reminder_text.split("a las")
            reminder_time = datetime.strptime(time_str.strip(), "%H:%M")
            reminder_time = reminder_time.replace(year=datetime.now().year, month=datetime.now().month, day=datetime.now().day)
            if reminder_time < datetime.now():
                reminder_time += timedelta(days=1)
        else:
            raise ValueError("Formato no válido")

        if user_id not in reminders:
            reminders[user_id] = []

        reminders[user_id].append({
            "task": task.strip(),
            "time": reminder_time.isoformat()
        })
        save_reminders(reminders)

        await update.message.reply_text(
            f"Recordatorio establecido: '{task.strip()}' a las {reminder_time.strftime('%H:%M')}.",
            reply_markup=get_main_menu_keyboard()
        )

        context.bot.loop.create_task(schedule_reminder(context, user_id, task.strip(), reminder_time))

    except Exception as e:
        print(f"Error: {e}")  
        await update.message.reply_text(
            f"Formato de recordatorio no válido. Usa el formato 'tarea en X minutos' o 'tarea a las HH:MM'.",
            reply_markup=get_main_menu_keyboard()
        )

async def schedule_reminder(context: ContextTypes.DEFAULT_TYPE, user_id: str, task: str, reminder_time: datetime):
    delay = (reminder_time - datetime.now()).total_seconds()
    await asyncio.sleep(delay)

    await context.bot.send_message(
        chat_id=user_id,
        text=f"Recordatorio: {task}"
    )

async def reschedule_reminders(context: ContextTypes.DEFAULT_TYPE):
    for user_id, user_reminders in reminders.items():
        for reminder in user_reminders:
            task = reminder["task"]
            reminder_time = datetime.fromisoformat(reminder["time"])
            if reminder_time > datetime.now():
                context.bot.loop.create_task(schedule_reminder(context, user_id, task, reminder_time))

reminders = load_reminders()
