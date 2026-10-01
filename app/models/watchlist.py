from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from app.db import Base

# --------------------------------------------------
# WATCHLIST (KULLANICI İZLEME LİSTESİ) TABLOSU
# --------------------------------------------------

class Watchlist(Base):
    __tablename__ = "watchlist"

    id = Column(Integer, primary_key=True)
    user_id = Column(Integer, ForeignKey("users.id"))
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi izleme listesine
    # birden fazla kez eklemesini engeller
    # Veri tutarlılığını sağlar

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_watchlist"),)
