import os
import logging
import asyncio
from flask import Flask, request, Response
from aiogram import Bot, Dispatcher, types
from aiogram.types import Update

API_TOKEN = '7950008551:AAE-OOtnkR6zyQhyWAPbCueJmBhmlb9WecI'

# تنظیمات Flask و Aiogram
app = Flask(__name__)
bot = Bot(token=API_TOKEN)
dp = Dispatcher(bot)
logging.basicConfig(level=logging.INFO)

# لیست زبان‌ها
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

# هندلر شروع
@dp.message_handler(commands=['start'])
async def send_welcome(message: types.Message):
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    buttons = [types.InlineKeyboardButton(text=lang, callback_data=f"lang_{code}") for code, lang in LANGUAGES.items()]
    keyboard.add(*buttons)
    await message.answer("Please select your language / لطفا زبان خود را انتخاب کنید / 请选择您的语言:", reply_markup=keyboard)

# هندلر انتخاب زبان
@dp.callback_query_handler(lambda c: c.data.startswith('lang_'))
async def process_language(callback_query: types.CallbackQuery):
    lang_code = callback_query.data[5:]
    user_id = callback_query.from_user.id
    user_languages[user_id] = lang_code
    await bot.answer_callback_query(callback_query.id)
    await bot.send_message(user_id, WELCOME_MESSAGES.get(lang_code, "Welcome!"))

# مسیری که تلگرام بهش پیام POST می‌کنه
@app.route(f"/webhook/{API_TOKEN}", methods=["POST"])
def webhook():
    update = Update.to_object(request.json)
    asyncio.create_task(dp.process_update(update))
    return Response()

# راه‌اندازی اولیه
async def on_startup():
    webhook_url = f"https://{os.environ['RENDER_EXTERNAL_HOSTNAME']}/webhook/{API_TOKEN}"
    await bot.set_webhook(webhook_url)

if __name__ == "__main__":
    # ست کردن webhook و راه‌اندازی Flask
    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 5000)))
