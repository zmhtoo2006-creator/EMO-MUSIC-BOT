from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, ContextTypes

# သင့်ရဲ့ Bot အချက်အလက်များ
TOKEN = "8394007912:AAHckelw0s8mAxk87zhz1W5BBiT7ZnOU24U"
BOT_USERNAME = "emo_music_bot"
UPDATE_CHANNEL = "https://t.me/emobotupd"

# ** အရေးကြီးသည် ** - Bot နဲ့အတူပြချင်တဲ့ ပုံရဲ့ Direct URL လင့်ခ်ကို ဒီနေရာမှာ ထည့်ပါ
PHOTO_URL = "https://imgur.com/a/BXFHW8c" 

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # စာသားများ (မြန်မာ + English)
    text = (
        "EMO BOT MUSIC BOT သည် Telegram Group Chatတွင် "
        "သူငယ်ချင်းအားလုံး တူတူ သီချင်း‌နားထောင်နိုင်ရန် ပြုလုပ်ထားခြင်းဖြစ်ပါသည်။\n\n"
        "(EMO BOT MUSIC BOT is created to allow everyone to listen to music together in Telegram Group Chats.)"
    )
    
    # Bottom Inline Buttons (Add Me နှင့် Bot Update)
    keyboard = [
        [
            InlineKeyboardButton(
                "➕ Add Me", 
                url=f"https://t.me/{BOT_USERNAME}?startgroup=true"
            ),
            InlineKeyboardButton(
                "📢 Bot Update", 
                url=UPDATE_CHANNEL
            )
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)

    # /start နှိပ်လိုက်ပါက ပုံ၊ စာသားနှင့် Buttons များ အတူတူ ပို့ဆောင်ခြင်း
    await update.message.reply_photo(
        photo=PHOTO_URL,
        caption=text,
        reply_markup=reply_markup
    )

def main():
    # Bot Application စတင်တည်ဆောက်ခြင်း
    application = Application.builder().token(TOKEN).build()

    # /start command ကို လက်ခံမည့် Handler ထည့်သွင်းခြင်း
    application.add_handler(CommandHandler("start", start))

    # Bot စတင်ပတ်မောင်းခြင်း
    print("Bot is running successfully...")
    application.run_polling()

if __name__ == "__main__":
    main()