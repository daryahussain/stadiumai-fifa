import logging

from contextlib import asynccontextmanager

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from slowapi import _rate_limit_exceeded_handler
from slowapi.errors import RateLimitExceeded

from app.core.config import settings
from app.api import auth, chat, crowd, dashboard, navigation, notifications, reports, sustainability, transport, translation
from app.services.crowd_simulator import simulator

logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    logger.info(f"CORS origins: {settings.BACKEND_CORS_ORIGINS}")
    await simulator.start()
    yield
    await simulator.stop()


app = FastAPI(
    title=settings.PROJECT_NAME,
    version=settings.VERSION,
    openapi_url=f"{settings.API_V1_STR}/openapi.json",
    lifespan=lifespan,
)

app.state.limiter = settings.LIMITER
app.add_exception_handler(RateLimitExceeded, _rate_limit_exceeded_handler)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router, prefix=f"{settings.API_V1_STR}/auth", tags=["auth"])
app.include_router(chat.router, prefix=f"{settings.API_V1_STR}/chat", tags=["chat"])
app.include_router(crowd.router, prefix=f"{settings.API_V1_STR}/crowd", tags=["crowd"])
app.include_router(dashboard.router, prefix=f"{settings.API_V1_STR}/dashboard", tags=["dashboard"])
app.include_router(navigation.router, prefix=f"{settings.API_V1_STR}/navigation", tags=["navigation"])
app.include_router(notifications.router, prefix=f"{settings.API_V1_STR}/notifications", tags=["notifications"])
app.include_router(reports.router, prefix=f"{settings.API_V1_STR}/reports", tags=["reports"])
app.include_router(sustainability.router, prefix=f"{settings.API_V1_STR}/sustainability", tags=["sustainability"])
app.include_router(transport.router, prefix=f"{settings.API_V1_STR}/transport", tags=["transport"])
app.include_router(translation.router, prefix=f"{settings.API_V1_STR}/translation", tags=["translation"])


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
        "cors_origins": settings.BACKEND_CORS_ORIGINS,
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
