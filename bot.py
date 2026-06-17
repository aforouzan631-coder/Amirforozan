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

user_data = {}        # مراحل کاربر
configs = {}          # چند کانفیگ برای هر کاربر
generated_links = {}

# ---------------- CONTRACT ----------------
CONTRACT_TEXT = f"""
📜 قرارداد استفاده

👤 سازنده: {CREATOR}

🌹🇮🇷 این ابزار برای شما ساخته شده امیر علی فروزان‌اصل 
⚠️ مسئولیت استفاده با کاربر است
⚠️ بدون پذیرش قرارداد امکان استفاده نیست
"""

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📜 شروع ساخت کانفیگ", callback_data="start")]
    ]

    await update.message.reply_text(
        "⚡ به Config Builder Pro خوش آمدی",
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

    # accept contract (اگر خواستی اضافه کنی)
    elif query.data == "accept":
        user_data[uid] = {"step": "name"}
        configs.setdefault(uid, [])
        await query.edit_message_text("✏️ اسم کانفیگ را وارد کن")

    # days
    elif query.data.startswith("days_"):
        if uid not in user_data:
            return

        user_data[uid]["days"] = int(query.data.split("_")[1])

        keyboard = [
            [InlineKeyboardButton("1GB ⚡", callback_data="size_1GB")],
            [InlineKeyboardButton("5GB ⚡", callback_data="size_5GB")],
            [InlineKeyboardButton("10GB ⚡", callback_data="size_10GB")],
        ]

        await query.edit_message_text(
            "📦 حجم را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # size → server select
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
            [InlineKeyboardButton("🇳🇱 هلند", callback_data="srv_nl")],
        ]

        await query.edit_message_text(
            "🌍 سرور را انتخاب کن",
            reply_markup=InlineKeyboardMarkup(keyboard)
        )

    # server → finish config
    elif query.data.startswith("srv_"):
        uid_data = user_data.get(uid)
        if not uid_data:
            return

        server_map = {
            "srv_germany": "Germany 🇩🇪",
            "srv_usa": "USA 🇺🇸",
            "srv_iran": "Iran 🇮🇷",
            "srv_russia": "Russia 🇷🇺",
            "srv_india": "India 🇮🇳",
            "srv_nl": "Netherlands 🇳🇱",
        }

        server = server_map.get(query.data, "Unknown")

        fake_uuid = str(uuid.uuid4())
        name = uid_data.get("name", "Config")

        link = f"vless://{fake_uuid}@example.com:443?type=grpc#{name}"

        cfg = {
            "name": name,
            "days": uid_data.get("days"),
            "size": uid_data.get("size"),
            "server": server,
            "link": link,
        }

        configs.setdefault(uid, []).append(cfg)

        generated_links[uid] = link

        keyboard = [
            [InlineKeyboardButton("➕ ساخت کانفیگ جدید", callback_data="start")],
            [InlineKeyboardButton("📦 لیست کانفیگ‌ها", callback_data="list")]
        ]

        text = f"""
╔══════════════════════╗
   ⚡ CONFIG BUILDER PRO ⚡
╚══════════════════════╝

📝 اسم: {name}
📦 حجم: {cfg['size']}
📅 مدت: {cfg['days']}
🌍 سرور: {server}

🔗 لینک:
{link}

━━━━━━━━━━━━━━━━━━━━━━
✔ کانفیگ ذخیره شد
"""

        await query.edit_message_text(text, reply_markup=InlineKeyboardMarkup(keyboard))

    # list configs
    elif query.data == "list":
        user_cfgs = configs.get(uid, [])

        if not user_cfgs:
            await query.edit_message_text("❌ هیچ کانفیگی ساخته نشده")
            return

        text = "📦 لیست کانفیگ‌ها:\n\n"

        for i, c in enumerate(user_cfgs, 1):
            text += f"{i}. {c['name']} | {c['server']} | {c['size']} | {c['days']} روز\n"

        await query.edit_message_text(text)

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
