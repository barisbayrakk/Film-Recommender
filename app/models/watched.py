# Tarih ve zaman bilgisini otomatik üretmek için datetime modülü
from datetime import datetime
from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base

# --------------------------------------------------
# WATCHED (KULLANICININ İZLEDİĞİ FİLMLER) TABLOSU
# --------------------------------------------------

class Watched(Base):
    __tablename__ = "watched_movies"

    id = Column(Integer, primary_key=True, index=True)
    
     # Filmi izleyen kullanıcının kimliği
    # Kullanıcı silinirse, ona ait izleme kayıtları da otomatik silinir
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False, index=True)
    # İzlenen filmin kimliği
    # Film silinirse, ona ait izleme kayıtları da otomatik silinir
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False, index=True)
    
    # Filmin kullanıcı tarafından izlenmiş olarak işaretlendiği zaman
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # Watched ↔ User ilişkisi
    # Bir kullanıcı birçok filmi izleyebilir

    user = relationship("User", back_populates="watched")
     # Watched ↔ Movie ilişkisi
    # Bir izleme kaydı yalnızca bir filme karşılık gelir
    movie = relationship("Movie")
    
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi birden fazla kez
    # "izlendi" olarak işaretlemesini engeller
    # Veri tutarlılığı sağlar

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_watched"),
    )
