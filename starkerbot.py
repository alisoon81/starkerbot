from aiogram import Bot, Dispatcher, executor, types

API_TOKEN = '7950008551:AAE-OOtnkR6zyQhyWAPbCueJmBhmlb9WecI'

PROXY_URL = 'socks5://127.0.0.1:1080'  # یا هر پراکسی دیگر، مثلاً: http://127.0.0.1:8889

bot = Bot(token=API_TOKEN, proxy=PROXY_URL)
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

if __name__ == '__main__':
    executor.start_polling(dp, skip_updates=True)
