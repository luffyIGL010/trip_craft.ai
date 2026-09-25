from fastapi import APIRouter
from app.config import settings

router = APIRouter()

@router.get("/api/health")
async def health_check():
    return {
        "status": "online",
        "app": settings.APP_NAME,
        "version": settings.APP_VERSION,
        "gemini_configured": bool(settings.GEMINI_API_KEY),
        "openai_configured": bool(settings.OPENAI_API_KEY),
        "openweather_configured": bool(settings.OPENWEATHER_API_KEY),
        "database": "SQLite (travelgenie.db)",
    }
