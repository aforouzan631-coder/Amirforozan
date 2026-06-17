import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing")

CREATOR = "امیر علی فروزان اصل"
user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده

👤 سازنده: {CREATOR}

⚠️ این ابزار فقط برای ساخت کانفیگ نمایشی است
⚠️ هرگونه سوء استفاده بر عهده کاربر است
⚠️ استفاده آموزشی و سرگرمی

اگر موافق هستی ادامه بده
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 خواندن قرارداد", callback_data="contract")]
    ]

    await update.message.reply_text(
        "👋 خوش آمدی دوست من",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # contract
    if query.data == "contract":
        keyboard = [
            [
                InlineKeyboardButton("✅ قبول می‌کنم", callback_data="accept"),
                InlineKeyboardButton("❌ قبول نمی‌کنم", callback_data="reject"),
            ]
        ]

        await query.edit_message_text(
            CONTRACT_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # reject
    elif query.data == "reject":
        await query.edit_message_text("⛔ بدون پذیرش قرارداد امکان ادامه نیست")

    # accept
    elif query.data == "accept":
        user_data[uid] = {}

        keyboard = [
            [InlineKeyboardButton("1 تا 50 روز", callback_data="days_50")],
            [InlineKeyboardButton("50 تا 100 روز", callback_data="days_100")],
            [InlineKeyboardButton("100 تا 200 روز", callback_data="days_200")],
        ]

        await query.edit_message_text(
            "📅 مدت کانفیگ را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # days
    elif query.data.startswith("days_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        max_days = int(query.data.split("_")[1])

        user_data[uid]["days"] = max_days

        keyboard = [
            [InlineKeyboardButton("1GB ⚡", callback_data="size_1GB")],
            [InlineKeyboardButton("5GB ⚡", callback_data="size_5GB")],
            [InlineKeyboardButton("10GB ⚡", callback_data="size_10GB")],
        ]

        await query.edit_message_text(
            "📦 حجم را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # size + fake config result
    elif query.data.startswith("size_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        size = query.data.split("_")[1]
        data = user_data[uid]

        result = f"""
╔════════════════════╗
   ⚡ FAKE CONFIG BUILDER ⚡
╚════════════════════╝

👤 سازنده: {CREATOR}

📅 مدت: {data.get('days')} روز
📦 حجم: {size}

━━━━━━━━━━━━━━
⚠️این یک کانفیگ از طرف من امیر علی فروزان عشق من نیست
⚠️ فقط برای تو  است
━━━━━━━━━━━━━━
"""

        await query.edit_message_text(result)

# run
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
