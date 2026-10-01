from datetime import datetime

from sqlalchemy import Column, Integer, ForeignKey, DateTime, UniqueConstraint
from sqlalchemy.orm import relationship
# Kimlik doğrulama işlemlerinde kullanılan yardımcı fonksiyon
from app.core.security import get_current_user
from app.db import Base

# --------------------------------------------------
# LIST ITEM (KULLANICI LİSTE / WATCHLIST) TABLOSU
# --------------------------------------------------


class ListItem(Base):
    __tablename__ = "list_items"

    id = Column(Integer, primary_key=True, index=True)
    # Listeye ekleyen kullanıcının kimliği
    # Kullanıcı silinirse, ona ait liste kayıtları da otomatik silinir. 
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    # Listeye eklenen filmin kimliği
    # Film silinirse, filme ait liste kayıtları da otomatik silinir
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    
     # Filmin kullanıcının listesine eklendiği zaman
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # ListItem ↔ User ilişkisi
    # Bir kullanıcı birden fazla filmi listesine ekleyebilir
    user = relationship("User", back_populates="lists")
    movie = relationship("Movie")

    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi listeye birden fazla kez eklemesini engeller
    # Veri tutarlılığı ve mantıksal bütünlük sağlar
    __table_args__ = (
        UniqueConstraint("user_id", "movie_id", name="uq_user_movie_list"),
    )
