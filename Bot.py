import os
import threading
import time
from flask import Flask
import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8973617780:AAErTwc1zEK8vSh0DZJqNFLIhJZmP3tFl4E'

# আপনার টেলিগ্রামের সংখ্যাসূচক আইডি (Numeric Chat ID)
ADMIN_ID = 7283303333 

WHATSAPP_LINK = 'https://wa.me' # WhatsApp লিংক
ADMIN_TELEGRAM = 'https://t.me' # টেলিগ্রাম প্রোফাইল লিংক
bot = telebot.TeleBot(API_TOKEN)

# রেন্ডার সার্ভার সচল রাখার জন্য হালকা ফ্ল্যাস্ক সার্ভার
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running successfully!"

def run_flask():
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)

# ব্যবহারকারীর বর্তমান স্টেপ ও অর্ডার ট্র্যাক করার জন্য ডিকশনারি ও সেট
user_states = {}
user_orders = {}
notified_users = set()  # নতুন ব্যবহারকারী ট্র্যাক করার জন্য সেট

# সঠিক পেমেন্ট নম্বর
PAYMENT_NUMBERS = {
    "bkash": "01820313593",
    "rocket": "01820313593"
}

# প্যাকেজের তালিকা ও দাম
packages = {
    "pack1": {"name": "💎 ২৫ ডায়মন্ড", "price": "২১ TK"},
    "pack2": {"name": "💎 ৫০ ডায়মন্ড", "price": "৩৬ TK"},
    "pack3": {"name": "💎 ১১৫ ডায়মন্ড", "price": "৭৬ TK"},
    "pack4": {"name": "💎 ২৪০ ডায়মন্ড", "price": "১৫৩ TK"},
    "pack5": {"name": "💎 ৬১০ ডায়মন্ড", "price": "৩৮০ TK"},
    "pack6": {"name": "💎 ১২৫০ ডায়মন্ড", "price": "৭৭০ TK"},
    "pack7": {"name": "weekly membership", "price": "১৫০ TK"},
    "pack8": {"name": "Monthly membership", "price": "৭৬০ TK"},
    "pack9": {"name": "২০০০ Unipin out ofstok", "price": "১৬৯০ TK"}
}

# মূল মেনু দেখানোর ফাংশন
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
    
    # শুধুমাত্র প্রথমবার ইউজারের ক্ষেত্রে এডমিনকে অ্যালার্ট পাঠানো হবে
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
    bot.send_message(
        message.chat.id, 
        "সাপোর্ট ও যোগাযোগের জন্য নিচের মাধ্যমগুলো ব্যবহার করুন:", 
        reply_markup=markup
    )

@bot.message_handler(commands=['owner'])
def contact_owner(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👑 সরাসরি ওনারের সাথে চ্যাট করুন", url=ADMIN_TELEGRAM))
    bot.send_message(
        message.chat.id,
        "বটের ওনার বা এডমিনের সাথে সরাসরি কথা বলতে নিচের বাটনে ক্লিক করুন:",
        reply_markup=markup
    )

@bot.message_handler(commands=['rate'])
def payment_rate(message):
    text = (
        "💳 **পেমেন্ট মেথড (Payment Method):**\n"
        "আমাদের বিকাশ বা রকেট পার্সোনাল নম্বরে টাকা পাঠান:\n"
        "• বিকাশ (Personal): `01820313593`\n"
        "• রকেট (Personal): `01820313593`\n"
        "• সাপোর্ট (Support): `/contact`\n"
        "• ওনার (Owner): `/owner`\n\n"
        "কোনো সমস্যা হলে সহায়তা পেতে যোগাযোগ করুন।"
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
        # ধাপ ১ এর পরে ইউজার এখন প্রথমে গেম UID দেওয়ার স্টেপে যাবে
        user_states[chat_id] = "WAITING_FOR_UID"
        user_orders[chat_id] = {
            "package": selected_package
        }
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        try:
            bot.edit_message_text(
                text=f"আপনি সিলেক্ট করেছেন: **{selected_package['name']}** ({selected_package['price']}).\n\n📌 **ধাপ ১: এখন আপনার গেম ইউআইডি (UID) টি লিখে পাঠান:**",
                chat_id=chat_id, 
                message_id=call.message.message_id, 
                reply_markup=markup,
                parse_mode="Markdown"
            )
        except Exception:
            pass
    
    elif call.data.startswith("pay_"):
        parts = call.data.split('_')
        payment_method = parts[1]  
        
        if chat_id not in user_orders:
            bot.answer_callback_query(call.id, "সেশন শেষ হয়ে গেছে। আবার শুরু করুন।")
            return
            
        method_name = "বিকাশ" if payment_method == "bkash" else "রকেট"
        acc_number = PAYMENT_NUMBERS[payment_method]
        
        user_orders[chat_id]["method"] = method_name
        user_states[chat_id] = "WAITING_FOR_TRX"
        
        selected_package = user_orders[chat_id]["package"]
        
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

# ব্যবহারকারী বা এডমিনের মেসেজ হ্যান্ডেল করার ফাংশন
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo'])
def handle_all_messages(message):
    chat_id = message.chat.id
    is_admin = (chat_id == ADMIN_ID)
    
    # এডমিন হ্যান্ডলার (অটো রিপ্লাই সিস্টেম)
    if is_admin:
        if message.reply_to_message:
            replied_text = message.reply_to_message.text or message.reply_to_message.caption
            if replied_text and "ID:" in replied_text:
                try:
                    parts = replied_text.split("ID:")
                    user_id_part = int(parts[1].split(')')[0].strip())
                    
                    success_msg = (
                        "🎉 **অভিনন্দন! আপনার টপ-আপ সফলভাবে সম্পন্ন হয়েছে।** 🎮\n\n"
                        "আপনার অর্ডারটি সফলভাবে চেক ও ডেলিভারি করা হয়েছে। আমাদের সাথে থাকার জন্য ধন্যবাদ! ❤️"
                    )
                    
                    final_reply = message.text if message.text else success_msg
                    
                    bot.send_message(user_id_part, final_reply, parse_mode="Markdown")
                    bot.reply_to(message, "✅ ইউজারের কাছে সফলভাবে কনফার্মেশন মেসেজ চলে গেছে!")
                except Exception as e:
                    bot.reply_to(message, f"❌ পাঠাতে সমস্যা হয়েছে: {e}")
        return

    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
    current_state = user_states.get(chat_id)
    
    # ধাপ ১: গেম ইউআইডি (UID) গ্রহণ করা এবং পেমেন্ট অপশন দেখানো
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

    # ধাপ ২: পেমেন্ট মেথড সিলেক্ট করার স্টেট (যদি ইউজার টেক্সট লেখে)
    elif current_state == "WAITING_FOR_PAYMENT_METHOD":
        bot.reply_to(message, "দয়া করে নিচের বাটন থেকে আপনার পেমেন্ট মেথড (বিকাশ বা রকেট) সিলেক্ট করুন।")
        return

    # ধাপ ৩: ট্রানজেকশন আইডি বা স্ক্রিনশট গ্রহণ করা এবং এডমিনকে পাঠানো
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
            # ট্রানজেকশন আইডি কমপক্ষে ৬ অক্ষরের না হলে তা গ্রহণ করবে না
            if len(trx_text) < 6:
                bot.reply_to(message, "❌ ভুল ট্রানজেকশন আইডি! দয়া করে আপনার সঠিক TrxID লিখে পাঠান।")
                return
        
        user_orders[chat_id]["trx"] = trx_text
        user_orders[chat_id]["photo_id"] = photo_id
        
        order_info = user_orders[chat_id]
        selected_package = order_info.get("package", {"name": "অজানা", "price": ""})
        method_name = order_info.get("method", "N/A")
        uid = order_info.get("uid", "N/A")
        
        # ইউজারকে ১-২ মিনিটের টাইমার ও প্রসেসিং মেসেজ পাঠানো
        bot.reply_to(message, "⏳ আপনার ট্রানজেকশন আইডি এবং গেম UID যাচাই করা হচ্ছে...\n\n🕒 দয়া করে ১ থেকে ২ মিনিট অপেক্ষা করুন, আপনার অর্ডারটি সফলভাবে চেক করে দ্রুত আপনার ইন-গেমে অ্যাড করা হবে।")
        
        admin_msg = (f"🔔 নতুন অর্ডার যাচাইয়ের জন্য এসেছে!\n\n"
                     f"👤 ক্রেতা: {user_info}\n"
                     f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
                     f"💳 মাধ্যম: {method_name}\n"
                     f"🔤 TrxID: {trx_text}\n"
                     f"🆔 গেম UID: `{uid}`")
        
        try:
            if photo_id:
                bot.send_photo(ADMIN_ID, photo_id, caption=admin_msg, parse_mode="Markdown")
            else:
                bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
        except Exception as e:
            print(f"Forward order failed: {e}")
            bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        return

    else:
        bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে প্যাকেজ সিলেক্ট করুন।")

if __name__ == '__main__':
    # আলাদা থ্রেডে Flask সার্ভার চালু করা যাতে রেন্ডার পোর্ট ওপেন রাখতে পারে
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    
    # বট সচল রাখা
    bot.infinity_polling()
