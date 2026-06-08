#!/usr/bin/env python3
"""
DONA UZBEK FROZEN FOOD - Telegram Bot
O'zbek / Rus / Koreys tillarida ishlaydi
"""

import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup, KeyboardButton
from telegram.ext import (
    Application, CommandHandler, CallbackQueryHandler,
    MessageHandler, filters, ContextTypes, ConversationHandler
)
import json
import os
from datetime import datetime

# ============================================================
# ⚙️  SOZLAMALAR — BU YERDA O'ZGARTIRING
# ============================================================
BOT_TOKEN = "8944732139:AAF9TFV3sbtfVCls-6JdqIkiK8T0WD-3_lo"       # @BotFather dan olingan token
ADMIN_CHAT_ID = "961419057"      # Sizning Telegram ID (@mr_yigitaliev)
ADMIN_USERNAME = "@mr_yigitaliev"

# ============================================================
# 🛍️  MAHSULOTLAR — NARX VA NOMLARNI BU YERDA O'ZGARTIRING
# ============================================================
PRODUCTS = {
    "manti":      {"uz": "🥟 Manti",      "ru": "🥟 Манты",      "ko": "🥟 만티",      "price": 10000, "unit": "won"},
    "somsa":      {"uz": "🥐 Somsa",      "ru": "🥐 Самса",      "ko": "🥐 삼사",      "price": 10000, "unit": "won"},
    "kotlet":     {"uz": "🍖 Kotlet",     "ru": "🍖 Котлеты",    "ko": "🍖 커틀릿",    "price": 10000, "unit": "won"},
    "blinchik":   {"uz": "🌯 Blinchik",   "ru": "🌯 Блинчики",   "ko": "🌯 블린치크",  "price": 10000, "unit": "won"},
    "varenik":    {"uz": "🥟 Varenik",    "ru": "🥟 Вареники",   "ko": "🥟 바레닉",    "price": 10000, "unit": "won"},
    "honim":      {"uz": "🫔 Honim",      "ru": "🫔 Хоним",      "ko": "🫔 호님",      "price": 10000, "unit": "won"},
    "frikadelka": {"uz": "🍡 Frikadelka", "ru": "🍡 Фрикадельки","ko": "🍡 미트볼",    "price": 10000, "unit": "won"},
}

# ============================================================
# 🌐  TILLAR
# ============================================================
TEXTS = {
    "uz": {
        "welcome": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b> ga xush kelibsiz!\n\nMushtaq o'zbek taomlari — muzlatilgan, sifatli, tez pishadi! ❄️",
        "choose_lang": "🌐 Tilni tanlang / Выберите язык / 언어를 선택하세요:",
        "menu": "📋 <b>Menyu</b>\n\nMahsulot tanlang:",
        "cart": "🛒 Savatcha",
        "order": "📦 Buyurtma berish",
        "my_orders": "📋 Mening buyurtmalarim",
        "contact": "📞 Aloqa",
        "add_to_cart": "✅ Savatchaga qo'shildi!",
        "cart_empty": "🛒 Savatcha bo'sh",
        "cart_title": "🛒 <b>Sizning savatchingiz:</b>",
        "total": "💰 Jami:",
        "place_order": "✅ Buyurtma berish",
        "clear_cart": "🗑️ Tozalash",
        "enter_name": "👤 Ismingizni kiriting:",
        "enter_phone": "📱 Telefon raqamingizni yuboring:",
        "enter_address": "📍 Manzilingizni kiriting (shahar, ko'cha):",
        "order_confirmed": "✅ <b>Buyurtmangiz qabul qilindi!</b>\n\nTez orada siz bilan bog'lanamiz. Rahmat! 🙏",
        "order_cancelled": "❌ Buyurtma bekor qilindi",
        "back": "⬅️ Ortga",
        "price_per": "dona",
        "quantity": "Miqdor:",
        "delivery": "🚚 Butun Koreya bo'yicha yetkazib beramiz",
        "share_phone": "📱 Telefon raqamni yuborish",
    },
    "ru": {
        "welcome": "🇺🇿 Добро пожаловать в <b>DONA UZBEK FROZEN FOOD</b>!\n\nВкусные узбекские блюда — замороженные, качественные, быстро готовятся! ❄️",
        "menu": "📋 <b>Меню</b>\n\nВыберите продукт:",
        "cart": "🛒 Корзина",
        "order": "📦 Оформить заказ",
        "my_orders": "📋 Мои заказы",
        "contact": "📞 Контакты",
        "add_to_cart": "✅ Добавлено в корзину!",
        "cart_empty": "🛒 Корзина пуста",
        "cart_title": "🛒 <b>Ваша корзина:</b>",
        "total": "💰 Итого:",
        "place_order": "✅ Оформить заказ",
        "clear_cart": "🗑️ Очистить",
        "enter_name": "👤 Введите ваше имя:",
        "enter_phone": "📱 Отправьте номер телефона:",
        "enter_address": "📍 Введите ваш адрес (город, улица):",
        "order_confirmed": "✅ <b>Ваш заказ принят!</b>\n\nМы свяжемся с вами в ближайшее время. Спасибо! 🙏",
        "order_cancelled": "❌ Заказ отменён",
        "back": "⬅️ Назад",
        "price_per": "шт",
        "quantity": "Количество:",
        "delivery": "🚚 Доставляем по всей Корее",
        "share_phone": "📱 Отправить номер телефона",
    },
    "ko": {
        "welcome": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b>에 오신 것을 환영합니다!\n\n맛있는 우즈베크 요리 — 냉동, 고품질, 빠른 조리! ❄️",
        "menu": "📋 <b>메뉴</b>\n\n제품을 선택하세요:",
        "cart": "🛒 장바구니",
        "order": "📦 주문하기",
        "my_orders": "📋 내 주문",
        "contact": "📞 연락처",
        "add_to_cart": "✅ 장바구니에 추가됨!",
        "cart_empty": "🛒 장바구니가 비어 있습니다",
        "cart_title": "🛒 <b>장바구니:</b>",
        "total": "💰 합계:",
        "place_order": "✅ 주문하기",
        "clear_cart": "🗑️ 비우기",
        "enter_name": "👤 이름을 입력하세요:",
        "enter_phone": "📱 전화번호를 보내주세요:",
        "enter_address": "📍 주소를 입력하세요 (도시, 거리):",
        "order_confirmed": "✅ <b>주문이 접수되었습니다!</b>\n\n곧 연락드리겠습니다. 감사합니다! 🙏",
        "order_cancelled": "❌ 주문 취소됨",
        "back": "⬅️ 뒤로",
        "price_per": "개",
        "quantity": "수량:",
        "delivery": "🚚 한국 전국 배달",
        "share_phone": "📱 전화번호 보내기",
    }
}

# ============================================================
# ConversationHandler states
# ============================================================
CHOOSING_LANG, BROWSING, IN_CART, CHECKOUT_NAME, CHECKOUT_PHONE, CHECKOUT_ADDRESS = range(6)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================
# YORDAMCHI FUNKSIYALAR
# ============================================================
def get_lang(context):
    return context.user_data.get("lang", "uz")

def t(key, context):
    lang = get_lang(context)
    return TEXTS[lang].get(key, TEXTS["uz"].get(key, key))

def get_cart(context):
    return context.user_data.setdefault("cart", {})

def cart_total(cart):
    return sum(PRODUCTS[k]["price"] * v for k, v in cart.items() if k in PRODUCTS)

def format_cart(cart, lang):
    if not cart:
        return ""
    lines = []
    for key, qty in cart.items():
        if key in PRODUCTS:
            p = PRODUCTS[key]
            name = p[lang]
            price = p["price"] * qty
            lines.append(f"{name} x{qty} — {price:,} won")
    return "\n".join(lines)

# ============================================================
# INLINE KLAVIATURA GENERATORLARI
# ============================================================
def lang_keyboard():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="lang_uz")],
        [InlineKeyboardButton("🇷🇺 Русский",   callback_data="lang_ru")],
        [InlineKeyboardButton("🇰🇷 한국어",      callback_data="lang_ko")],
    ])

def main_menu_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["menu"].split("\n")[0], callback_data="menu")],
        [InlineKeyboardButton(TEXTS[lang]["cart"],    callback_data="cart"),
         InlineKeyboardButton(TEXTS[lang]["order"],   callback_data="checkout")],
        [InlineKeyboardButton(TEXTS[lang]["contact"], callback_data="contact")],
        [InlineKeyboardButton("🌐 Til / Язык / 언어", callback_data="change_lang")],
    ])

def products_keyboard(lang, cart):
    buttons = []
    for key, p in PRODUCTS.items():
        qty = cart.get(key, 0)
        label = f"{p[lang]} — {p['price']:,} won"
        if qty > 0:
            label = f"✅ {label} (x{qty})"
        buttons.append([InlineKeyboardButton(label, callback_data=f"add_{key}")])
    buttons.append([
        InlineKeyboardButton(TEXTS[lang]["cart"], callback_data="cart"),
        InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu"),
    ])
    return InlineKeyboardMarkup(buttons)

def cart_keyboard(lang):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(TEXTS[lang]["place_order"], callback_data="checkout")],
        [InlineKeyboardButton(TEXTS[lang]["clear_cart"],  callback_data="clear_cart")],
        [InlineKeyboardButton(TEXTS[lang]["back"],        callback_data="menu")],
    ])

# ============================================================
# HANDLERLAR
# ============================================================
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.clear()
    await update.message.reply_text(
        "🌐 Tilni tanlang / Выберите язык / 언어를 선택하세요:",
        reply_markup=lang_keyboard()
    )
    return CHOOSING_LANG

async def language_chosen(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = query.data.split("_")[1]
    context.user_data["lang"] = lang
    await query.edit_message_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang)
    )
    return BROWSING

async def main_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    await query.edit_message_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang)
    )
    return BROWSING

async def show_menu(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    cart = get_cart(context)
    await query.edit_message_text(
        TEXTS[lang]["menu"],
        parse_mode="HTML",
        reply_markup=products_keyboard(lang, cart)
    )
    return BROWSING

async def add_to_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    cart = get_cart(context)
    product_key = query.data.replace("add_", "")
    if product_key in PRODUCTS:
        cart[product_key] = cart.get(product_key, 0) + 1
        await query.answer(TEXTS[lang]["add_to_cart"], show_alert=False)
    await query.edit_message_text(
        TEXTS[lang]["menu"],
        parse_mode="HTML",
        reply_markup=products_keyboard(lang, cart)
    )
    return BROWSING

async def show_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    cart = get_cart(context)
    if not cart:
        await query.edit_message_text(
            TEXTS[lang]["cart_empty"],
            reply_markup=InlineKeyboardMarkup([[
                InlineKeyboardButton(TEXTS[lang]["back"], callback_data="menu")
            ]])
        )
        return BROWSING
    items = format_cart(cart, lang)
    total = cart_total(cart)
    text = f"{TEXTS[lang]['cart_title']}\n\n{items}\n\n{TEXTS[lang]['total']} <b>{total:,} won</b>\n\n{TEXTS[lang]['delivery']}"
    await query.edit_message_text(text, parse_mode="HTML", reply_markup=cart_keyboard(lang))
    return IN_CART

async def clear_cart(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    context.user_data["cart"] = {}
    lang = get_lang(context)
    await query.edit_message_text(
        TEXTS[lang]["cart_empty"],
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(TEXTS[lang]["back"], callback_data="menu")
        ]])
    )
    return BROWSING

async def start_checkout(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    cart = get_cart(context)
    if not cart:
        await query.edit_message_text(TEXTS[lang]["cart_empty"])
        return BROWSING
    await query.edit_message_text(TEXTS[lang]["enter_name"], parse_mode="HTML")
    return CHECKOUT_NAME

async def checkout_name(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data["order_name"] = update.message.text
    lang = get_lang(context)
    phone_button = KeyboardButton(TEXTS[lang]["share_phone"], request_contact=True)
    await update.message.reply_text(
        TEXTS[lang]["enter_phone"],
        reply_markup=ReplyKeyboardMarkup([[phone_button]], one_time_keyboard=True, resize_keyboard=True)
    )
    return CHECKOUT_PHONE

async def checkout_phone(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    if update.message.contact:
        phone = update.message.contact.phone_number
    else:
        phone = update.message.text
    context.user_data["order_phone"] = phone
    from telegram import ReplyKeyboardRemove
    await update.message.reply_text(TEXTS[lang]["enter_address"], reply_markup=ReplyKeyboardRemove())
    return CHECKOUT_ADDRESS

async def checkout_address(update: Update, context: ContextTypes.DEFAULT_TYPE):
    lang = get_lang(context)
    context.user_data["order_address"] = update.message.text
    cart = get_cart(context)
    total = cart_total(cart)
    items_text = format_cart(cart, lang)
    name = context.user_data.get("order_name", "—")
    phone = context.user_data.get("order_phone", "—")
    address = context.user_data.get("order_address", "—")
    order_id = datetime.now().strftime("%Y%m%d%H%M%S")

    # Mijozga tasdiq
    await update.message.reply_text(
        f"{TEXTS[lang]['order_confirmed']}\n\n📋 Buyurtma #{order_id}",
        parse_mode="HTML"
    )

    # Adminaga xabar
    admin_text = (
        f"🆕 <b>YANGI BUYURTMA #{order_id}</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"👤 Ism: {name}\n"
        f"📱 Tel: {phone}\n"
        f"📍 Manzil: {address}\n"
        f"🌐 Til: {lang.upper()}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"🛒 Mahsulotlar:\n{items_text}\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"💰 JAMI: <b>{total:,} won</b>\n"
        f"━━━━━━━━━━━━━━━━\n"
        f"⏰ Vaqt: {datetime.now().strftime('%Y-%m-%d %H:%M')}"
    )
    await context.bot.send_message(
        chat_id=ADMIN_CHAT_ID,
        text=admin_text,
        parse_mode="HTML"
    )

    # Savatchani tozalash
    context.user_data["cart"] = {}

    # Asosiy menuga qaytish
    await update.message.reply_text(
        TEXTS[lang]["welcome"],
        parse_mode="HTML",
        reply_markup=main_menu_keyboard(lang)
    )
    return BROWSING

async def contact_info(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    lang = get_lang(context)
    text = (
        f"📞 <b>DONA UZBEK FROZEN FOOD</b>\n\n"
        f"📱 Telegram: {ADMIN_USERNAME}\n"
        f"📸 Instagram: @dona_uzbek_frozen\n"
        f"🚚 Yetkazib berish: Butun Koreya\n\n"
        f"⏰ Ish vaqti: 9:00 — 21:00"
    )
    await query.edit_message_text(
        text, parse_mode="HTML",
        reply_markup=InlineKeyboardMarkup([[
            InlineKeyboardButton(TEXTS[lang]["back"], callback_data="main_menu")
        ]])
    )
    return BROWSING

async def change_lang(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    await query.edit_message_text(
        "🌐 Tilni tanlang / Выберите язык / 언어를 선택하세요:",
        reply_markup=lang_keyboard()
    )
    return CHOOSING_LANG

# ============================================================
# MAIN
# ============================================================
def main():
    app = Application.builder().token(BOT_TOKEN).build()

    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            CHOOSING_LANG: [CallbackQueryHandler(language_chosen, pattern="^lang_")],
            BROWSING: [
                CallbackQueryHandler(show_menu,      pattern="^menu$"),
                CallbackQueryHandler(show_cart,      pattern="^cart$"),
                CallbackQueryHandler(add_to_cart,    pattern="^add_"),
                CallbackQueryHandler(start_checkout, pattern="^checkout$"),
                CallbackQueryHandler(contact_info,   pattern="^contact$"),
                CallbackQueryHandler(main_menu,      pattern="^main_menu$"),
                CallbackQueryHandler(change_lang,    pattern="^change_lang$"),
            ],
            IN_CART: [
                CallbackQueryHandler(start_checkout, pattern="^checkout$"),
                CallbackQueryHandler(clear_cart,     pattern="^clear_cart$"),
                CallbackQueryHandler(show_menu,      pattern="^menu$"),
            ],
            CHECKOUT_NAME:    [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_name)],
            CHECKOUT_PHONE:   [
                MessageHandler(filters.CONTACT, checkout_phone),
                MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_phone),
            ],
            CHECKOUT_ADDRESS: [MessageHandler(filters.TEXT & ~filters.COMMAND, checkout_address)],
        },
        fallbacks=[CommandHandler("start", start)],
    )

    app.add_handler(conv)
    print("✅ DONA BOT ishga tushdi!")
    app.run_polling()

if __name__ == "__main__":
    main()
