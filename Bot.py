import json
import os
import threading
import time
from flask import Flask
import telebot
from telebot.types import (
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    ReplyKeyboardMarkup,
)

# আপনার টেলিগ্রাম বট টোকেন
API_TOKEN = "9120055505:AAHFGkjefGTxTEulB16xGbaOgu2AifHPoKg"

# এডমিনের সংখ্যাসূচক আইডি
ADMIN_ID = 7283303333

# লিংকসমূহ
WHATSAPP_LINK = "https://wa.me/message/25RTDSJ2EXQ7E1"
ADMIN_TELEGRAM = "https://t.me/ownerastopup"

bot = telebot.TeleBot(API_TOKEN)

# ডাটা ট্র্যাক করার ডিকশনারি ও সেট
user_states = {}
user_orders = {}
active_users = set()

# কন্টাক্ট নম্বর স্থায়ীভাবে সেভ রাখার ফাইল
CONTACTS_FILE = "user_contacts.json"


def load_contacts():
  if os.path.exists(CONTACTS_FILE):
    try:
      with open(CONTACTS_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)
        return {int(k): v for k, v in data.items()}
    except Exception:
      return {}
  return {}


def save_contacts():
  try:
    with open(CONTACTS_FILE, "w", encoding="utf-8") as f:
      json.dump(user_contacts, f, ensure_ascii=False, indent=4)
  except Exception as e:
    print(f"Error saving contacts: {e}")


user_contacts = load_contacts()

# ব্রডকাস্ট মেসেজ
latest_broadcast = (
    "🔥 **বিশেষ অফার ও আপডেট!**\n\nআমাদের বট থেকে খুব কম মূল্যে ডায়মন্ড টপ-আপ"
    " করুন এবং দারুণ সব অফার উপভোগ করুন।"
)
sent_users = set()

# পেমেন্ট নিয়মাবলী ও সিস্টেম
PAYMENT_INFO = {
    "bkash": {
        "number": "01820313593",
        "name": "বিকাশ",
        "instructions": (
            "📌 **বিকাশ পেমেন্ট করার নিয়ম:**\n"
            "১. প্রথমে আপনার ডায়াল প্যাডে গিয়ে `*247#` ডায়াল করুন।\n"
            "২. এরপর **Send Money** অপশন (১ নম্বর) সিলেক্ট করুন।\n"
            "৩. প্রাপক হিসেবে আমাদের এই পার্সোনাল নম্বরটি দিন: `01820313593`\n"
            "৪. আপনার প্যাকেজের নির্দিষ্ট টাকার পরিমাণ বসিয়ে পিন নম্বর দিয়ে সেন্ড মানি সম্পন্ন করুন।\n"
            "৫. পরিশেষে প্রাপ্ত **TrxID** অথবা পেমেন্টের স্ক্রিনশট এখানে পাঠিয়ে দিন।"
        ),
    },
    "rocket": {
        "number": "01820313593",
        "name": "রকেট",
        "instructions": (
            "📌 **রকেট পেমেন্ট করার নিয়ম:**\n"
            "১. প্রথমে আপনার ডায়াল প্যাডে গিয়ে `*322#` ডায়াল করুন।\n"
            "২. এরপর **Send Money** অপশন সিলেক্ট করুন।\n"
            "৩. প্রাপক হিসেবে আমাদের এই পার্সোনাল নম্বরটি দিন: `01820313593`\n"
            "৪. আপনার প্যাকেজের নির্দিষ্ট টাকার পরিমাণ বসিয়ে পিন নম্বর দিয়ে লেনদেন সম্পন্ন করুন।\n"
            "৫. পরিশেষে প্রাপ্ত **TrxID** অথবা পেমেন্টের স্ক্রিনশট এখানে পাঠিয়ে দিন।"
        ),
    },
}

# প্যাকেজ তালিকা
packages = {
    "pack1": {"name": "💎 25 ডায়মন্ড", "price": "22 TK"},
    "pack2": {"name": "💎 50 ডায়মন্ড", "price": "36 TK"},
    "pack3": {"name": "💎 115 ডায়মন্ড", "price": "77 TK"},
    "pack4": {"name": "💎 240 ডায়মন্ড", "price": "154 TK"},
    "pack5": {"name": "💎 610 ডায়মন্ড", "price": "385 TK"},
    "pack6": {"name": "💎 1240 ডায়মন্ড", "price": "780 TK"},
    "pack7": {"name": "Weekly", "price": "152 TK"},
    "pack8": {"name": "Monthly", "price": "770 TK"},
    "pack9": {"name": "❌২০০০ Unipin (Out of stock)", "price": "1690 TK"},
}

# Flask Server (রেন্ডার স্লিপ মোড রোধ করতে)
app = Flask(__name__)


@app.route("/")
def home():
  return "Bot is running and active!"


def run_flask():
  app.run(host="0.0.0.0", port=8080)


# স্টার্ট কমান্ড
@bot.message_handler(commands=["start"])
def send_welcome(message):
  chat_id = message.chat.id

  if chat_id != ADMIN_ID:
    active_users.add(chat_id)

  if chat_id == ADMIN_ID:
    bot.send_message(
        chat_id,
        "এডমিন প্যানেলে স্বাগতম! বট সচল আছে।\n\n📢 সবার কাছে অফার পাঠাতে ব্যবহার"
        " করুন:\n`/broadcast আপনার অফার বা মেসেজ`",
        parse_mode="Markdown",
    )
    return

  user_states.pop(chat_id, None)
  user_orders.pop(chat_id, None)

  if int(chat_id) not in user_contacts:
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_phone = KeyboardButton(
        "📱 আমার কন্টাক্ট নম্বরটি দিন", request_contact=True
    )
    markup.add(button_phone)

    bot.send_message(
        chat_id,
        f"{latest_broadcast}\n\n━━━━━━━━━━━━━━━\nআসসালামু আলাইকুম। আমাদের টপ"
        " আপ বটে আপনাকে স্বাগতম! 🎮✨\n\nবট ব্যবহারের পূর্বে আপনার কন্টাক্ট নম্বরটি"
        " শেয়ার করুন:",
        reply_markup=markup,
        parse_mode="Markdown",
    )
    user_states[chat_id] = "WAITING_FOR_CONTACT"
  else:
    bot.send_message(chat_id, latest_broadcast, parse_mode="Markdown")
    show_main_menu(chat_id)


# ব্রডকাস্ট কমান্ড
@bot.message_handler(commands=["broadcast"])
def broadcast_message(message):
  global latest_broadcast, sent_users
  chat_id = message.chat.id

  if chat_id != ADMIN_ID:
    return

  text_to_send = message.text.replace("/broadcast", "").strip()
  if not text_to_send:
    bot.reply_to(
        message,
        "❌ দয়া করে মেসেজসহ কমান্ডটি দিন। যেমন:\n`/broadcast 🔥 বিশাল অফার!`",
        parse_mode="Markdown",
    )
    return

  latest_broadcast = text_to_send
  sent_users.clear()
  success_count = 0
  fail_count = 0

  bot.reply_to(message, "⏳ সকল ইউজারের কাছে নোটিফিকেশন পাঠানো হচ্ছে...")

  for uid in active_users:
    try:
      bot.send_message(
          uid,
          f"🔔 **বিশেষ ঘোষণা / অফার:**\n\n{text_to_send}",
          parse_mode="Markdown",
      )
      sent_users.add(uid)
      success_count += 1
      time.sleep(0.3)
    except Exception as e:
      print(f"Failed to send to {uid}: {e}")
      fail_count += 1

  bot.send_message(
      ADMIN_ID,
      f"✅ ব্রডকাস্ট সম্পন্ন!\n\n• সফলভাবে পাঠানো হয়েছে: {success_count}"
      f" জন\n• ব্যর্থ হয়েছে: {fail_count} জন",
  )


# মূল মেনু দেখানোর ফাংশন
def show_main_menu(chat_id):
  markup = InlineKeyboardMarkup()
  markup.add(
      InlineKeyboardButton("💎 টপ আপ লিস্ট দেখুন", callback_data="show_list")
  )
  markup.add(
      InlineKeyboardButton(
          "💳 পেমেন্ট মেথড ও নিয়ম", callback_data="show_payment"
      )
  )
  markup.add(
      InlineKeyboardButton(
          "💬 এডমিনের সাথে যোগাযোগ", callback_data="show_contact"
      )
  )

  text = (
      "স্বাগতম! নিচের অপশনগুলো থেকে আপনার প্রয়োজনীয় অপশনটি সিলেক্ট করুন:"
  )
  bot.send_message(chat_id, text, reply_markup=markup)


# প্যাকেজ মেনু
def show_packages_menu(chat_id, message_id=None):
  markup = InlineKeyboardMarkup()
  for key, value in packages.items():
    markup.add(
        InlineKeyboardButton(
            f"{value['name']} - {value['price']}", callback_data=key
        )
    )

  markup.add(
      InlineKeyboardButton(
          "⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"
      )
  )

  text = (
      "💎 **আমাদের টপ-আপ প্যাকেজসমূহ:**\n\nনিচের প্যাকেজগুলো থেকে আপনার পছন্দের"
      " প্যাকেজটি সিলেক্ট করুন:"
  )
  if message_id:
    try:
      bot.edit_message_text(
          text=text,
          chat_id=chat_id,
          message_id=message_id,
          reply_markup=markup,
          parse_mode="Markdown",
      )
    except Exception:
      bot.send_message(
          chat_id, text, reply_markup=markup, parse_mode="Markdown"
      )
  else:
    bot.send_message(chat_id, text, reply_markup=markup, parse_mode="Markdown")


# ইনলাইন বাটন হ্যান্ডলার
@bot.callback_query_handler(func=lambda call: True)
def callback_query(call):
  chat_id = call.message.chat.id

  if call.data == "show_list":
    show_packages_menu(chat_id, call.message.message_id)

  elif call.data == "show_payment":
    text = (
        "💳 **পেমেন্ট মেথড ও নিয়মাবলী:**\n\n"
        "🔹 **বিকাশ (Personal):** `01820313593` (`*247#` ডায়াল করে সেন্ড মানি"
        " করুন)\n"
        "🔹 **রকেট (Personal):** `01820313593` (`*322#` ডায়াল করে সেন্ড মানি"
        " করুন)\n\n"
        "টাকা পাঠিয়ে ট্রানজেকশন আইডি বটে জমা দিন।"
    )
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"
        )
    )
    try:
      bot.edit_message_text(
          text=text,
          chat_id=chat_id,
          message_id=call.message.message_id,
          reply_markup=markup,
          parse_mode="Markdown",
      )
    except Exception:
      pass

  elif call.data == "show_contact":
    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "👑 সরাসরি ওনারের সাথে চ্যাট করুন", url=ADMIN_TELEGRAM
        )
    )
    markup.add(
        InlineKeyboardButton("💬 WhatsApp-এ যোগাযোগ করুন", url=WHATSAPP_LINK)
    )
    markup.add(
        InlineKeyboardButton(
            "⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"
        )
    )
    try:
      bot.edit_message_text(
          text=(
              "সাপোর্ট ও এডমিনের সাথে যোগাযোগের জন্য নিচের মাধ্যমগুলো ব্যবহার"
              " করুন:"
          ),
          chat_id=chat_id,
          message_id=call.message.message_id,
          reply_markup=markup,
      )
    except Exception:
      pass

  elif call.data.startswith("admin_reply_"):
    if chat_id != ADMIN_ID:
      return

    parts = call.data.split("_")
    action = parts[2]
    target_user_id = int(parts[3])

    success_msg = (
        "✅ **আপনার পেমেন্ট সফলভাবে যাচাই করা হয়েছে!** 🎉\n\n"
        "দয়া করে আপনার সঠিক গেম ইউআইডি (Game UID) এই চ্যাটে লিখে পাঠিয়ে দিন,"
        " যেন টপ-আপ দেওয়া যায়:"
    )
    not_found_msg = (
        "❌ **দুঃখিত, আপনার ট্রানজেকশন আইডি খুঁজে পাওয়া যায়নি।**\n\n"
        "দয়া করে আপনার সঠিক ট্রানজেকশন আইডি (TrxID) আবার পাঠিয়ে দিন।"
    )

    if action == "success":
      final_reply = success_msg
      user_states[target_user_id] = "WAITING_FOR_UID"
    else:
      final_reply = not_found_msg
      user_states[target_user_id] = "WAITING_FOR_TRX"

    try:
      bot.send_message(target_user_id, final_reply, parse_mode="Markdown")
      bot.answer_callback_query(
          call.id, "✅ ইউজারের কাছে মেসেজ সফলভাবে পাঠানো হয়েছে!"
      )
      bot.edit_message_reply_markup(
          chat_id=chat_id, message_id=call.message.message_id, reply_markup=None
      )
    except Exception as e:
      bot.answer_callback_query(call.id, f"❌ সমস্যা হয়েছে: {e}")
    return

  elif call.data == "back_to_menu":
    user_states.pop(chat_id, None)
    user_orders.pop(chat_id, None)
    show_main_menu(chat_id)

  elif call.data in packages:
    selected_package = packages[call.data]
    if "Out of stock" in selected_package["name"]:
      bot.answer_callback_query(
          call.id,
          "❌ দুঃখিত! এই প্যাকেজটি বর্তমানে আউট অফ স্টক রয়েছে।",
          show_alert=True,
      )
      return

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton("বিকাশ", callback_data=f"pay_bkash_{call.data}")
    )
    markup.add(
        InlineKeyboardButton("রকেট", callback_data=f"pay_rocket_{call.data}")
    )
    markup.add(
        InlineKeyboardButton(
            "⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"
        )
    )

    try:
      bot.edit_message_text(
          text=(
              f"আপনি সিলেক্ট করেছেন: {selected_package['name']}"
              f" ({selected_package['price']}). এখন আপনার পেমেন্ট মেথড সিলেক্ট"
              " করুন:"
          ),
          chat_id=chat_id,
          message_id=call.message.message_id,
          reply_markup=markup,
      )
    except Exception:
      pass

  elif call.data.startswith("pay_"):
    parts = call.data.split("_")
    payment_method = parts[1]
    package_key = parts[2]

    selected_package = packages[package_key]
    pay_data = PAYMENT_INFO[payment_method]

    user_states[chat_id] = "WAITING_FOR_TRX"
    user_orders[chat_id] = {
        "package": selected_package,
        "method": pay_data["name"],
    }

    text = (
        f"ধন্যবাদ! আপনি {selected_package['name']} ({selected_package['price']})"
        f" এর জন্য {pay_data['name']} সিলেক্ট করেছেন。\n\n"
        f"{pay_data['instructions']}"
    )

    markup = InlineKeyboardMarkup()
    markup.add(
        InlineKeyboardButton(
            "⬅️ মূল মেনুতে ফিরে যান", callback_data="back_to_menu"
        )
    )

    try:
      bot.edit_message_text(
          text=text,
          chat_id=chat_id,
          message_id=call.message.message_id,
          reply_markup=markup,
          parse_mode="Markdown",
      )
    except Exception:
      pass


# মেসেজ এবং কন্টাক্ট হ্যান্ডেলিং
@bot.message_handler(
    func=lambda message: True,
    content_types=[
        "text",
        "photo",
        "document",
        "video",
        "sticker",
        "audio",
        "voice",
        "contact",
    ],
)
def handle_all_messages(message):
  chat_id = message.chat.id
  if chat_id == ADMIN_ID:
    return

  user = message.from_user
  current_state = user_states.get(chat_id)

  if message.contact:
    phone_number = message.contact.phone_number
    user_contacts[int(chat_id)] = phone_number
    save_contacts()

    user_info_msg = (
        f"👤 **নতুন ইউজার যুক্ত হয়েছে!**\n\n"
        f"• নাম: {user.first_name} {user.last_name or ''}\n"
        f"• ইউজারনেম: @{user.username if user.username else 'নেই'}\n"
        f"• ইউজার আইডি (Chat ID): `{user.id}`\n"
        f"• কন্টাক্ট নম্বর: `{phone_number}`"
    )

    try:
      bot.send_message(ADMIN_ID, user_info_msg, parse_mode="Markdown")
    except Exception as e:
      print(f"Failed to send contact to admin: {e}")

    bot.reply_to(
        message,
        "✅ আপনার কন্টাক্ট সফলভাবে ভেরিফাই করা হয়েছে!",
        reply_markup=telebot.types.ReplyKeyboardRemove(),
    )
    user_states.pop(chat_id, None)
    show_main_menu(chat_id)
    return

  if current_state == "WAITING_FOR_CONTACT":
    markup = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
    button_phone = KeyboardButton(
        "📱 আমার কন্টাক্ট নম্বরটি দিন", request_contact=True
    )
    markup.add(button_phone)
    bot.reply_to(
        message,
        "দয়া করে নিচের বাটনে ক্লিক করে আপনার কন্টাক্ট নম্বরটি শেয়ার করুন:",
        reply_markup=markup,
    )
    return

  user_info = (
      f"@{user.username}" if user.username else f"{user.first_name} (ID:"
      f" {user.id})"
  )
  phone_num = user_contacts.get(int(chat_id), "শেয়ার করা হয়নি")

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
      bot.reply_to(
          message,
          "❌ দয়া করে সঠিক ট্রানজেকশন আইডি অথবা পেমেন্টের স্ক্রিনশট দিন।",
      )
      return

    bot.reply_to(
        message, "⏳ আপনার ট্রানজেকশন আইডিটি চেক করা হচ্ছে, অপেক্ষা করুন।"
    )

    order_info = user_orders.get(chat_id, {})
    selected_package = order_info.get(
        "package", {"name": "অজানা", "price": ""}
    )
    method_name = order_info.get("method", "N/A")
    trx = order_info.get("trx", "N/A")
    photo_id = order_info.get("photo_id")

    admin_msg = (
        "🔔 নতুন পেমেন্ট যাচাইয়ের অনুরোধ!\n\n"
        f"👤 ক্রেতা: {user_info}\n"
        f"📞 মোবাইল: `{phone_num}`\n"
        f"🆔 ইউজার আইডি: `{chat_id}`\n"
        f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
        f"💳 মাধ্যম: {method_name}\n"
        f"🔤 TrxID: `{trx}`"
    )

    admin_markup = InlineKeyboardMarkup()
    admin_markup.add(
        InlineKeyboardButton(
            "✅ পেমেন্ট সফল (UID চান)",
            callback_data=f"admin_reply_success_{chat_id}",
        ),
        InlineKeyboardButton(
            "❌ ট্রানজেকশন আইডি পাওয়া যায়নি",
            callback_data=f"admin_reply_notfound_{chat_id}",
        ),
    )

    try:
      if photo_id:
        bot.send_photo(
            ADMIN_ID,
            photo_id,
            caption=admin_msg,
            parse_mode="Markdown",
            reply_markup=admin_markup,
        )
      else:
        bot.send_message(
            ADMIN_ID,
            admin_msg,
            parse_mode="Markdown",
            reply_markup=admin_markup,
        )
    except Exception as e:
      print(f"Forward payment failed: {e}")
      bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")
    return

  elif current_state == "WAITING_FOR_UID":
    if chat_id not in user_orders:
      bot.reply_to(message, "দয়া করে প্রথমে /start কমান্ড দিয়ে মেনুতে যান।")
      user_states.pop(chat_id, None)
      return

    if not message.text:
      bot.reply_to(
          message, "❌ দয়া করে আপনার গেম UID টেক্সট আকারে লিখে পাঠান।"
      )
      return

    uid = message.text
    order_info = user_orders.get(chat_id, {})
    selected_package = order_info.get(
        "package", {"name": "অজানা", "price": ""}
    )
    method_name = order_info.get("method", "N/A")
    trx = order_info.get("trx", "N/A")

    admin_msg = (
        "🎮 পেমেন্ট কনফার্মড! এখন টপ-আপ দিন:\n\n"
        f"👤 ক্রেতা: {user_info}\n"
        f"📞 মোবাইল: `{phone_num}`\n"
        f"🆔 ইউজার আইডি: `{chat_id}`\n"
        f"📦 প্যাকেজ: {selected_package['name']} - {selected_package['price']}\n"
        f"💳 মাধ্যম: {method_name}\n"
        f"🔤 TrxID: `{trx}`\n"
        f"🆔 গেম UID: `{uid}`"
    )

    try:
      bot.send_message(ADMIN_ID, admin_msg, parse_mode="Markdown")
      bot.reply_to(
          message,
          "✅ আপনার গেম ইউআইডি সফলভাবে জমা হয়েছে!\n⏳ ১ থেকে ২ মিনিট"
          " অপেক্ষা করুন, খুব শীঘ্রই আপনার আইডিতে ডায়মন্ড চলে যাবে।"
          " ধন্যবাদ! ❤️",
      )
    except Exception as e:
      print(f"Failed to forward UID: {e}")
      bot.reply_to(message, "❌ তথ্য পাঠাতে সমস্যা হয়েছে। আবার চেষ্টা করুন।")

    user_states.pop(chat_id, None)
    user_orders.pop(chat_id, None)
    return

  else:
    bot.reply_to(message, "বট সচল আছে। নতুন করে শুরু করতে /start কমান্ড দিন।")


# মূল রান সেকশন
if __name__ == "__main__":
  flask_thread = threading.Thread(target=run_flask)
  flask_thread.daemon = True
  flask_thread.start()
  print("Flask web server started on port 8080...")

  try:
    bot.remove_webhook()
    print("Old webhooks removed successfully.")
  except Exception as e:
    print(f"Could not remove webhook: {e}")

  print("Bot is running with infinity polling...")
  while True:
    try:
      bot.infinity_polling(
          interval=0, timeout=20, long_polling_timeout=20
      )
    except Exception as e:
      print(f"Bot encountered an error: {e}")
      print("Restarting polling in 5 secondscharts...")
      time.sleep(5)
