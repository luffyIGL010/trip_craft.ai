from contextlib import asynccontextmanager
from pathlib import Path
from typing import Any

from fastapi import FastAPI, Depends, HTTPException, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import RedirectResponse
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates

from app.config import settings
from app.db.database import init_db
from app.auth.dependencies import get_current_user

# API routers
from app.api import health, chat, sessions, trips, bookings, tools
from app.api import auth as auth_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    await init_db()
    yield


app = FastAPI(
    title=settings.APP_NAME,
    version=settings.APP_VERSION,
    description="Full-stack AI travel planning and booking assistant for Indian domestic travel.",
    lifespan=lifespan,
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Static files & templates
BASE_DIR = Path(__file__).resolve().parent
templates = Jinja2Templates(directory=str(BASE_DIR / "templates"))
app.mount("/static", StaticFiles(directory=str(BASE_DIR / "static")), name="static")

# ── API routers ────────────────────────────────────────────────────────────────
app.include_router(health.router)
app.include_router(auth_router.router, prefix="/auth")   # /auth/login, /auth/logout
app.include_router(chat.router)
app.include_router(sessions.router)
app.include_router(trips.router)
app.include_router(bookings.router)
app.include_router(tools.router)


# ── UI routes ─────────────────────────────────────────────────────────────────

@app.get("/")
async def root(request: Request):
    """Public landing / login page. Redirect to /dashboard if already authenticated."""
    try:
        await get_current_user(request)
        return RedirectResponse(url="/dashboard")
    except HTTPException:
        return templates.TemplateResponse(
            request=request, name="login.html", context={"app_name": settings.APP_NAME}
        )


@app.get("/dashboard")
async def dashboard(request: Request, user: Any = Depends(get_current_user)):
    """Main SPA – requires authentication."""
    return templates.TemplateResponse(
        request=request, name="index.html", context={"app_name": settings.APP_NAME}
    )
