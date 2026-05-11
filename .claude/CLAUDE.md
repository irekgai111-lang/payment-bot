# Service Upgrade System — контекст для Claude

Telegram-бот продажи гайда «Обучение администраторов» (автор: Энже Гайнемухаметова).
Клиент выбирает один из двух вариантов продукта → видит реквизиты карты → переводит деньги → нажимает «Я оплатил» → получает PDF-гайд.

**GitHub:** https://github.com/irekgai111-lang/service-upgrade-system

## Стек
- Python 3.12, aiogram 3.27.0, python-dotenv 1.2.2
- SQLite (`payments.db`) — встроенная БД платежей
- Запуск: `python bot.py` из папки `service-upgrade-system/`
- Защита от двойного запуска через PID-файл `bot.pid`
- Rate limiting 5 сек между запросами

## Файлы
- `bot.py` — хэндлеры `/start`, `/help`, `/stats`, выбор продукта, реквизиты, подтверждение оплаты, отдача `guide.pdf`
- `config.py` — словарь `PRODUCTS` (2 варианта) + чтение `.env`
- `.env` — `BOT_TOKEN`, `ADMIN_ID`, `CARD_NUMBER`, `CARD_HOLDER`, `SUPPORT_PHONE` (в `.gitignore`)
- `payments.db` — SQLite (создаётся автоматически; в `.gitignore`)
- `guide.pdf` — PDF, который высылается клиенту после оплаты (положить вручную)
- `plans/ROADMAP.md` — план доработок
- `docs/` — пользовательские сценарии и research

## Текущие продукты (config.py → PRODUCTS)
- `product_1` — Вариант 1, $29.99, «Базовый пакет»
- `product_2` — Вариант 2, $49.99, «Премиум пакет»

> Названия/цены меняются в `config.py`, перезапуск бота применяет изменения.

## Команды бота
- `/start` — приветствие и выбор варианта
- `/help` — справка + контакты + список вариантов
- `/stats` — количество и сумма pending-платежей (только `ADMIN_ID`)

## Карта оплаты
Visa `4278 3200 2347 0544`, держатель `ENZHE GAINEMUKHAMETOVA`.
Поддержка: `+7 927 479 3004`.

## Правила
- ⛔ **НИКОГДА не удалять папку `.git`**
- НЕ коммитить `.env`, `payments.db`, `bot.pid`, `bot_logs.log` (всё в `.gitignore`)
- Этот проект живёт только в `service-upgrade-system/` — копий бота в других папках не создавать
- После каждого изменения: `git commit` + `git push`
- Все сообщения боту — по-русски, обращение на «ты»

## Открытые задачи
См. `plans/ROADMAP.md`.
