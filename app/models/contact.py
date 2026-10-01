# app/models/contact.py
from sqlalchemy import Column, Integer, String, DateTime, Boolean
# Sunucu tarafında otomatik zaman üretmek için func.now()
from sqlalchemy.sql import func
from app.db import Base

# --------------------------------------------------
# CONTACT MESSAGE (İLETİŞİM FORMU MESAJLARI) TABLOSU
# --------------------------------------------------
class ContactMessage(Base):
    __tablename__ = "contact_messages"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, nullable=False)
    email = Column(String, nullable=False)
    message = Column(String, nullable=False)
    reply = Column(String, nullable=True) 
    replied_at = Column(DateTime(timezone=True), nullable=True) 
    # Mesajın sisteme kaydedildiği zaman
    # server_default=func.now() sayesinde zaman bilgisi
    # veritabanı sunucusu tarafından otomatik atanır
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
# --------------------------------------------------
# CAPTCHA SESSION (BOT KORUMASI) TABLOSU
# --------------------------------------------------
class CaptchaSession(Base):
    __tablename__ = "captcha_sessions"

    # Frontend tarafına gönderilen benzersiz captcha kimliği (UUID)
    # Primary Key olarak kullanılır
    uuid = Column(String, primary_key=True, index=True) 
    # Matematiksel captcha sorusunun doğru cevabı
    # Kullanıcının cevabı bununla karşılaştırılır
    answer = Column(Integer, nullable=False) 
    # Captcha oturumunun geçerlilik süresi
    # Bu süre dolduğunda captcha geçersiz sayılır
    expires_at = Column(DateTime(timezone=True), nullable=False) 
