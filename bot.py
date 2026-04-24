import asyncio
import logging
import os
import sys

from aiogram import Bot, Dispatcher, Router, F
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.filters import Command
from aiogram.types import (
    CallbackQuery,
    InlineKeyboardButton,
    InlineKeyboardMarkup,
    KeyboardButton,
    Message,
    ReplyKeyboardMarkup,
)

from config import ADMIN_ID, BOT_TOKEN, CARD_HOLDER, CARD_NUMBER, SERVICES

logging.basicConfig(level=logging.INFO, format="%(asctime)s [%(levelname)s] %(message)s")
logger = logging.getLogger(__name__)

# ── Защита от двойного запуска ─────────────────────────────────

PID_FILE = os.path.join(os.path.dirname(__file__), "bot.pid")


def _acquire_lock():
    if os.path.exists(PID_FILE):
        try:
            old_pid = int(open(PID_FILE).read().strip())
            # Проверяем, жив ли процесс
            os.kill(old_pid, 0)
            logger.error(
                f"Бот уже запущен (PID {old_pid}). "
                "Останови предыдущий процесс и попробуй снова."
            )
            sys.exit(1)
        except (ProcessLookupError, OSError):
            pass  # Старый процесс умер — PID-файл устарел, перезаписываем

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


def fmt_card(number: str) -> str:
    return " ".join(number[i: i + 4] for i in range(0, 16, 4))


def main_menu() -> ReplyKeyboardMarkup:
    return ReplyKeyboardMarkup(
        keyboard=[[KeyboardButton(text="💳 Оплатить")]],
        resize_keyboard=True,
    )


def services_keyboard() -> InlineKeyboardMarkup:
    buttons = [
        [InlineKeyboardButton(text=f"{s['name']} — {s['price']} ₽", callback_data=f"pay:{key}")]
        for key, s in SERVICES.items()
    ]
    return InlineKeyboardMarkup(inline_keyboard=buttons)


# ── /start ─────────────────────────────────────────────────────

@router.message(Command("start"))
async def cmd_start(message: Message):
    user = message.from_user
    await message.answer(
        f"Привет, {user.first_name}! 👋\n\n"
        "Это бот для оплаты <b>гайда по обучению администраторов</b>.\n"
        "Выбери формат и нажми кнопку ниже, чтобы оплатить.",
        reply_markup=main_menu(),
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


# ── Выбор услуги ───────────────────────────────────────────────

@router.message(F.text == "💳 Оплатить")
async def show_services(message: Message):
    await message.answer(
        "<b>Выберите услугу:</b>",
        reply_markup=services_keyboard(),
    )


# ── Реквизиты для оплаты ───────────────────────────────────────

@router.callback_query(F.data.startswith("pay:"))
async def show_payment_details(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 1)[1]
    service = SERVICES.get(key)
    if not service:
        await callback.message.edit_text("Услуга не найдена. Попробуй ещё раз.")
        return

    card = fmt_card(CARD_NUMBER)

    await callback.message.edit_text(
        f"💳 <b>Реквизиты для оплаты</b>\n\n"
        f"Услуга: <b>{service['name']}</b>\n"
        f"Сумма: <b>{service['price']} ₽</b>\n\n"
        f"Номер карты:\n"
        f"<code>{card}</code>\n"
        f"Получатель: <b>{CARD_HOLDER}</b>\n\n"
        f"Переведи точную сумму и нажми кнопку ниже 👇",
        reply_markup=InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="✅ Я оплатил", callback_data=f"paid:{key}")],
            [InlineKeyboardButton(text="◀️ Назад", callback_data="back")],
        ]),
    )


# ── Клиент нажал "Я оплатил" ───────────────────────────────────

@router.callback_query(F.data.startswith("paid:"))
async def payment_done(callback: CallbackQuery):
    await callback.answer()
    key = callback.data.split(":", 1)[1]
    service = SERVICES.get(key)
    user = callback.from_user
    username = f"@{user.username}" if user.username else "—"

    await callback.message.edit_text(
        "✅ <b>Спасибо за оплату!</b>\n\n"
        "Мы проверим поступление и подтвердим в течение 15 минут.\n"
        "Если вопросы — пишите напрямую."
    )

    if ADMIN_ID and service:
        try:
            await bot.send_message(
                ADMIN_ID,
                f"💰 <b>Клиент оплатил!</b>\n\n"
                f"Клиент: {user.full_name}\n"
                f"TG: {username}\n"
                f"Услуга: {service['name']}\n"
                f"Сумма: {service['price']} ₽\n\n"
                f"Проверь поступление на карту.",
            )
        except Exception as e:
            logger.error(f"Admin notify error: {e}")


# ── Назад к списку услуг ───────────────────────────────────────

@router.callback_query(F.data == "back")
async def go_back(callback: CallbackQuery):
    await callback.answer()
    await callback.message.edit_text(
        "<b>Выберите услугу:</b>",
        reply_markup=services_keyboard(),
    )


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
