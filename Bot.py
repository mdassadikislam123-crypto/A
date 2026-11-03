import os
from flask import Flask
from threading import Thread
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '7876371780:AAHGmCSKlZUDbJyJ_Uyn3vkHMOS5DYZo'
ADMIN_ID = 7283303333

WHATSAPP_LINK = 'https://wa.me/message/25RTDSJ2EXQ7E1'
ADMIN_TELEGRAM = 'https://t.me/mdassadikislam123'

bot = telebot.TeleBot(API_TOKEN)

app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

def run_flask():
    app.run(host="0.0.0.0", port=10000)

user_states = {}
user_orders = {}

PAYMENT_NUMBERS = {
    "bkasth": "01820333593",
    "rocket": "01820333593"
}

packages = {
    "pack1": {"name": "💎 ২৫ ডায়মন্ড", "price": "২০ TK"},
    "pack2": {"name": "💎 ৫০ ডায়মন্ড", "price": "৪০ TK"},
    "pack3": {"name": "💎 ১১৫ ডায়মন্ড", "price": "৮০ TK"},
    "pack4": {"name": "💎 ২৪০ ডায়মন্ড", "price": "১৬০ TK"},
    "pack5": {"name": "💎 ৬০৫ ডায়মন্ড", "price": "৪০০ TK"},
    "pack6": {"name": "💎 Weekly membership", "price": "১৬০ TK"},
    "pack7": {"name": "💎 Monthly membership", "price": "৫৫০ TK"},
    "pack8": {"name": "⚡ Asooo Unipun out ofstock", "price": "৭৫০ TK"}
}

def show_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    for key, value in packages.items():
        markup.add(InlineKeyboardButton(f"{value['name']} ({value['price']})", callback_data=key))
    
    markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK))
    markup.add(InlineKeyboardButton("🧑‍💻 এডমিনের সাথে যোগাযোগ", url=ADMIN_TELEGRAM))
    
    text = "👋 স্বাগতম! নিচের প্যাকেজগুলো থেকে আপনার প্রয়োজনীয় প্যাকেজটি সিলেক্ট করুন:"
    if message_id:
        try:
            bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['start', 'top_up'])
def send_welcome(message):
    user_states.pop(message.chat.id, None)
    user_orders.pop(message.chat.id, None)
    show_main_menu(message.chat.id)
    bot.send_message(ADMIN_ID, "New user: " + str(message.chat.id))

@bot.message_handler(commands=['contact'])
def contact_support(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK))
    markup.add(InlineKeyboardButton("🧑‍💻 এডমিনের সাথে যোগাযোগ করুন", url=ADMIN_TELEGRAM))
    bot.send_message(message.chat.id, "💬 এডমিনের সাথে যোগাযোগ করার মাধ্যম করুন:", reply_markup=markup)

@bot.message_handler(commands=['owner'])
def contact_owner(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👑 এডমিনের সাথে যোগাযোগ", url=ADMIN_TELEGRAM))
    bot.send_message(message.chat.id, "👑 এই লিংকে ক্লিক করে এডমিনের সাথে যোগাযোগ করতে পারেন:", reply_markup=markup)

@bot.callback_query_handler(func=lambda call: True)
def callback_data(call):
    chat_id = call.message.chat.id
    message_id = call.message.message_id
    data = call.data

    if data in packages:
        user_orders[chat_id] = {'package': data}
        user_states[chat_id] = 'PAYMENT_METHOD'
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💳 bKash (Payment Method)", callback_data='pay_bkash'))
        markup.add(InlineKeyboardButton("🚀 Rocket (Payment Method)", callback_data='pay_rocket'))
        
        text = f"📦 আপনি সিলেক্ট করেছেন: {packages[data]['name']} - দাম: {packages[data]['price']}\n\nপেমেন্ট মেথড সিলেক্ট করুন:"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, reply_markup=markup)

    elif data in ['pay_bkash', 'pay_rocket']:
        payment_key = "bkasth" if data == 'pay_bkash' else "rocket"
        method_name = "bKash" if data == 'pay_bkash' else "Rocket"
        number = PAYMENT_NUMBERS.get(payment_key, "")
        
        user_states[chat_id] = 'WAITING_FOR_TXID'
        
        text = f"💵 আপনি পেমেন্ট মাধ্যম হিসেবে **{method_name}** সিলেক্ট করেছেন।\n\nদয়া করে এই নম্বরে টাকা পাঠান: `{number}`\n\nটাকা পাঠানোর পর আপনার **Transaction ID (TrxID)** এখানে লিখে পাঠান।"
        bot.edit_message_text(text, chat_id=chat_id, message_id=message_id, parse_mode="Markdown")

@bot.message_handler(func=lambda message: user_states.get(message.chat.id) == 'WAITING_FOR_TXID')
def receive_txid(message):
    chat_id = message.chat.id
    txid = message.text
    selected_pkg = user_orders.get(chat_id, {}).get('package')
    pkg_info = packages.get(selected_pkg, {'name': 'Unknown', 'price': ''})

    bot.send_message(chat_id, "✅ আপনার পেমেন্ট ইনফরমেশন সফলভাবে জমা হয়েছে! এডমিন দ্রুত এটি চেক করে অর্ডারটি কনফার্ম করবেন। ধন্যবাদ।")
    
    admin_text = f"🔔 **নতুন টপ-আপ অর্ডার!**\n\n👤 ইউজার আইডি: `{chat_id}`\n📦 প্যাকেজ: {pkg_info['name']} ({pkg_info['price']})\n💳 TrxID: `{txid}`"
    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")
    
    user_states.pop(chat_id, None)
    user_orders.pop(chat_id, None)
    show_main_menu(chat_id)

if __name__ == "__main__":
    t = Thread(target=run_flask)
    t.start()
    bot.infinity_polling()
