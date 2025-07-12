import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from aiohttp import web

API_TOKEN = os.getenv("API_TOKEN")
WEBHOOK_HOST = os.getenv("WEBHOOK_HOST")  # مثل https://mybot.onrender.com
WEBHOOK_PATH = f"/webhook/{API_TOKEN}"
WEBHOOK_URL = f"{WEBHOOK_HOST}{WEBHOOK_PATH}"

logging.basicConfig(level=logging.INFO)

bot = Bot(token=API_TOKEN, parse_mode=ParseMode.HTML)
dp = Dispatcher(bot)

# دیتاست‌ها (در حافظه)
user_data = {}  # user_id: {lang, balance, deposits, referrals, referral_deposits}
referrals = {}  # user_id: set of referred user_ids

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
    "main_menu": {
        "en": "Choose an option:",
        "zh": "选择一个选项：",
        "ru": "Выберите опцию:"
    },
    "deposit_prompt": {
        "en": "Enter amount of Stars to deposit:",
        "zh": "输入充值的星星数量：",
        "ru": "Введите количество Звезд для пополнения:"
    },
    "market_prompt_price": {
        "en": "Enter price range to buy (min max):",
        "zh": "输入购买价格范围（最小 最大）：",
        "ru": "Введите ценовой диапазон для покупки (мин макс):"
    },
    "market_prompt_quantity": {
        "en": "Enter quantity to buy:",
        "zh": "输入购买数量：",
        "ru": "Введите количество для покупки:"
    },
    "withdraw_prompt": {
        "en": "Enter amount of Stars to withdraw:",
        "zh": "输入要提取的星星数量：",
        "ru": "Введите количество Звезд для вывода:"
    },
    "deposit_success": {
        "en": "You deposited {amount} Stars. Your balance is now {balance}.",
        "zh": "您充值了 {amount} 星星。您的余额现在是 {balance}。",
        "ru": "Вы пополнили {amount} Звезд. Ваш баланс теперь {balance}."
    },
    "withdraw_success": {
        "en": "Withdrawal request for {amount} Stars registered.",
        "zh": "提现请求已注册，数量：{amount} 星星。",
        "ru": "Запрос на вывод {amount} Звезд зарегистрирован."
    },
    "market_confirm": {
        "en": "You requested to buy {quantity} gifts in price range {min_price} - {max_price}. Purchase will be done manually.",
        "zh": "您请求购买价格范围 {min_price} - {max_price} 内的 {quantity} 个礼物。购买将手动完成。",
        "ru": "Вы запросили покупку {quantity} подарков в ценовом диапазоне {min_price} - {max_price}. Покупка будет выполнена вручную."
    },
    "profile_info": {
        "en": "Your balance: {balance} Stars\nDeposited: {deposits} Stars\nReferrals: {ref_count}\nReferral deposits: {ref_deposits} Stars\nReferral bonus (2%): {bonus} Stars (not withdrawable)",
        "zh": "您的余额：{balance} 星星\n充值总额：{deposits} 星星\n邀请人数：{ref_count}\n邀请充值总额：{ref_deposits} 星星\n邀请奖励（2%）：{bonus} 星星（不可提现）",
        "ru": "Ваш баланс: {balance} Звезд\nВнесено: {deposits} Звезд\nРефералы: {ref_count}\nРеферальные депозиты: {ref_deposits} Звезд\nРеферальный бонус (2%): {bonus} Звезд (не выводится)"
    },
    "invalid_input": {
        "en": "Invalid input. Please try again.",
        "zh": "输入无效，请重试。",
        "ru": "Неверный ввод. Пожалуйста, попробуйте снова."
    }
}

# ذخیره حالت‌های مکالمه (state) برای ورودی کاربر
user_states = {}  # user_id: current state, and temp data

# استیت‌ها
STATE_NONE = 0
STATE_DEPOSIT = 1
STATE_MARKET_PRICE = 2
STATE_MARKET_QUANTITY = 3
STATE_WITHDRAW = 4

def get_user_data(user_id):
    if user_id not in user_data:
        user_data[user_id] = {
            "lang": None,
            "balance": 0,
            "deposits": 0,
            "referrals": set(),
            "referral_deposits": 0
        }
    return user_data[user_id]

def get_message(user_id, key, **kwargs):
    lang = get_user_data(user_id).get("lang") or "en"
    text = MESSAGES.get(key, {}).get(lang, "")
    if kwargs:
        return text.format(**kwargs)
    return text

def main_menu_keyboard(lang):
    buttons = [
        types.InlineKeyboardButton(text={"en":"Deposit","zh":"充值","ru":"Внести"}[lang], callback_data="menu_deposit"),
        types.InlineKeyboardButton(text={"en":"Market","zh":"市场","ru":"Маркет"}[lang], callback_data="menu_market"),
        types.InlineKeyboardButton(text={"en":"Withdraw","zh":"提现","ru":"Вывести"}[lang], callback_data="menu_withdraw"),
        types.InlineKeyboardButton(text={"en":"Profile","zh":"个人资料","ru":"Профиль"}[lang], callback_data="menu_profile"),
    ]
    keyboard = types.InlineKeyboardMarkup(row_width=2)
    keyboard.add(*buttons)
    return keyboard

@dp.message_handler(commands=["start"])
async def cmd_start(message: types.Message):
    user_id = message.from_user.id
    args = message.get_args()
    if args:
        try:
            ref_id = int(args)
            if ref_id != user_id:
                if ref_id not in referrals:
                    referrals[ref_id] = set()
                referrals[ref_id].add(user_id)
                ref_user = get_user_data(ref_id)
                ref_user["referrals"].add(user_id)
        except:
            pass
    user_data.setdefault(user_id, {"lang": None, "balance":0, "deposits":0, "referrals": set(), "referral_deposits":0})
    user_states[user_id] = {"state": STATE_NONE}
    keyboard = types.InlineKeyboardMarkup(row_width=3)
    for code, lang_name in LANGUAGES.items():
        keyboard.insert(types.InlineKeyboardButton(text=lang_name, callback_data=f"lang_{code}"))
    await message.answer(MESSAGES["choose_language"]["en"], reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data.startswith("lang_"))
async def process_language(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    lang_code = callback_query.data[5:]
    user = get_user_data(user_id)
    user["lang"] = lang_code
    user_states[user_id] = {"state": STATE_NONE}

    await callback_query.answer()
    await bot.send_message(user_id, MESSAGES["welcome"][lang_code])

    invite_link = f"https://t.me/{(await bot.get_me()).username}?start={user_id}"
    await bot.send_message(user_id, f"Your invite link:\n{invite_link}")

    await bot.send_message(user_id, get_message(user_id, "main_menu"), reply_markup=main_menu_keyboard(lang_code))

@dp.callback_query_handler(lambda c: c.data.startswith("menu_"))
async def process_menu(callback_query: types.CallbackQuery):
    user_id = callback_query.from_user.id
    user_state = user_states.get(user_id, {"state": STATE_NONE})
    lang = get_user_data(user_id).get("lang") or "en"
    data = callback_query.data

    await callback_query.answer()

    if data == "menu_deposit":
        user_states[user_id] = {"state": STATE_DEPOSIT}
        await bot.send_message(user_id, get_message(user_id, "deposit_prompt"))
    elif data == "menu_market":
        user_states[user_id] = {"state": STATE_MARKET_PRICE}
        await bot.send_message(user_id, get_message(user_id, "market_prompt_price"))
    elif data == "menu_withdraw":
        user_states[user_id] = {"state": STATE_WITHDRAW}
        await bot.send_message(user_id, get_message(user_id, "withdraw_prompt"))
    elif data == "menu_profile":
        user = get_user_data(user_id)
        ref_count = len(user["referrals"])
        bonus = int(user["referral_deposits"] * 0.02)
        text = get_message(user_id, "profile_info",
            balance=user["balance"],
            deposits=user["deposits"],
            ref_count=ref_count,
            ref_deposits=user["referral_deposits"],
            bonus=bonus
        )
        await bot.send_message(user_id, text, reply_markup=main_menu_keyboard(lang))

@dp.message_handler()
async def process_message(message: types.Message):
    user_id = message.from_user.id
    state_info = user_states.get(user_id)
    if not state_info:
        keyboard = types.InlineKeyboardMarkup(row_width=3)
        for code, lang_name in LANGUAGES.items():
            keyboard.insert(types.InlineKeyboardButton(text=lang_name, callback_data=f"lang_{code}"))
        await message.answer(MESSAGES["choose_language"]["en"], reply_markup=keyboard)
        return

    state = state_info.get("state", STATE_NONE)
    lang = get_user_data(user_id).get("lang") or "en"

    if state == STATE_DEPOSIT:
        try:
            amount = int(message.text)
            if amount <= 0:
                raise ValueError
        except:
            await message.answer(get_message(user_id, "invalid_input"))
            return
        user = get_user_data(user_id)
        user["balance"] += amount
        user["deposits"] += amount
        for ref_id, referred_set in referrals.items():
            if user_id in referred_set:
                ref_user = get_user_data(ref_id)
                ref_user["referral_deposits"] += amount
        user_states[user_id] = {"state": STATE_NONE}
        await message.answer(get_message(user_id, "deposit_success", amount=amount, balance=user["balance"]), reply_markup=main_menu_keyboard(lang))

    elif state == STATE_MARKET_PRICE:
        parts = message.text.split()
        if len(parts) != 2:
            await message.answer(get_message(user_id, "invalid_input"))
            return
        try:
            min_price = int(parts[0])
            max_price = int(parts[1])
            if min_price <= 0 or max_price <= 0 or min_price > max_price:
                raise
