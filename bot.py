import os
from dotenv import load_dotenv
load_dotenv()
# остальные импорты...
import requests
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Твои данные
TELEGRAM_TOKEN = '7613669504:AAFRpkXmuL2eQw0zROvaXEz_M2mcFOZJkug'
NOWPAYMENTS_API_KEY = '76WKCA2-4K24612-PPXE9Z3-MD82EDD'
NOWPAYMENTS_API_URL = 'https://api.nowpayments.io/v1/invoice'
BOT_OWNER_CHAT_ID = 7169536049  # чтобы уведомлять себя
import os
import logging
from aiogram import Bot, Dispatcher, executor, types
import requests

logging.basicConfig(level=logging.INFO)

TOKEN = os.getenv("7613669504:AAFRpkXmuL2eQw0zROvaXEz_M2mcFOZJkug")
NEWPAYMENTS_API_KEY = os.getenv("76WKCA2-4K24612-PPXE9Z3-MD82EDD")
NEWPAYMENTS_DOMAIN = os.getenv("https://t.me/+JnNOOw0o8WQwYjUy")  # например, "yourdomain.com" или ссылка на канал

bot = Bot(token=TOKEN)
dp = Dispatcher(bot)

PRODUCT_PRICE = 10  # USD
PRODUCT_DESC = "Эксклюзивный прогноз по крипте на неделю"

@dp.message_handler(commands=['start'])
async def cmd_start(message: types.Message):
    keyboard = types.InlineKeyboardMarkup()
    btn = types.InlineKeyboardButton(text=f"Купить прогноз за ${PRODUCT_PRICE}", callback_data='buy')
    keyboard.add(btn)
    await message.answer("Привет! Хочешь купить прогноз по крипте?", reply_markup=keyboard)

@dp.callback_query_handler(lambda c: c.data == 'buy')
async def process_buy(callback_query: types.CallbackQuery):
    chat_id = callback_query.from_user.id

    payment_data = {
        "amount": PRODUCT_PRICE,
        "currency": "USD",
        "description": PRODUCT_DESC,
        "order_id": f"order_{chat_id}_{callback_query.message.message_id}",
        "success_url": f"https://{NEWPAYMENTS_DOMAIN}/success",
        "cancel_url": f"https://{NEWPAYMENTS_DOMAIN}/cancel"
    }

    headers = {
        "Authorization": f"Bearer {NEWPAYMENTS_API_KEY}",
        "Content-Type": "application/json"
    }

    response = requests.post("https://api.newpayments.io/v1/payments", json=payment_data, headers=headers)

    if response.status_code == 200:
        pay_url = response.json().get("payment_url")
        if pay_url:
            await bot.send_message(chat_id, f"Перейди по ссылке и оплати прогноз:\n{pay_url}")
        else:
            await bot.send_message(chat_id, "Ошибка: ссылка на оплату не получена.")
    else:
        await bot.send_message(chat_id, "Ошибка при создании платежа, попробуйте позже.")

    await bot.answer_callback_query(callback_query.id)

@dp.message_handler(commands=['help'])
async def cmd_help(message: types.Message):
    await message.answer("Команды:\n/start - начать\n/help - помощь")

if __name__ == '__main__':
    executor.start_polling(dp)

