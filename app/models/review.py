# app/models/review.py
# SQLAlchemy kolon tipleri ve ForeignKey tanımı
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, Boolean
# Yorumun oluşturulma zamanını otomatik almak için datetime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db import Base


# --------------------------------------------------
# REVIEW (KULLANICI YORUMU) TABLOSU
# --------------------------------------------------
class Review(Base):
    # Veritabanındaki tablo adı
    __tablename__ = "reviews"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String, nullable=False)
      # Yorumun oluşturulduğu tarih ve saat bilgisi
    created_at = Column(DateTime, default=datetime.utcnow)
     # Yorumun spoiler içerip içermediğini belirtir
    # True ise frontend tarafında uyarı gösterilebilir
    is_spoiler = Column(Boolean, default=False)
    
    # --------------------------------------------------
    # FOREIGN KEY ALANLARI
    # --------------------------------------------------

    # Yorumu yazan kullanıcının kimliği
    # users tablosuna ForeignKey ile bağlanır

    user_id = Column(Integer, ForeignKey("users.id"))
    # Yorumun ait olduğu filmin kimliği
    # movies tablosuna ForeignKey ile bağlanır
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    # Review ↔ User ilişkisi
    # Bir kullanıcı birden fazla yorum yazabilir
    user = relationship("User", back_populates="reviews")
    # Review ↔ Movie ilişkisi
    # Bir film birden fazla yoruma sahip olabilir
    movie = relationship("Movie", back_populates="reviews")
