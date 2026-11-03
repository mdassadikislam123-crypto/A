import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton
import time
import threading
from flask import Flask

API_TOKEN = '8973617780:AAGObYqffLwVJqn3uKjp2LH0QQqUiTMHMcc'

# আপনার টেলিগ্রামের সংখ্যাসূচক আইডি (Numeric Chat ID)
ADMIN_ID = 7283303333 

WHATSAPP_LINK = 'https://wa.me https://wa.me/message/25RTDSJ2EXQ7E1'  # WhatsApp লিংক
ADMIN_TELEGRAM = 'https://t.me @ownerastopup' # টেলিগ্রাম প্রোফাইল লিংক
bot = telebot.TeleBot(API_TOKEN)

# ব্যবহারকারীর বর্তমান স্টেপ ও অর্ডার ডাটা ট্র্যাক করার জন্য ডিকশনারি
user_states = {}
user_orders = {}

# সঠিক পেমেন্ট নম্বর ও নিয়মাবলী
PAYMENT_INFO = {
    "bkash": {
        "number": "01820313593",
        "name": "বিকাশ",
        "instructions": (
            "📌 **বিকাশ পেমেন্ট করার নিয়ম:**\n"
            "১. প্রথমে আপনার ডায়াল প্যাডে গিয়ে `*247#` ডায়াল করুন।\n"
            "২. এরপর **Send Money** অপশন (১ নম্বর) সিলেক্ট করুন।\n"
            "৩. প্রাপক হিসেবে আমাদের এই পার্সোনাল নম্বরটি দিন: `01820313593`\n"
            "৪. আপনার প্যাকেজের নির্দিষ্ট টাকার পরিমাণ (Price) বসিয়ে পিন নম্বর দিয়ে সেন্ড মানি সম্পন্ন করুন।\n"
            "৫. পরিশেষে প্রাপ্ত **TrxID** (ট্রানজেকশন আইডি) অথবা পেমেন্টের স্ক্রিনশট এখানে পাঠিয়ে দিন।"
        )
    },
    "rocket": {
        "number": "01820313593",
        "name": "রকেট",
        "instructions": (
            "📌 **রকেট পেমেন্ট করার নিয়ম:**\n"
            "১. প্রথমে আপনার ডায়াল প্যাডে গিয়ে `*322#` ডায়াল করুন।\n"
            "২. এরপর **Send Money** অপশন সিলেক্ট করুন।\n"
            "৩. প্রাপক হিসেবে আমাদের এই পার্সোনাল নম্বরটি দিন: `01820313593`\n"
            "৪. আপনার প্যাকেজের নির্দিষ্ট টাকার পরিমাণ (Price) বসিয়ে পিন নম্বর দিয়ে লেনদেন সম্পন্ন করুন।\n"
            "৫. পরিশেষে প্রাপ্ত **TrxID** (ট্রানজেকশন আইডি) অথবা পেমেন্টের স্ক্রিনশট এখানে পাঠিয়ে দিন।"
        )
    }
}

# প্যাকেজের তালিকা ও দাম
packages = {
    "pack1": {"name": "💎 ২৫ ডায়মন্ড", "price": "২২ TK"},
    "pack2": {"name": "💎 ৫০ ডায়মন্ড", "price": "৩৬ TK"},
    "pack3": {"name": "💎 ১১৫ ডায়মন্ড", "price": "৭৭ TK"},
    "pack4": {"name": "💎 ২৪০ ডায়মন্ড", "price": "১৫৪ TK"},
    "pack5": {"name": "💎 ৬১০ ডায়মন্ড", "price": "৩৯০ TK"},
    "pack6": {"name": "💎 ১২৫০ ডায়মন্ড", "price": "৭৮০ TK"},
    "pack7": {"name": "Monthly", "price": "৭৭০ TK"},
    "pack8": {"name": "২০০০ Unipin", "price": "১৬৯০ TK"}
}

# --- Flask Server (স্লিপ মোড রোধ করার জন্য) ---
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running and active!"

def run_flask():
    app.run(host='0.0.0.0', port=8080)
# ---------------------------------------------

# ১. প্রথম কমান্ড: স্টার্ট (ইন্দ্রো ও মেইন অপশন মেনু)
@bot.message_handler(commands=['start'])
def send_welcome(message):
    user_states.pop(message.chat.id, None)
    user_orders.pop(message.chat.id, None)
    
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("💎 টপ আপ লিস্ট দেখুন", callback_data="show_list"))
    markup.add(InlineKeyboardButton("💳 পেমেন্ট মেথড ও নিয়ম", callback_data="show_payment"))
    markup.add(InlineKeyboardButton("💬 এডমিনের সাথে যোগাযোগ", callback_data="show_contact"))
    
    text = (
        "আসসালামু আলাইকুম। আমাদের টপ আপ বটে আপনাকে স্বাগতম! 🎮✨\n\n"
        "নিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় অপশনটি সিলেক্ট করুন:"
    )
    bot.send_message(message.chat.id, text, reply_markup=markup)

# ২. দ্বিতীয় কমান্ড: টপ আপ লিস্ট
@bot.message_handler(commands=['list', 'top_up'])
def show_packages_command(message):
    show_packages_menu(message.chat.id)

def show_packages_menu(chat_id, message_id=None):
    markup = InlineKeyboardMarkup()
    for key, value in packages.items():
        markup.add(InlineKeyboardButton(f"{value['name']} - {value['price']}", callback_data=key))
    
    markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
    
    text = "💎 **আমাদের টপ-আপ প্যাকেজসমূহ:**\n\nনিচের প্যাকেজগুলো থেকে আপনার পছন্দের প্যাকেজটি সিলেক্ট করুন:"
    if message_id:
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")
    else:
        bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")

# ৩. তৃতীয় কমান্ড: পেমেন্ট মেথড
@bot.message_handler(commands=['payment', 'rate'])
def payment_rate(message):
    text = (
        "💳 **পেমেন্ট মেথড ও নিয়মাবলী:**\n\n"
        "🔹 **বিকাশ (Personal):** `01820313593` (`*247#` ডায়াল করে সেন্ড মানি করুন)\n"
        "🔹 **রকেট (Personal):** `01820313593` (`*322#` ডায়াল করে সেন্ড মানি করুন)\n\n"
        "টাকা পাঠিয়ে ট্রানজেকশন আইডি বটে জমা দিন।"
    )
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
    bot.send_message(message.chat.id, text, reply_markup=markup, parse_mode="Markdown")

# ৪. চতুর্থ কমান্ড: কন্টাক্ট (এডমিনের সাথে যোগাযোগ)
@bot.message_handler(commands=['contact', 'owner'])
def contact_support(message):
    markup = InlineKeyboardMarkup()
    markup.add(InlineKeyboardButton("👑 সরাসরি ওনারের সাথে চ্যাট করুন", url=ADMIN_TELEGRAM))
    markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK))
    markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
    
    bot.send_message(
        message.chat.id, 
        "সাপোর্ট ও এডমিনের সাথে যোগাযোগের জন্য নিচের মাধ্যমগুলো ব্যবহার করুন:", 
        reply_markup=markup
    )

# ইনলাইন বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
    chat_id = call.message.chat.id
    
    if call.data == "show_list":
        show_packages_menu(chat_id, call.message.message_id)
        
    elif call.data == "show_payment":
        text = (
            "💳 **পেমেন্ট মেথড ও নিয়মাবলী:**\n\n"
            "🔹 **বিকাশ (Personal):** `01820313593` (`*247#` ডায়াল করে সেন্ড মানি করুন)\n"
            "🔹 **রকেট (Personal):** `01820313593` (`*322#` ডায়াল করে সেন্ড মানি করুন)\n\n"
            "টাকা পাঠিয়ে ট্রানজেকশন আইডি বটে জমা দিন।"
        )
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            pass

    elif call.data == "show_contact":
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("👑 সরাসরি ওনারের সাথে চ্যাট করুন", url=ADMIN_TELEGRAM))
        markup.add(InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK))
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        try:
            bot.edit_message_text(text="সাপোর্ট ও এডমিনের সাথে যোগাযোগের জন্য নিচের মাধ্যমগুলো ব্যবহার করুন:", chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        except Exception:
            pass

    # এডমিনের জন্য ইনলাইন বাটন ক্লিক হ্যান্ডেলিং
    elif call.data.startswith("admin_reply_"):
        if chat_id != ADMIN_ID:
            return
        
        parts = call.data.split('_')
        action = parts[2] # 'success' অথবা 'notfound'
        target_user_id = int(parts[3])
        
        success_msg = (
            "🎉 **অভিনন্দন! আপনার পেমেন্ট সফলভাবে সম্পন্ন হয়েছে এবং টপ-আপ দেওয়া হয়েছে।** 🎮\n\n"
            "আপনার অর্ডারটি সফলভাবে চেক ও ডেলিভারি করা হয়েছে। আমাদের সাথে থাকার জন্য ধন্যবাদ! ❤️"
        )
        
        not_found_msg = (
            "❌ **দুঃখিত, আপনার ট্রানজেকশন আইডি খুঁজে পাওয়া যায়নি।**\n\n"
            "দয়া করে আপনার সঠিক ট্রানজেকশন আইডি (TrxID) অথবা পেমেন্টের সঠিক স্ক্রিনশট আবার এই চ্যাটে পাঠিয়ে দিন।"
        )
        
        if action == "success":
            final_reply = success_msg
            user_states.pop(target_user_id, None)
            user_orders.pop(target_user_id, None)
        else:
            final_reply = not_found_msg
            user_states[target_user_id] = "WAITING_FOR_TRX"
        
        try:
            bot.send_message(target_user_id, final_reply, parse_mode="Markdown")
            bot.answer_callback_query(call.id, "✅ ইউজারের কাছে মেসেজ সফলভাবে পাঠানো হয়েছে!")
            bot.edit_message_reply_markup(chat_id=chat_id, message_id=call.message.message_id, reply_markup=None)
        except Exception as e:
            bot.answer_callback_query(call.id, f"❌ সমস্যা হয়েছে: {e}")
        return

    elif call.data == "back_to_menu":
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("💎 টপ আপ লিস্ট দেখুন", callback_data="show_list"))
        markup.add(InlineKeyboardButton("💳 পেমেন্ট মেথড ও নিয়ম", callback_data="show_payment"))
        markup.add(InlineKeyboardButton("💬 এডমিনের সাথে যোগাযোগ", callback_data="show_contact"))
        
        text = (
            "আসসালামু আলাইকুম। আমাদের টপ আপ বটে আপনাকে স্বাগতম! 🎮✨\n\n"
            "নিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় অপশনটি সিলেক্ট করুন:"
        )
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup)
        except Exception:
            bot.send_message(chat_id, text, reply_markup=markup)
        
    elif call.data in packages:
        selected_package = packages[call.data]
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("বিকাশ", callback_data=f"pay_bkash_{call.data}"))
        markup.add(InlineKeyboardButton("রকেট", callback_data=f"pay_rocket_{call.data}"))
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        try:
            bot.edit_message_text(
                text=f"আপনি সিলেক্ট করেছেন: {selected_package['name']} ({selected_package['price']}). এখন আপনার পেমেন্ট মেথড সিলেক্ট করুন:",
                chat_id=chat_id, 
                message_id=call.message.message_id, 
                reply_markup=markup
            )
        except Exception:
            pass
    
    elif call.data.startswith("pay_"):
        parts = call.data.split('_')
        payment_method = parts[1]  
        package_key = parts[2]     
        
        selected_package = packages[package_key]
        pay_data = PAYMENT_INFO[payment_method]
        
        user_states[chat_id] = "WAITING_FOR_TRX"
        user_orders[chat_id] = {
            "package": selected_package,
            "method": pay_data['name']
        }
        
        text = (
            f"ধন্যবাদ! আপনি {selected_package['name']} ({selected_package['price']}) এর জন্য {pay_data['name']} সিলেক্ট করেছেন।\n\n"
            f"{pay_data['instructions']}"
        )
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
        try:
            bot.edit_message_text(text=text, chat_id=chat_id, message_id=call.message.message_id, reply_markup=markup, parse_mode="Markdown")
        except Exception:
            pass

# ব্যবহারকারী বা এডমিনের মেসেজ হ্যান্ডেল করার ফাংশন
@bot.message_handler(func=lambda message: True, content_types=['text', 'photo', 'document', 'video', 'sticker', 'audio', 'voice'])
def handle_all_messages(message):
    chat_id = message.chat.id
    is_admin = (chat_id == ADMIN_ID)
    
    if is_admin:
        return

    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
    current_state = user_states.get(chat_id)
    
    # ধাপ ১: ট্রানজেকশন আইডি বা স্ক্রিনশট গ্রহণ করা
    if current_state == "WAITING_FOR_TRX":
        if chat_id not in user_orders:
            bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে মেনুতে যান।")
            return

        if message.photo:
            photo_id = message.photo[-1].file_id
            user_orders[chat_id]["trx"] = "[স্ক্রিনশট]"
            user_orders[chat_id]["photo_id"] = photo_id
        elif message.text:
            user_orders[chat_id]["trx"] = message.text
            user_orders[chat_id]["photo_id"] = None
        else:
            bot.reply_to(message, "❌ দয়া করে সঠিক ট্রানজেকশন আইডি অথবা পেমেন্টের স্ক্রিনশট দিন।")
            return
            
        bot.reply_to(
            message, 
            "⏳ আপনার ট্রানজেকশন আইডিটি চেক করা হচ্ছে, দয়া করে ১ থেকে ২ মিনিট অপেক্ষা করুন।"
        )

        order_info = user_orders.get(chat_id, {})
        selected_package = order_info.get("package", {"name": "অজানা", "price": ""})
        method_name = order_info.get("method", "N/A")
        trx = order_info.get("trx", "N/A")
        photo_id = order_info.get("photo_id")
        
        admin_msg = (f"🔔 নতুন পেমেন্ট যাচাইয়ের অনুরোধ!\n\n"
                     f"👤 ক্রেতা: {user_info}\n"
                     f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
                     f"💳 মাধ্যম: {method_name}\n"
                     f"🔤 TrxID: `{trx}`")
        
        admin_markup = InlineKeyboardMarkup()
        admin_markup.add(
            InlineKeyboardButton("✅ পেমেন্ট সফল (UID চান)", callback_data=f"admin_reply_success_{chat_id}"),
            InlineKeyboardButton("❌ ট্রানজেকশন আইডি পাওয়া যায়নি", callback_data=f"admin_reply_notfound_{chat_id}")
        )
        
        try:
            if photo_id:
                bot.send_photo(ADMIN_ID, photo_id, caption=admin_msg, parse_mode="Markdown", reply_markup=admin_markup)
            else:
                bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown", reply_markup=admin_markup)
        except Exception as e:
            print(f"Forward payment failed: {e}")
            bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            
        return

    # ধাপ ২: পেমেন্ট সফল হওয়ার পরে ইউজার যখন গেম ইউআইডি (UID) পাঠাবে
    elif current_state == "WAITING_FOR_UID":
        if chat_id not in user_orders:
            bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে মেনুতে যান।")
            user_states.pop(chat_id, None)
            return
            
        if not message.text:
            bot.reply_to(message, "❌ দয়া করে আপনার গেম UID টেক্সট আকারে লিখে পাঠান।")
            return

        uid = message.text
        order_info = user_orders.get(chat_id, {})
        selected_package = order_info.get("package", {"name": "অজানা", "price": ""})
        method_name = order_info.get("method", "N/A")
        trx = order_info.get("trx", "N/A")
        
        admin_msg = (f"🎮 পেমেন্ট কনফার্মড! এখন টপ-আপ দিন:\n\n"
                     f"👤 ক্রেতা: {user_info}\n"
                     f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
                     f"💳 মাধ্যম: {method_name}\n"
                     f"🔤 TrxID: `{trx}`\n"
                     f"🆔 গেম UID: `{uid}`")
        
        try:
            bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
            
            bot.reply_to(
                message,
                "✅ আপনার গেম ইউআইডি সফলভাবে জমা হয়েছে!\n"
                "⏳ ১ থেকে ২ মিনিট অপেক্ষা করুন, খুব শীঘ্রই আপনার আইডিতে ডায়মন্ড চলে যাবে। ধন্যবাদ! ❤️"
            )
        except Exception as e:
            print(f"Forward UID failed: {e}")
            bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        return

    else:
        bot.reply_to(message, "বট সচল আছে। নতুন করে শুরু করতে /start কমান্ড দিন।")

# মেইন রান ফাংশন যেখানে ফ্লাস্ক সার্ভার এবং টেলিগ্রাম বট একসাথে চলবে
if __name__ == '__main__':
    t = threading.Thread(target=run_flask)
    t.daemon = True
    t.start()
    print("Flask web server started to prevent sleep mode...")

    print("Bot is running...")
    while True:
        try:
            bot.polling(none_stop=True, interval=0, timeout=20)
        except Exception as e:
            print(f"Bot crashed with error: {e}")
            print("Restarting bot in 5 seconds...")
            time.sleep(5)
