# SQLAlchemy kolon tipleri ve veritabanı alanları için gerekli importlar
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime
# ORM tabloları arası ilişkileri tanımlamak için relationship
from sqlalchemy.orm import relationship
# Tarih ve zaman bilgisini otomatik eklemek için datetime modülü
from datetime import datetime
# Tüm ORM model sınıflarının miras aldığı Base sınıfı
from app.db import Base

# --------------------------------------------------
# COMMENT (KULLANICI YORUMU) TABLOSU
# --------------------------------------------------
class Comment(Base):
    __tablename__ = "comments"

    id = Column(Integer, primary_key=True, index=True)
    text = Column(String)
    # Yorumun hangi filme ait olduğunu belirtir
    # ForeignKey ile movies tablosuna bağlanır
    movie_id = Column(Integer, ForeignKey("movies.id"))
    user_id = Column(Integer, ForeignKey("users.id"))
    created_at = Column(DateTime, default=datetime.utcnow)
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # Yorum ↔ Kullanıcı ilişkisi
    # Bir yorum yalnızca bir kullanıcıya aittir
    user = relationship("User")
    # Yorum ↔ Film ilişkisi
    # Bir yorum yalnızca bir filme aittir
    movie = relationship("Movie")
   