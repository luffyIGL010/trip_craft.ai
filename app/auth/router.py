from fastapi import APIRouter, HTTPException, Request, Response, status, Depends
import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from pydantic import BaseModel
from datetime import datetime, timedelta
import jwt
from app.auth.config import auth_settings
from app.db import models
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

# Initialize Firebase Admin SDK (use service account path if provided)
if not firebase_admin._apps:
    if auth_settings.FIREBASE_SERVICE_ACCOUNT_PATH:
        cred = credentials.Certificate(auth_settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

router = APIRouter()

class TokenRequest(BaseModel):
    idToken: str

async def _get_or_create_user(uid: str, provider: str, email: str | None, name: str | None, picture: str | None, db: AsyncSession):
    # Try to find existing user by provider UID
    user = await db.scalar(models.UserModel.select().where(models.UserModel.provider_user_id == uid))
    if user:
        return user
    # Create new user record
    new_user = models.UserModel(
        auth_provider=provider,
        provider_user_id=uid,
        email=email,
        name=name,
        profile_image=picture,
    )
    db.add(new_user)
    await db.commit()
    await db.refresh(new_user)
    return new_user

def _create_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    token = jwt.encode(payload, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALGORITHM)
    return token

@router.post("/login", response_model=None)
async def login(request: TokenRequest, response: Response, db: AsyncSession = Depends(get_db)):
    try:
        decoded = firebase_auth.verify_id_token(request.idToken)
    except Exception as e:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")
    uid = decoded.get("uid")
    provider = decoded.get("firebase", {}).get("sign_in_provider", "unknown")
    email = decoded.get("email")
    name = decoded.get("name")
    picture = decoded.get("picture")
    user = await _get_or_create_user(uid, provider, email, name, picture, db)
    jwt_token = _create_jwt(str(user.id))
    # Set HttpOnly cookie
    response.set_cookie(
        key=auth_settings.SESSION_COOKIE_NAME,
        value=jwt_token,
        httponly=True,
        secure=auth_settings.COOKIE_SECURE,
        samesite=auth_settings.COOKIE_SAMESITE,
        max_age=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        path="/",
    )
    return {"success": True}

@router.post("/logout")
async def logout(response: Response):
    response.delete_cookie(key=auth_settings.SESSION_COOKIE_NAME, path="/")
    return {"success": True}
