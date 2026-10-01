import os
from datetime import datetime, timedelta

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import jwt, JWTError

from app.db import SessionLocal
from app.models.users import User

from dotenv import load_dotenv
load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY", "supersecret")
if SECRET_KEY == "supersecret":
    import logging
    logging.getLogger("uvicorn.error").warning("⚠️ GÜVENLİK UYARISI: Varsayılan zayıf 'SECRET_KEY' kullanılıyor! Lütfen .env dosyasında güçlü bir SECRET_KEY belirleyin.")

ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", 60 * 24))

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")


# ====================================================
# TOKEN OLUŞTURMA
# ====================================================
def create_access_token(data: dict) -> str:
    """Return a JWT access token."""
    to_encode = data.copy()
    expire = datetime.utcnow() + timedelta(minutes=ACCESS_TOKEN_EXPIRE_MINUTES)
    to_encode["exp"] = expire

    return jwt.encode(to_encode, SECRET_KEY, algorithm=ALGORITHM)


# ====================================================
# TOKEN ÇÖZME (BÜTÜN PROJECT BUNU KULLANACAK)
# ====================================================
def decode_access_token(token: str):
    """Decode and validate token. Return payload or None."""
    try:
        return jwt.decode(token, SECRET_KEY, algorithms=[ALGORITHM])
    except JWTError:
        return None


# ====================================================
# GEÇERLİ USER GETİRME
# ====================================================
def get_current_user(token: str = Depends(oauth2_scheme)) -> User:
    payload = decode_access_token(token)

    if not payload or "user_id" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid or expired token."
        )

    user_id = payload["user_id"]

    db = SessionLocal()
    try:
        user = db.query(User).filter(User.id == user_id).first()
    finally:
        db.close()

    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found."
        )

    return user
