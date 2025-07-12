import os
import logging
from quart import Quart, request, Response
import asyncio
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

API_TOKEN = os.getenv("API_TOKEN")  # توکن ربات از متغیر محیطی خونده میشه
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"https://{os.getenv('RENDER_EXTERNAL_HOSTNAME')}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
app = Quart(__name__)

user_languages = {}

LANGUAGES = {
    "en": "English 🇺🇸",
    "zh": "中文 🇨🇳",
    "ru": "Русский 🇷🇺"
}

WELCOME_MESSAGES = {
    "en": "Welcome! You chose English 🇺🇸",
    "zh": "欢迎！你选择了中文 🇨🇳",
    "ru": "Добро пожаловать! Вы выбрали русский 🇷🇺"
}

@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=lang, callback_data=f"lang_{code}") for code, lang in LANGUAGES.items()]
    keyboard.add(*buttons)
    await message.answer("Please select your language / لطفا زبان خود را انتخاب کنید / 请选择您的语言:", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery):
    lang_code = callback_query.data[5:]
    user_id = callback_query.from_user.id
    user_languages[user_id] = lang_code
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, WELCOME_MESSAGES.get(lang_code, "Welcome!"))

@app.route(WEBHOOK_PATH, methods=['POST'])
async def webhook_handler():
    data = await request.get_json()
    update = Update.to_object(data)
    await dp.process_update(update)
    return Response(status=200)

async def on_startup():
    await bot.delete_webhook()
    await bot.set_webhook(WEBHOOK_URL)
    logging.info(f"Webhook set to {WEBHOOK_URL}")

if __name__ == '__main__':
    asyncio.run(on_startup())
    app.run(host='0.0.0.0', port=int(os.environ.get('PORT', 5000)))
