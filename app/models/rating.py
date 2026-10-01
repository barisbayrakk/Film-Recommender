from sqlalchemy import Column, Integer, ForeignKey
# ORM tabloları arası ilişkileri tanımlamak için relationship
from sqlalchemy.orm import relationship
from app.db import Base

# --------------------------------------------------
# RATING (KULLANICI PUANLAMASI) TABLOSU
# --------------------------------------------------

class Rating(Base):
    __tablename__ = "ratings"

    id = Column(Integer, primary_key=True, index=True)
    # Kullanıcının filme verdiği puan
    # Genellikle 1–5 veya 1–10 aralığında kullanılır
    score = Column(Integer)
     # Puanı veren kullanıcının kimliği
    # users tablosuna ForeignKey ile bağlanır
    user_id = Column(Integer, ForeignKey("users.id"))
     # Puan verilen filmin kimliği
    # movies tablosuna ForeignKey ile bağlanır
    movie_id = Column(Integer, ForeignKey("movies.id"))
    
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # Rating ↔ User ilişkisi
    # Bir kullanıcı birden fazla filme puan verebilir

    user = relationship("User", back_populates="ratings")
    
    # Rating ↔ Movie ilişkisi
    # Bir film birden fazla kullanıcıdan puan alabilir
    movie = relationship("Movie", back_populates="ratings")
