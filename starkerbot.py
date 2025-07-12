import os
import logging
from aiogram import Bot, Dispatcher, types
from aiogram.types import ParseMode
from quart import Quart, request

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

# ادامه کد (هندلرها، منوها، استیت‌ها) همانند قبل باقی می‌ماند...

app = Quart(__name__)

@app.route(WEBHOOK_PATH, methods=["POST"])
async def webhook():
    data = await request.get_data()
    update = types.Update.de_json(data.decode("utf-8"))
    await dp.process_update(update)
    return "", 200

@app.route("/", methods=["GET"])
async def index():
    return "Bot is alive!", 200

async def on_startup():
    await bot.set_webhook(WEBHOOK_URL)
    print("Webhook set!")

async def on_shutdown():
    await bot.delete_webhook()
    await bot.session.close()

if __name__ == "__main__":
    import asyncio

    loop = asyncio.get_event_loop()
    loop.run_until_complete(on_startup())
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 8080)))
