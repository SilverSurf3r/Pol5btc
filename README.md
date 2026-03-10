# Pol5btc — Polymarket BTC mean-reversion bot (5m)

Бот для торговли отклонением от средней на рынке прогнозов BTC в Polymarket.

## Что есть
- Стратегия mean reversion по Z-score на скользящей средней.
- Режимы:
  - `paper` (эмуляция, по умолчанию)
  - `real` (пока безопасный каркас без отправки реальных ордеров)
- Веб-дашборд (FastAPI + WebSocket):
  - цена, MA, Z-score, сигнал, позиция, PnL
  - лента событий
  - переключение режима
  - звуковые сигналы BUY/SELL (генерируются в браузере через Web Audio API, без бинарных файлов)
  - WalletConnect login UI
- Healthcheck endpoint для деплоя: `/health`.

## Локальный запуск
```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
uvicorn app.main:app --host 0.0.0.0 --port 8000
```
Откройте `http://localhost:8000` (или `http://localhost:8000/dashboard`).

## Конфигурация
Скопируйте `.env.example` в `.env` и при необходимости измените:

```env
POLYMARKET_MARKET_SLUG=will-bitcoin-price-be-above-100000-on-may-31
POLL_INTERVAL_SEC=15
MA_WINDOW=12
Z_THRESHOLD=1.3
ORDER_SIZE_USD=25
MAX_POSITION_USD=200
PAPER_MODE=true
```

## Деплой на Railway
Проект подготовлен для Railway:
- `Procfile` c командой старта `uvicorn ... --port $PORT`
- `railway.json` c healthcheck по `/health`
- `.env.example` для удобного задания переменных

Шаги:
1. Создайте новый Railway project и подключите репозиторий.
2. Добавьте переменные окружения из `.env.example`.
3. Деплой выполнится автоматически, проверка здоровья — `/health`.

## WalletConnect
Для рабочей авторизации нужен ваш WalletConnect Project ID.
В текущем UI можно сохранить его в браузере:

```js
localStorage.setItem('walletconnect_project_id', 'YOUR_PROJECT_ID')
```

## Дисклеймер
Не финансовый совет. Используйте на свой риск.
