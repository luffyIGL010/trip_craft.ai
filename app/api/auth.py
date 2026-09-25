from fastapi import APIRouter, Response, HTTPException, Depends
from pydantic import BaseModel
from datetime import datetime, timedelta
from typing import Optional
import uuid
import jwt

import firebase_admin
from firebase_admin import auth as firebase_auth, credentials
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select

from app.auth.config import auth_settings
from app.db import models
from app.db.database import get_db

# Initialise Firebase Admin SDK once
if not firebase_admin._apps:
    if auth_settings.FIREBASE_SERVICE_ACCOUNT_PATH:
        cred = credentials.Certificate(auth_settings.FIREBASE_SERVICE_ACCOUNT_PATH)
        firebase_admin.initialize_app(cred)
    else:
        firebase_admin.initialize_app()

router = APIRouter()


class TokenRequest(BaseModel):
    idToken: str


def _create_jwt(user_id: str) -> str:
    payload = {
        "sub": user_id,
        "iat": datetime.utcnow(),
        "exp": datetime.utcnow() + timedelta(minutes=auth_settings.ACCESS_TOKEN_EXPIRE_MINUTES),
    }
    return jwt.encode(payload, auth_settings.JWT_SECRET, algorithm=auth_settings.JWT_ALGORITHM)


async def _get_or_create_user(
    uid: str,
    provider: str,
    email: Optional[str],
    name: Optional[str],
    picture: Optional[str],
    db: AsyncSession,
) -> models.UserModel:
    result = await db.execute(
        select(models.UserModel).where(models.UserModel.provider_user_id == uid)
    )
    user = result.scalar_one_or_none()
    if user:
        return user
    new_user = models.UserModel(
        id=str(uuid.uuid4()),
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


@router.post("/login")
async def login(request: TokenRequest, response: Response, db: AsyncSession = Depends(get_db)):
    """Verify Firebase ID token, create/fetch user, issue JWT session cookie."""
    try:
        decoded = firebase_auth.verify_id_token(request.idToken)
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid Firebase ID token")

    uid = decoded.get("uid")
    provider = decoded.get("firebase", {}).get("sign_in_provider", "unknown")
    user = await _get_or_create_user(
        uid, provider,
        decoded.get("email"),
        decoded.get("name"),
        decoded.get("picture"),
        db,
    )
    jwt_token = _create_jwt(str(user.id))
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
    """Clear the session cookie."""
    response.delete_cookie(key=auth_settings.SESSION_COOKIE_NAME, path="/")
    return {"success": True}
