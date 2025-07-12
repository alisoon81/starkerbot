import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.types import ParseMode
from quart import Quart, request
import asyncio

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")

if not API_TOKEN or not WEBHOOK_HOST:
    raise RuntimeError("API_TOKEN and WEBHOOK_HOST environment variables must be set")

WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)
app = Quart(__name__)

LANGUAGES = {
    "en": "English 🇺🇸",
    "zh": "中文 🇨🇳",
    "ru": "Русский 🇷🇺"
}

MESSAGES = {
    "choose_language": {
        "en": "Please select your language:",
        "zh": "请选择您的语言：",
        "ru": "Пожалуйста, выберите язык:"
    },
    "welcome": {
        "en": "Welcome! You chose English 🇺🇸",
        "zh": "欢迎！你选择了中文 🇨🇳",
        "ru": "Добро пожаловать! Вы выбрали русский 🇷🇺"
    }
}

user_data = {}

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"lang": None}
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for code, name in LANGUAGES.items():
        keyboard.insert(types.InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    await message.answer(MESSAGES["choose_language"]["en"], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def process_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = callback_query.data[5:]
    user_data[user_id]["lang"] = lang_code
    await bot.send_message(user_id, MESSAGES["welcome"][lang_code])
    await callback_query.answer()  # برای بستن اسپینر تلگرام

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    request_body_dict = await request.get_json()
    update = types.Update.to_object(request_body_dict)
    await dp.process_update(update)
    return "ok"

@app.before_serving
async def on_startup():
    logging.info(f"Setting webhook: {WEBHOOK_URL}")
    await bot.set_webhook(WEBHOOK_URL)

@app.after_serving
async def on_shutdown():
    logging.info("Deleting webhook")
    await bot.delete_webhook()
    await dp.storage.close()
    await dp.storage.wait_closed()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
