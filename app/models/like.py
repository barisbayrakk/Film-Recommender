# Tarih ve zaman bilgisini otomatik olarak oluşturmak için datetime modülü
from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
# ORM tabloları arası ilişkileri tanımlamak için relationship
from sqlalchemy.orm import relationship

from app.db import Base

# --------------------------------------------------
# LIKE (KULLANICI BEĞENİSİ) TABLOSU
# --------------------------------------------------

class Like(Base):
    __tablename__ = "likes"

    id = Column(Integer, primary_key=True, index=True)

    # Beğeniyi yapan kullanıcının kimliği
    # ondelete="CASCADE" sayesinde kullanıcı silinirse
    # ona ait tüm beğeni kayıtları da otomatik olarak silinir

    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)

    created_at = Column(DateTime, default=datetime.utcnow)
    
     # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # Like ↔ User ilişkisi
    # Bir kullanıcı birden fazla filmi beğenebilir

    user = relationship("User", back_populates="likes")
    # Like ↔ Movie ilişkisi
    # Bir beğeni yalnızca bir filme karşılık gelir
    movie = relationship("Movie")
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi birden fazla kez beğenmesini engeller
    # Veri tutarlılığı ve mantıksal bütünlük sağlar

    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_like"),
    )
