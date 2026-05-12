import asyncio
import logging
import os
import random
import sqlite3
import sys
from datetime import datetime
from typing import Optional

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

DB_PATH = os.path.join(os.path.dirname(__file__), "payments.db")
PID_FILE = os.path.join(os.path.dirname(__file__), "bot.pid")

RATE_LIMIT_SECONDS = 3
PAYMENT_TTL_SECONDS = 2 * 60 * 60   # 2 часа на pending
EXPIRY_INTERVAL_SECONDS = 5 * 60    # проверка раз в 5 минут
MAX_AMOUNT_OFFSET_CENTS = 29        # сумма уменьшается на 0..29 центов
ACTIVE_STATUSES = ("awaiting_receipt", "awaiting_review")

# ── PID-lock ───────────────────────────────────────────────────

def _acquire_lock():
    if os.path.exists(PID_FILE):
        try:
            old_pid = int(open(PID_FILE).read().strip())
            os.kill(old_pid, 0)
            logger.error(f"Бот уже запущен (PID {old_pid}).")
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

def _conn() -> sqlite3.Connection:
    c = sqlite3.connect(DB_PATH)
    c.row_factory = sqlite3.Row
    return c


def init_db():
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("""
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
        cur.execute("PRAGMA table_info(payments)")
        cols = {row[1] for row in cur.fetchall()}
        for col, ddl in [
            ("screenshot_file_id", "ALTER TABLE payments ADD COLUMN screenshot_file_id TEXT"),
            ("product_key",        "ALTER TABLE payments ADD COLUMN product_key TEXT"),
            ("base_amount",        "ALTER TABLE payments ADD COLUMN base_amount REAL"),
            ("reviewed_at",        "ALTER TABLE payments ADD COLUMN reviewed_at TIMESTAMP"),
            ("reviewed_by",        "ALTER TABLE payments ADD COLUMN reviewed_by INTEGER"),
        ]:
            if col not in cols:
                cur.execute(ddl)

        cur.execute("""
            CREATE TABLE IF NOT EXISTS users (
                user_id INTEGER PRIMARY KEY,
                lang TEXT,
                first_seen_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                last_start_at TIMESTAMP,
                active_payment_id INTEGER
            )
        """)
        conn.commit()


def upsert_user_on_start(user_id: int) -> bool:
    """Возвращает True, если пользователь новый (первый /start)."""
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute("SELECT user_id FROM users WHERE user_id = ?", (user_id,))
        is_new = cur.fetchone() is None
        if is_new:
            cur.execute(
                "INSERT INTO users (user_id, last_start_at) VALUES (?, CURRENT_TIMESTAMP)",
                (user_id,),
            )
        else:
            cur.execute(
                "UPDATE users SET last_start_at = CURRENT_TIMESTAMP WHERE user_id = ?",
                (user_id,),
            )
        conn.commit()
        return is_new


def get_user_lang(user_id: int) -> Optional[str]:
    with _conn() as conn:
        row = conn.execute("SELECT lang FROM users WHERE user_id = ?", (user_id,)).fetchone()
        return row["lang"] if row and row["lang"] else None


def set_user_lang(user_id: int, lang: str):
    with _conn() as conn:
        conn.execute(
            "INSERT INTO users (user_id, lang) VALUES (?, ?) "
            "ON CONFLICT(user_id) DO UPDATE SET lang = excluded.lang",
            (user_id, lang),
        )
        conn.commit()


def set_active_payment(user_id: int, payment_id: Optional[int]):
    with _conn() as conn:
        conn.execute(
            "UPDATE users SET active_payment_id = ? WHERE user_id = ?",
            (payment_id, user_id),
        )
        conn.commit()


def get_active_payment(user_id: int) -> Optional[sqlite3.Row]:
    with _conn() as conn:
        row = conn.execute(
            "SELECT p.* FROM payments p "
            "JOIN users u ON u.active_payment_id = p.id "
            "WHERE u.user_id = ? AND p.status IN (?, ?)",
            (user_id, *ACTIVE_STATUSES),
        ).fetchone()
        return row


def get_payment(payment_id: int) -> Optional[sqlite3.Row]:
    with _conn() as conn:
        return conn.execute("SELECT * FROM payments WHERE id = ?", (payment_id,)).fetchone()


def pick_unique_amount(base_amount: float) -> float:
    """Базовая сумма минус случайные центы; уникально среди активных pending."""
    with _conn() as conn:
        used = {
            round(r["amount"], 2) for r in conn.execute(
                "SELECT amount FROM payments WHERE status IN (?, ?)",
                ACTIVE_STATUSES,
            ).fetchall()
        }
    offsets = list(range(0, MAX_AMOUNT_OFFSET_CENTS + 1))
    random.shuffle(offsets)
    for off in offsets:
        candidate = round(base_amount - off / 100, 2)
        if candidate > 0 and candidate not in used:
            return candidate
    # переполнение — крайне маловероятно; возвращаем базу
    return round(base_amount, 2)


def create_payment(
    user_id: int, name: str, username: str,
    product_key: str, product_name: str, base_amount: float, amount: float,
) -> int:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "INSERT INTO payments "
            "(user_id, name, username, product_key, product_name, base_amount, amount, status) "
            "VALUES (?, ?, ?, ?, ?, ?, ?, 'awaiting_receipt')",
            (user_id, name, username, product_key, product_name, base_amount, amount),
        )
        pid = cur.lastrowid
        conn.commit()
        return pid


def attach_screenshot(payment_id: int, file_id: str) -> bool:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE payments SET screenshot_file_id = ?, status = 'awaiting_review' "
            "WHERE id = ? AND status = 'awaiting_receipt'",
            (file_id, payment_id),
        )
        conn.commit()
        return cur.rowcount > 0


def skip_screenshot(payment_id: int) -> bool:
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE payments SET status = 'awaiting_review' "
            "WHERE id = ? AND status = 'awaiting_receipt'",
            (payment_id,),
        )
        conn.commit()
        return cur.rowcount > 0


def review_payment(payment_id: int, admin_id: int, approve: bool) -> bool:
    """Идемпотентно — переводит только из 'awaiting_review'."""
    new_status = "confirmed" if approve else "rejected"
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            "UPDATE payments SET status = ?, reviewed_at = CURRENT_TIMESTAMP, reviewed_by = ? "
            "WHERE id = ? AND status = 'awaiting_review'",
            (new_status, admin_id, payment_id),
        )
        conn.commit()
        return cur.rowcount > 0


def expire_stale_payments() -> int:
    cutoff_sql = f"datetime('now', '-{PAYMENT_TTL_SECONDS} seconds')"
    with _conn() as conn:
        cur = conn.cursor()
        cur.execute(
            f"UPDATE payments SET status = 'expired' "
            f"WHERE status IN ('awaiting_receipt','awaiting_review') AND created_at < {cutoff_sql}"
        )
        conn.commit()
        return cur.rowcount


def get_stats() -> dict:
    with _conn() as conn:
        row = conn.execute(
            "SELECT COUNT(*) AS c, COALESCE(SUM(amount), 0) AS s "
            "FROM payments WHERE status IN ('awaiting_receipt','awaiting_review')"
        ).fetchone()
        return {"count": row["c"], "total": row["s"]}


# ── Bot ────────────────────────────────────────────────────────

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_last_request: dict[int, datetime] = {}


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
    return get_user_lang(user_id) or DEFAULT_LANG


def t(user_id: int, key: str) -> str:
    return TEXTS[lang_of(user_id)][key]


# ── Keyboards ──────────────────────────────────────────────────

def lang_keyboard() -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="🇷🇺 Русский", callback_data="lang:ru"),
        InlineKeyboardButton(text="🇬🇧 English", callback_data="lang:en"),
    ]])


def products_keyboard(lang: str) -> InlineKeyboardMarkup:
    rows = [
        [InlineKeyboardButton(
            text=f"{p['name'][lang]} — ${p['price']:.2f}",
            callback_data=f"product:{key}",
        )]
        for key, p in PRODUCTS.items()
    ]
    rows.append([InlineKeyboardButton(
        text=TEXTS[lang]["change_lang_btn"], callback_data="change_lang",
    )])
    return InlineKeyboardMarkup(inline_keyboard=rows)


def product_details_keyboard(lang: str, key: str, price: float) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(
            text=TEXTS[lang]["product_card_btn"].format(price=price),
            callback_data=f"pay:{key}",
        )],
        [InlineKeyboardButton(text=TEXTS[lang]["back_btn"], callback_data="back_to_products")],
    ])


def payment_keyboard(lang: str, payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text=TEXTS[lang]["paid_btn"], callback_data=f"paid:{payment_id}")],
        [InlineKeyboardButton(text=TEXTS[lang]["cancel_btn"], callback_data=f"cancel_payment:{payment_id}")],
    ])


def receipt_skip_keyboard(lang: str, payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text=TEXTS[lang]["receipt_skip_btn"], callback_data=f"skip_receipt:{payment_id}"),
    ]])


def admin_review_keyboard(payment_id: int) -> InlineKeyboardMarkup:
    return InlineKeyboardMarkup(inline_keyboard=[[
        InlineKeyboardButton(text="✅ Подтвердить", callback_data=f"confirm:{payment_id}"),
        InlineKeyboardButton(text="❌ Отклонить",  callback_data=f"reject:{payment_id}"),
    ]])


# ── /start ─────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    is_new = upsert_user_on_start(user.id)
    set_active_payment(user.id, None)

    if not get_user_lang(user.id):
        await message.answer(TEXTS[DEFAULT_LANG]["choose_lang"], reply_markup=lang_keyboard())
    else:
        await _show_products(message, user)

    if ADMIN_ID and is_new:
        username = f"@{user.username}" if user.username else "—"
        try:
            await bot.send_message(
                ADMIN_ID,
                TEXTS[DEFAULT_LANG]["admin_new_user"].format(
                    name=user.full_name, username=username, user_id=user.id,
                ),
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")


async def _show_products(message_or_cb, user):
    lang = lang_of(user.id)
    text = TEXTS[lang]["greeting"].format(name=user.first_name)
    if isinstance(message_or_cb, Message):
        await message_or_cb.answer(text, reply_markup=products_keyboard(lang))
    else:
        await message_or_cb.message.edit_text(text, reply_markup=products_keyboard(lang))


# ── Язык ───────────────────────────────────────────────────────

@router.callback_query(F.data.startswith("lang:"))
async def select_lang(callback: CallbackQuery):
    await callback.answer()
    lang = callback.data.split(":", 1)[1]
    if lang not in LANGUAGES:
        lang = DEFAULT_LANG
    set_user_lang(callback.from_user.id, lang)
    await _show_products(callback, callback.from_user)


@router.callback_query(F.data == "change_lang")
async def change_lang(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        TEXTS[DEFAULT_LANG]["choose_lang"], reply_markup=lang_keyboard(),
    )


# ── /help ──────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message):
    lang = lang_of(message.from_user.id)
    await message.answer(TEXTS[lang]["help"].format(phone=SUPPORT_PHONE))


# ── /stats ─────────────────────────────────────────────────────

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Admin only")
        return
    s = get_stats()
    await message.answer(
        f"📊 <b>Active payments</b>\n\n"
        f"Count: {s['count']}\nTotal: ${s['total']:.2f}"
    )


# ── Карточка продукта ──────────────────────────────────────────

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


@router.callback_query(F.data == "back_to_products")
async def back_to_products(callback: CallbackQuery):
    await callback.answer()
    set_active_payment(callback.from_user.id, None)
    await _show_products(callback, callback.from_user)


# ── Создаём заявку, показываем реквизиты ───────────────────────

@router.callback_query(F.data.startswith("pay:"))
async def show_payment(callback: CallbackQuery):
    await callback.answer()
    user = callback.from_user
    if not check_rate_limit(user.id):
        await callback.answer(t(user.id, "rate_limit"), show_alert=True)
        return

    key = callback.data.split(":", 1)[1]
    product = PRODUCTS.get(key)
    if not product:
        await callback.message.edit_text("❌ Product not found")
        return

    lang = lang_of(user.id)
    base = float(product["price"])
    amount = pick_unique_amount(base)
    username = f"@{user.username}" if user.username else "—"

    payment_id = create_payment(
        user.id, user.full_name, username,
        key, product["name"][lang], base, amount,
    )
    set_active_payment(user.id, payment_id)

    await callback.message.edit_text(
        TEXTS[lang]["payment_info"].format(
            title=TEXTS[lang]["payment_title"],
            product=product["name"][lang],
            price=amount,
            base_price=base,
            card_type=CARD_TYPE,
            card=fmt_card(CARD_NUMBER),
            holder=CARD_HOLDER,
            order_id=payment_id,
        ),
        reply_markup=payment_keyboard(lang, payment_id),
    )


@router.callback_query(F.data.startswith("cancel_payment:"))
async def cancel_payment(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    set_active_payment(user_id, None)
    await _show_products(callback, callback.from_user)


# ── Клиент нажал «Я оплатил» — просим скриншот ─────────────────

@router.callback_query(F.data.startswith("paid:"))
async def payment_done(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    payment_id = int(callback.data.split(":", 1)[1])
    payment = get_payment(payment_id)
    lang = lang_of(user_id)

    if not payment or payment["user_id"] != user_id or payment["status"] != "awaiting_receipt":
        await callback.message.edit_text(TEXTS[lang]["no_active_payment"])
        return

    await callback.message.edit_text(
        TEXTS[lang]["ask_receipt"].format(order_id=payment_id),
        reply_markup=receipt_skip_keyboard(lang, payment_id),
    )


# ── Скриншот ───────────────────────────────────────────────────

@router.message(F.photo)
async def receive_photo(message: Message):
    user = message.from_user
    user_id = user.id
    lang = lang_of(user_id)
    active = get_active_payment(user_id)

    if not active or active["status"] != "awaiting_receipt":
        await message.answer(TEXTS[lang]["photo_no_context"])
        return

    file_id = message.photo[-1].file_id
    payment_id = active["id"]
    if not attach_screenshot(payment_id, file_id):
        # параллельный переход — заявка уже не в awaiting_receipt
        await message.answer(TEXTS[lang]["no_active_payment"])
        return

    await _notify_admin_for_review(payment_id, with_photo=file_id)
    await message.answer(TEXTS[lang]["receipt_received"])
    set_active_payment(user_id, None)


@router.callback_query(F.data.startswith("skip_receipt:"))
async def skip_receipt_cb(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    payment_id = int(callback.data.split(":", 1)[1])
    payment = get_payment(payment_id)
    lang = lang_of(user_id)

    if not payment or payment["user_id"] != user_id:
        await callback.message.edit_text(TEXTS[lang]["no_active_payment"])
        return
    if not skip_screenshot(payment_id):
        await callback.message.edit_text(TEXTS[lang]["no_active_payment"])
        return

    await _notify_admin_for_review(payment_id, with_photo=None)
    await callback.message.edit_text(TEXTS[lang]["receipt_skipped"])
    set_active_payment(user_id, None)


async def _notify_admin_for_review(payment_id: int, with_photo: Optional[str]):
    if not ADMIN_ID:
        return
    p = get_payment(payment_id)
    if not p:
        return
    caption = TEXTS[DEFAULT_LANG]["admin_review"].format(
        order_id=p["id"],
        name=p["name"],
        username=p["username"] or "—",
        user_id=p["user_id"],
        product=p["product_name"],
        base_price=float(p["base_amount"] or 0),
        price=float(p["amount"]),
        time=str(p["created_at"]),
        screenshot="📎 со скриншотом" if with_photo else "⚠️ без скриншота",
    )
    kb = admin_review_keyboard(payment_id)
    try:
        if with_photo:
            await bot.send_photo(ADMIN_ID, with_photo, caption=caption, reply_markup=kb)
        else:
            await bot.send_message(ADMIN_ID, caption, reply_markup=kb)
    except Exception as e:
        logger.error(f"Admin review notify error: {e}")


# ── Подтверждение / отклонение админом ─────────────────────────

@router.callback_query(F.data.startswith("confirm:"))
async def admin_confirm(callback: CallbackQuery):
    await _admin_review(callback, approve=True)


@router.callback_query(F.data.startswith("reject:"))
async def admin_reject(callback: CallbackQuery):
    await _admin_review(callback, approve=False)


async def _admin_review(callback: CallbackQuery, approve: bool):
    if callback.from_user.id != ADMIN_ID:
        await callback.answer("❌ Admin only", show_alert=True)
        return

    payment_id = int(callback.data.split(":", 1)[1])
    payment = get_payment(payment_id)
    if not payment:
        await callback.answer("Payment not found", show_alert=True)
        return

    if payment["status"] != "awaiting_review":
        await callback.answer(f"Уже {payment['status']}", show_alert=True)
        try:
            await callback.message.edit_reply_markup(reply_markup=None)
        except Exception:
            pass
        return

    if not review_payment(payment_id, callback.from_user.id, approve):
        await callback.answer("Race condition", show_alert=True)
        return

    await callback.answer("✅ Подтверждено" if approve else "❌ Отклонено")
    try:
        await callback.message.edit_reply_markup(reply_markup=None)
    except Exception:
        pass

    client_lang = get_user_lang(payment["user_id"]) or DEFAULT_LANG
    key = "client_confirmed" if approve else "client_rejected"
    try:
        await bot.send_message(
            payment["user_id"],
            TEXTS[client_lang][key].format(
                order_id=payment_id,
                product=payment["product_name"],
                price=float(payment["amount"]),
                phone=SUPPORT_PHONE,
            ),
        )
    except Exception as e:
        logger.error(f"Client notify error: {e}")


# ── Фоновая задача: TTL ────────────────────────────────────────

async def ttl_worker():
    while True:
        try:
            expired = expire_stale_payments()
            if expired:
                logger.info(f"Expired {expired} stale payment(s)")
        except Exception as e:
            logger.error(f"TTL worker error: {e}")
        await asyncio.sleep(EXPIRY_INTERVAL_SECONDS)


# ── Fallback на любые другие сообщения ─────────────────────────

@router.message()
async def fallback(message: Message):
    lang = lang_of(message.from_user.id)
    await message.answer(TEXTS[lang]["fallback"])


# ── Запуск ─────────────────────────────────────────────────────

async def main():
    _acquire_lock()
    init_db()
    try:
        logger.info("Service Upgrade System started (PID %s)...", os.getpid())
        asyncio.create_task(ttl_worker())
        await dp.start_polling(bot)
    finally:
        _release_lock()
        logger.info("Service Upgrade System stopped.")


if __name__ == "__main__":
    asyncio.run(main())
