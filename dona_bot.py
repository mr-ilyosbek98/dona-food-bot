#!/usr/bin/env python3
import logging
import asyncio
from datetime import datetime
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, KeyboardButton, ReplyKeyboardMarkup, ReplyKeyboardRemove
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes, ConversationHandler

logging.basicConfig(level=logging.INFO)

BOT_TOKEN = "8944732139:AAG5ONRQCyGsKkre6vSxdyODUC_vPR8eVaY"
ADMIN_ID = 961419057

PRODUCTS = {
    "manti":      {"uz":"🥟 Manti",      "ru":"🥟 Манты",       "ko":"🥟 만티",     "price":10000},
    "somsa":      {"uz":"🥐 Somsa",      "ru":"🥐 Самса",       "ko":"🥐 삼사",     "price":10000},
    "kotlet":     {"uz":"🍖 Kotlet",     "ru":"🍖 Котлеты",     "ko":"🍖 커틀릿",   "price":10000},
    "blinchik":   {"uz":"🌯 Blinchik",   "ru":"🌯 Блинчики",    "ko":"🌯 블린치크", "price":10000},
    "varenik":    {"uz":"🥟 Varenik",    "ru":"🥟 Вареники",    "ko":"🥟 바레닉",   "price":10000},
    "honim":      {"uz":"🫔 Honim",      "ru":"🫔 Хоним",       "ko":"🫔 호님",     "price":10000},
    "frikadelka": {"uz":"🍡 Frikadelka", "ru":"🍡 Фрикадельки", "ko":"🍡 미트볼",   "price":10000},
}

S_LANG, S_MENU, S_CART, S_NAME, S_PHONE, S_ADDR = range(6)

def lang(ctx): return ctx.user_data.get("lang","uz")
def cart(ctx): return ctx.user_data.setdefault("cart",{})

WELCOME = {
    "uz": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b>ga xush kelibsiz!\nMuzlatilgan o'zbek milliy taomlari ❄️",
    "ru": "🇺🇿 Добро пожаловать в <b>DONA UZBEK FROZEN FOOD</b>!\nЗамороженные узбекские блюда ❄️",
    "ko": "🇺🇿 <b>DONA UZBEK FROZEN FOOD</b>에 오신 것을 환영합니다!\n냉동 우즈베크 음식 ❄️",
}
MENU_T = {"uz":"📋 Mahsulot tanlang:","ru":"📋 Выберите продукт:","ko":"📋 제품을 선택하세요:"}
CART_T = {"uz":"🛒 Savatcha","ru":"🛒 Корзина","ko":"🛒 장바구니"}
EMPTY  = {"uz":"🛒 Savatcha bo'sh","ru":"🛒 Корзина пуста","ko":"🛒 장바구니 비어 있음"}
TOTAL  = {"uz":"💰 Jami","ru":"💰 Итого","ko":"💰 합계"}
ORDER  = {"uz":"✅ Buyurtma berish","ru":"✅ Оформить заказ","ko":"✅ 주문하기"}
CLEAR  = {"uz":"🗑️ Tozalash","ru":"🗑️ Очистить","ko":"🗑️ 비우기"}
BACK   = {"uz":"⬅️ Ortga","ru":"⬅️ Назад","ko":"⬅️ 뒤로"}
NAMET  = {"uz":"👤 Ismingizni yozing:","ru":"👤 Введите имя:","ko":"👤 이름 입력:"}
PHONET = {"uz":"📱 Telefon raqamingizni yuboring:","ru":"📱 Отправьте номер:","ko":"📱 전화번호 보내기:"}
ADDRT  = {"uz":"📍 Manzilingizni yozing:","ru":"📍 Введите адрес:","ko":"📍 주소 입력:"}
DONE   = {"uz":"✅ <b>Buyurtmangiz qabul qilindi!</b>\nTez orada bog'lanamiz 🙏","ru":"✅ <b>Заказ принят!</b>\nСвяжемся с вами 🙏","ko":"✅ <b>주문 접수!</b>\n곧 연락드립니다 🙏"}
PHBTN  = {"uz":"📱 Raqamni yuborish","ru":"📱 Отправить номер","ko":"📱 번호 보내기"}

def lang_kb():
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("🇺🇿 O'zbekcha", callback_data="L_uz")],
        [InlineKeyboardButton("🇷🇺 Русский",   callback_data="L_ru")],
        [InlineKeyboardButton("🇰🇷 한국어",      callback_data="L_ko")],
    ])

def main_kb(l):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton("📋 Menyu",          callback_data="menu")],
        [InlineKeyboardButton(CART_T[l],           callback_data="cart"),
         InlineKeyboardButton(ORDER[l],            callback_data="checkout")],
        [InlineKeyboardButton("📞 Aloqa/Контакт",  callback_data="contact")],
        [InlineKeyboardButton("🌐 Til/Язык/언어",   callback_data="chlang")],
    ])

def prod_kb(l, c):
    rows = []
    for k,p in PRODUCTS.items():
        q = c.get(k,0)
        label = p[l]+" — {:,} won".format(p["price"]) + (f" ✅{q}" if q else "")
        rows.append([InlineKeyboardButton(label, callback_data="A_"+k)])
    rows.append([InlineKeyboardButton(CART_T[l], callback_data="cart"),
                 InlineKeyboardButton(BACK[l],   callback_data="main")])
    return InlineKeyboardMarkup(rows)

def cart_kb(l):
    return InlineKeyboardMarkup([
        [InlineKeyboardButton(ORDER[l],  callback_data="checkout")],
        [InlineKeyboardButton(CLEAR[l],  callback_data="clearcart")],
        [InlineKeyboardButton(BACK[l],   callback_data="menu")],
    ])

def fmt_cart(c, l):
    return "\n".join(f"{PRODUCTS[k][l]} x{v} = {PRODUCTS[k]['price']*v:,} won" for k,v in c.items() if k in PRODUCTS)

def total(c):
    return sum(PRODUCTS[k]["price"]*v for k,v in c.items() if k in PRODUCTS)

async def start(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data.clear()
    await u.message.reply_text("🌐 Tilni tanlang / Выберите язык / 언어 선택:", reply_markup=lang_kb())
    return S_LANG

async def set_lang(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    l = q.data[2:]; ctx.user_data["lang"] = l
    await q.edit_message_text(WELCOME[l], parse_mode="HTML", reply_markup=main_kb(l))
    return S_MENU

async def go_main(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    l = lang(ctx)
    await q.edit_message_text(WELCOME[l], parse_mode="HTML", reply_markup=main_kb(l))
    return S_MENU

async def go_menu(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    l = lang(ctx); c = cart(ctx)
    await q.edit_message_text(MENU_T[l], parse_mode="HTML", reply_markup=prod_kb(l,c))
    return S_MENU

async def add(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    k = q.data[2:]; c = cart(ctx)
    if k in PRODUCTS: c[k] = c.get(k,0)+1
    l = lang(ctx)
    await q.edit_message_text(MENU_T[l], parse_mode="HTML", reply_markup=prod_kb(l,c))
    return S_MENU

async def go_cart(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    l = lang(ctx); c = cart(ctx)
    if not c:
        await q.edit_message_text(EMPTY[l], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BACK[l], callback_data="menu")]]))
        return S_MENU
    await q.edit_message_text(f"{CART_T[l]}\n\n{fmt_cart(c,l)}\n\n{TOTAL[l]}: <b>{total(c):,} won</b>", parse_mode="HTML", reply_markup=cart_kb(l))
    return S_CART

async def do_clear(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    ctx.user_data["cart"] = {}; l = lang(ctx)
    await q.edit_message_text(EMPTY[l], reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BACK[l], callback_data="menu")]]))
    return S_MENU

async def go_checkout(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    l = lang(ctx)
    if not cart(ctx):
        await q.edit_message_text(EMPTY[l]); return S_MENU
    await q.edit_message_text(NAMET[l], parse_mode="HTML")
    return S_NAME

async def get_name(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["name"] = u.message.text; l = lang(ctx)
    kb = ReplyKeyboardMarkup([[KeyboardButton(PHBTN[l], request_contact=True)]], one_time_keyboard=True, resize_keyboard=True)
    await u.message.reply_text(PHONET[l], reply_markup=kb)
    return S_PHONE

async def get_phone(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["phone"] = u.message.contact.phone_number if u.message.contact else u.message.text
    l = lang(ctx)
    await u.message.reply_text(ADDRT[l], reply_markup=ReplyKeyboardRemove())
    return S_ADDR

async def get_addr(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    ctx.user_data["addr"] = u.message.text; l = lang(ctx)
    c = cart(ctx); t = total(c); items = fmt_cart(c,l)
    oid = datetime.now().strftime("%d%m%H%M")
    await u.message.reply_text(DONE[l], parse_mode="HTML")
    await ctx.bot.send_message(
        chat_id=ADMIN_ID, parse_mode="HTML",
        text=f"🆕 <b>BUYURTMA #{oid}</b>\n👤 {ctx.user_data.get('name')}\n📱 {ctx.user_data.get('phone')}\n📍 {ctx.user_data.get('addr')}\n🌐 {l.upper()}\n\n{items}\n\n💰 <b>{t:,} won</b>"
    )
    ctx.user_data["cart"] = {}
    await u.message.reply_text(WELCOME[l], parse_mode="HTML", reply_markup=main_kb(l))
    return S_MENU

async def contact(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer(); l = lang(ctx)
    await q.edit_message_text("📞 Telegram: @mr_yigitaliev\n🚚 Butun Koreya / Вся Корея / 한국 전국",
        reply_markup=InlineKeyboardMarkup([[InlineKeyboardButton(BACK[l], callback_data="main")]]))
    return S_MENU

async def chlang(u: Update, ctx: ContextTypes.DEFAULT_TYPE):
    q = u.callback_query; await q.answer()
    await q.edit_message_text("🌐 Tilni tanlang / Выберите язык / 언어 선택:", reply_markup=lang_kb())
    return S_LANG

if __name__ == "__main__":
    app = Application.builder().token(BOT_TOKEN).build()
    conv = ConversationHandler(
        entry_points=[CommandHandler("start", start)],
        states={
            S_LANG: [CallbackQueryHandler(set_lang, pattern="^L_")],
            S_MENU: [
                CallbackQueryHandler(go_menu,     pattern="^menu$"),
                CallbackQueryHandler(go_cart,     pattern="^cart$"),
                CallbackQueryHandler(add,         pattern="^A_"),
                CallbackQueryHandler(go_checkout, pattern="^checkout$"),
                CallbackQueryHandler(contact,     pattern="^contact$"),
                CallbackQueryHandler(go_main,     pattern="^main$"),
                CallbackQueryHandler(chlang,      pattern="^chlang$"),
            ],
            S_CART: [
                CallbackQueryHandler(go_checkout, pattern="^checkout$"),
                CallbackQueryHandler(do_clear,    pattern="^clearcart$"),
                CallbackQueryHandler(go_menu,     pattern="^menu$"),
            ],
            S_NAME:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_name)],
            S_PHONE: [MessageHandler(filters.CONTACT | (filters.TEXT & ~filters.COMMAND), get_phone)],
            S_ADDR:  [MessageHandler(filters.TEXT & ~filters.COMMAND, get_addr)],
        },
        fallbacks=[CommandHandler("start", start)],
    )
    app.add_handler(conv)
    print("✅ DONA BOT ishga tushdi!")
    app.run_polling(drop_pending_updates=True)
