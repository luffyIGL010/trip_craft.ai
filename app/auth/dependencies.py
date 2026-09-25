from fastapi import Depends, HTTPException, Cookie
import jwt
from app.auth.config import auth_settings
from app.db import models
from app.db.database import get_db
from sqlalchemy.ext.asyncio import AsyncSession

async def _get_user_from_db(user_id: str, db: AsyncSession):
    return await db.get(models.UserModel, user_id)

async def get_current_user(token: str = Cookie(None, alias=auth_settings.SESSION_COOKIE_NAME)):
    """FastAPI dependency that validates JWT session cookie and returns the authenticated user.

    Raises:
        HTTPException 401: if token missing, invalid, or expired.
    """
    if not token:
        raise HTTPException(status_code=401, detail="Not authenticated")
    try:
        payload = jwt.decode(token, auth_settings.JWT_SECRET, algorithms=[auth_settings.JWT_ALGORITHM])
        user_id: str = payload.get("sub")
        if not user_id:
            raise HTTPException(status_code=401, detail="Invalid token payload")
    except jwt.ExpiredSignatureError:
        raise HTTPException(status_code=401, detail="Token expired")
    except jwt.PyJWTError:
        raise HTTPException(status_code=401, detail="Token verification failed")
    # Retrieve user from DB
    async def _dependency(db: AsyncSession = Depends(get_db)):
        user = await _get_user_from_db(user_id, db)
        if not user:
            raise HTTPException(status_code=401, detail="User not found")
        return user
    return await _dependency()
