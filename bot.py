import logging
import os
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# ─── SOZLAMALAR ───
BOT_TOKEN = os.environ.get("BOT_TOKEN", "BU_YERGA_BOT_TOKENINGIZNI_KIRITING")
SITE_URL = "https://mr-ilyosbek98.github.io/dona-website/dona_website.html"
BUTTON_TEXT = "🛒 Buyurtma berish"

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO
)
logger = logging.getLogger(__name__)

async def handle_channel_post(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Kanalga yangi post kelganda avtomatik tugma qo'shadi"""
    post = update.channel_post
    if not post:
        return

    # Tugma yaratish
    keyboard = InlineKeyboardMarkup([
        [InlineKeyboardButton(BUTTON_TEXT, url=SITE_URL)]
    ])

    try:
        # Postga tugma qo'shish (edit)
        if post.text:
            await context.bot.edit_message_reply_markup(
                chat_id=post.chat_id,
                message_id=post.message_id,
                reply_markup=keyboard
            )
        elif post.photo or post.video or post.document:
            await context.bot.edit_message_reply_markup(
                chat_id=post.chat_id,
                message_id=post.message_id,
                reply_markup=keyboard
            )
        logger.info(f"Tugma qo'shildi: {post.chat.title} - {post.message_id}")
    except Exception as e:
        logger.error(f"Xatolik: {e}")

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.ChatType.CHANNEL, handle_channel_post))
    logger.info("Bot ishga tushdi...")
    app.run_polling(allowed_updates=["channel_post"])

if __name__ == "__main__":
    main()
