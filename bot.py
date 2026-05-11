import asyncio
import logging
import os
import sys
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

from config import ADMIN_ID, BOT_TOKEN, CARD_HOLDER, CARD_NUMBER

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


# ── Bot & Dispatcher ───────────────────────────────────────────

bot = Bot(token=BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
dp = Dispatcher()
router = Router()
dp.include_router(router)

user_amounts: Dict[int, float] = {}


def fmt_card(number: str) -> str:
    return " ".join(number[i: i + 4] for i in range(0, 16, 4))


# ── /start ─────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    await message.answer(
        f"Привет, {user.first_name}! 👋\n\n"
        "💳 <b>Введи сумму в USD</b> для оплаты\n\n"
        "Например: <code>50</code> или <code>$100</code>"
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


# ── Обработка ввода суммы ──────────────────────────────────────

@router.message()
async def handle_amount(message: Message):
    user_id = message.from_user.id
    text = message.text.strip().replace("$", "").strip()

    try:
        amount = float(text)
        if amount <= 0:
            await message.answer("❌ Сумма должна быть больше 0")
            return

        user_amounts[user_id] = amount
        card = fmt_card(CARD_NUMBER)

        await message.answer(
            f"💳 <b>Реквизиты для оплаты</b>\n\n"
            f"Сумма: <b>${amount:.2f}</b>\n\n"
            f"Номер карты:\n"
            f"<code>{card}</code>\n"
            f"Получатель: <b>{CARD_HOLDER}</b>\n\n"
            f"Переведи точную сумму и нажми кнопку ниже 👇",
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

    await callback.message.edit_text(
        "✅ <b>Спасибо за оплату!</b>\n\n"
        "Мы проверим поступление и подтвердим в течение 15 минут.\n"
        "Если вопросы — пишите напрямую."
    )

    if ADMIN_ID and amount:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"💰 <b>Клиент оплатил!</b>\n\n"
                f"Клиент: {user.full_name}\n"
                f"TG: {username}\n"
                f"Сумма: <b>${amount:.2f}</b>\n\n"
                f"Проверь поступление на карту.",
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")

    if user_id in user_amounts:
        del user_amounts[user_id]


# ── Запуск ─────────────────────────────────────────────────────

async def main():
    _acquire_lock()
    try:
        logger.info("Payment bot starting (PID %s)...", os.getpid())
        await dp.start_polling(bot)
    finally:
        _release_lock()
        logger.info("Payment bot stopped.")


if __name__ == "__main__":
    asyncio.run(main())
