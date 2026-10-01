# --------------------------------------------------
# AUTH / USER SCHEMAS
# Kullanıcı kayıt, giriş ve token veri modelleri
# --------------------------------------------------
from pydantic import BaseModel, EmailStr, Field
# ==================================================
# KULLANICI KAYIT (REGISTER) ŞEMASI
# ==================================================
class UserRegister(BaseModel):
    username: str = Field(..., min_length=3, max_length=50) # Kullanıcı adı (benzersiz olmalı, min 3 karakter)
    email: EmailStr # Email formatı otomatik doğrulanır
    password: str = Field(..., min_length=6, max_length=128) # Düz metin şifre (backend'de hashlenir, min 6 karakter)


# ==================================================
# KULLANICI GİRİŞ (LOGIN) ŞEMASI
# ==================================================
class UserLogin(BaseModel):
    email: EmailStr# Giriş için email
    password: str# Giriş için şifre

# ==================================================
# JWT TOKEN RESPONSE ŞEMASI
# ==================================================
class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"
