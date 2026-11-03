import os
import threading
from flask import Flask, request
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import re

API_TOKEN = '8973617780:AAErTwc1zEK8vSh0DZJqNFLIhJZmP3tFl4E'

# আপনার টেলিগ্রামের সংখ্যাসূচক আইডি (Numeric Chat ID)
ADMIN_ID = 7283303333 

WHATSAPP_LINK = 'https://wa.me/message/25RTDSJ2EXQ7E1'
ADMIN_TELEGRAM = 'https://t.me/ownerastopupup'
bot = telebot.TeleBot(API_TOKEN)

# রেন্ডার সার্ভার সচল রাখার জন্য ফ্লাস্ক সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

@app.route(f'/{API_TOKEN}', methods=['POST'])
def webhook():
    if request.headers.get('content-type') == 'application/json':
        json_string = request.get_data().decode('utf-8')
        update = telebot.types.Update.de_json(json_string)
        bot.process_new_updates([update])
        return "!", 200
    else:
        return "Invalid request", 403

# ডিকশনারি ও সেটসমূহ
user_states = {}
user_orders = {}
notified_users = set()

# চলমান অর্ডারগুলো সঠিকভাবে ট্র্যাক করার জন্য গ্লোবাল স্টোর (Admin Reply Fix)
active_orders = {}

PAYMENT_NUMBERS = {
    "bkash": "01820313593",
    "rocket": "01820313593"
}

packages = {
    "pack1": {"name": "💎 ২৫ ডায়মন্ড", "price": "২১ TK"},
    "pack2": {"name": "💎 ৫০ ডায়মন্ড", "price": "৩৬ TK"},
    "pack3": {"name": "💎 ১১ ৫ম ডায়মন্ড", "price": "৭৬ TK"},
    "pack4": {"name": "💎 ২৪০ ডায়মন্ড", "price": "১৫৩ TK"},
    "pack5": {"name": "💎 ৬১০ ডায়মন্ড", "price": "৩৮০ TK"},
    "pack6": {"name": "💎 ১২৫০ ডায়মন্ড", "price": "৭৭০ TK"},
    "pack7": {"name": "weekly membership", "price": "১৫০ TK"},
    "pack8": {"name": "Monthly membership", "price": "৭৬০ TK"},
    "pack9": {"name": "২০০০ Unipin out ofstok", "price": "১৬৯০ TK"}
}

def show_main_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    for key, value in packages.items():
        markup.add(InlineKeyboardButton(f"{value['name']} - {value['price']}", callback_data=key))
    
    markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ", url=WHATSAPP_LINK))
    markup.add(InlineKeyboardButton("👑 ওনারের সাথে যোগাযোগ", url=ADMIN_TELEGRAM))
    
    text = "স্বাগতম! নিচের প্যাকেজগুলো থেকে আপনার প্রয়োজনীয় প্যাকেজটি সিলেক্ট করুন:"
    if message_id:
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup)
    else:
        bot.send_message(chat_id, text, reply_markup=markup)

@bot.message_handler(commands=['start', 'top_up'])
def send_welcome(message):
    user_states.pop(message.chat.id, None)
    user_orders.pop(message.chat.id, None)
    show_main_menu(message.chat.id)
    
    if message.chat.id not in notified_users:
        notified_users.add(message.chat.id)
        try:
            bot.send_message(ADMIN_ID, f"New user: {message.chat.id}")
        except Exception as e:
            print(f"Failed to send alert to admin: {e}")

@bot.message_handler(commands=['contact'])
def contact_support(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK))
    markup.add(InlineKeyboardButton("👑 ওনারের টেলিগ্রাম", url=ADMIN_TELEGRAM))
    bot.send_message(message.chat.id, "সাপোর্ট ও যোগাযোগের জন্য নিচের মাধ্যমগুলো ব্যবহার করুন:", reply_markup=markup)

@bot.message_handler(commands=['owner'])
def contact_owner(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👑 সরাসরি ওনারের সাথে চ্যাট করুন", url=ADMIN_TELEGRAM))
    bot.send_message(message.chat.id, "বটের ওনার বা এডমিনের সাথে সরাসরি কথা বলতে নিচের বাটনে ক্লিক করুন:", reply_markup=markup)

@bot.message_handler(commands=['rate'])
def payment_rate(message):
    text = (
        "💳 **পেমেন্ট মেথড (Payment Method):**\n"
        "আমাদের বিকাশ বা রকেট পার্সোনাল নম্বরে টাকা পাঠান:\n"
        "• বিকাশ (Personal): `01820313593`\n"
        "• রকেট (Personal): `01820313593`\n"
    )
    bot.send_message(message.chat.id, text, parse_mode="Markdown")

@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    if call.data == "back_to_menu":
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        show_main_menu(chat_id, call.message.message_id)
        
    elif call.data in packages:
        selected_package = packages[call.data]
        user_states[chat_id] = "WAITING_FOR_UID"
        user_orders[chat_id] = {"package": selected_package}
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        try:
            bot.edit_message_text(
                text=f"আপনি সিলেক্ট করেছেন: **{selected_package['name']}** ({selected_package['price']}).\n\n📌 **ধাপ ১: এখন আপনার গেম ইউআইডি (UID) টি লিখে পাঠান:**",
                chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown"
            )
        except Exception:
            pass
    
    elif call.data.startswith("pay_"):
        payment_method = call.data.split('_')[1]  
        if chat_id not in user_orders:
            bot.answer_callback_query(call.id, "সেশন শেষ হয়ে গেছে। আবার শুরু করুন।")
            return
            
        method_name = "বিকাশ" if payment_method == "bkash" else "রকেট"
        acc_number = PAYMENT_NUMBERS[payment_method]
        
        user_orders[chat_id]["method"] = method_name
        user_states[chat_id] = "WAITING_FOR_TRX"
        
        text = (f"ধন্যবাদ! আপনি পেমেন্ট মাধ্যম হিসেবে **{method_name}** সিলেক্ট করেছেন।\n\n"
                f"আমাদের পার্সোনাল নম্বরে টাকা পাঠিয়ে দিন:\n"
                f"📌 **{method_name} (Personal):** `{acc_number}`\n\n"
                f"📥 **ধাপ ৩: টাকা পাঠানোর পর আপনার ট্রানজেকশন আইডি (TrxID) অথবা পেমেন্টের স্ক্রিনশট এই চ্যাটে পাঠিয়ে দিন।**")
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            pass

@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    chat_id = message.chat.id
    is_admin = (chat_id == ADMIN_ID)
    
    # ----------------- এডমিন প্যানেল হ্যান্ডলিং -----------------
    if is_admin:
        if message.reply_to_message:
            replied_msg = message.reply_to_message
            target_user_id = None
            
            # ১. প্রথমে একটিভ অর্ডার ডিকশনারি থেকে খোঁজার চেষ্টা করবে (সবচেয়ে নির্ভরযোগ্য পদ্ধতি)
            if replied_msg.message_id in active_orders:
                target_user_id = active_orders[replied_msg.message_id]
            else:
                # ২. যদি ডিকশনারিতে না থাকে, তবে মেসেজ টেক্সট থেকে রেগুলার এক্সপ্রেশন দিয়ে আইডি বের করার চেষ্টা করবে
                full_text = ""
                if replied_msg.text:
                    full_text += replied_msg.text
                if replied_msg.caption:
                    full_text += "\n" + replied_msg.caption
                
                # ফ্লেক্সিবল ম্যাচিং (ID: 123456 বা (ID: 123456) উভয় ফরম্যাট রিড করবে)
                match = re.search(r'(?:ID[:\s]*|chat_id[:\s]*)(\d{5,15})', full_text, re.IGNORECASE)
                if match:
                    try:
                        target_user_id = int(match.group(1))
                    except Exception:
                        pass
            
            if target_user_id:
                success_msg = (
                    "🎉 **অভিনন্দন! আপনার টপ-আপ সফলভাবে সম্পন্ন হয়েছে।** 🎮\n\n"
                    "আপনার অর্ডারটি সফলভাবে চেক ও ডেলিভারি করা হয়েছে। আমাদের সাথে থাকার জন্য ধন্যবাদ! ❤️"
                )
                final_reply = message.text if message.text else success_msg
                
                try:
                    bot.send_message(target_user_id, final_reply, parse_mode="Markdown")
                    bot.reply_to(message, f"✅ ইউজারের ({target_user_id}) কাছে সফলভাবে মেসেজ চলে গেছে!")
                except Exception as e:
                    bot.reply_to(message, f"❌ ইউজারের কাছে মেসেজ পাঠাতে সমস্যা হয়েছে: {e}")
            else:
                bot.reply_to(message, "❌ এই মেসেজ থেকে ইউজারের আইডি শনাক্ত করা যায়নি। দয়া করে সঠিক অর্ডার নোটিফিকেশনে রিপ্লাই দিন।")
        return

    # ----------------- সাধারণ ইউজার হ্যান্ডলিং -----------------
    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
    current_state = user_states.get(chat_id)
    
    if current_state == "WAITING_FOR_UID":
        if chat_id not in user_orders:
            bot.reply_to(message, "সেশন শেষ হয়ে গেছে। দয়া করে /start দিয়ে আবার শুরু করুন।")
            user_states.pop(chat_id, None)
            return
            
        if not message.text:
            bot.reply_to(message, "❌ দয়া করে আপনার গেম UID টেক্সট আকারে লিখে পাঠান।")
            return

        uid = message.text.strip()
        user_orders[chat_id]["uid"] = uid
        user_states[chat_id] = "WAITING_FOR_PAYMENT_METHOD"
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("বিকাশ", callback_data="pay_bkash"))
        markup.add(InlineKeyboardButton("রকেট", callback_data="pay_rocket"))
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        bot.reply_to(message, f"✅ গেম UID (`{uid}`) সফলভাবে গ্রহণ করা হয়েছে।\n\n📌 **ধাপ ২: আপনার পেমেন্ট মেথড সিলেক্ট করুন:**", reply_markup=markup, parse_mode="Markdown")
        return

    elif current_state == "WAITING_FOR_PAYMENT_METHOD":
        bot.reply_to(message, "দয়া করে নিচের বাটন থেকে আপনার পেমেন্ট মেথড (বিকাশ বা রকেট) সিলেক্ট করুন।")
        return

    elif current_state == "WAITING_FOR_TRX":
        if chat_id not in user_orders:
            bot.reply_to(message, "সেশন শেষ হয়ে গেছে। দয়া করে /start দিয়ে আবার শুরু করুন।")
            user_states.pop(chat_id, None)
            return

        photo_id = None
        trx_text = "N/A"

        if message.photo:
            photo_id = message.photo[-1].file_id
            trx_text = "[স্ক্রিনশট]"
        elif message.text:
            trx_text = message.text.strip()
            if len(trx_text) < 4:
                bot.reply_to(message, "❌ ভুল ট্রানজেকশন আইডি! দয়া করে আপনার সঠিক TrxID লিখে পাঠান।")
                return
        
        user_orders[chat_id]["trx"] = trx_text
        user_orders[chat_id]["photo_id"] = photo_id
        
        order_info = user_orders[chat_id]
        selected_package = order_info.get("package", {"name": "অজানা", "price": ""})
        method_name = order_info.get("method", "N/A")
        uid = order_info.get("uid", "N/A")
        
        bot.reply_to(message, "⏳ আপনার ট্রানজেকশন আইডি এবং গেম UID যাচাই করা হচ্ছে...\n\n🕒 দয়া করে ১ থেকে ২ মিনিট অপেক্ষা করুন, আপনার অর্ডারটি সফলভাবে চেক করে দ্রুত আপনার ইন-গেমে অ্যাড করা হবে।")
        
        admin_header = (f"🔔 নতুন অর্ডার যাচাইয়ের জন্য এসেছে!\n\n"
                        f"👤 ক্রেতা: {user_info}\n"
                        f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
                        f"💳 মাধ্যম: {method_name}")
        
        trx_msg = f"🔤 TrxID:\n`{trx_text}`"
        uid_msg = f"🆔 গেম UID:\n`{uid}` (ID: {chat_id})"
        
        try:
            sent_msg1 = None
            sent_msg2 = None
            sent_msg3 = None
            
            if photo_id:
                sent_msg1 = bot.send_photo(ADMIN_ID, photo_id, caption=admin_header, parse_mode="Markdown")
                sent_msg2 = bot.send_message(ADMIN_ID, trx_msg, parse_mode="Markdown")
                sent_msg3 = bot.send_message(ADMIN_ID, uid_msg, parse_mode="Markdown")
            else:
                sent_msg1 = bot.send_message(ADMIN_ID, admin_header, parse_mode="Markdown")
                sent_msg2 = bot.send_message(ADMIN_ID, trx_msg, parse_mode="Markdown")
                sent_msg3 = bot.send_message(ADMIN_ID, uid_msg, parse_mode="Markdown")
            
            # অ্যাডমিনের পাঠানো প্রতিটি মেসেজের সাথে ইউজারের আসল চ্যাট আইডি ম্যাপ করে রাখা হলো
            if sent_msg1: active_orders[sent_msg1.message_id] = chat_id
            if sent_msg2: active_orders[sent_msg2.message_id] = chat_id
            if sent_msg3: active_orders[sent_msg3.message_id] = chat_id
            
        except Exception as e:
            print(f"Forward order failed: {e}")
            bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        return

    else:
        bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে প্যাকেজ সিলেক্ট করুন।")

if __name__ == '__main__':
    RENDER_EXTERNAL_URL = os.environ.get("RENDER_EXTERNAL_URL")
    if RENDER_EXTERNAL_URL:
        bot.remove_webhook()
        bot.set_webhook(url=f"{RENDER_EXTERNAL_URL}/{API_TOKEN}")
    
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
