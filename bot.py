from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

BOT_TOKEN = "YOUR_BOT_TOKEN"

CREATOR = "امیر علی فروزان اصل"

# وضعیت ساده کاربر
user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده از ربات

سازنده: {CREATOR}

1. استفاده از این ربات فقط برای تست و آموزش است.
2. هرگونه سوء استفاده بر عهده کاربر است.
3. مدت سرویس حداکثر 30 روز می‌باشد.
4. کاربر موظف است قوانین را رعایت کند.

اگر موافق هستید روی "قبول می‌کنم" بزنید.
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 خواندن قرارداد", callback_data="contract")]
    ]
    await update.message.reply_text(
        "👋 خوش آمدید\nبرای ادامه ابتدا قرارداد را بخوانید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# کنترل دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    user_id = query.from_user.id

    # قرارداد
    if query.data == "contract":
        keyboard = [
            [InlineKeyboardButton("✅ قبول می‌کنم", callback_data="accept"),
             InlineKeyboardButton("❌ قبول ندارم", callback_data="reject")]
        ]
        await query.edit_message_text(CONTRACT_TEXT, reply_markup=InlineKeyboardMarkup(keyboard))

    # قبول قرارداد
    elif query.data == "accept":
        user_data[user_id] = {"accepted": True}
        await show_config_menu(query)

    # رد قرارداد
    elif query.data == "reject":
        await query.edit_message_text("⛔ بدون پذیرش قرارداد نمی‌توانید استفاده کنید.")

    # انتخاب مدت
    elif query.data.startswith("days_"):
        days = int(query.data.split("_")[1])
        user_data[user_id]["days"] = days
        await query.edit_message_text(f"📅 مدت انتخاب شد: {days} روز\nحالا حجم را انتخاب کنید:")
        await show_size_menu(query)

    # انتخاب حجم
    elif query.data.startswith("size_"):
        size = query.data.split("_")[1]
        user_data[user_id]["size"] = size

        data = user_data[user_id]

        result = f"""
✅ کانفیگ ساخته شد

👤 کاربر: {query.from_user.first_name}
📅 مدت: {data.get('days')} روز
📦 حجم: {data.get('size')}

🧑‍💻 سازنده: {CREATOR}
"""
        await query.edit_message_text(result)

# منوی تنظیمات
async def show_config_menu(query):
    keyboard = [
        [InlineKeyboardButton("7 روز", callback_data="days_7"),
         InlineKeyboardButton("15 روز", callback_data="days_15")],
        [InlineKeyboardButton("30 روز", callback_data="days_30")]
    ]
    await query.edit_message_text(
        "📅 مدت سرویس را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# منوی حجم
async def show_size_menu(query):
    keyboard = [
        [InlineKeyboardButton("1GB", callback_data="size_1GB"),
         InlineKeyboardButton("5GB", callback_data="size_5GB")],
        [InlineKeyboardButton("10GB", callback_data="size_10GB")]
    ]
    await query.message.reply_text(
        "📦 حجم را انتخاب کنید:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
