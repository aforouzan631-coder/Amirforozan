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
configs = {}
generated_links = {}

# ---------------- CONTRACT ----------------
CONTRACT_TEXT = f"""
📜 قرارداد استفاده

👤 سازنده: {CREATOR}

⚠️ اگر قبول نکنید امکان استفاده ندارید
⚠️ مسئولیت استفاده با کاربر است
⚠️ این ابزار فقط نمایشی است
"""

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 شروع ساخت کانفیگ", callback_data="start")]
    ]

    await update.message.reply_text(
        "⚡ Config Builder Pro",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

# ---------------- BUTTONS ----------------
async def button(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    uid = query.from_user.id

    # start
    if query.data == "start":
        user_data[uid] = {"step": "name"}
        configs.setdefault(uid, [])
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

    # size → server
    elif query.data.startswith("size_"):
        if uid not in user_data:
            return

        user_data[uid]["size"] = query.data.split("_")[1]

        keyboard = [
            [InlineKeyboardButton("🇩🇪 آلمان", callback_data="srv_de")],
            [InlineKeyboardButton("🇺🇸 آمریکا", callback_data="srv_us")],
            [InlineKeyboardButton("🇮🇷 ایران", callback_data="srv_ir")],
            [InlineKeyboardButton("🇷🇺 روسیه", callback_data="srv_ru")],
            [InlineKeyboardButton("🇮🇳 هند", callback_data="srv_in")],
        ]

        await query.edit_message_text(
            "🌍 سرور را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # server → final
    elif query.data.startswith("srv_"):
        data = user_data.get(uid)
        if not data:
            return

        server_map = {
            "srv_de": "Germany 🇩🇪",
            "srv_us": "USA 🇺🇸",
            "srv_ir": "Iran 🇮🇷",
            "srv_ru": "Russia 🇷🇺",
            "srv_in": "India 🇮🇳",
        }

        server = server_map.get(query.data, "Unknown")

        name = data.get("name", "Config")
        fake_uuid = str(uuid.uuid4())

        link = f"vless://{fake_uuid}@example.com:443?type=grpc#{name}"

        configs.setdefault(uid, []).append({
            "name": name,
            "days": data.get("days"),
            "size": data.get("size"),
            "server": server,
            "link": link
        })

        generated_links[uid] = link

        keyboard = [
            [InlineKeyboardButton("📋 کپی لینک", callback_data="copy")],
            [InlineKeyboardButton("➕ ساخت کانفیگ جدید", callback_data="start")]
        ]

        text = f"""
╔══════════════════════╗
   ⚡ CONFIG BUILDER PRO ⚡
╚══════════════════════╝

👤 سازنده: {CREATOR}

📝 اسم: {name}
📦 حجم: {data.get('size')}
📅 مدت: {data.get('days')}
🌍 سرور: {server}

🔗 لینک:
{link}

━━━━━━━━━━━━━━━━━━━━━━
✔ کانفیگ ساخته شد
"""

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # copy link
    elif query.data == "copy":
        link = generated_links.get(uid)

        if not link:
            await query.edit_message_text("❌ لینکی وجود ندارد")
            return

        await query.message.reply_text(
            f"📋 لینک برای کپی 👇\n\n{link}\n\n(روی متن نگه دار و Copy کن)"
        )

# ---------------- TEXT ----------------
async def handle_text(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.message.from_user.id
    text = update.message.text

    if uid not in user_data:
        user_data[uid] = {"step": "name"}

    data = user_data[uid]

    if data.get("step") == "name":
        data["name"] = text
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

# ---------------- RUN ----------------
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(button))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
