# SQLAlchemy kolon tipleri, ForeignKey ve benzersizlik kısıtlamaları
from sqlalchemy import Column, Integer, ForeignKey, UniqueConstraint
from sqlalchemy.orm import relationship
from app.db import Base
# --------------------------------------------------
# USER LIKED MOVIES (KULLANICI BEĞENİLERİ) TABLOSU
# --------------------------------------------------

class UserLikedMovie(Base):
    __tablename__ = "user_liked_movies"
    id = Column(Integer, primary_key=True, index=True)
    # Beğeniyi yapan kullanıcının kimliği
    # users tablosuna ForeignKey ile bağlanır
    user_id = Column(Integer, ForeignKey("users.id"))
    # Beğenilen filmin kimliği
    # movies tablosuna ForeignKey ile bağlanır
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi birden fazla kez beğenmesini engeller
    # Veri tutarlılığı sağlar
    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_like"),)
    
    
# --------------------------------------------------
# USER WATCHLIST (KULLANICI İZLEME LİSTESİ) TABLOSU
# --------------------------------------------------

class UserWatchList(Base):
    __tablename__ = "user_watchlist"
    id = Column(Integer, primary_key=True, index=True)
    # Listeyi oluşturan kullanıcının kimliği
    # users tablosuna ForeignKey ile bağlanır
    user_id = Column(Integer, ForeignKey("users.id"))
     # İzleme listesine eklenen filmin kimliği
    # movies tablosuna ForeignKey ile bağlanır
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı kullanıcının aynı filmi izleme listesine
    # birden fazla kez eklemesini engeller

    __table_args__ = (UniqueConstraint("user_id", "movie_id", name="unique_watchlist"),)
