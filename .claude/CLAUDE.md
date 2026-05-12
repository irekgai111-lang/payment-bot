# Service Upgrade System — контекст для Claude

Telegram-бот приёма оплат **в долларах США на узбекскую карту**. Двуязычный (RU/EN), демо-режим.
Клиент в Узбекистане (получатель: Enzhe) принимает USD-переводы вручную; бот показывает реквизиты, собирает заявки и держит их в status-машине до ручного подтверждения админом.

**GitHub:** https://github.com/irekgai111-lang/payment-bot

## Стек

- Python 3.12, aiogram 3.27.0, python-dotenv 1.2.2
- SQLite (`payments.db`) — БД заявок и пользователей; источник истины состояния клиента (FSM не используется)
- Запуск: `python bot.py` из папки `service-upgrade-system/`
- PID-lock `bot.pid` против двойного запуска
- Rate limiting 3 сек между callback-запросами
- Фоновая задача `ttl_worker`: каждые 5 мин помечает зависшие заявки `expired` после 2 часов

## Файлы

- `bot.py` — хэндлеры, status-машина заявки, антифрод (уникальные суммы, идемпотентные переходы), TTL-воркер
- `config.py` — `PRODUCTS` (двуязычные), `TEXTS` (RU/EN), чтение `.env`
- `.env` — `BOT_TOKEN`, `ADMIN_ID`, `CARD_NUMBER`, `CARD_HOLDER`, `CARD_TYPE`, `SUPPORT_PHONE` (в `.gitignore`)
- `payments.db` — SQLite (создаётся автоматически; в `.gitignore`)
- `plans/ROADMAP.md` — план доработок
- `docs/RESEARCH.md` — рыночное и техническое исследование
- `docs/user-flow.md` — пользовательский сценарий
- `docs/OPERATIONS.md` — ежедневные операции для админа
- `start-bot.bat` — launcher для Windows Task Scheduler
- `bot_logs.log` — лог (в `.gitignore`)

## Схема БД

**payments** — заявки:
`id`, `user_id`, `name`, `username`, `product_key`, `product_name`, `base_amount` (цена каталога),
`amount` (уникальная сумма к оплате), `status`, `screenshot_file_id`, `created_at`, `reviewed_at`, `reviewed_by`.

**users** — пользователи:
`user_id`, `lang`, `first_seen_at`, `last_start_at`, `active_payment_id`.

## Status-машина заявки

```text
created → awaiting_receipt ──(фото)──→ awaiting_review ──(✅ админ)──→ confirmed
                          └─(skip)────→ awaiting_review ──(❌ админ)──→ rejected
                                                │
                                          (TTL 2 часа)
                                                ↓
                                            expired
```

Все переходы идемпотентны через `UPDATE ... WHERE status = ?` — повторный клик не пересчитывает.

## Антифрод

- **Уникальная сумма** на заявку: базовая цена минус случайные 0..29 центов, уникально среди активных заявок (`pick_unique_amount`). Защищает от присвоения чужого перевода.
- **Reference number** `#ORDER-{id}` в реквизитах + просьба указать в комментарии перевода.
- В админских уведомлениях — **`user_id`** (неподделываем) рядом с `@username`.
- Админу приходят inline-кнопки **✅ Подтвердить / ❌ Отклонить**; бот ничего не выдаёт автоматически.
- `/start` шлёт админу уведомление **только при первом** появлении пользователя (`users.first_seen_at`).
- Фото принимается **только** если у пользователя активная заявка `awaiting_receipt`.

## Persistence

Состояние клиента (выбранный язык, активная заявка) хранится в SQLite, не в памяти процесса. Рестарт бота не теряет ни клиентов в середине оплаты, ни язык интерфейса.

## Автозапуск (Windows Task Scheduler)

Задача `ServiceUpgradeBot`:

- Trigger: `AtLogOn`
- Action: `start-bot.bat` (cd в папку, удаление stale `bot.pid`, запуск `python bot.py`, логи в `bot_logs.log`)
- Restart: 3 попытки с интервалом 1 минута
- MultipleInstances: `IgnoreNew`

Управление:

- `Start-ScheduledTask -TaskName ServiceUpgradeBot`
- `Stop-ScheduledTask -TaskName ServiceUpgradeBot` (+ `Stop-Process -Name python`)
- `Get-ScheduledTaskInfo -TaskName ServiceUpgradeBot`

## Поток клиента

1. `/start` → выбор языка (RU/EN), сохраняется в `users.lang`
2. Список продуктов с ценами в USD
3. Клик по продукту → описание + кнопка «💳 Оплатить»
4. Создаётся заявка с уникальной суммой; показ реквизитов + `#ORDER-{id}` + просьба указать его в комментарии
5. Клиент жмёт «✅ Я оплатил» → бот просит скриншот (или кнопка «Пропустить»)
6. Бот шлёт админу карточку с кнопками ✅/❌
7. Админ сверяет с банком, жмёт ✅ или ❌
8. Клиенту приходит сообщение о подтверждении/отклонении

## Демо-продукты (config.py → PRODUCTS)

- `product_1` — Demo Product A / Стартовый пакет — **$19.99** базовая (клиенту видна уникальная)
- `product_2` — Demo Product B / Премиум пакет — **$49.99** базовая

Реальные продукты заказчик задаст позже.

## Команды бота

- `/start` — выбор языка → список продуктов
- `/help` — справка на текущем языке
- `/stats` — активные заявки (count + total), только `ADMIN_ID`

## Карта оплаты

VISA USD `4278 3200 2347 0544`, держатель `Enzhe` (Узбекистан). Только USD. Поддержка `+7 927 479 3004`.

## Почему ручной перевод

ЮKassa/CloudPayments не выплачивают на UZ-карты; Stripe не принимает UZ как страну получателя; Payme/Click — только UZS. Единственный рабочий вариант — ручной перевод + ручная сверка в банке. См. `docs/RESEARCH.md`.

## Правила

- ⛔ **НИКОГДА не удалять `.git`**
- НЕ коммитить `.env`, `payments.db`, `bot.pid`, `bot_logs.log`
- Бот живёт только в `service-upgrade-system/`
- После каждого изменения: `git commit` + `git push origin master`
- UI двуязычный (RU/EN), русский — на «вы», английский — нейтральный
- **Авто-выдача продукта выключена**: только админ переводит заявку в `confirmed` через ✅
- Все переходы статусов — через `UPDATE ... WHERE status = ?` (идемпотентность обязательна)

## Открытые задачи

См. `plans/ROADMAP.md`.
