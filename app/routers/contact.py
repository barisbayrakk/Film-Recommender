# app/routers/contact.py
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from sqlalchemy import desc
from app.db import get_db
from app.models.contact import ContactMessage
from app.routers.auth import get_current_user
from app.models.users import User
import requests
import os
from datetime import datetime
# --------------------------------------------------
# CONTACT ROUTER TANIMI
# --------------------------------------------------
# Tüm endpoint’ler /contact ile başlar
router = APIRouter(prefix="/contact", tags=["Contact"])

# --------------------------------------------------
# GOOGLE reCAPTCHA SECRET KEY
# --------------------------------------------------
# Kullanıcıların bot olup olmadığını kontrol etmek için kullanılır (ortam değişkeninden okunur)
RECAPTCHA_SECRET_KEY = os.getenv("RECAPTCHA_SECRET_KEY", "")

# ==================================================
# ================ ADMIN ENDPOINTS =================
# ==================================================


@router.get("/messages")
def get_all_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
     # Kullanıcı admin değilse erişim engellenir
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")
    
    # Tüm mesajlar en yeni en üstte olacak şekilde sıralanır
    messages = db.query(ContactMessage).order_by(desc(ContactMessage.created_at)).all()
    return messages

@router.put("/{message_id}/reply")
def reply_message(
    message_id: int,
    reply: str = Body(..., embed=True),
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # Admin yetkisi kontrolü
    if not current_user.is_admin:
        raise HTTPException(status_code=403, detail="Yetkisiz erişim")
    
   # Mesaj veritabanında var mı kontrol edilir
    msg = db.query(ContactMessage).filter(ContactMessage.id == message_id).first()
    if not msg:
        raise HTTPException(status_code=404, detail="Mesaj bulunamadı")
    
    # Admin cevabı ve cevaplanma zamanı kaydedilir    
    msg.reply = reply
    msg.replied_at = datetime.now()
    
    db.commit()
    db.refresh(msg)
    return msg

# ==================================================
# ================ USER ENDPOINTS ==================
# ==================================================
@router.get("/my-messages")
def get_my_messages(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    
    messages = db.query(ContactMessage).filter(
        ContactMessage.email == current_user.email
    ).order_by(desc(ContactMessage.created_at)).all()
    
    return messages

# ==================================================
# ================ PUBLIC ENDPOINT =================
# ==================================================
@router.post("/send")
def send_contact_message(
    name: str = Body(...),
    email: str = Body(...),
    message: str = Body(...),
    captcha_token: str = Body(...),
    db: Session = Depends(get_db)
):
    """
    Verifies google reCAPTCHA and saves the contact message.
    """
     # Google reCAPTCHA doğrulama endpoint’i
    verify_url = "https://www.google.com/recaptcha/api/siteverify"
    
    # Eğer RECAPTCHA_SECRET_KEY yapılandırılmamışsa uyarı logla (geliştirme ortamı için)
    if not RECAPTCHA_SECRET_KEY:
        print("⚠️ RECAPTCHA_SECRET_KEY tanımlanmamış, geliştirme modunda captcha atlanıyor.")
        result = {"success": True}
    else:
        # Google’a gönderilecek doğrulama verisi
        data = {
            "secret": RECAPTCHA_SECRET_KEY,
            "response": captcha_token
        }
        
        # reCAPTCHA doğrulama isteği
        try:
            response = requests.post(verify_url, data=data, timeout=10)
            result = response.json()
        except Exception as e:
            print(f"Captcha servisi hatası: {e}")
            raise HTTPException(status_code=502, detail="Captcha doğrulama servisine ulaşılamadı. Lütfen daha sonra tekrar deneyin.")

    if not result.get("success"):
        raise HTTPException(status_code=400, detail="Captcha doğrulaması başarısız. Lütfen tekrar deneyin.")


    new_message = ContactMessage(
        name=name,
        email=email,
        message=message
    )
    db.add(new_message)
    db.commit()
    
    return {"message": "Mesajınız başarıyla iletildi! 🚀"}
