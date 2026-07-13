import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import auth, chat, crowd, dashboard, navigation, notifications, reports, seed, sustainability, transport, translation
from app.services.crowd_simulator import simulator

logger = logging.getLogger(__name__)


_ROUTERS = [
    (auth.router, "auth"),
    (chat.router, "chat"),
    (crowd.router, "crowd"),
    (dashboard.router, "dashboard"),
    (navigation.router, "navigation"),
    (notifications.router, "notifications"),
    (reports.router, "reports"),
    (seed.router, "seed"),
    (sustainability.router, "sustainability"),
    (transport.router, "transport"),
    (translation.router, "translation"),
]


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"CORS origins: {settings.cors_origins}")
    await simulator.start()
    yield
    await simulator.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = settings.limiter
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

for router, tag in _ROUTERS:
    app.include_router(router, prefix=f"{settings.API_V1_STR}/{tag}", tags=[tag])


@app.get("/")
async def root():
    return {
        "message": "StadiumAI API",
        "version": settings.VERSION,
        "docs": "/docs",
    }


@app.get("/health")
async def health():
    return {"status": "healthy"}


@app.get("/config")
async def config():
    return {
        "cors_origins": settings.cors_origins,
        "database_url": settings.DATABASE_URL.replace(settings.DATABASE_URL.split("@")[-1], "***") if "@" in settings.DATABASE_URL else "sqlite",
        "project": settings.PROJECT_NAME,
        "version": settings.VERSION,
    }


@app.websocket("/ws/crowd")
async def crowd_websocket(ws: WebSocket):
    await ws.accept()
    queue = simulator.add_listener()
    try:
        while True:
            data = await queue.get()
            await ws.send_json(data)
    except WebSocketDisconnect:
        pass
    finally:
        simulator.remove_listener(queue)
