import os
from pathlib import Path
from dotenv import load_dotenv

BASE_DIR = Path(__file__).resolve().parent.parent.parent
load_dotenv(BASE_DIR / ".env")


class AuthSettings:
    # JWT
    JWT_SECRET: str = os.getenv(
        "JWT_SECRET",
        "travelgenie_super_secret_jwt_key_2026_indian_domestic_travel_agent",
    )
    JWT_ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24 * 7  # 7 days
    SESSION_COOKIE_NAME: str = "travelgenie_session"
    COOKIE_SECURE: bool = os.getenv("ENVIRONMENT", "development") == "production"
    COOKIE_SAMESITE: str = "lax"

    # Firebase (optional – only needed for backend Admin SDK verification)
    FIREBASE_API_KEY: str = os.getenv("FIREBASE_API_KEY", "")
    FIREBASE_PROJECT_ID: str = os.getenv("FIREBASE_PROJECT_ID", "authentication-ae570")
    FIREBASE_SERVICE_ACCOUNT_PATH: str = os.getenv("FIREBASE_SERVICE_ACCOUNT_PATH", "")

    # OTP (Firebase phone-auth handles this on the client; kept for reference)
    OTP_EXPIRE_SECONDS: int = 300
    OTP_COOLDOWN_SECONDS: int = 30
    OTP_MAX_ATTEMPTS: int = 5
    OTP_RATE_LIMIT_PER_HOUR: int = 6


auth_settings = AuthSettings()
