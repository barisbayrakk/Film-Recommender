from fastapi import APIRouter, Depends, HTTPException
# SQLAlchemy veritabanı oturumu
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
# OAuth2 tabanlı token doğrulama
from fastapi.security import OAuth2PasswordBearer

from app.db import get_db
from app.models.users import User
from app.core.security import hash_password, verify_password
from app.core.jwt import create_access_token, decode_access_token
from app.schemas.auth import UserRegister, UserLogin, Token
from app.schemas.users import UserOut
# --------------------------------------------------
# AUTH ROUTER TANIMI
# --------------------------------------------------
router = APIRouter(prefix="/auth", tags=["Auth"])

# OAuth2 token'ın hangi endpoint'ten alınacağını belirtir
oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/login")




# --------------------------------------------------
# GİRİŞ YAPMIŞ KULLANICIYI BULMA
# --------------------------------------------------

def get_current_user(token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)):

    payload = decode_access_token(token)
    if not payload or "user_id" not in payload:
        raise HTTPException(status_code=401, detail="Geçersiz veya süresi dolmuş oturum")

    user = db.query(User).filter(User.id == payload["user_id"]).first()
    if not user:
        raise HTTPException(status_code=404, detail="Kullanıcı bulunamadı")

    return user



# --------------------------------------------------
# MAİL DOĞRULAMA AYARLARI (MAILTRAP)
# --------------------------------------------------
import os
import uuid  
from dotenv import load_dotenv
from fastapi_mail import FastMail, MessageSchema, ConnectionConfig, MessageType
from pydantic import EmailStr

load_dotenv() 

# Mail sunucu ayarları (test ortamı)
conf = ConnectionConfig(
    MAIL_USERNAME = os.getenv("MAILTRAP_USERNAME", ""),
    MAIL_PASSWORD = os.getenv("MAILTRAP_PASSWORD", ""),
    MAIL_FROM = os.getenv("MAIL_FROM", "no-reply@filmrecommender.com"),
    MAIL_PORT = int(os.getenv("MAILTRAP_PORT", 2525)),
    MAIL_SERVER = os.getenv("MAILTRAP_HOST", "sandbox.smtp.mailtrap.io"),
    MAIL_STARTTLS = True,
    MAIL_SSL_TLS = False,
    USE_CREDENTIALS = True,
    VALIDATE_CERTS = True
)
# --------------------------------------------------
# DOĞRULAMA MAİLİ GÖNDERME
# --------------------------------------------------
async def send_verification_email(email: str, token: str):
    backend_url = os.getenv("BACKEND_URL", "http://localhost:8000").rstrip("/")
    verification_link = f"{backend_url}/auth/verify-email?token={token}"
    
    html = f"""
    <p>Merhaba,</p>
    <p>Hesabını doğrulamak için lütfen aşağıdaki linke tıkla:</p>
    <p><a href="{verification_link}">{verification_link}</a></p>
    <p>FilmRec Ekibi</p>
    """

    message = MessageSchema(
        subject="FilmRec Doğrulama",
        recipients=[email],
        body=html,
        subtype=MessageType.html
    )

    if not conf.MAIL_USERNAME or not conf.MAIL_PASSWORD:
        print(f"⚠️ SMTP kimlik bilgileri tanımlanmamış. Doğrulama linki: {verification_link}")
        return

    fm = FastMail(conf)

    try:
        await fm.send_message(message)
    except Exception as e:
        print(f"SMTP Mail sending failed: {e}")
    

# --------------------------------------------------
# KULLANICI KAYIT (REGISTER)
# --------------------------------------------------
@router.post("/register")
async def register(data: UserRegister, db: Session = Depends(get_db)):
    
     # E-posta benzersizlik kontrolü
    if db.query(User).filter(User.email == data.email).first():
        raise HTTPException(400, "Bu e-posta adresi zaten kullanımda")

   # Kullanıcı adı benzersizlik kontrolü
    if db.query(User).filter(User.username == data.username).first():
        raise HTTPException(400, "Bu kullanıcı adı zaten kullanımda")
    
    # E-posta doğrulama için token üret
    token = str(uuid.uuid4())
    
    # Yeni kullanıcı oluşturulur (şifre hashlenerek)
    new_user = User(
        username=data.username,
        email=data.email,
        name=data.username,
        hashed_password=hash_password(data.password),
        is_verified=0,  
        verification_token=token
    )

    try:
        db.add(new_user)
        db.commit()
        db.refresh(new_user)
        
        
        try:
            await send_verification_email(new_user.email, token)
        except Exception as e:
            print(f"⚠️ Mail gönderilemedi (Önemli değil, link aşağıda): {e}")
            
        print(f"\n{'='*40}")
        print(f"✅ KAYIT BAŞARILI! DOĞRULAMA LİNKİ:")
        print(f"http://localhost:8000/auth/verify-email?token={token}")
        print(f"{'='*40}\n")
        
    except IntegrityError:
        db.rollback()
        raise HTTPException(400, "Kullanıcı oluşturulurken hata oluştu")
    except Exception as e:
        db.rollback()
        print(f"Register Error: {e}")
        raise HTTPException(500, "Sunucu hatası oluştu. Lütfen daha sonra tekrar deneyin.")

    return {"msg": "Kayıt başarılı! Lütfen e-postanızı kontrol edip doğrulama işlemini tamamlayın."}


# --------------------------------------------------
# E-POSTA DOĞRULAMA
# --------------------------------------------------
@router.get("/verify-email")
def verify_email(token: str, db: Session = Depends(get_db)):
    user = db.query(User).filter(User.verification_token == token).first()
    if not user:
        raise HTTPException(400, "Geçersiz token")
        
    if user.is_verified:
        return {"msg": "Hesap zaten doğrulanmış"}
        
    user.is_verified = 1
    user.verification_token = None 
    db.commit()
    
    return {"msg": "Hesap başarıyla doğrulandı! Şimdi giriş yapabilirsiniz."}


# --------------------------------------------------
# GİRİŞ (LOGIN)
# --------------------------------------------------
@router.post("/login", response_model=Token)
def login(data: UserLogin, db: Session = Depends(get_db)):

    user = db.query(User).filter(User.email == data.email).first()

    if not user:
        raise HTTPException(400, "Geçersiz e-posta veya şifre")

    if not verify_password(data.password, user.hashed_password):
        raise HTTPException(400, "Geçersiz e-posta veya şifre")
        
   
    if not user.is_verified:
         raise HTTPException(400, "Lütfen önce e-posta adresinizi doğrulayın.")

    token = create_access_token({"user_id": user.id, "sub": user.username})
    return Token(access_token=token, token_type="bearer")

# --------------------------------------------------
# PROFİL FOTOĞRAFI GÜNCELLEME
# --------------------------------------------------
@router.put("/avatar")
def update_avatar(body: dict, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    avatar_url = body.get("avatar_url")
    if not avatar_url:
        raise HTTPException(400, "Avatar URL gerekli")
    
    current_user.avatar_url = avatar_url
    db.commit()
    return {"msg": "Profil fotoğrafı güncellendi", "avatar_url": avatar_url}


# --------------------------------------------------
# HESAP SİLME
# --------------------------------------------------
@router.delete("/me")
def delete_account(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    db.delete(current_user)
    db.commit()
    return {"msg": "Hesap başarıyla silindi"}




@router.get("/me", response_model=UserOut)
def me(current_user: User = Depends(get_current_user)):
    return current_user
