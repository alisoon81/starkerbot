import logging
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
import os
import asyncio
from aiohttp import web  # برای سرور فیک

API_TOKEN = os.getenv("API_TOKEN")

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

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

# 🭳 حذف Webhook هنگام شروع
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook حذف شد. در حال اجرای polling...")

# ⚖️ سرور فیک برای Render (port binding)
async def start_fake_server():
    async def handle(request):
        return web.Response(text="Bot is running.")
    app = web.Application()
    app.router.add_get("/", handle)
    port = int(os.environ.get("PORT", 10000))
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, "0.0.0.0", port)
    await site.start()
    logging.info(f"🌐 Fake server started on port {port}")

# اجرای همزمان bot + fake server
async def main():
    await asyncio.gather(
        start_fake_server(),
        dp.start_polling(on_startup=on_startup)
    )

if __name__ == "__main__":
    asyncio.run(main())
