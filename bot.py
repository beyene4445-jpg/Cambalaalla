import os
import logging
from datetime import datetime
from dotenv import load_dotenv
from telegram import (
    Update, InlineKeyboardButton, InlineKeyboardMarkup,
    WebAppInfo, MenuButtonWebApp
)
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    ContextTypes, MessageHandler, filters
)
from telegram.constants import ParseMode

from database import (
    init_db, upsert_user, set_language, get_language,
    toggle_subscription, get_subscribers
)
from sidama_calendar import predict_fichee, get_sidama_calendar

load_dotenv()
BOT_TOKEN = os.getenv("BOT_TOKEN")
MINI_APP_URL = os.getenv("MINI_APP_URL")
PORT = int(os.getenv("PORT", 10000))
WEBHOOK_URL = os.getenv("WEBHOOK_URL")

logging.basicConfig(level=logging.INFO, format="%(asctime)s - %(levelname)s - %(message)s")
log = logging.getLogger(__name__)

# ---------- Text Templates ----------
TEXTS = {
    'en': {
        'welcome': (
            "🌿 *Welcome to Fichee Cambalaalla Bot!*\n\n"
            "I bring you the heritage of the *Sidama people* — their calendar, "
            "culture, and the sacred *Fichee Cambalaalla* new year celebration.\n\n"
            "━━━━━━━━━━━━━━━\n"
            "📌 *What I can do:*\n"
            "• /fichee — Learn about the festival\n"
            "• /predict — Next celebration date\n"
            "• /calendar — Sidama calendar\n"
            "• /science — Modern science link\n"
            "• /notify — Subscribe to alerts\n"
            "• /language — Change language\n"
            "• /app — Open Mini App"
        ),
        'fichee': (
            "🎉 *Fichee Cambalaalla*\n\n"
            "*Fichee Cambalaalla* is the New Year festival of the Sidama people, "
            "inscribed by *UNESCO* in 2015 as Intangible Cultural Heritage.\n\n"
            "🕊️ *Symbolism:*\n"
            "• *Fichee* = the stick (symbol of unity)\n"
            "• *Cambalaalla* = transition / renewal\n"
            "• Celebrated with *buurisame* (shared feast), songs, and dance\n\n"
            "📍 *When:* Mid-April, after the *Kore* (Pleiades) star cycle\n"
            "🏡 *Where:* Sidama Region, Ethiopia\n\n"
            "👥 *Significance:* Unity, peace, forgiveness, and new beginnings."
        ),
        'science': (
            "🔬 *Fichee & Modern Science*\n\n"
            "The Sidama ancestors used *astronomical observation* long before modern tools:\n\n"
            "⭐ *Pleiades (Kore) star cluster* — its heliacal rising marked the year's turn\n"
            "🌙 *Lunar phases* — 12–13 moon cycles defined the months\n"
            "☀️ *Solar position* — used with the star to fix the date\n\n"
            "*Modern equivalence:*\n"
            "• Pleiades = M45 in Taurus (visible to naked eye)\n"
            "• Heliacal rising ≈ when it appears just before sunrise\n"
            "• This matches modern *sidereal calendar* principles used by NASA/ESA\n\n"
            "_Conclusion:_ Sidama time-keeping is *astronomically grounded science*."
        ),
    },
    'sid': (
        'welcome': (
            "🌿 *Fichee Cambalaalla Bota!*\n\n"
            "Sidama manchi aana — loosu, qara, ninke *Fichee Cambalaalla* "
            "barru-barra kalaqu.\n\n"
            "📌 *Ani danda'u:*\n"
            "• /fichee — Fichee xa'mo\n"
            "• /predict — Aante barru qara\n"
            "• /calendar — Sidama agana\n"
            "• /science — Saayinsi xa'mo\n"
            "• /notify — Xa'mo soqqansha\n"
            "• /language — Afo woraqa\n"
            "• /app — Mini App fa'na"
        ),
        'fichee': (
            "🎉 *Fichee Cambalaalla*\n\n"
            "*Fichee Cambalaalla* Sidama manchi haaru barru. "
            "2015 EC *UNESCO* qara xa'mo.\n\n"
            "🕊️ *Mala:*\n"
            "• *Fichee* = uda (maretto)\n"
            "• *Cambalaalla* = haaru barru\n"
            "• *Buurisame*, maretto, heexo\n\n"
            "📍 *Aante:* Woxawessa (April)\n"
            "🏡 *Bota:* Sidama Kifle"
        ),
        'science': (
            "🔬 *Fichee & Saayinsi*\n\n"
            "Sidama aayyooti *saayinsi* xa'mo aana loossi:\n\n"
            "⭐ *Kore* (Pleiades) — bari qara mulu\n"
            "🌙 *Agana* — 12–13 adha'a\n"
            "☀️ *Awa* — qara loosu\n\n"
            "Ka *NASA*, *ESA* loosansi ledo muli."
        ),
    }
}

def t(chat_id: int, key: str) -> str:
    lang = get_language(chat_id)
    return TEXTS.get(lang, TEXTS['en']).get(key, TEXTS['en'][key])

# ---------- Handlers ----------
async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    upsert_user(user.id, user.username or "")
    keyboard = [[InlineKeyboardButton("🌿 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]]
    await update.message.reply_text(
        t(user.id, 'welcome'),
        parse_mode=ParseMode.MARKDOWN,
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cmd_fichee(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        t(update.effective_chat.id, 'fichee'),
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_science(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        t(update.effective_chat.id, 'science'),
        parse_mode=ParseMode.MARKDOWN
    )

async def cmd_predict(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    p = predict_fichee(datetime.now().year)
    msg = (
        f"🔮 *Fichee Cambalaalla Prediction*\n\n"
        f"📅 *Gregorian:* {p['gregorian']}\n"
        f"🇪🇹 *Ethiopian:* {p['ethiopian']}\n"
        f"🌾 *Sidama Month:* {p['sidama_month']}\n"
        f"⏳ *Days left:* {p['days_left']} days\n\n"
        f"_Based on Kore (Pleiades) cycle + lunar calculation_"
    )
    await update.message.reply_text(msg, parse_mode=ParseMode.MARKDOWN)

async def cmd_calendar(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    cal = get_sidama_calendar()
    lines = ["📜 *Sidama Calendar*\n"]
    for m in cal:
        lines.append(f"• *{m['sidama']}* → {m['gregorian']} — _{m['meaning']}_")
    await update.message.reply_text("\n".join(lines), parse_mode=ParseMode.MARKDOWN)

async def cmd_notify(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    chat_id = update.effective_chat.id
    subscribed = toggle_subscription(chat_id)
    if subscribed:
        await update.message.reply_text("✅ Subscribed! You'll receive Fichee updates.")
    else:
        await update.message.reply_text("🔕 Unsubscribed.")

async def cmd_language(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [
        [InlineKeyboardButton("🇬🇧 English", callback_data="lang_en")],
        [InlineKeyboardButton("🇪🇹 Sidaamu Afoo", callback_data="lang_sid")]
    ]
    await update.message.reply_text(
        "Choose language / Afo woraqa:",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def cmd_app(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("🌿 Open Mini App", web_app=WebAppInfo(url=MINI_APP_URL))]]
    await update.message.reply_text("Tap to open:", reply_markup=InlineKeyboardMarkup(keyboard))

async def on_callback(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    data = q.data
    chat_id = q.message.chat.id
    if data.startswith("lang_"):
        lang = data.split("_")[1]
        set_language(chat_id, lang)
        await q.edit_message_text(
            "✅ Language updated." if lang == 'en' else "✅ Afo woraqantino."
        )

# ---------- Daily Reminder Job ----------
async def daily_reminder(ctx: ContextTypes.DEFAULT_TYPE):
    p = predict_fichee(datetime.now().year)
    if p['days_left'] in (30, 14, 7, 3, 1, 0):
        subs = get_subscribers()
        msg = (
            f"🔔 *Fichee Countdown*\n"
            f"⏳ Only *{p['days_left']}* days until Fichee Cambalaalla!\n"
            f"📅 {p['gregorian']}"
        )
        for cid in subs:
            try:
                await ctx.bot.send_message(cid, msg, parse_mode=ParseMode.MARKDOWN)
            except Exception as e:
                log.warning(f"Failed {cid}: {e}")

# ---------- Main ----------
def main():
    init_db()
    app = Application.builder().token(BOT_TOKEN).build()

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("fichee", cmd_fichee))
    app.add_handler(CommandHandler("science", cmd_science))
    app.add_handler(CommandHandler("predict", cmd_predict))
    app.add_handler(CommandHandler("calendar", cmd_calendar))
    app.add_handler(CommandHandler("notify", cmd_notify))
    app.add_handler(CommandHandler("language", cmd_language))
    app.add_handler(CommandHandler("app", cmd_app))
    app.add_handler(CallbackQueryHandler(on_callback))

    # Daily reminder at 08:00 UTC
    app.job_queue.run_daily(daily_reminder, time=datetime.strptime("08:00", "%H:%M").time())

    log.info("Bot starting (webhook mode)...")
    app.run_webhook(
        listen="0.0.0.0",
        port=PORT,
        url_path=BOT_TOKEN,
        webhook_url=f"{WEBHOOK_URL}/{BOT_TOKEN}",
        drop_pending_updates=True
    )

if __name__ == "__main__":
    main()
