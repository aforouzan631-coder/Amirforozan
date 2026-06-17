import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
    MessageHandler,
    filters
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

CREATOR = "امیر علی فروزان اصل"

user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده

سازنده: {CREATOR}

✔ استفاده فقط آموزشی است
✔ سوء استفاده ممنوع
✔ حداکثر مدت 30 روز

اگر موافق هستی روی دکمه بزن
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 قرارداد", callback_data="contract")]
    ]

    await update.message.reply_text(
        "👋 خوش آمدید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# دکمه‌ها
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    if query.data == "contract":
        keyboard = [
            [
                InlineKeyboardButton("✅ قبول", callback_data="accept"),
                InlineKeyboardButton("❌ رد", callback_data="reject")
            ]
        ]

        await query.edit_message_text(
            CONTRACT_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data == "reject":
        await query.edit_message_text("⛔ بدون قبول قرارداد نمی‌شود ادامه داد")

    elif query.data == "accept":
        elif query.data.startswith("days_"):
    if uid not in user_data:
        await query.edit_message_text("❌ اول قرارداد را قبول کن")
        return
    

        keyboard = [
            [InlineKeyboardButton("7 روز", callback_data="days_7")],
            [InlineKeyboardButton("15 روز", callback_data="days_15")],
            [InlineKeyboardButton("30 روز", callback_data="days_30")]
        ]

        await query.edit_message_text(
            "📅 مدت را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("days_"):
        days = int(query.data.split("_")[1])
        user_data[uid]["days"] = days

        keyboard = [
            [InlineKeyboardButton("1GB", callback_data="size_1GB")],
            [InlineKeyboardButton("5GB", callback_data="size_5GB")],
            [InlineKeyboardButton("10GB", callback_data="size_10GB")]
        ]

        await query.edit_message_text(
            "📦 حجم را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    elif query.data.startswith("size_"):
        size = query.data.split("_")[1]
        user_data[uid]["size"] = size

        data = user_data[uid]

        result = f"""
✅ کانفیگ ساخته شد

📅 مدت: {data.get('days')} روز
📦 حجم: {data.get('size')}

🧑‍💻 سازنده: {CREATOR}
"""

        await query.edit_message_text(result)

# keep alive (برای Railway)
async def ping(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("I'm alive ✅")

def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("ping", ping))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
