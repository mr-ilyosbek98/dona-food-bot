#!/usr/bin/env python3
"""
DONA UZBEK FROZEN FOOD - Telegram Bot v2
python-telegram-bot 21.x uchun
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler
from datetime import datetime

BOT_TOKEN = "8944732139:AAF9TFV3sbtfVCls-6JdqIkiK8T0WD-3_lo"
ADMIN_CHAT_ID = 961419057

PRODUCTS = {
    "manti":      {"uz": "🥟 Manti",      "ru": "🥟 Манты",       "ko": "🥟 만티",     "price": 10000},
    "somsa":      {"uz": "🥐 Somsa",      "ru": "🥐 Самса",       "ko": "🥐 삼사",     "price": 10000},
    "kotlet":     {"uz": "🍖 Kotlet",     "ru": "🍖 Котлеты",     "ko": "🍖 커틀릿",   "price": 10000},
    "blinchik":   {"uz": "🌯 Blinchik",   "ru": "🌯 Блинчики",    "ko": "🌯 블린치크", "price": 10000},
    "varenik":    {"uz": "🥟 Varenik",    "ru": "🥟 Вареники",    "ko": "🥟 바레닉",   "price": 10000},
    "honim":      {"uz": "🫔 Honim",      "ru": "🫔 Хоним",       "ko": "🫔 호님",     "price": 10000},
    "frikadelka": {"uz": "🍡 Frikadelka", "ru": "🍡 Фрикадельки", "ko": "🍡 미트볼",   "price": 10000},
}

TEXTS = {
    "uz": {
        "welcome": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b>ga xush kelibsiz!\n\nMuzlatilgan o'zbek milliy taomlari ❄️",
        "menu": "📋 Mahsulot tanlang:",
        "cart": "🛒 Savatcha",
        "cart_empty": "🛒 Savatcha bo'sh",
        "total": "💰 Jami",
        "order_btn": "✅ Buyurtma berish",
        "clear": "🗑️ Tozalash",
        "back": "⬅️ Ortga",
        "enter_name": "👤 Ismingizni yozing:",
        "enter_phone": "📱 Telefon raqamingizni yuboring:",
        "enter_address": "📍 Manzilingizni yozing:",
        "confirmed": "✅ <b>Buyurtmangiz qabul qilindi!</b>\nTez orada bog'lanamiz. Rahmat! 🙏",
        "contact": "📞 <b>Aloqa:</b>\nTelegram: @mr_yigitaliev\n🚚 Butun Koreya",
        "share_phone": "📱 Raqamni yuborish",
    },
    "ru": {
        "welcome": "🇺🇿 Добро пожаловать в <b>DONA UZBEK FROZEN FOOD</b>!\n\nЗамороженные узбекские блюда ❄️",
        "menu": "📋 Выберите продукт:",
        "cart": "🛒 Корзина",
        "cart_empty": "🛒 Корзина пуста",
        "total": "💰 Итого",
        "order_btn": "✅ Оформить заказ",
        "clear": "🗑️ Очистить",
        "back": "⬅️ Назад",
        "enter_name": "👤 Введите ваше имя:",
        "enter_phone": "📱 Отправьте номер телефона:",
        "enter_address": "📍 Введите ваш адрес:",
        "confirmed": "✅ <b>Заказ принят!</b>\nСвяжемся с вами. Спасибо! 🙏",
        "contact": "📞 <b>Контакты:</b>\nTelegram: @mr_yigitaliev\n🚚 По всей Корее",
        "share_phone": "📱 Отправить номер",
    },
    "ko": {
        "welcome": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b>에 오신 것을 환영합니다!\n\n냉동 우즈베크 음식 ❄️",
        "menu": "📋 제품을 선택하세요:",
        "cart": "🛒 장바구니",
        "cart_empty": "🛒 장바구니 비어 있음",
        "total": "💰 합계",
        "order_btn": "✅ 주문하기",
        "clear": "🗑️ 비우기",
        "back": "⬅️ 뒤로",
        "enter_name": "👤 이름을 입력하세요:",
        "enter_phone": "📱 전화번호를 보내주세요:",
        "enter_address": "📍 주소를 입력하세요:",
        "confirmed": "✅ <b>주문 접수!</b>\n곧 연락드립니다. 감사합니다! 🙏",
        "contact": "📞 <b>연락처:</b>\nTelegram: @mr_yigitaliev\n🚚 한국 전국",
        "share_phone": "📱 번호 보내기",
    }
}

LANG, MENU, CART, NAME, PHONE, ADDRESS = range(6)

logging.basicConfig(level=logging.INFO)

def T(ctx, key):
    return TEXTS[ctx.user_data.get("lang","uz")][key]

def get_cart(ctx):
    return ctx.user_data.setdefault("cart", {})

def cart_total(cart):
    return sum(PRODUCTS[k]["price"] * v for k, v in cart.items() if k in PRODUCTS)

def format_cart(cart, lang):
    lines = []
    for k, v in cart.items():
        if k in PRODUCTS:
            lines.append(f"{PRODUCTS[k][lang]} x{v} = {PRODUCTS[k]['price']*v:,} won")
    return "\n".join(lines)

def lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский", callback_data="lang_ru")],
        [InlineKeyboardButton("🇰🇷 한국어", callback_data="lang_ko")],
    ])

def main_kb(lang):
    T = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Menyu / Меню / 메뉴", callback_data="menu")],
        [InlineKeyboardButton(T["cart"], callback_data="cart"),
         InlineKeyboardButton(T["order_btn"], callback_data="checkout")],
        [InlineKeyboardButton(T["contact"], callback_data="contact")],
        [InlineKeyboardButton("🌐 Til / Язык / 언어", callback_data="change_lang")],
    ])

def products_kb(lang, cart):
    T = TEXTS[lang]
    rows = []
    for k, p in PRODUCTS.items():
        qty = cart.get(k, 0)
        label = f"{p[lang]} — {p['price']:,} won" + (f" ✅x{qty}" if qty else "")
        rows.append([InlineKeyboardButton(label, callback_data=f"add_{k}")])
    rows.append([
        InlineKeyboardButton(T["cart"], callback_data="cart"),
        InlineKeyboardButton(T["back"], callback_data="main"),
    ])
    return InlineKeyboardMarkup(rows)

def cart_kb(lang):
    T = TEXTS[lang]
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(T["order_btn"], callback_data="checkout")],
        [InlineKeyboardButton(T["clear"], callback_data="clear_cart")],
        [InlineKeyboardButton(T["back"], callback_data="menu")],
    ])

async def start(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык / 언어 선택:",
        reply_markup=lang_kb()
    )
    return LANG

async def lang_chosen(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = q.data.split("_")[1]
    ctx.user_data["lang"] = lang
    await q.edit_message_text(
        TEXTS[lang]["welcome"], parse_mode="HTML",
        reply_markup=main_kb(lang)
    )
    return MENU

async def show_main(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang","uz")
    await q.edit_message_text(
        TEXTS[lang]["welcome"], parse_mode="HTML",
        reply_markup=main_kb(lang)
    )
    return MENU

async def show_menu(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang","uz")
    cart = get_cart(ctx)
    await q.edit_message_text(
        TEXTS[lang]["menu"], parse_mode="HTML",
        reply_markup=products_kb(lang, cart)
    )
    return MENU

async def add_item(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    key = q.data.replace("add_","")
    cart = get_cart(ctx)
    if key in PRODUCTS:
        cart[key] = cart.get(key, 0) + 1
    lang = ctx.user_data.get("lang","uz")
    await q.edit_message_text(
        TEXTS[lang]["menu"], parse_mode="HTML",
        reply_markup=products_kb(lang, cart)
    )
    return MENU

async def show_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang","uz")
    cart = get_cart(ctx)
    if not cart:
        await q.edit_message_text(
            TEXTS[lang]["cart_empty"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(TEXTS[lang]["back"], callback_data="menu")
            ]])
        )
        return MENU
    items = format_cart(cart, lang)
    total = cart_total(cart)
    await q.edit_message_text(
        f"{TEXTS[lang]['cart']}\n\n{items}\n\n{TEXTS[lang]['total']}: <b>{total:,} won</b>",
        parse_mode="HTML", reply_markup=cart_kb(lang)
    )
    return CART

async def clear_cart(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    ctx.user_data["cart"] = {}
    lang = ctx.user_data.get("lang","uz")
    await q.edit_message_text(
        TEXTS[lang]["cart_empty"],
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(TEXTS[lang]["back"], callback_data="menu")
        ]])
    )
    return MENU

async def checkout(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang","uz")
    cart = get_cart(ctx)
    if not cart:
        await q.edit_message_text(TEXTS[lang]["cart_empty"])
        return MENU
    await q.edit_message_text(TEXTS[lang]["enter_name"], parse_mode="HTML")
    return NAME

async def get_name(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = update.message.text
    lang = ctx.user_data.get("lang","uz")
    kb = ReplyKeyboardMarkup(
        [[KeyboardButton(TEXTS[lang]["share_phone"], request_contact=True)]],
        one_time_keyboard=True, resize_keyboard=True
    )
    await update.message.reply_text(TEXTS[lang]["enter_phone"], reply_markup=kb)
    return PHONE

async def get_phone(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang","uz")
    ctx.user_data["phone"] = update.message.contact.phone_number if update.message.contact else update.message.text
    await update.message.reply_text(TEXTS[lang]["enter_address"], reply_markup=ReplyKeyboardRemove())
    return ADDRESS

async def get_address(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    lang = ctx.user_data.get("lang","uz")
    ctx.user_data["address"] = update.message.text
    cart = get_cart(ctx)
    total = cart_total(cart)
    items = format_cart(cart, lang)
    oid = datetime.now().strftime("%d%m%H%M")

    await update.message.reply_text(
        TEXTS[lang]["confirmed"], parse_mode="HTML"
    )

    admin_msg = (
        f"🆕 <b>BUYURTMA #{oid}</b>\n"
        f"👤 {ctx.user_data.get('name')}\n"
        f"📱 {ctx.user_data.get('phone')}\n"
        f"📍 {ctx.user_data.get('address')}\n"
        f"🌐 {lang.upper()}\n\n"
        f"🛒 {items}\n\n"
        f"💰 <b>{total:,} won</b>\n"
        f"⏰ {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await ctx.bot.send_message(chat_id=ADMIN_CHAT_ID, text=admin_msg, parse_mode="HTML")

    ctx.user_data["cart"] = {}
    await update.message.reply_text(
        TEXTS[lang]["welcome"], parse_mode="HTML",
        reply_markup=main_kb(lang)
    )
    return MENU

async def contact(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    lang = ctx.user_data.get("lang","uz")
    await q.edit_message_text(
        TEXTS[lang]["contact"], parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main")
        ]])
    )
    return MENU

async def change_lang(update: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    await q.edit_message_text(
        "🌐 Tilni tanlang / Выберите язык / 언어 선택:",
        reply_markup=lang_kb()
    )
    return LANG

def main():
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            LANG: [CallbackQueryHandler(lang_chosen, pattern="^lang_")],
            MENU: [
                CallbackQueryHandler(show_menu, pattern="^menu$"),
                CallbackQueryHandler(show_cart, pattern="^cart$"),
                CallbackQueryHandler(add_item, pattern="^add_"),
                CallbackQueryHandler(checkout, pattern="^checkout$"),
                CallbackQueryHandler(contact, pattern="^contact$"),
                CallbackQueryHandler(show_main, pattern="^main$"),
                CallbackQueryHandler(change_lang, pattern="^change_lang$"),
            ],
            CART: [
                CallbackQueryHandler(checkout, pattern="^checkout$"),
                CallbackQueryHandler(clear_cart, pattern="^clear_cart$"),
                CallbackQueryHandler(show_menu, pattern="^menu$"),
            ],
            NAME: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            PHONE: [
                MessageHandler(filters.CONTACT, get_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, get_phone),
            ],
            ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, get_address)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv)
    print("✅ DONA BOT ishga tushdi!")
    app.run_polling(drop_pending_updates=True)

if __name__ == "__main__":
    main()
