import asyncio
import logging
import os
import sys
import sqlite3
from datetime import datetime
from typing import Dict

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import (
    ADMIN_ID,
    BOT_TOKEN,
    CARD_HOLDER,
    CARD_NUMBER,
    CARD_TYPE,
    DEFAULT_LANG,
    LANGUAGES,
    PRODUCTS,
    SUPPORT_PHONE,
    TEXTS,
)

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Защита от двойного запуска ─────────────────────────────────

PID_FILE = os.path.join(os.path.dirname(__file__), "bot.pid")


def _acquire_lock():
    if os.path.exists(PID_FILE):
        try:
            old_pid = int(open(PID_FILE).read().strip())
            os.kill(old_pid, 0)
            logger.error(
                f"Бот уже запущен (PID {old_pid}). "
                "Останови предыдущий процесс и попробуй снова."
            )
            sys.exit(1)
        except (ProcessLookupError, OSError):
            pass

    with open(PID_FILE, "w") as f:
        f.write(str(os.getpid()))


def _release_lock():
    try:
        os.remove(PID_FILE)
    except FileNotFoundError:
        pass


# ── Database ───────────────────────────────────────────────────

def init_db():
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            name TEXT NOT NULL,
            username TEXT,
            product_name TEXT NOT NULL,
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_payment(user_id: int, name: str, username: str, product_name: str, amount: float):
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO payments (user_id, name, username, product_name, amount) VALUES (?, ?, ?, ?, ?)",
        (user_id, name, username, product_name, amount)
    )
    conn.commit()
    conn.close()


def get_stats() -> dict:
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute("SELECT COUNT(*), SUM(amount) FROM payments WHERE status='pending'")
    count, total = cursor.fetchone()
    conn.close()
    return {"count": count or 0, "total": total or 0}


# ── Bot & Dispatcher ───────────────────────────────────────────

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_lang: Dict[int, str] = {}
user_products: Dict[int, dict] = {}
user_last_request: Dict[int, datetime] = {}

RATE_LIMIT_SECONDS = 3


def fmt_card(number: str) -> str:
    return " ".join(number[i: i + 4] for i in range(0, len(number), 4))


def check_rate_limit(user_id: int) -> bool:
    now = datetime.now()
    last = user_last_request.get(user_id)
    if last and (now - last).total_seconds() < RATE_LIMIT_SECONDS:
        return False
    user_last_request[user_id] = now
    return True


def lang_of(user_id: int) -> str:
    return user_lang.get(user_id, DEFAULT_LANG)


def t(user_id: int, key: str) -> str:
    return TEXTS[lang_of(user_id)][key]


def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])


def products_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{p['name'][lang]} — ${p['price']:.2f}",
            callback_data=f"product:{key}"
        )]
        for key, p in PRODUCTS.items()
    ]
    rows.append([InlineKeyboardButton(
        text=TEXTS[lang]["change_lang_btn"],
        callback_data="change_lang",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_details_keyboard(lang: str, key: str, price: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=TEXTS[lang]["product_card_btn"].format(price=price),
            callback_data=f"pay:{key}",
        )],
        [InlineKeyboardButton(
            text=TEXTS[lang]["back_btn"],
            callback_data="back_to_products",
        )],
    ])


def payment_keyboard(lang: str) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["paid_btn"], callback_data="paid")],
        [InlineKeyboardButton(text=TEXTS[lang]["back_btn"], callback_data="back_to_products")],
    ])


# ── /start ─────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    # Сбрасываем выбранный продукт, язык спрашиваем заново только если не выбран
    if user.id not in user_lang:
        await message.answer(TEXTS[DEFAULT_LANG]["choose_lang"], reply_markup=lang_keyboard())
    else:
        await _show_products(message, user)

    if ADMIN_ID:
        username = f"@{user.username}" if user.username else "—"
        try:
            await bot.send_message(
                ADMIN_ID,
                TEXTS[DEFAULT_LANG]["admin_new_user"].format(
                    name=user.full_name, username=username
                ),
            )
        except Exception:
            pass


async def _show_products(message_or_cb, user):
    lang = lang_of(user.id)
    text = TEXTS[lang]["greeting"].format(name=user.first_name)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=products_keyboard(lang))
    else:
        await message_or_cb.message.edit_text(text, reply_markup=products_keyboard(lang))


# ── Выбор языка ────────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang:"))
async def select_lang(callback: CallbackQuery):
    await callback.answer()
    lang = callback.data.split(":", 1)[1]
    if lang not in LANGUAGES:
        lang = DEFAULT_LANG
    user_lang[callback.from_user.id] = lang
    await _show_products(callback, callback.from_user)


@router.callback_query(F.data == "change_lang")
async def change_lang(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        TEXTS[DEFAULT_LANG]["choose_lang"], reply_markup=lang_keyboard()
    )


# ── /help ──────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message):
    lang = lang_of(message.from_user.id)
    await message.answer(TEXTS[lang]["help"].format(phone=SUPPORT_PHONE))


# ── /stats (только админ) ───────────────────────────────────────

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Admin only")
        return

    stats = get_stats()
    await message.answer(
        f"📊 <b>Pending payments</b>\n\n"
        f"Count: {stats['count']}\n"
        f"Total: ${stats['total']:.2f}"
    )


# ── Открыть карточку продукта (описание + цена + Оплатить) ─────

@router.callback_query(F.data.startswith("product:"))
async def open_product(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if not check_rate_limit(user_id):
        await callback.answer(t(user_id, "rate_limit"), show_alert=True)
        return

    key = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(key)
    if not product:
        await callback.message.edit_text("❌ Product not found")
        return

    lang = lang_of(user_id)
    await callback.message.edit_text(
        product["description"][lang],
        reply_markup=product_details_keyboard(lang, key, product["price"]),
    )


# ── Назад к списку продуктов ───────────────────────────────────

@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    await callback.answer()
    await _show_products(callback, callback.from_user)


# ── Кнопка «Оплатить» внутри карточки → реквизиты ──────────────

@router.callback_query(F.data.startswith("pay:"))
async def show_payment(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id

    if not check_rate_limit(user_id):
        await callback.answer(t(user_id, "rate_limit"), show_alert=True)
        return

    key = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(key)
    if not product:
        await callback.message.edit_text("❌ Product not found")
        return

    lang = lang_of(user_id)
    user_products[user_id] = {
        "key": key,
        "name": product["name"][lang],
        "price": product["price"],
    }

    await callback.message.edit_text(
        TEXTS[lang]["payment_info"].format(
            title=TEXTS[lang]["payment_title"],
            product=product["name"][lang],
            price=product["price"],
            card_type=CARD_TYPE,
            card=fmt_card(CARD_NUMBER),
            holder=CARD_HOLDER,
        ),
        reply_markup=payment_keyboard(lang),
    )


# ── Клиент нажал «Я оплатил» ───────────────────────────────────

@router.callback_query(F.data == "paid")
async def payment_done(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    product = user_products.get(user_id)
    user = callback.from_user
    username = f"@{user.username}" if user.username else "—"
    lang = lang_of(user_id)

    if not product:
        await callback.message.edit_text(TEXTS[lang]["no_product"])
        return

    save_payment(user_id, user.full_name, username, product["name"], product["price"])

    await callback.message.edit_text(TEXTS[lang]["paid_confirm"])

    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                TEXTS[lang]["admin_paid"].format(
                    name=user.full_name,
                    username=username,
                    product=product["name"],
                    price=product["price"],
                    time=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                ),
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")

    user_products.pop(user_id, None)


# ── Запуск ─────────────────────────────────────────────────────

async def main():
    _acquire_lock()
    init_db()
    try:
        logger.info("Service Upgrade System started (PID %s)...", os.getpid())
        await dp.start_polling(bot)
    finally:
        _release_lock()
        logger.info("Service Upgrade System stopped.")


if __name__ == "__main__":
    asyncio.run(main())
