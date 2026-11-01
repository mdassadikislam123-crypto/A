import telebot
from telebot.types import InlineKeyboardMarkup, InlineKeyboardButton

API_TOKEN = '8973617780:AAHcgmcSLKk2UDBjyj_Uyn33vkHMOS5DYz0'

# আপনার টেলিগ্রামের সংখ্যাসূচক আইডি (Numeric Chat ID)
ADMIN_ID = 7283303333 

WHATSAPP_LINK = 'https://wa.me/message/25RTDSJ2EXQ7E1–#WhatsApppp লিংক
ADMIN_TELEGRAM = 'https://t.me/ownerastopupup # টেলিগ্রাম প্রোফাইল লিংক
bot = telebot.TeleBot(API_TOKEN)

# ব্যবহারকারীর বর্তমান স্টেপ ও অর্ডার ডাটা ট্র্যাক করার জন্য ডিকশনারি
user_states = {}
user_orders = {}

# সঠিক পেমেন্ট নম্বর
PAYMENT_NUMBERS = {
    "bkash": "01820313593",
    "rocket": "01820313593"
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
        method_name = "বিকাশ" if payment_method == "bkash" else "রকেট"
        acc_number = PAYMENT_NUMBERS[payment_method]
        
        user_states[chat_id] = "WAITING_FOR_TRX"
        user_orders[chat_id] = {
            "package": selected_package,
            "method": method_name
        }
        
        text = (f"ধন্যবাদ! আপনি {selected_package['name']} এর জন্য {method_name} সিলেক্ট করেছেন।\n\n"
                f"আমাদের পার্সোনাল নম্বরে টাকা পাঠিয়ে দিন:\n"
                f"📌 **{method_name} (Personal):** `{acc_number}`\n\n"
                f"📥 **ধাপ ১: এখন আপনার ট্রানজেকশন আইডি (TrxID) অথবা পেমেন্টের স্ক্রিনশট এই চ্যাটে পাঠিয়ে দিন।**")
        
        markup = InlineKeyboardMarkup()
        markup.add(InlineKeyboardButton("⬅️ প্যাকেজ মেনুতে ফিরে যান", callback_data="back_to_menu"))
        
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
                    # আইডি সঠিকভাবে আলাদা করার লজিক
                    parts = replied_text.split("ID:")
                    user_id_part = int(parts[1].split(')')[0].strip())
                    
                    # স্বয়ংক্রিয় ডিফল্ট মেসেজ (যদি এডমিন কিছু লিখে না পাঠান)
                    success_msg = (
                        "🎉 **অভিনন্দন! আপনার টপ-আপ সফলভাবে সম্পন্ন হয়েছে।** 🎮\n\n"
                        "আপনার অর্ডারটি সফলভাবে চেক ও ডেলিভারি করা হয়েছে। আমাদের সাথে থাকার জন্য ধন্যবাদ! ❤️"
                    )
                    
                    # এডমিন যদি আলাদা কিছু লিখে পাঠান সেটা যাবে, না হলে ডিফল্ট সাকসেস মেসেজ যাবে
                    final_reply = message.text if message.text else success_msg
                    
                    bot.send_message(user_id_part, final_reply, parse_mode="Markdown")
                    bot.reply_to(message, "✅ ইউজারের কাছে সফলভাবে কনফার্মেশন মেসেজ চলে গেছে!")
                except Exception as e:
                    bot.reply_to(message, f"❌ পাঠাতে সমস্যা হয়েছে: {e}")
        return

    user = message.from_user
    user_info = f"@{user.username}" if user.username else f"{user.first_name} (ID: {user.id})"
    current_state = user_states.get(chat_id)
    
    # ধাপ ১: ট্রানজেকশন আইডি বা স্ক্রিনশট গ্রহণ করা
    if current_state == "WAITING_FOR_TRX":
        if chat_id not in user_orders:
            bot.reply_to(message, "সেশন শেষ হয়ে গেছে। দয়া করে /start দিয়ে আবার শুরু করুন।")
            user_states.pop(chat_id, None)
            return

        if message.photo:
            photo_id = message.photo[-1].file_id
            user_orders[chat_id]["trx"] = "[স্ক্রিনশট]"
            user_orders[chat_id]["photo_id"] = photo_id
        elif message.text:
            user_orders[chat_id]["trx"] = message.text
            user_orders[chat_id]["photo_id"] = None
            
        user_states[chat_id] = "WAITING_FOR_UID"
        bot.reply_to(message, "✅ ট্রানজেকশন আইডি বা স্ক্রিনশট সফলভাবে গ্রহণ করা হয়েছে।\n\n📌 **ধাপ ২: এখন আপনার গেম ইউআইডি (UID) টি লিখে পাঠান:**")
        return

    # ধাপ ২: গেম ইউআইডি (UID) গ্রহণ ও এডমিনকে পাঠানো
    elif current_state == "WAITING_FOR_UID":
        if chat_id not in user_orders:
            bot.reply_to(message, "সেশন শেষ হয়ে গেছে। দয়া করে /start দিয়ে আবার শুরু করুন।")
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
        photo_id = order_info.get("photo_id")
        
        # ফরম্যাটটি এডমিন রিপ্লাই সিস্টেমের (ID: xxxxx) সাথে মিলানো হয়েছে
        admin_msg = (f"🔔 নতুন অর্ডার কনফার্ম হয়েছে!\n\n"
                     f"👤 ক্রেতা: {user_info}\n"
                     f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
                     f"💳 মাধ্যম: {method_name}\n"
                     f"🔤 TrxID: {trx}\n"
                     f"🆔 গেম UID: `{uid}`")
        
        try:
            if photo_id:
                bot.send_photo(ADMIN_ID, photo_id, caption=admin_msg, parse_mode="Markdown")
            else:
                bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
                
            bot.reply_to(message, "✅ আপনার গেম ইউআইডি সফলভাবে জমা হয়েছে! এডমিন যাচাই করে দ্রুত টপ-আপ সম্পন্ন করে দেবেন। ধন্যবাদ!")
        except Exception as e:
            print(f"Forward order failed: {e}")
            bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
            
        user_states.pop(chat_id, None)
        user_orders.pop(chat_id, None)
        return

    else:
        bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে প্যাকেজ সিলেক্ট করুন।")

bot.polling(none_stop=True)
