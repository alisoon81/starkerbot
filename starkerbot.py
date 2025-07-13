import logging
import os
import threading
from aiogram import Bot, Dispatcher, types, executor
from aiogram.contrib.fsm_storage.memory import MemoryStorage
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup

# -- fake_server.py باید یه سرور فیک راه بندازه برای نگه داشتن پورت روی Render
# اگر نداریش حذفش کن یا یه فانکشن خالی بذار --

from fake_server import start_fake_server

# اجرای سرور فیک در بک‌گراند (برای Render)
threading.Thread(target=start_fake_server).start()

API_TOKEN = os.getenv("API_TOKEN")  # تو محیطت تنظیم کن
logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN)
storage = MemoryStorage()
dp = Dispatcher(bot, storage=storage)

# زبان‌ها و پیام‌ها
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
    },
    "deposit_ask": {
        "en": "Enter how many Stars you want to deposit:",
        "zh": "请输入您想充值的星星数量：",
        "ru": "Введите, сколько Звезд вы хотите внести:"
    },
    "market_price_ask": {
        "en": "Enter price range to buy (e.g. 100-50000):",
        "zh": "输入购买价格范围（例如100-50000）：",
        "ru": "Введите ценовой диапазон для покупки (например, 100-50000):"
    },
    "market_quantity_ask": {
        "en": "Enter how many items you want to buy:",
        "zh": "输入您想购买的数量：",
        "ru": "Введите, сколько товаров вы хотите купить:"
    },
    "withdraw_ask": {
        "en": "Enter how many Stars you want to withdraw:",
        "zh": "请输入您想提现的星星数量：",
        "ru": "Введите, сколько Звезд вы хотите вывести:"
    },
    "invalid_number": {
        "en": "Please enter a valid positive integer.",
        "zh": "请输入有效的正整数。",
        "ru": "Пожалуйста, введите корректное положительное число."
    },
    "deposit_success": {
        "en": "You deposited {amount} Stars successfully.",
        "zh": "您已成功充值 {amount} 星星。",
        "ru": "Вы успешно внесли {amount} Звезд."
    },
    "withdraw_registered": {
        "en": "Withdraw request of {amount} Stars has been registered. We will process it manually.",
        "zh": "提现请求已登记 {amount} 星星。我们将手动处理。",
        "ru": "Запрос на вывод {amount} Звезд зарегистрирован. Мы обработаем его вручную."
    },
    "invalid_withdraw": {
        "en": "Invalid amount. Check your available Stars.",
        "zh": "无效金额。请检查您的可用星星。",
        "ru": "Недопустимая сумма. Проверьте доступные Звезды."
    },
    "market_order_received": {
        "en": "Market order received: Buy {quantity} items in price range {price_range}.\n(Note: Purchase is manual and simulated.)",
        "zh": "市场订单已接收：在价格范围 {price_range} 购买 {quantity} 件商品。\n（注意：购买为手动模拟。）",
        "ru": "Заказ на маркет получен: Купить {quantity} товаров в ценовом диапазоне {price_range}.\n(Покупка выполняется вручную и симулируется.)"
    },
    "back_to_menu": {
        "en": "Back to main menu:",
        "zh": "返回主菜单：",
        "ru": "Назад в главное меню:"
    }
}

user_data = {}

# حالت‌ها برای FSM
class Form(StatesGroup):
    deposit_amount = State()
    market_price_range = State()
    market_quantity = State()
    withdraw_amount = State()

def main_menu_kb(lang):
    texts = {
        "deposit": {"en": "Deposit", "zh": "充值", "ru": "Внести"},
        "market": {"en": "Market", "zh": "市场", "ru": "Маркет"},
        "withdraw": {"en": "Withdraw", "zh": "提现", "ru": "Вывести"},
        "profile": {"en": "Profile", "zh": "个人资料", "ru": "Профиль"},
    }
    kb = types.InlineKeyboardMarkup(row_width=2)
    kb.add(
        types.InlineKeyboardButton(text=texts["deposit"][lang], callback_data="tab_deposit"),
        types.InlineKeyboardButton(text=texts["market"][lang], callback_data="tab_market"),
        types.InlineKeyboardButton(text=texts["withdraw"][lang], callback_data="tab_withdraw"),
        types.InlineKeyboardButton(text=texts["profile"][lang], callback_data="tab_profile"),
    )
    return kb

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    user_data[user_id] = {"lang": None, "stars": 0, "deposited": 0, "subordinates": 0, "sub_deposited": 0}
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for code, name in LANGUAGES.items():
        keyboard.insert(types.InlineKeyboardButton(text=name, callback_data=f"lang_{code}"))
    await message.answer(MESSAGES["choose_language"]["en"], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def process_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = callback_query.data[5:]
    user_data[user_id]["lang"] = lang_code

    # لینک اختصاصی ساده با user_id به عنوان کد ارجاع
    referral_link = f"https://t.me/YourBot?start={user_id}"

    await bot.send_message(user_id, MESSAGES["welcome"][lang_code])
    await bot.send_message(user_id, f"Your referral link:\n{referral_link}", reply_markup=main_menu_kb(lang_code))

@dp.callback_query_handler(lambda c: c.data.startswith("tab_"))
async def tab_handler(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang = user_data[user_id]["lang"]
    data = callback_query.data

    if data == "tab_deposit":
        await bot.send_message(user_id, MESSAGES["deposit_ask"][lang])
        await Form.deposit_amount.set()

    elif data == "tab_market":
        await bot.send_message(user_id, MESSAGES["market_price_ask"][lang])
        await Form.market_price_range.set()

    elif data == "tab_withdraw":
        await bot.send_message(user_id, MESSAGES["withdraw_ask"][lang])
        await Form.withdraw_amount.set()

    elif data == "tab_profile":
        stars = user_data[user_id]["stars"]
        deposited = user_data[user_id]["deposited"]
        sub_count = user_data[user_id]["subordinates"]
        sub_deposited = user_data[user_id]["sub_deposited"]
        bonus = int(sub_deposited * 0.02)
        profile_text = (
            f"Profile:\n"
            f"Stars deposited: {deposited}\n"
            f"Current Stars: {stars}\n"
            f"Referrals joined: {sub_count}\n"
            f"Stars deposited by referrals: {sub_deposited}\n"
            f"Your 2% referral bonus (not withdrawable): {bonus}"
        )
        await bot.send_message(user_id, profile_text)

@dp.message_handler(state=Form.deposit_amount)
async def deposit_stars(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = user_data[user_id]["lang"]
    try:
        amount = int(message.text)
        if amount <= 0:
            raise ValueError
        user_data[user_id]["stars"] += amount
        user_data[user_id]["deposited"] += amount
        await message.answer(MESSAGES["deposit_success"][lang].format(amount=amount))
    except ValueError:
        await message.answer(MESSAGES["invalid_number"][lang])
    await state.finish()
    await message.answer(MESSAGES["back_to_menu"][lang], reply_markup=main_menu_kb(lang))

@dp.message_handler(state=Form.market_price_range)
async def market_price_range(message: types.Message, state: FSMContext):
    await state.update_data(price_range=message.text)
    lang = user_data[message.from_user.id]["lang"]
    await message.answer(MESSAGES["market_quantity_ask"][lang])
    await Form.next()

@dp.message_handler(state=Form.market_quantity)
async def market_quantity(message: types.Message, state: FSMContext):
    data = await state.get_data()
    price_range = data.get("price_range")
    quantity = message.text
    lang = user_data[message.from_user.id]["lang"]
    await message.answer(MESSAGES["market_order_received"][lang].format(quantity=quantity, price_range=price_range))
    await state.finish()
    await message.answer(MESSAGES["back_to_menu"][lang], reply_markup=main_menu_kb(lang))

@dp.message_handler(state=Form.withdraw_amount)
async def withdraw_stars(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    lang = user_data[user_id]["lang"]
    try:
        amount = int(message.text)
        if amount <= 0 or amount > user_data[user_id]["stars"]:
            await message.answer(MESSAGES["invalid_withdraw"][lang])
        else:
            # شبیه‌سازی ثبت درخواست برداشت
            await message.answer(MESSAGES["withdraw_registered"][lang].format(amount=amount))
    except ValueError:
        await message.answer(MESSAGES["invalid_number"][lang])
    await state.finish()
    await message.answer(MESSAGES["back_to_menu"][lang], reply_markup=main_menu_kb(lang))


# حذف Webhook موقع شروع ربات
async def on_startup(dp):
    await bot.delete_webhook(drop_pending_updates=True)
    logging.info("✅ Webhook حذف شد. در حال اجرای polling...")

if __name__ == "__main__":
    executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
