from __future__ import annotations

import asyncio
from datetime import datetime, timezone
from pathlib import Path

from fastapi import FastAPI, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from .config import settings
from .models import BotState
from .polymarket import PolymarketClient
from .strategy import MeanReversionStrategy
from .trader import PaperTrader

BASE_DIR = Path(__file__).parent

app = FastAPI(title="Polymarket BTC 5m Mean Reversion Bot")
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))

state = BotState(mode="paper" if settings.paper_mode else "real")
client = PolymarketClient(settings.market_slug)
strategy = MeanReversionStrategy(window=settings.ma_window, z_threshold=settings.z_threshold)
trader = PaperTrader(order_size_usd=settings.order_size_usd, max_position_usd=settings.max_position_usd)
connections: set[WebSocket] = set()


@app.get("/", response_class=HTMLResponse)
@app.get("/dashboard", response_class=HTMLResponse)
async def dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})


@app.get("/health")
async def healthcheck():
    return {"ok": True, "ts": datetime.now(timezone.utc).isoformat()}


@app.get("/api/state")
async def get_state():
    return state.to_dict()


@app.post("/api/mode/{mode}")
async def set_mode(mode: str):
    if mode not in {"paper", "real"}:
        return {"ok": False, "error": "mode must be paper|real"}
    state.mode = mode
    return {"ok": True, "mode": state.mode}


async def broadcast(payload: dict):
    stale = []
    for ws in connections:
        try:
            await ws.send_json(payload)
        except Exception:
            stale.append(ws)
    for ws in stale:
        connections.discard(ws)


@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket.accept()
    connections.add(websocket)
    try:
        await websocket.send_json(state.to_dict())
        while True:
            await websocket.receive_text()
    except WebSocketDisconnect:
        connections.discard(websocket)


async def bot_loop():
    while True:
        try:
            price, ts = await client.get_price()
            out = strategy.on_price(price)

            fill = None
            if state.mode == "paper":
                fill = trader.execute(out["signal"], price)

            state.last_price = round(price, 4)
            state.moving_avg = round(out["moving_avg"], 4)
            state.zscore = round(out["zscore"], 3)
            state.signal = out["signal"]
            state.position_qty = round(trader.qty, 4)
            state.realized_pnl = round(trader.realized_pnl, 4)
            state.unrealized_pnl = round(trader.unrealized(price), 4)
            state.equity = round(10000 + state.realized_pnl + state.unrealized_pnl, 4)
            state.last_update = ts.isoformat()
            state.last_error = ""

            payload = state.to_dict()
            payload["fill"] = fill.__dict__ if fill else None
            await broadcast(payload)
        except Exception as exc:
            state.last_error = str(exc)
            state.last_update = datetime.now(timezone.utc).isoformat()
            await broadcast(state.to_dict())

        await asyncio.sleep(settings.poll_interval_sec)


@app.on_event("startup")
async def on_startup():
    asyncio.create_task(bot_loop())
