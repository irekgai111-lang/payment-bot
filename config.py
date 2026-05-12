import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "4278320023470544")
CARD_HOLDER = os.getenv("CARD_HOLDER", "Enzhe")
CARD_TYPE = os.getenv("CARD_TYPE", "VISA (USD)")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+7 927 479 3004")

LANGUAGES = ("ru", "en")
DEFAULT_LANG = "ru"

# ── Два демо-продукта ──────────────────────────────────────────
PRODUCTS = {
    "product_1": {
        "price": 19.99,
        "name": {
            "ru": "Демо-продукт A",
            "en": "Demo Product A",
        },
        "short": {
            "ru": "Стартовый пакет",
            "en": "Starter pack",
        },
        "description": {
            "ru": (
                "📦 <b>Демо-продукт A — Стартовый пакет</b>\n\n"
                "Что входит:\n"
                "• Базовое руководство (PDF)\n"
                "• Шаблоны для быстрого старта\n"
                "• Доступ к материалам на 30 дней\n\n"
                "Подходит для тех, кто только начинает."
            ),
            "en": (
                "📦 <b>Demo Product A — Starter pack</b>\n\n"
                "What's included:\n"
                "• Basic guide (PDF)\n"
                "• Quick-start templates\n"
                "• 30 days access to materials\n\n"
                "Best for beginners."
            ),
        },
    },
    "product_2": {
        "price": 49.99,
        "name": {
            "ru": "Демо-продукт B",
            "en": "Demo Product B",
        },
        "short": {
            "ru": "Премиум пакет",
            "en": "Premium pack",
        },
        "description": {
            "ru": (
                "💎 <b>Демо-продукт B — Премиум пакет</b>\n\n"
                "Что входит:\n"
                "• Полное руководство (PDF)\n"
                "• Расширенные шаблоны и чек-листы\n"
                "• Видео-разборы\n"
                "• Доступ к материалам навсегда\n"
                "• Поддержка в чате\n\n"
                "Полный пакет для серьёзной работы."
            ),
            "en": (
                "💎 <b>Demo Product B — Premium pack</b>\n\n"
                "What's included:\n"
                "• Full guide (PDF)\n"
                "• Advanced templates and checklists\n"
                "• Video walkthroughs\n"
                "• Lifetime access to materials\n"
                "• Chat support\n\n"
                "The complete package for serious work."
            ),
        },
    },
}

# ── Локализация интерфейса ─────────────────────────────────────
TEXTS = {
    "ru": {
        "choose_lang": "🌐 Выберите язык / Choose language:",
        "greeting": (
            "Привет, {name}! 👋\n\n"
            "💳 <b>Выберите продукт:</b>"
        ),
        "product_card_btn": "💳 Оплатить — ${price:.2f}",
        "back_btn": "◀️ Назад",
        "change_lang_btn": "🌐 EN",
        "payment_title": "💳 <b>Реквизиты для оплаты</b>",
        "payment_info": (
            "{title}\n\n"
            "Продукт: <b>{product}</b>\n"
            "Сумма: <b>${price:.2f}</b>\n\n"
            "Тип карты: <b>{card_type}</b>\n"
            "Номер карты:\n"
            "<code>{card}</code>\n"
            "Получатель: <b>{holder}</b>\n\n"
            "⚠️ <b>Переведите ровно эту сумму в долларах США.</b>\n\n"
            "После перевода нажмите кнопку ниже 👇"
        ),
        "paid_btn": "✅ Я оплатил",
        "paid_confirm": (
            "✅ <b>Спасибо за оплату!</b>\n\n"
            "Мы проверим поступление в течение 10–15 минут.\n"
            "После подтверждения вы получите доступ к продукту.\n\n"
            f"По вопросам: {SUPPORT_PHONE}"
        ),
        "no_product": "❌ Сначала выберите продукт через /start",
        "rate_limit": "⏱️ Подождите несколько секунд",
        "help": (
            "<b>📖 Как пользоваться ботом:</b>\n\n"
            "1️⃣ Выберите продукт\n"
            "2️⃣ Посмотрите описание и цену\n"
            "3️⃣ Нажмите «Оплатить»\n"
            "4️⃣ Переведите указанную сумму на карту\n"
            "5️⃣ Нажмите «Я оплатил»\n\n"
            "Поддержка: {phone}"
        ),
        "admin_new_user": "👤 <b>Новый клиент</b>\nИмя: {name}\nTG: {username}",
        "admin_paid": (
            "💰 <b>Клиент нажал «Я оплатил»</b>\n\n"
            "Клиент: {name}\n"
            "TG: {username}\n"
            "Продукт: {product}\n"
            "Сумма: <b>${price:.2f}</b>\n"
            "Время: {time}\n\n"
            "⚠️ <b>Проверьте поступление на карту!</b>"
        ),
        "ask_receipt": (
            "📸 <b>Пришлите скриншот чека об оплате</b>\n\n"
            "Это ускорит проверку. Отправьте одно фото в этот чат.\n"
            "Если чека нет — нажмите «Пропустить»."
        ),
        "receipt_skip_btn": "⏭️ Пропустить",
        "receipt_received": (
            "✅ Скриншот получен, передан администратору.\n"
            "Мы проверим поступление в течение 10–15 минут."
        ),
        "receipt_skipped": (
            "Хорошо, проверим оплату вручную.\n"
            "Это может занять чуть больше времени."
        ),
        "not_a_photo": "⚠️ Пришлите, пожалуйста, именно фото (скриншот чека).",
        "admin_receipt": (
            "🧾 <b>Скриншот чека</b>\n\n"
            "Клиент: {name}\n"
            "TG: {username}\n"
            "Продукт: {product}\n"
            "Сумма: <b>${price:.2f}</b>"
        ),
        "admin_receipt_skipped": (
            "⚠️ <b>Клиент пропустил скриншот</b>\n\n"
            "Клиент: {name}\n"
            "TG: {username}\n"
            "Продукт: {product}\n"
            "Сумма: <b>${price:.2f}</b>"
        ),
    },
    "en": {
        "choose_lang": "🌐 Choose language / Выберите язык:",
        "greeting": (
            "Hi, {name}! 👋\n\n"
            "💳 <b>Choose a product:</b>"
        ),
        "product_card_btn": "💳 Pay — ${price:.2f}",
        "back_btn": "◀️ Back",
        "change_lang_btn": "🌐 RU",
        "payment_title": "💳 <b>Payment details</b>",
        "payment_info": (
            "{title}\n\n"
            "Product: <b>{product}</b>\n"
            "Amount: <b>${price:.2f}</b>\n\n"
            "Card type: <b>{card_type}</b>\n"
            "Card number:\n"
            "<code>{card}</code>\n"
            "Recipient: <b>{holder}</b>\n\n"
            "⚠️ <b>Transfer the exact amount in US dollars.</b>\n\n"
            "After the transfer, tap the button below 👇"
        ),
        "paid_btn": "✅ I have paid",
        "paid_confirm": (
            "✅ <b>Thank you for your payment!</b>\n\n"
            "We will verify the transfer within 10–15 minutes.\n"
            "Once confirmed, you'll get access to the product.\n\n"
            f"Support: {SUPPORT_PHONE}"
        ),
        "no_product": "❌ Please choose a product first via /start",
        "rate_limit": "⏱️ Please wait a few seconds",
        "help": (
            "<b>📖 How to use the bot:</b>\n\n"
            "1️⃣ Choose a product\n"
            "2️⃣ Review the description and price\n"
            "3️⃣ Tap «Pay»\n"
            "4️⃣ Transfer the amount to the card\n"
            "5️⃣ Tap «I have paid»\n\n"
            "Support: {phone}"
        ),
        "admin_new_user": "👤 <b>New client</b>\nName: {name}\nTG: {username}",
        "admin_paid": (
            "💰 <b>Client tapped «I have paid»</b>\n\n"
            "Client: {name}\n"
            "TG: {username}\n"
            "Product: {product}\n"
            "Amount: <b>${price:.2f}</b>\n"
            "Time: {time}\n\n"
            "⚠️ <b>Check the card for the incoming transfer!</b>"
        ),
        "ask_receipt": (
            "📸 <b>Please send a screenshot of the payment receipt</b>\n\n"
            "It speeds up verification. Send one photo to this chat.\n"
            "If you don't have a receipt — tap «Skip»."
        ),
        "receipt_skip_btn": "⏭️ Skip",
        "receipt_received": (
            "✅ Screenshot received and forwarded to the administrator.\n"
            "We will verify the transfer within 10–15 minutes."
        ),
        "receipt_skipped": (
            "Okay, we'll verify the payment manually.\n"
            "This may take a bit longer."
        ),
        "not_a_photo": "⚠️ Please send a photo (a screenshot of the receipt).",
        "admin_receipt": (
            "🧾 <b>Payment receipt</b>\n\n"
            "Client: {name}\n"
            "TG: {username}\n"
            "Product: {product}\n"
            "Amount: <b>${price:.2f}</b>"
        ),
        "admin_receipt_skipped": (
            "⚠️ <b>Client skipped the receipt</b>\n\n"
            "Client: {name}\n"
            "TG: {username}\n"
            "Product: {product}\n"
            "Amount: <b>${price:.2f}</b>"
        ),
    },
}
