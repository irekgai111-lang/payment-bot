import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "")
CARD_HOLDER = os.getenv("CARD_HOLDER", "CARD HOLDER")
SUPPORT_PHONE = os.getenv("SUPPORT_PHONE", "+7 927 479 3004")

# ── Два варианта продукта ──────────────────────────────────────
PRODUCTS = {
    "product_1": {
        "name": "Вариант 1",
        "price": 29.99,
        "description": "Базовый пакет"
    },
    "product_2": {
        "name": "Вариант 2",
        "price": 49.99,
        "description": "Премиум пакет"
    },
}
