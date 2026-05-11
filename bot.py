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
    FSInputFile,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    Message,
)

from config import ADMIN_ID, BOT_TOKEN, CARD_HOLDER, CARD_NUMBER, SUPPORT_PHONE, MIN_AMOUNT, MAX_AMOUNT

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
            amount REAL NOT NULL,
            status TEXT DEFAULT 'pending',
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    """)
    conn.commit()
    conn.close()


def save_payment(user_id: int, name: str, username: str, amount: float):
    conn = sqlite3.connect("payments.db")
    cursor = conn.cursor()
    cursor.execute(
        "INSERT INTO payments (user_id, name, username, amount) VALUES (?, ?, ?, ?)",
        (user_id, name, username, amount)
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

user_amounts: Dict[int, float] = {}
user_last_request: Dict[int, datetime] = {}

RATE_LIMIT_SECONDS = 5


def fmt_card(number: str) -> str:
    return " ".join(number[i: i + 4] for i in range(0, 16, 4))


def check_rate_limit(user_id: int) -> bool:
    now = datetime.now()
    last = user_last_request.get(user_id)
    if last and (now - last).total_seconds() < RATE_LIMIT_SECONDS:
        return False
    user_last_request[user_id] = now
    return True


# ── /start ─────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    await message.answer(
        f"Привет, {user.first_name}! 👋\n\n"
        "💳 <b>Введи сумму в USD</b> для оплаты\n\n"
        "Минимум: <b>${}</b> | Максимум: <b>${}</b>\n\n"
        "Например: <code>50</code> или <code>$100</code>\n\n"
        "Введи /help для подробной информации".format(MIN_AMOUNT, MAX_AMOUNT)
    )
    if ADMIN_ID:
        username = f"@{user.username}" if user.username else "—"
        try:
            await bot.send_message(
                ADMIN_ID,
                f"👤 <b>Новый клиент зашёл в бот</b>\n"
                f"Имя: {user.full_name}\n"
                f"TG: {username}",
            )
        except Exception:
            pass


# ── /help ──────────────────────────────────────────────────────

@router.message(Command("help"))
async def cmd_help(message: Message):
    await message.answer(
        "<b>📖 Как пользоваться ботом:</b>\n\n"
        "1️⃣ Введи сумму в USD (например: 50 или $100)\n"
        "2️⃣ Получишь реквизиты карты\n"
        "3️⃣ Переведи ровно эту сумму\n"
        "4️⃣ Нажми «Я оплатил»\n"
        "5️⃣ Получи ссылку на скачивание гайда\n\n"
        "<b>❓ Вопросы?</b>\n"
        f"📞 Телефон: {SUPPORT_PHONE}\n"
        f"💳 Карта: {fmt_card(CARD_NUMBER)}\n"
        f"👤 Получатель: {CARD_HOLDER}"
    )


# ── /stats (только админ) ───────────────────────────────────────

@router.message(Command("stats"))
async def cmd_stats(message: Message):
    if message.from_user.id != ADMIN_ID:
        await message.answer("❌ Доступно только администратору")
        return

    stats = get_stats()
    await message.answer(
        f"📊 <b>Статистика платежей:</b>\n\n"
        f"Ожидающих платежей: {stats['count']}\n"
        f"Сумма: ${stats['total']:.2f}",
        parse_mode=ParseMode.HTML
    )


# ── Обработка ввода суммы ──────────────────────────────────────

@router.message()
async def handle_amount(message: Message):
    user_id = message.from_user.id

    if not check_rate_limit(user_id):
        await message.answer("⏱️ Подожди несколько секунд перед следующей попыткой")
        return

    text = message.text.strip().replace("$", "").strip()

    try:
        amount = float(text)

        if amount < MIN_AMOUNT:
            await message.answer(f"❌ Минимальная сумма: ${MIN_AMOUNT}")
            return
        if amount > MAX_AMOUNT:
            await message.answer(f"❌ Максимальная сумма: ${MAX_AMOUNT}")
            return

        user_amounts[user_id] = amount
        card = fmt_card(CARD_NUMBER)

        await message.answer(
            f"💳 <b>Реквизиты для оплаты</b>\n\n"
            f"Сумма: <b>${amount:.2f}</b>\n\n"
            f"Номер карты:\n"
            f"<code>{card}</code>\n"
            f"Получатель: <b>{CARD_HOLDER}</b>\n\n"
            f"<b>⚠️ Переведи ровно эту сумму!</b>\n\n"
            f"Когда переведёшь — нажми кнопку ниже 👇",
            reply_markup=InlineKeyboardMarkup(inline_keyboard=[
                [InlineKeyboardButton(text="✅ Я оплатил", callback_data="paid")],
            ]),
        )
    except ValueError:
        await message.answer("❌ Неверный формат. Введи число, например: <code>50</code> или <code>$100</code>")


# ── Клиент нажал "Я оплатил" ───────────────────────────────────

@router.callback_query(F.data == "paid")
async def payment_done(callback: CallbackQuery):
    await callback.answer()
    user_id = callback.from_user.id
    amount = user_amounts.get(user_id)
    user = callback.from_user
    username = f"@{user.username}" if user.username else "—"

    if not amount:
        await callback.message.edit_text("❌ Ошибка. Попробуй ещё раз: введи сумму")
        return

    save_payment(user_id, user.full_name, username, amount)

    await callback.message.edit_text(
        "✅ <b>Спасибо за оплату!</b>\n\n"
        "Мы проверим поступление в течение 10-15 минут.\n\n"
        "После подтверждения ты получишь ссылку на скачивание гайда.",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="📥 Скачать гайд", callback_data="download_guide")],
        ])
    )

    if ADMIN_ID:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"💰 <b>Клиент оплатил!</b>\n\n"
                f"Клиент: {user.full_name}\n"
                f"TG: {username}\n"
                f"Сумма: <b>${amount:.2f}</b>\n"
                f"Время: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n\n"
                f"⚠️ <b>Проверь поступление на карту!</b>\n"
                f"Когда подтвердишь — напиши в ответ: /approve_{user_id}",
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")

    if user_id in user_amounts:
        del user_amounts[user_id]


# ── Скачивание гайда ───────────────────────────────────────────

@router.callback_query(F.data == "download_guide")
async def download_guide(callback: CallbackQuery):
    await callback.answer()

    guide_path = "guide.pdf"

    if not os.path.exists(guide_path):
        await callback.message.edit_text(
            "❌ Гайд временно недоступен.\n\n"
            f"📞 Свяжись с поддержкой: {SUPPORT_PHONE}"
        )
        return

    try:
        guide = FSInputFile(guide_path)
        await callback.message.answer_document(
            guide,
            caption="📖 <b>Твой гайд готов!</b>\n\nЭто документ содержит всю информацию для успешного старта."
        )
        await callback.message.edit_text("✅ Гайд отправлен! Проверь загрузки.")
    except Exception as e:
        logger.error(f"Download error: {e}")
        await callback.message.edit_text(
            "❌ Ошибка при загрузке.\n\n"
            f"📞 Свяжись с поддержкой: {SUPPORT_PHONE}"
        )


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
