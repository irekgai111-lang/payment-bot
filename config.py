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
        "name": {"ru": "Демо-продукт A", "en": "Demo Product A"},
        "short": {"ru": "Стартовый пакет", "en": "Starter pack"},
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
        "name": {"ru": "Демо-продукт B", "en": "Demo Product B"},
        "short": {"ru": "Премиум пакет", "en": "Premium pack"},
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
        "greeting": "Привет, {name}! 👋\n\n💳 <b>Выберите продукт:</b>",
        "product_card_btn": "💳 Оплатить — ${price:.2f}",
        "back_btn": "◀️ Назад",
        "cancel_btn": "❌ Отменить",
        "change_lang_btn": "🌐 EN",
        "payment_title": "💳 <b>Реквизиты для оплаты</b>",
        "payment_info": (
            "{title}\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n"
            "Продукт: <b>{product}</b>\n"
            "Сумма к оплате: <b>${price:.2f}</b>\n\n"
            "Тип карты: <b>{card_type}</b>\n"
            "Номер карты:\n<code>{card}</code>\n"
            "Получатель: <b>{holder}</b>\n\n"
            "⚠️ <b>Важно:</b>\n"
            "• Переведите <b>ровно ${price:.2f}</b> — сумма уникальна для вашей заявки.\n"
            "• В комментарии перевода укажите: <code>#ORDER-{order_id}</code>\n"
            "• Заявка действительна 2 часа.\n\n"
            "После перевода нажмите кнопку ниже 👇"
        ),
        "paid_btn": "✅ Я оплатил",
        "no_active_payment": (
            "❌ У вас нет активной заявки или она устарела.\n"
            "Начните заново через /start"
        ),
        "ask_receipt": (
            "📸 <b>Пришлите скриншот чека об оплате</b>\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n\n"
            "Это ускорит проверку. Отправьте одно фото в этот чат.\n"
            "Если чека нет — нажмите «Пропустить»."
        ),
        "receipt_skip_btn": "⏭️ Пропустить",
        "receipt_received": (
            "✅ Скриншот получен, заявка отправлена администратору.\n"
            "Ожидайте подтверждения — мы напишем сюда после сверки."
        ),
        "receipt_skipped": (
            "Хорошо, проверим оплату вручную.\n"
            "Это может занять чуть больше времени — мы напишем сюда после сверки."
        ),
        "photo_no_context": (
            "ℹ️ Чтобы прислать чек, сначала выберите продукт и нажмите «Я оплатил». /start"
        ),
        "client_confirmed": (
            "✅ <b>Оплата подтверждена!</b>\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n"
            "Продукт: <b>{product}</b>\n"
            "Сумма: <b>${price:.2f}</b>\n\n"
            "Спасибо! Мы свяжемся для выдачи продукта.\n"
            "Поддержка: {phone}"
        ),
        "client_rejected": (
            "❌ <b>Оплата не подтверждена</b>\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n"
            "Сумма: <b>${price:.2f}</b>\n\n"
            "Возможные причины: средства не поступили, сумма не совпала, "
            "истёк срок ожидания.\n"
            "Свяжитесь с поддержкой: {phone}"
        ),
        "fallback": "ℹ️ Используйте кнопки или команду /start.",
        "rate_limit": "⏱️ Подождите несколько секунд",
        "help": (
            "<b>📖 Как пользоваться ботом:</b>\n\n"
            "1️⃣ Выберите продукт\n"
            "2️⃣ Получите номер заявки и точную сумму\n"
            "3️⃣ Переведите ровно эту сумму на карту\n"
            "4️⃣ Нажмите «Я оплатил» и пришлите скриншот\n"
            "5️⃣ Дождитесь подтверждения администратора\n\n"
            "Поддержка: {phone}"
        ),
        "admin_new_user": (
            "👤 <b>Новый клиент</b>\n"
            "Имя: {name}\nTG: {username}\nID: <code>{user_id}</code>"
        ),
        "admin_review": (
            "💰 <b>Заявка на проверку</b> {screenshot}\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n"
            "Клиент: {name}\n"
            "TG: {username}\n"
            "ID: <code>{user_id}</code>\n"
            "Продукт: {product}\n"
            "Каталог: ${base_price:.2f}\n"
            "💵 К зачислению: <b>${price:.2f}</b>\n"
            "Создана: {time}\n\n"
            "⚠️ Сверьте сумму с банком и нажмите ✅ или ❌"
        ),
    },
    "en": {
        "choose_lang": "🌐 Choose language / Выберите язык:",
        "greeting": "Hi, {name}! 👋\n\n💳 <b>Choose a product:</b>",
        "product_card_btn": "💳 Pay — ${price:.2f}",
        "back_btn": "◀️ Back",
        "cancel_btn": "❌ Cancel",
        "change_lang_btn": "🌐 RU",
        "payment_title": "💳 <b>Payment details</b>",
        "payment_info": (
            "{title}\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n"
            "Product: <b>{product}</b>\n"
            "Amount due: <b>${price:.2f}</b>\n\n"
            "Card type: <b>{card_type}</b>\n"
            "Card number:\n<code>{card}</code>\n"
            "Recipient: <b>{holder}</b>\n\n"
            "⚠️ <b>Important:</b>\n"
            "• Transfer <b>exactly ${price:.2f}</b> — the amount is unique to your order.\n"
            "• In the transfer comment specify: <code>#ORDER-{order_id}</code>\n"
            "• The order is valid for 2 hours.\n\n"
            "After the transfer, tap the button below 👇"
        ),
        "paid_btn": "✅ I have paid",
        "no_active_payment": (
            "❌ You have no active order or it has expired.\n"
            "Start again with /start"
        ),
        "ask_receipt": (
            "📸 <b>Please send a screenshot of the payment receipt</b>\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n\n"
            "It speeds up verification. Send one photo to this chat.\n"
            "If you don't have a receipt — tap «Skip»."
        ),
        "receipt_skip_btn": "⏭️ Skip",
        "receipt_received": (
            "✅ Screenshot received, your order is forwarded to the administrator.\n"
            "Wait for confirmation — we will write here after verification."
        ),
        "receipt_skipped": (
            "Okay, we'll verify the payment manually.\n"
            "This may take a bit longer — we will write here after verification."
        ),
        "photo_no_context": (
            "ℹ️ To send a receipt, first choose a product and tap «I have paid». /start"
        ),
        "client_confirmed": (
            "✅ <b>Payment confirmed!</b>\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n"
            "Product: <b>{product}</b>\n"
            "Amount: <b>${price:.2f}</b>\n\n"
            "Thank you! We will contact you to deliver the product.\n"
            "Support: {phone}"
        ),
        "client_rejected": (
            "❌ <b>Payment was not confirmed</b>\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n"
            "Amount: <b>${price:.2f}</b>\n\n"
            "Possible reasons: funds not received, amount mismatch, timeout.\n"
            "Contact support: {phone}"
        ),
        "fallback": "ℹ️ Use the buttons or the /start command.",
        "rate_limit": "⏱️ Please wait a few seconds",
        "help": (
            "<b>📖 How to use the bot:</b>\n\n"
            "1️⃣ Choose a product\n"
            "2️⃣ Get your order number and exact amount\n"
            "3️⃣ Transfer exactly that amount to the card\n"
            "4️⃣ Tap «I have paid» and send the screenshot\n"
            "5️⃣ Wait for admin confirmation\n\n"
            "Support: {phone}"
        ),
        "admin_new_user": (
            "👤 <b>New client</b>\n"
            "Name: {name}\nTG: {username}\nID: <code>{user_id}</code>"
        ),
        "admin_review": (
            "💰 <b>Order awaiting review</b> {screenshot}\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n"
            "Client: {name}\n"
            "TG: {username}\n"
            "ID: <code>{user_id}</code>\n"
            "Product: {product}\n"
            "Catalog: ${base_price:.2f}\n"
            "💵 To receive: <b>${price:.2f}</b>\n"
            "Created: {time}\n\n"
            "⚠️ Verify the amount with the bank and tap ✅ or ❌"
        ),
    },
}
