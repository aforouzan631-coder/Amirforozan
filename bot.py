import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

# 🔑 BOT TOKEN (حتماً باید در Railway Variables باشد)
BOT_TOKEN = os.getenv("BOT_TOKEN")

# ❗ جلوگیری از کرش اگر توکن نبود
if not BOT_TOKEN:
    raise Exception("❌ BOT_TOKEN is missing in Railway variables")

CREATOR = "امیر علی فروزان اصل"

user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده

سازنده: {CREATOR}

✔ استفاده فقط آموزشی است
✔ سوء استفاده ممنوع
✔ حداکثر مدت 30 روز
"""

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 قرارداد", callback_data="contract")]
    ]

    await update.message.reply_text(
        "👋 خوش آمدید",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTON HANDLER ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # 📜 contract
    if query.data == "contract":
        keyboard = [
            [
                InlineKeyboardButton("✅ قبول", callback_data="accept"),
                InlineKeyboardButton("❌ رد", callback_data="reject"),
            ]
        ]

        await query.edit_message_text(
            CONTRACT_TEXT,
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # ❌ reject
    elif query.data == "reject":
        await query.edit_message_text("⛔ بدون قبول قرارداد نمی‌شود ادامه داد")

    # ✅ accept
    elif query.data == "accept":
        user_data[uid] = {}

        keyboard = [
            [InlineKeyboardButton("7 روز", callback_data="days_7")],
            [InlineKeyboardButton("15 روز", callback_data="days_15")],
            [InlineKeyboardButton("30 روز", callback_data="days_30")],
        ]

        await query.edit_message_text(
            "📅 مدت را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 📅 days
    elif query.data.startswith("days_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        user_data[uid]["days"] = int(query.data.split("_")[1])

        keyboard = [
            [InlineKeyboardButton("1GB", callback_data="size_1GB")],
            [InlineKeyboardButton("5GB", callback_data="size_5GB")],
            [InlineKeyboardButton("10GB", callback_data="size_10GB")],
        ]

        await query.edit_message_text(
            "📦 حجم را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # 📦 size
    elif query.data.startswith("size_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        user_data[uid]["size"] = query.data.split("_")[1]

        data = user_data[uid]

        result = f"""
✅ کانفیگ ساخته شد

📅 مدت: {data.get('days')} روز
📦 حجم: {data.get('size')}

🧑‍💻 سازنده: {CREATOR}
"""

        await query.edit_message_text(result)

# ---------------- RUN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
