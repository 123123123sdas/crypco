import os
import requests
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Updater, CommandHandler, CallbackContext

# Твои данные
TELEGRAM_TOKEN = '7613669504:AAFRpkXmuL2eQw0zROvaXEz_M2mcFOZJkug'
NOWPAYMENTS_API_KEY = '76WKCA2-4K24612-PPXE9Z3-MD82EDD'
NOWPAYMENTS_API_URL = 'https://api.nowpayments.io/v1/invoice'
BOT_OWNER_CHAT_ID = твой_телега_id  # чтобы уведомлять себя

app = Flask(__name__)
bot = Bot(token=TELEGRAM_TOKEN)

# Словарь для хранения заказов (можно заменить на базу)
orders = {}

def start(update: Update, context: CallbackContext):
    update.message.reply_text("Привет! Чтобы купить крипто-прогноз, отправь /buy")

def buy(update: Update, context: CallbackContext):
    chat_id = update.message.chat_id
    price_usd = 10  # цена прогноза в USD
    currency = 'usd'
    
    # Создаём платёж
    headers = {
        'x-api-key': NOWPAYMENTS_API_KEY,
        'Content-Type': 'application/json',
    }
    data = {
        "price_amount": price_usd,
        "price_currency": currency,
        "pay_currency": "btc",  # или любая другая крипта
        "ipn_callback_url": "https://твой_домен/nowpayments_callback",
        "order_id": str(chat_id),
        "order_description": "Крипто-прогноз",
    }
    response = requests.post(NOWPAYMENTS_API_URL, json=data, headers=headers)
    if response.status_code == 200:
        result = response.json()
        payment_url = result['invoice_url']
        invoice_id = result['id']
        
        # Сохраняем заказ
        orders[invoice_id] = chat_id
        
        update.message.reply_text(f"Плати по ссылке:\n{payment_url}")
    else:
        update.message.reply_text("Ошибка создания платежа. Попробуй позже.")

# Вебхук для уведомлений от NOWPayments
@app.route('/nowpayments_callback', methods=['POST'])
def nowpayments_callback():
    data = request.json
    invoice_id = data.get('invoice_id')
    payment_status = data.get('payment_status')
    
    if payment_status == 'finished' and invoice_id in orders:
        chat_id = orders[invoice_id]
        # Отправляем прогноз пользователю
        bot.send_message(chat_id=chat_id, text="Оплата получена! Вот твой крипто-прогноз: ...")
        
        # Можно удалить заказ
        del orders[invoice_id]
    return jsonify({'status': 'ok'})

def main():
    updater = Updater(TELEGRAM_TOKEN)
    dp = updater.dispatcher
    
    dp.add_handler(CommandHandler("start", start))
    dp.add_handler(CommandHandler("buy", buy))
    
    updater.start_polling()
    print("Бот запущен")
    updater.idle()

if __name__ == "__main__":
    from threading import Thread
    # Запускаем Flask в отдельном потоке
    Thread(target=lambda: app.run(host="0.0.0.0", port=5000)).start()
    
    # Запускаем Telegram бота
    main()
