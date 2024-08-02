import os
import json
from data_handler import get_user_conversation, store_user_message
import httpx
from dotenv import load_dotenv
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ContextTypes, ConversationHandler
from datetime import datetime, timedelta
import asyncio
from openai import OpenAI

load_dotenv()

OPENWEATHERMAP_API_KEY = os.getenv("OPENWEATHERMAP_API_KEY")
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
COUNTER_FILE = 'counters.json'
REMINDERS_FILE = 'reminders.json'

client = OpenAI(api_key=OPENAI_API_KEY)

user_context = {}
user_conversations = {}

def get_main_menu_keyboard():
    keyboard = [
        ["¡Quiero saber el clima!", "¡Quiero contar!", "Agregar Recordatorio", "Analizar Comentario"]
    ]
    return ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

# Cargar contadores desde el archivo JSON
def load_counters():
    if os.path.exists(COUNTER_FILE):
        with open(COUNTER_FILE, 'r') as f:
            return json.load(f)
    return {}

# Guardar contadores en el archivo JSON
def save_counters(counters):
    with open(COUNTER_FILE, 'w') as f:
        json.dump(counters, f)

# Cargar recordatorios desde el archivo JSON
def load_reminders():
    if os.path.exists(REMINDERS_FILE):
        with open(REMINDERS_FILE, 'r') as f:
            return json.load(f)
    return {}

# Guardar recordatorios en un archivo JSON
def save_reminders(reminders):
    with open(REMINDERS_FILE, 'w') as f:
        json.dump(reminders, f)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¡Hola! Soy tu bot de Telegram. Usa los botones a continuación para interactuar conmigo:",
        reply_markup=get_main_menu_keyboard()
    )

# Manejar mensajes entrantes
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    user_id = str(update.message.from_user.id)
    
    store_user_message(user_id, text)

    if "analizar comentario" in text:
        await analyze_comment(update, context)

    if user_id not in context.user_data:
        context.user_data[user_id] = []
    context.user_data[user_id].append(update.message.text)
    
    if user_id in user_context and user_context[user_id] == "clima":
        await handle_location(update, context)
        user_context.pop(user_id, None)
    elif "clima" in text:
        await update.message.reply_text(
            "Por favor, ingrese la ubicación que quiere saber el clima en el formato: Ciudad, País",
            reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
        )
        user_context[user_id] = "clima"
    elif "contar" in text:
        await handle_count(update, context)
    elif "recordatorio" in text:
        await update.message.reply_text(
            "Por favor, envíame el recordatorio en el formato: 'tarea en X minutos' o 'tarea a las HH:MM'.",
            reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
        )
        return
    elif ("en" in text or "a las" in text) and user_context.get(user_id) == "recordatorio":
        await handle_reminder(update, context)
        user_context.pop(user_id, None)

    else:
        await update.message.reply_text(
            "No entiendo tu solicitud. Por favor, usa los botones a continuación:",
            reply_markup=get_main_menu_keyboard()
        )

# Manejar la entrada de ubicación y obtener el clima
async def handle_location(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    location = update.message.text
    await update_weather(update, location)

async def cancel(update: Update, context: ContextTypes.DEFAULT_TYPE) -> int:
    await update.message.reply_text(
        "Operación cancelada. Usa los botones a continuación para interactuar conmigo:",
        reply_markup=get_main_menu_keyboard()
    )
    return ConversationHandler.END

# Obtener y enviar la información del clima para la ciudad especificada
async def update_weather(update: Update, location: str) -> None:
    url = f"http://api.openweathermap.org/data/2.5/weather?q={location}&appid={OPENWEATHERMAP_API_KEY}&units=metric&lang=es"
    async with httpx.AsyncClient() as client:
        response = await client.get(url)
        data = response.json()
    
    if data.get("cod") != 200:
        await update.message.reply_text(
            "No se pudo obtener el clima para la ubicación especificada. Asegúrate de que la ciudad y el país sean correctos.",
            reply_markup=get_main_menu_keyboard()
        )
        return

    weather_description = data["weather"][0]["description"]
    temperature = data["main"]["temp"]

    # Generar una recomendación basada en el clima
    recommendation = await generate_recommendation_local(weather_description, temperature)
    
    await update.message.reply_text(
        f"El clima en {location} es {weather_description} con una temperatura de {temperature}°C. Recomendación: {recommendation}",
        reply_markup=get_main_menu_keyboard()
    )

# Generar una recomendación breve sobre el clima
async def generate_recommendation_local(weather_description: str, temperature: float) -> str:
    weather_description = weather_description.lower()
    
    weather_description = weather_description.replace(" ", "")
    weather_description = weather_description.replace(":", "")
    
    recommendations = {
        "lluvia": "Lleva un paraguas.",
        "lluvioso": "Lleva un paraguas.",
        "soleado": "Usa protector solar.",
        "calor": "No te abrigues mucho.",
        "caluroso": "No te abrigues mucho.",
        "frío": "Abrígate bien.",
        "nieve": "Ten cuidado al caminar.",
        "nevado": "Ten cuidado al caminar.",
        "nuboso": "Podría llover, lleva abrigo.",
        "tormenta": "Permanece en un lugar seguro."
    }
    
    for condition, recommendation in recommendations.items():
        if condition in weather_description:
            return recommendation
    
    return "Ten un buen día."

async def count(update: Update, number: int) -> None:
    response = " ".join(str(i) for i in range(1, number + 1))
    await update.message.reply_text(
        response,
        reply_markup=get_main_menu_keyboard()
    )

async def handle_count(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "¿Hasta qué número te gustaría contar?",
        reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
    )

# Manejar los recordatorios
async def handle_reminder(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    text = update.message.text.lower()
    user_id = str(update.message.from_user.id)

    reminders = load_reminders()

    if user_id not in reminders:
        reminders[user_id] = []

    if "en" in text:
        parts = text.split(" en ")
        task = parts[0].strip()
        time_part = parts[1].strip()

        if "minutos" in time_part:
            minutes = int(time_part.split()[0])
            reminder_time = datetime.now() + timedelta(minutes=minutes)
        elif "horas" in time_part:
            hours = int(time_part.split()[0])
            reminder_time = datetime.now() + timedelta(hours=hours)
        else:
            await update.message.reply_text(
                "Formato de tiempo no reconocido. Usa 'en X minutos' o 'en X horas'.",
                reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
            )
            return

    elif "a las" in text:
        parts = text.split(" a las ")
        task = parts[0].strip()
        time_part = parts[1].strip()

        try:
            reminder_time = datetime.strptime(time_part, "%H:%M").replace(
                year=datetime.now().year,
                month=datetime.now().month,
                day=datetime.now().day
            )
            if reminder_time < datetime.now():
                reminder_time += timedelta(days=1)
        except ValueError:
            await update.message.reply_text(
                "Formato de hora no reconocido. Usa 'a las HH:MM'.",
                reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
            )
            return
    else:
        await update.message.reply_text(
            "Formato no reconocido. Usa 'tarea en X minutos' o 'tarea a las HH:MM'.",
            reply_markup=ReplyKeyboardMarkup([["Cancelar"]], resize_keyboard=True)
        )
        return

    reminders[user_id].append({"task": task, "time": reminder_time.isoformat()})
    save_reminders(reminders)

    await update.message.reply_text(
        f"Recordatorio para '{task}' establecido para {reminder_time.strftime('%H:%M')}.",
        reply_markup=get_main_menu_keyboard()
    )



async def analyze_comment(update, context):
    user_id = update.effective_user.id
    conversation = get_user_conversation(user_id)
    
    if not conversation:
        await update.message.reply_text("No se encontraron mensajes para analizar.")
        return

    messages = [{"role": "user", "content": msg} for msg in conversation]
    
    try:
        response = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=messages
        )
        
        print(f"API Response: {response}")

        result = response.choices[0].message["content"]  

        await update.message.reply_text(f"Análisis del comentario:\n{result}")
    
    except Exception as e:
        await update.message.reply_text(f"Hubo un error al analizar el comentario: {str(e)}")