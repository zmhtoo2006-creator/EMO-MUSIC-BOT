import logging
import sqlite3
import asyncio
from datetime import datetime, timedelta
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, Chat
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

# Logging setup
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# Database Name
DB_NAME = "telegram_games.db"

# Database Initialization
def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS game_logs (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER,
            username TEXT,
            full_name TEXT,
            game TEXT,
            score INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    conn.close()

# Save Score to Database
def save_score(user_id, username, full_name, game, score):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO game_logs (user_id, username, full_name, game, score, timestamp)
        VALUES (?, ?, ?, ?, ?, datetime('now', 'localtime'))
    ''', (user_id, username, full_name, game, score))
    conn.commit()
    conn.close()

# /start Command Handler (Private Chat & Inline Keyboards)
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    chat = update.effective_chat
    user = update.effective_user

    # Private Chat တွင်သာမကဘဲ အခြားနေရာများပါ အလုပ်လုပ်နိုင်ရန် စီစဉ်ထားသည်
    welcome_caption = (
        f"👋 မင်္ဂလာပါ **{user.full_name}**!\n\n"
        "🎮 ဒီ Bot ကတော့ Telegram Group Chat တွေမှာ Emoji ဂိမ်းတွေဆော့ပြီး "
        "အမှတ်ပြိုင်ဆိုင်နိုင်မယ့် Game Bot တစ်ခု ဖြစ်ပါတယ်။\n\n"
        "✨ **ရရှိနိုင်တဲ့ ဂိမ်းအမျိုးအစားများ:**\n"
        "🎲 `/dice` - အန်စာတုံး\n"
        "🎯 `/dart` - မြားပစ်\n"
        "🏀 `/basket` - ဘတ်စကက်ဘော\n"
        "⚽ `/football` - ဘောလုံးကန်\n"
        "🎳 `/bowling` - ဘိုးလင်း\n"
        "🎰 `/slot` - စလော့မက်ရှင်\n\n"
        "🏆 `/leaderboard` - နောက်ဆုံး ၁ နာရီအတွင်း Top 5 အမှတ်စာရင်းကြည့်ရန်"
    )

    # Inline Keyboards (Bot Username နေရာတွင် မိမိ Bot ၏ Username ကို ထည့်ပါ - @ မပါရ)
    BOT_USERNAME = "gplayer0_bot" 
    CHANNEL_URL = "https://t.me/emobotupd"

    keyboard = [
        [
            InlineKeyboardButton("➕ Add Me to Group", url=f"https://t.me/{BOT_USERNAME}?startgroup=true")
        ],
        [
            InlineKeyboardButton("📢 Bot Updates Channel", url=CHANNEL_URL)
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # Sample Image URL for reply_photo (Placeholder image)
    photo_url = "https://imgur.com/a/aGg3mvm"

    try:
        await update.message.reply_photo(
            photo=photo_url,
            caption=welcome_caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )
    except Exception as e:
        # ပုံလွှင့်မရပါက စာသားသက်သက် ပို့ပေးမည်
        await update.message.reply_text(
            welcome_caption,
            reply_markup=reply_markup,
            parse_mode="Markdown"
        )

# Generic Game Handler function (with 4 seconds wait for animation)
async def play_game(update: Update, context: ContextTypes.DEFAULT_TYPE, emoji: str, game_name: str):
    chat = update.effective_chat
    user = update.effective_user

    # Group Chat ဖြစ်မှသာ ဂိမ်းဆော့ခွင့်ပြုရန် စစ်ဆေးလိုပါက ဤနေရာတွင် စစ်နိုင်သည် (သို့မဟုတ် အားလုံးတွင် သုံးခွင့်ပေးသည်)
    # Send Animated Emoji Game
    message = await context.bot.send_dice(chat_id=chat.id, emoji=emoji)
    
    # Wait for 4 seconds to let the animation fully complete
    await asyncio.sleep(4)

    # Get score after animation ends
    score = message.dice.value

    # Prepare user details
    username = user.username if user.username else "NoUsername"
    full_name = user.full_name if user.full_name else "Player"

    # Save score to database
    save_score(user.id, username, full_name, game_name, score)

    # Reply with score notification after 4 seconds
    await update.message.reply_text(
        f"👤 **{full_name}** က {game_name} ({emoji}) ဆော့လို့ "
        f"🎯 **{score}** မှတ် ရရှိသွားပါတယ်!",
        parse_mode="Markdown"
    )

# Individual Game Commands
async def dice_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "🎲", "Dice")

async def dart_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "🎯", "Dart")

async def basket_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "🏀", "Basketball")

async def football_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "⚽", "Football")

async def bowling_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "🎳", "Bowling")

async def slot_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await play_game(update, context, "🎰", "Slot Machine")

# /leaderboard Command Handler (Last 1 Hour Window with Medals)
async def leaderboard_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    
    # Calculate timestamp for 1 hour ago
    one_hour_ago = (datetime.now() - timedelta(hours=1)).strftime('%Y-%m-%d %H:%M:%S')

    # Query to sum total score per user within the last 1 hour
    cursor.execute('''
        SELECT full_name, username, SUM(score) as total_score
        FROM game_logs
        WHERE timestamp >= ?
        GROUP BY user_id
        ORDER BY total_score DESC
        LIMIT 5
    ''', (one_hour_ago,))
    rows = cursor.fetchall()
    conn.close()

    if not rows:
        await update.message.reply_text(
            "📊 နောက်ဆုံး ၁ နာရီအတွင်း ဆော့ကစားထားသော အမှတ်စာရင်း မရှိသေးပါ။ "
            "ဂိမ်းစတင်ဆော့ကစားပြီး အမှတ်ဝင်ယူနိုင်ပါတယ်!"
        )
        return

    text = "🏆 **နောက်ဆုံး (၁) နာရီအတွင်း Top 5 Leaderboard** 🏆\n🕒 *(၁ နာရီခြား တစ်ခါ အမှတ်အသစ် ပြန်စသည်)*\n\n"
    medals = ["🥇", "🥈", "🥉", "4️⃣", "5️⃣"]

    for idx, row in enumerate(rows):
        full_name, username, total_score = row
        medal = medals[idx] if idx < len(medals) else f"{idx+1}."
        display_name = f"{full_name} (@{username})" if username != "NoUsername" else full_name
        text += f"{medal} **{display_name}** — ` {total_score} ` မှတ်\n"

    await update.message.reply_text(text, parse_mode="Markdown")

def main():
    # Initialize SQLite Database
    init_db()

    # Telegram Bot Token (BotFather ထံမှ ရရှိသော Token ကို ထည့်ပါ)
    TOKEN = "9142685867:AAHX6w57D1D2eYP4nP6ji3wCG6iD1QfVAec"

    # Build Application (python-telegram-bot v20+)
    application = ApplicationBuilder().token(TOKEN).build()

    # Register Handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("dice", dice_command))
    application.add_handler(CommandHandler("dart", dart_command))
    application.add_handler(CommandHandler("basket", basket_command))
    application.add_handler(CommandHandler("football", football_command))
    application.add_handler(CommandHandler("bowling", bowling_command))
    application.add_handler(CommandHandler("slot", slot_command))
    application.add_handler(CommandHandler("leaderboard", leaderboard_command))

    print("🤖 Telegram Game Bot အောင်မြင်စွာ စတင်အလုပ်လုပ်နေပါပြီ...")
    
    # Run the bot
    application.run_polling()

if __name__ == "__main__":
    main()