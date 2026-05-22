import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "4278320023470544")
CARD_HOLDER = os.getenv("CARD_HOLDER", "ENZHE GAINEMUKHAMETOVA")
CARD_TYPE = os.getenv("CARD_TYPE", "VISA (USD)")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+7 927 479 3004")

# Ссылка на материал, выдаваемый после подтверждения оплаты. Можно перебить
# через .env (одна общая ссылка для всех продуктов — для placeholder-режима).
DOWNLOAD_URL_DEFAULT = os.getenv(
    "DOWNLOAD_URL", "https://example.com/service-upgrade-material.pdf"
)

LANGUAGES = ("ru", "en")
DEFAULT_LANG = "ru"

# ── Продукты (по сценарию) ─────────────────────────────────────
# Beauty / Medical / Dental — $50, тренинг — $350. У каждого своя ссылка
# на скачивание материала (пока placeholder; подменим позже).
PRODUCTS = {
    "beauty": {
        "price": 50.0,
        "name": {
            "ru": "Service Upgrade Beauty",
            "en": "Service Upgrade Beauty",
        },
        "description": {
            "ru": (
                "💇 <b>Service Upgrade Beauty — $50</b>\n\n"
                "Гайд по работе администраторов салонов красоты:\n"
                "• Скрипты переписки с клиентами\n"
                "• Чек-листы ошибок и как их избежать\n"
                "• Шаблоны для увеличения записей\n"
            ),
            "en": (
                "💇 <b>Service Upgrade Beauty — $50</b>\n\n"
                "Guide for beauty salon administrators:\n"
                "• Client chat scripts\n"
                "• Checklists of mistakes and how to avoid them\n"
                "• Templates to grow bookings\n"
            ),
        },
        "download_url": DOWNLOAD_URL_DEFAULT,
    },
    "medical": {
        "price": 50.0,
        "name": {
            "ru": "Service Upgrade Medical",
            "en": "Service Upgrade Medical",
        },
        "description": {
            "ru": (
                "🏥 <b>Service Upgrade Medical — $50</b>\n\n"
                "Гайд для администраторов медицинских клиник:\n"
                "• Скрипты звонков и переписки\n"
                "• Работа с возражениями пациентов\n"
                "• Чек-листы конверсии в запись\n"
            ),
            "en": (
                "🏥 <b>Service Upgrade Medical — $50</b>\n\n"
                "Guide for medical clinic administrators:\n"
                "• Call and chat scripts\n"
                "• Handling patient objections\n"
                "• Booking-conversion checklists\n"
            ),
        },
        "download_url": DOWNLOAD_URL_DEFAULT,
    },
    "dental": {
        "price": 50.0,
        "name": {
            "ru": "Service Upgrade Dental",
            "en": "Service Upgrade Dental",
        },
        "description": {
            "ru": (
                "🦷 <b>Service Upgrade Dental — $50</b>\n\n"
                "Гайд для администраторов стоматологий:\n"
                "• Скрипты записи и удержания пациентов\n"
                "• Работа со страхами и ценой\n"
                "• Шаблоны напоминаний и follow-up\n"
            ),
            "en": (
                "🦷 <b>Service Upgrade Dental — $50</b>\n\n"
                "Guide for dental clinic administrators:\n"
                "• Booking and retention scripts\n"
                "• Handling fear and price objections\n"
                "• Reminder and follow-up templates\n"
            ),
        },
        "download_url": DOWNLOAD_URL_DEFAULT,
    },
    "training": {
        "price": 350.0,
        "name": {
            "ru": "Service Upgrade System (тренинг)",
            "en": "Service Upgrade System (training)",
        },
        "description": {
            "ru": (
                "🎓 <b>Service Upgrade System — Тренинг — $350</b>\n\n"
                "Полный тренинг для команды:\n"
                "• Все три гайда (Beauty + Medical + Dental)\n"
                "• Видео-разборы и кейсы\n"
                "• Сопровождение внедрения\n"
                "• Поддержка в чате\n"
            ),
            "en": (
                "🎓 <b>Service Upgrade System — Training — $350</b>\n\n"
                "Full team training:\n"
                "• All three guides (Beauty + Medical + Dental)\n"
                "• Video walkthroughs and cases\n"
                "• Implementation support\n"
                "• Chat support\n"
            ),
        },
        "download_url": DOWNLOAD_URL_DEFAULT,
    },
}

# ── Локализация интерфейса ─────────────────────────────────────
TEXTS = {
    "ru": {
        "choose_lang": "🌐 Выберите язык / Choose language:",
        "welcome": (
            "Добро пожаловать в <b>Service Upgrade System!</b> 💫\n\n"
            "Здесь вы найдёте готовые инструменты, которые помогают салонам, "
            "клиникам и малому бизнесу увеличивать записи без дополнительных "
            "затрат на рекламу!\n\n"
            "Пожалуйста, напишите ваше <b>ФИО</b>:"
        ),
        "ask_phone": "Пришлите ваш <b>номер для связи</b>:",
        "invalid_fio": "❌ Введите ФИО (минимум 2 слова, только буквы):",
        "invalid_phone": "❌ Введите телефон в формате +7XXXXXXXXXX или 8XXXXXXXXXX:",
        "info_received": (
            "Благодарю за информацию 🤝\n"
            "Выберите ниже, какой продукт хотите приобрести:"
        ),
        "greeting_returning": "С возвращением, {name}! 👋\n\n💳 <b>Выберите продукт:</b>",
        "product_card_btn": "💳 Оплатить — ${price:.2f}",
        "back_btn": "◀️ Назад",
        "cancel_btn": "❌ Отменить",
        "change_lang_btn": "🌐 EN",
        "payment_info": (
            "<b>Заказ №{order_id}</b>\n"
            "Продукт: <b>{product}</b>\n"
            "Стоимость: <b>${price:.2f}</b>\n\n"
            "Пожалуйста, переведите по номеру:\n"
            "<code>{card}</code>\n"
            "<b>{holder}</b>\n\n"
            "После оплаты пришлите чек и нажмите «Я оплатил»\n\n"
            "<i>Сумма уникальна для вашей заявки — переведите ровно "
            "${price:.2f}. Заявка действительна 2 часа.</i>"
        ),
        "paid_btn": "✅ Я оплатил",
        "no_active_payment": (
            "❌ У вас нет активной заявки или она устарела.\n"
            "Начните заново через /start"
        ),
        "ask_receipt": (
            "📸 Пришлите скриншот чека об оплате.\n"
            "Если чека нет — нажмите «Пропустить»."
        ),
        "receipt_skip_btn": "⏭️ Пропустить",
        "wait_review": "Спасибо! Проверим оплату в течение <b>15 мин</b> ⌚️",
        "photo_no_context": (
            "ℹ️ Чтобы прислать чек, сначала выберите продукт и нажмите «Я оплатил». /start"
        ),
        "client_confirmed": (
            "Оплата прошла успешно! 🙌🏻\n"
            "Ниже вы получите доступ к материалу, который поможет выявить "
            "ошибки в переписке с клиентами.\n\n"
            "<b>Что важно сделать дальше:</b>\n"
            "✔️ Изучите материал полностью.\n"
            "✔️ Передайте его администраторам или менеджерам.\n"
            "✔️ Внедрите рекомендации в ежедневную работу.\n"
            "✔️ Начните отслеживать конверсию и результаты.\n\n"
            "⚠️ <b>Важно:</b> сам материал даёт понимание и готовые "
            "инструменты, но максимальный результат достигается при "
            "правильном внедрении и регулярном контроле."
        ),
        "download_btn": "📥 СКАЧАТЬ ФАЙЛ",
        "client_rejected": (
            "Кажется, оплата не прошла :(\n"
            "Проверьте, правильную ли сумму вы отправили и пришлите чек заново.\n\n"
            "Заявка: <b>#ORDER-{order_id}</b> на сумму <b>${price:.2f}</b>.\n"
            "Поддержка: {phone}"
        ),
        "fallback": "ℹ️ Используйте кнопки или команду /start.",
        "rate_limit": "⏱️ Подождите несколько секунд",
        "help": (
            "<b>📖 Как пользоваться ботом:</b>\n\n"
            "1️⃣ Введите ФИО и телефон\n"
            "2️⃣ Выберите продукт\n"
            "3️⃣ Получите номер заявки и точную сумму\n"
            "4️⃣ Переведите ровно эту сумму на карту\n"
            "5️⃣ Нажмите «Я оплатил» и пришлите чек\n"
            "6️⃣ Ожидайте подтверждения (до 15 минут)\n\n"
            "Поддержка: {phone}"
        ),
        "admin_new_user": (
            "👤 <b>Новый клиент</b>\n"
            "Имя: {name}\nTG: {username}\nID: <code>{user_id}</code>"
        ),
        "admin_contact_collected": (
            "📋 <b>Контакт получен</b>\n"
            "ФИО: <b>{fio}</b>\n"
            "Телефон: <b>{phone}</b>\n"
            "TG: {username}\n"
            "ID: <code>{user_id}</code>"
        ),
        "admin_review": (
            "💰 <b>Заявка на проверку</b> {screenshot}\n\n"
            "Заявка: <b>#ORDER-{order_id}</b>\n"
            "ФИО: <b>{fio}</b>\n"
            "Телефон: <b>{phone}</b>\n"
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
        "welcome": (
            "Welcome to <b>Service Upgrade System!</b> 💫\n\n"
            "Here you'll find ready-to-use tools that help salons, clinics "
            "and small businesses grow bookings without extra ad spend!\n\n"
            "Please enter your <b>full name</b>:"
        ),
        "ask_phone": "Please send your <b>contact phone number</b>:",
        "invalid_fio": "❌ Enter your full name (at least 2 words, letters only):",
        "invalid_phone": "❌ Enter a phone number in international format (e.g. +1234567890):",
        "info_received": (
            "Thank you for the info 🤝\n"
            "Please choose which product you'd like to purchase:"
        ),
        "greeting_returning": "Welcome back, {name}! 👋\n\n💳 <b>Choose a product:</b>",
        "product_card_btn": "💳 Pay — ${price:.2f}",
        "back_btn": "◀️ Back",
        "cancel_btn": "❌ Cancel",
        "change_lang_btn": "🌐 RU",
        "payment_info": (
            "<b>Order №{order_id}</b>\n"
            "Product: <b>{product}</b>\n"
            "Price: <b>${price:.2f}</b>\n\n"
            "Please transfer to the card:\n"
            "<code>{card}</code>\n"
            "<b>{holder}</b>\n\n"
            "After payment, send the receipt and tap «I have paid»\n\n"
            "<i>The amount is unique to your order — transfer exactly "
            "${price:.2f}. Order valid for 2 hours.</i>"
        ),
        "paid_btn": "✅ I have paid",
        "no_active_payment": (
            "❌ You have no active order or it has expired.\n"
            "Start again with /start"
        ),
        "ask_receipt": (
            "📸 Send a screenshot of the payment receipt.\n"
            "If you don't have one — tap «Skip»."
        ),
        "receipt_skip_btn": "⏭️ Skip",
        "wait_review": "Thank you! We will verify the payment within <b>15 min</b> ⌚️",
        "photo_no_context": (
            "ℹ️ To send a receipt, first choose a product and tap «I have paid». /start"
        ),
        "client_confirmed": (
            "Payment successful! 🙌🏻\n"
            "Below you'll get access to the material that helps spot mistakes "
            "in client conversations.\n\n"
            "<b>What to do next:</b>\n"
            "✔️ Study the material fully.\n"
            "✔️ Share it with your administrators or managers.\n"
            "✔️ Apply the recommendations in daily work.\n"
            "✔️ Start tracking conversion and results.\n\n"
            "⚠️ <b>Important:</b> the material provides understanding and "
            "ready tools, but maximum results come from proper "
            "implementation and regular control."
        ),
        "download_btn": "📥 DOWNLOAD FILE",
        "client_rejected": (
            "Looks like the payment didn't go through :(\n"
            "Please double-check the amount and resend the receipt.\n\n"
            "Order: <b>#ORDER-{order_id}</b> for <b>${price:.2f}</b>.\n"
            "Support: {phone}"
        ),
        "fallback": "ℹ️ Use the buttons or /start command.",
        "rate_limit": "⏱️ Please wait a few seconds",
        "help": (
            "<b>📖 How to use the bot:</b>\n\n"
            "1️⃣ Enter your full name and phone\n"
            "2️⃣ Choose a product\n"
            "3️⃣ Get your order number and exact amount\n"
            "4️⃣ Transfer exactly that amount to the card\n"
            "5️⃣ Tap «I have paid» and send the receipt\n"
            "6️⃣ Wait for confirmation (up to 15 minutes)\n\n"
            "Support: {phone}"
        ),
        "admin_new_user": (
            "👤 <b>New client</b>\n"
            "Name: {name}\nTG: {username}\nID: <code>{user_id}</code>"
        ),
        "admin_contact_collected": (
            "📋 <b>Contact collected</b>\n"
            "Full name: <b>{fio}</b>\n"
            "Phone: <b>{phone}</b>\n"
            "TG: {username}\n"
            "ID: <code>{user_id}</code>"
        ),
        "admin_review": (
            "💰 <b>Order awaiting review</b> {screenshot}\n\n"
            "Order: <b>#ORDER-{order_id}</b>\n"
            "Full name: <b>{fio}</b>\n"
            "Phone: <b>{phone}</b>\n"
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
