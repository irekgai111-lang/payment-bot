import os
from dotenv import load_dotenv

load_dotenv()

BOT_TOKEN = os.getenv("BOT_TOKEN")
ADMIN_ID = int(os.getenv("ADMIN_ID", "0"))
CARD_NUMBER = os.getenv("CARD_NUMBER", "")
CARD_HOLDER = os.getenv("CARD_HOLDER", "CARD HOLDER")

# ── Услуги и цены ──────────────────────────────────────────────
# Гайд для администраторов салонов/студий
SERVICES = {
    "guide_basic": {
        "name": "Гайд «Администратор с нуля»",
        "price": 1990,
    },
    "guide_pro": {
        "name": "Гайд PRO + чек-листы и шаблоны",
        "price": 3490,
    },
    "guide_vip": {
        "name": "VIP: гайд + разбор 1-на-1 (60 мин)",
        "price": 6900,
    },
}
