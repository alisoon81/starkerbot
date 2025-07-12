import logging
import asyncio
import os

from aiogram import Bot, Dispatcher, types
from aiogram.types import Update
from flask import Flask, request, Response

API_TOKEN = '7950008551:AAE-OOtnkR6zyQhyWAPbCueJmBhmlb9WecI'

# حذف پراکسی چون در Render استفاده نمی‌کنیم
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)

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

app = Flask(__name__)
logging.basicConfig(level=logging.INFO)

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

WEBHOOK_HOST = os.getenv('WEBHOOK_HOST', 'https://yourdomain.com')  # آدرس دامنه‌ات را اینجا بگذار
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = WEBHOOK_HOST + WEBHOOK_PATH

@app.route(WEBHOOK_PATH, methods=['POST'])
def webhook_handler():
    update = Update.to_object(request.json)
    asyncio.create_task(dp.process_update(update))
    return Response(status=200)

async def on_startup():
    logging.info("Setting webhook")
    await bot.set_webhook(WEBHOOK_URL)

async def on_shutdown():
    logging.info("Removing webhook")
    await bot.delete_webhook()

if __name__ == '__main__':
    port = int(os.getenv('PORT', 5000))
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.run(host='0.0.0.0', port=port)
