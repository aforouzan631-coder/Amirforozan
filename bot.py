import os
import uuid
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

BOT_TOKEN = os.getenv("BOT_TOKEN")

if not BOT_TOKEN:
    raise Exception("BOT_TOKEN is missing")

CREATOR = "امیر علی فروزان اصل"
user_data = {}

CONTRACT_TEXT = f"""
📜 قرارداد استفاده

👤 سازنده: {CREATOR}

 مسؤلیت استفاده نادرست خود شما هستید لطفا استفاده  نادرست نکنید 🌹⚠️
🇮🇷به ربات ساز کافینگ امیر علی خوش آمدید 
"""

# /start
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 شروع", callback_data="start_flow")]
    ]

    await update.message.reply_text(
        "👋 خوش آمدی به کانفیگ ساز",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# buttons
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # start flow
    if query.data == "start_flow":
        user_data[uid] = {"step": "name"}

        await query.edit_message_text("✏️ اسم کانفیگ را وارد کن")

    # days
    elif query.data.startswith("days_"):
        if uid not in user_data:
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

    # size → server selection
    elif query.data.startswith("size_"):
        if uid not in user_data:
            return

        user_data[uid]["size"] = query.data.split("_")[1]

        keyboard = [
            [InlineKeyboardButton("🇩🇪 آلمان", callback_data="srv_germany")],
            [InlineKeyboardButton("🇺🇸 آمریکا", callback_data="srv_usa")],
            [InlineKeyboardButton("🇮🇷 ایران", callback_data="srv_iran")],
            [InlineKeyboardButton("🇷🇺 روسیه", callback_data="srv_russia")],
            [InlineKeyboardButton("🇮🇳 هند", callback_data="srv_india")],
            [InlineKeyboardButton("🇳🇱 هلند", callback_data="srv_netherlands")],
        ]

        await query.edit_message_text(
            "🌍 سرور را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # server → final
    elif query.data.startswith("srv_"):
        if uid not in user_data:
            return

        server_map = {
            "srv_germany": "Germany 🇩🇪",
            "srv_usa": "USA 🇺🇸",
            "srv_iran": "Iran 🇮🇷",
            "srv_russia": "Russia 🇷🇺",
            "srv_india": "India 🇮🇳",
            "srv_netherlands": "Netherlands 🇳🇱",
        }

        server = server_map.get(query.data, "Unknown")
        data = user_data[uid]

        fake_uuid = str(uuid.uuid4())

        name = data.get("name", "Config")

        vless = f"vless://{fake_uuid}@example.com:443?type=grpc#{name}"

        result = f"""
╔══════════════════════╗
   ⚡ CONFIG BUILDER ⚡
╚══════════════════════╝

👤 سازنده: {CREATOR}

📝 اسم: {name}
📦 حجم: {data.get('size')}
📅 مدت: {data.get('days')}
🌍 سرور: {server}

🔗 لینک:
{vless}

 《از طرف من به شما《امیر علی فروزان🌹🇮🇷
"""

        await query.edit_message_text(result)

# text handler
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id

    if uid not in user_data:
        user_data[uid] = {"step": "name"}

    data = user_data[uid]

    # name step
    if data.get("step") == "name":
        data["name"] = update.message.text
        data["step"] = "days"

        keyboard = [
            [InlineKeyboardButton("1-50 روز", callback_data="days_50")],
            [InlineKeyboardButton("51-100 روز", callback_data="days_100")],
            [InlineKeyboardButton("101-200 روز", callback_data="days_200")],
        ]

        await update.message.reply_text(
            "📅 مدت را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

# run
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    app.run_polling()

if __name__ == "__main__":
    main()
