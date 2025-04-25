import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import (
    Application, CommandHandler, ContextTypes,
    MessageHandler, CallbackQueryHandler, filters
)

# --- CONFIG ---
TOKEN = "7087006196:AAFMy-IOoukvXBwsQpjmIYqt4VJa5NM1TtQ"
ADMIN_ID = 6584561020  # Replace with your actual admin ID
PAID_USERS_FILE = "paid_users.txt"

# --- LOGGING ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)

# --- UTIL FUNCTIONS ---
def load_paid_users():
    try:
        with open(PAID_USERS_FILE, "r") as f:
            return [int(line.strip()) for line in f if line.strip()]
    except FileNotFoundError:
        return []

def save_paid_user(user_id):
    users = load_paid_users()
    if user_id not in users:
        with open(PAID_USERS_FILE, "a") as f:
            f.write(f"{user_id}\n")

def remove_paid_user(user_id):
    users = load_paid_users()
    users = [uid for uid in users if uid != user_id]
    with open(PAID_USERS_FILE, "w") as f:
        for uid in users:
            f.write(f"{uid}\n")

# --- HANDLERS ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("📞 Get Help", url="https://t.me/liileetg")],
        [InlineKeyboardButton("📷 Send Screenshot", url="https://t.me/liileeadmin")],
        [InlineKeyboardButton("💸 Refer and Earn", url="http://t.me/SIGNALSCOPE_BOT")]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    welcome_message = (
        "👋 Welcome to *Liilee Trade*!\n\n"
        "This is your source for high-profit signals. 💰\n"
        "You’ll enjoy making money with us—stay alert! We don’t have specific times for trades; "
        "once a signal is ready, you’ll receive it instantly.\n\n"
        "_We don't gramb, we trade confidently!_"
    )
    await update.message.reply_text(welcome_message, reply_markup=reply_markup, parse_mode="Markdown")

async def add_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /adduser user_id")
        return
    user_id = int(context.args[0])
    save_paid_user(user_id)
    await update.message.reply_text(f"✅ Added user ID {user_id} to the paid users list.")

async def remove_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /removeuser user_id")
        return
    user_id = int(context.args[0])
    remove_paid_user(user_id)
    await update.message.reply_text(f"❌ Removed user ID {user_id} from the paid users list.")

async def send_signal(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /signal your signal message here")
        return

    message = "📢 *Signal Update:*\n" + " ".join(context.args)
    paid_users = load_paid_users()
    sent = 0

    for user_id in paid_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message, parse_mode="Markdown")
            sent += 1
        except Exception as e:
            logging.error(f"❌ Error sending to {user_id}: {e}")

    await update.message.reply_text(f"✅ Signal sent to {sent} user(s).")

async def send_message_all(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if not context.args:
        await update.message.reply_text("Usage: /messageall your message here")
        return

    message = " ".join(context.args)
    paid_users = load_paid_users()
    sent = 0

    for user_id in paid_users:
        try:
            await context.bot.send_message(chat_id=user_id, text=message)
            sent += 1
        except Exception as e:
            logging.error(f"❌ Error sending to {user_id}: {e}")

    await update.message.reply_text(f"✅ Message sent to {sent} user(s).")

async def send_user(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    if len(context.args) < 2:
        await update.message.reply_text("Usage: /senduser user_id message here")
        return

    user_id = int(context.args[0])
    message = " ".join(context.args[1:])
    try:
        await context.bot.send_message(chat_id=user_id, text=message)
        await update.message.reply_text(f"✅ Message sent to user {user_id}.")
    except Exception as e:
        logging.error(f"❌ Failed to send message to {user_id}: {e}")
        await update.message.reply_text(f"❌ Failed to send message to {user_id}.")

async def show_paid_users(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.effective_user.id != ADMIN_ID:
        return
    users = load_paid_users()
    if not users:
        await update.message.reply_text("ℹ️ No users in the paid list.")
        return
    user_list = "\n".join([f"👤 {uid}" for uid in users])
    await update.message.reply_text(f"📋 Paid Users:\n{user_list}")

# --- MAIN ---
def main():
    print("🚀 Bot is starting...")

    app = Application.builder().token(TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("adduser", add_user))
    app.add_handler(CommandHandler("removeuser", remove_user))
    app.add_handler(CommandHandler("signal", send_signal))           # 📢 Signal with title
    app.add_handler(CommandHandler("messageall", send_message_all))  # ✉️ Message with no title
    app.add_handler(CommandHandler("senduser", send_user))           # 📩 Message to one user
    app.add_handler(CommandHandler("paidusers", show_paid_users))    # 👥 Show paid users

    app.run_polling()

if __name__ == "__main__":
    main()
