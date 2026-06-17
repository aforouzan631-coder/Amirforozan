import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ContextTypes,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing in Railway variables")

CREATOR = "امیر علی فروزان اصل"
user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده

👤 سازنده: {CREATOR}

⚠️ این ابزار فقط نمایشی است
⚠️ هیچ سرویس واقعی ارائه نمی‌دهد
⚠️ مسئولیت استفاده با کاربر است
"""

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 قرارداد", callback_data="contract")]
    ]

    await update.message.reply_text(
        "👋 خوش آمدی به کانفیگ ساز نمایشی",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # contract
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

    # reject
    elif query.data == "reject":
        await query.edit_message_text("⛔ بدون قبول قرارداد نمی‌توان ادامه داد")

    # accept
    elif query.data == "accept":
        user_data[uid] = {}

        keyboard = [
            [InlineKeyboardButton("1-50 روز", callback_data="days_50")],
            [InlineKeyboardButton("51-100 روز", callback_data="days_100")],
            [InlineKeyboardButton("101-200 روز", callback_data="days_200")],
        ]

        await query.edit_message_text(
            "📅 مدت را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # days
    elif query.data.startswith("days_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        days = int(query.data.split("_")[1])
        user_data[uid]["days"] = days

        keyboard = [
            [InlineKeyboardButton("1GB ⚡", callback_data="size_1GB")],
            [InlineKeyboardButton("5GB ⚡", callback_data="size_5GB")],
            [InlineKeyboardButton("10GB ⚡", callback_data="size_10GB")],
        ]

        await query.edit_message_text(
            "📦 حجم را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # size + generate fake VLESS
    elif query.data.startswith("size_"):
        if uid not in user_data:
            await query.edit_message_text("❌ اول قرارداد را قبول کن")
            return

        size = query.data.split("_")[1]
        data = user_data[uid]

        fake_uuid = str(uuid.uuid4())

        fake_link = f"vless://{fake_uuid}@example.com:443?type=grpc&security=none&encryption=none#{CREATOR.replace(' ', '-')}"

        result = f"""
╔══════════════════════╗
   ⚡ CONFIG BUILDER ⚡
╚══════════════════════╝

👤 سازنده: {CREATOR}

📅 مدت: {data.get('days')} روز
📦 حجم: {size}

🔗 لینک نمایشی:
{fake_link}

━━━━━━━━━━━━━━━━━━━━━━
🌹این از طرف من برای شما امیر علی فروزان برای نمایشاه
🇮🇷 این کافینگ و این ربات ها برای شما ساخته شده 
━━━━━━━━━━━━━━━━━━━━━━
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
