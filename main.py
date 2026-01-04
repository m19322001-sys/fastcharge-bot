import telebot
from telebot import types
import re

# ========= الإعدادات =========
TOKEN = "8211944216:AAH83QRkTHoY5NGzhsXuQxgNTmkBTojHstw"
ADMIN_ID = 6732122570

bot = telebot.TeleBot(TOKEN)
user_data = {}

# ========= /start =========
@bot.message_handler(commands=["start"])
def start(message):
    user_data[message.chat.id] = {"step": "operator"}

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("📱 Mobilis", "📱 Djezzy", "📱 Ooredoo")

    bot.send_message(
        message.chat.id,
        "👋 مرحبا بك في *FastCharge*\n\n"
        "📶 خدمات فليكسي لجميع الشرائح\n\n"
        "⬇️ اختر الشريحة:",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ========= اختيار الشريحة =========
@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id]["step"] == "operator")
def operator(message):
    if message.text not in ["📱 Mobilis", "📱 Djezzy", "📱 Ooredoo"]:
        bot.send_message(message.chat.id, "❗ اختر الشريحة من الأزرار")
        return

    user_data[message.chat.id]["operator"] = message.text
    user_data[message.chat.id]["step"] = "phone"

    bot.send_message(
        message.chat.id,
        "📞 أرسل رقم الهاتف:",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========= رقم الهاتف (تحقق ذكي) =========
@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id]["step"] == "phone")
def phone(message):
    operator = user_data[message.chat.id]["operator"]

    patterns = {
        "📱 Ooredoo": r"^05\d{8}$",
        "📱 Mobilis": r"^06\d{8}$",
        "📱 Djezzy": r"^07\d{8}$"
    }

    examples = {
        "📱 Ooredoo": "05XXXXXXXX",
        "📱 Mobilis": "06XXXXXXXX",
        "📱 Djezzy": "07XXXXXXXX"
    }

    if not re.match(patterns[operator], message.text):
        bot.send_message(
            message.chat.id,
            f"❌ رقم غير صحيح\n"
            f"📌 شريحة {operator}\n"
            f"📌 مثال صحيح: {examples[operator]}"
        )
        return

    user_data[message.chat.id]["phone"] = message.text
    user_data[message.chat.id]["step"] = "amount"

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("100", "200", "500")
    markup.add("1000", "1500", "2000")

    bot.send_message(
        message.chat.id,
        "💰 اختر مبلغ الفليكسي:",
        reply_markup=markup
    )

# ========= اختيار المبلغ =========
@bot.message_handler(func=lambda m: m.chat.id in user_data and user_data[m.chat.id]["step"] == "amount")
def amount(message):
    if message.text not in ["100", "200", "500", "1000", "1500", "2000"]:
        bot.send_message(message.chat.id, "❗ اختر المبلغ من الأزرار")
        return

    user_data[message.chat.id]["amount"] = message.text
    user_data[message.chat.id]["step"] = "confirm"

    data = user_data[message.chat.id]

    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("✅ تأكيد الطلب", "❌ إلغاء")

    bot.send_message(
        message.chat.id,
        f"📋 *تفاصيل الطلب:*\n\n"
        f"📶 الشريحة: {data['operator']}\n"
        f"📞 الرقم: {data['phone']}\n"
        f"💰 المبلغ: {data['amount']} دج\n\n"
        "هل تريد التأكيد؟",
        parse_mode="Markdown",
        reply_markup=markup
    )

# ========= تأكيد الطلب =========
@bot.message_handler(func=lambda m: m.text == "✅ تأكيد الطلب")
def confirm(message):
    data = user_data.get(message.chat.id)
    user = message.from_user

    username = f"@{user.username}" if user.username else "لا يوجد"
    user_link = f"[فتح المحادثة](tg://user?id={user.id})"

    admin_text = (
        "📥 *طلب جديد فليكسي*\n\n"
        f"👤 المستخدم: {username}\n"
        f"🆔 ID: {user.id}\n"
        f"🔗 {user_link}\n\n"
        f"📶 الشريحة: {data['operator']}\n"
        f"📞 الرقم: {data['phone']}\n"
        f"💰 المبلغ: {data['amount']} دج"
    )

    bot.send_message(ADMIN_ID, admin_text, parse_mode="Markdown")

    bot.send_message(
        message.chat.id,
        "✅ تم استلام طلبك بنجاح\n"
        "📞 سيتم التواصل معك قريبا\n\n"
        "🙏 شكرا لاختيارك خدمتنا",
        reply_markup=types.ReplyKeyboardRemove()
    )

    user_data.pop(message.chat.id, None)

# ========= إلغاء =========
@bot.message_handler(func=lambda m: m.text == "❌ إلغاء")
def cancel(message):
    user_data.pop(message.chat.id, None)
    bot.send_message(
        message.chat.id,
        "❌ تم إلغاء الطلب\n"
        "إذا حاب تعاود، اكتب /start",
        reply_markup=types.ReplyKeyboardRemove()
    )

# ========= رد لطيف على الشكر =========
@bot.message_handler(func=lambda m: m.text.lower() in ["شكرا", "شكراً", "merci", "thanks"])
def thanks(message):
    bot.send_message(
        message.chat.id,
        "🌸 العفو، في خدمتك دائما\n"
        "لأي طلب جديد اكتب /start"
    )

# ========= fallback =========
@bot.message_handler(func=lambda m: True)
def fallback(message):
    bot.send_message(
        message.chat.id,
        "🙂 من فضلك اتبع الخطوات أو اكتب /start"
    )

print("🤖 Bot is running...")
bot.infinity_polling(
