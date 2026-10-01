# Tarih ve zaman bilgisi oluşturmak için datetime modülü
from datetime import datetime
# SQLAlchemy kolon tipleri ve kısıtlamaları
from sqlalchemy import Column, Integer, String, ForeignKey, DateTime, UniqueConstraint
# ORM tabloları arası ilişkileri tanımlamak için relationship
from sqlalchemy.orm import relationship
# Tüm ORM modellerinin miras aldığı Base sınıfı
from app.db import Base

# --------------------------------------------------
# COLLECTION (KULLANICI KOLEKSİYONU) TABLOSU
# --------------------------------------------------
class Collection(Base):
     # Veritabanındaki tablo adı
    __tablename__ = "collections"
    
     # Koleksiyonun benzersiz kimliği (Primary Key)
    id = Column(Integer, primary_key=True, index=True)
    
    # Koleksiyonun hangi kullanıcıya ait olduğunu belirtir
    # ondelete="CASCADE" sayesinde kullanıcı silinirse
    # ona ait koleksiyonlar da otomatik olarak silinir
    user_id = Column(Integer, ForeignKey("users.id", ondelete="CASCADE"), nullable=False)
    
    # Koleksiyonun kullanıcı tarafından verilen adı
    # (ör. "Favorilerim", "İzlenecekler")
    name = Column(String, nullable=False)
    
     # Koleksiyonun oluşturulma zamanı
    created_at = Column(DateTime, default=datetime.utcnow)

   
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------

    # Koleksiyon ↔ Kullanıcı ilişkisi
    # Bir koleksiyon yalnızca bir kullanıcıya aittir
    user = relationship("User", back_populates="collections")
    
    # Koleksiyon ↔ KoleksiyonItem ilişkisi
    # Bir koleksiyon birden fazla film içerebilir
    # cascade="all, delete-orphan":
    # Koleksiyon silinirse içindeki tüm filmler de silinir
    items = relationship("CollectionItem", back_populates="collection", cascade="all, delete-orphan")
    
    # --------------------------------------------------
    # COLLECTION ITEM (KOLEKSİYON–FİLM BAĞLANTI) TABLOSU
    # --------------------------------------------------


class CollectionItem(Base):
    __tablename__ = "collection_items"

    id = Column(Integer, primary_key=True, index=True)
    collection_id = Column(Integer, ForeignKey("collections.id", ondelete="CASCADE"), nullable=False)
    movie_id = Column(Integer, ForeignKey("movies.id", ondelete="CASCADE"), nullable=False)
    added_at = Column(DateTime, default=datetime.utcnow)

    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # --------------------------------------------------
    # KoleksiyonItem ↔ Collection ilişkisi
    collection = relationship("Collection", back_populates="items")
    movie = relationship("Movie")
    
    # --------------------------------------------------
    # TABLO KISITLAMALARI
    # --------------------------------------------------

    # Aynı film, aynı koleksiyona birden fazla kez eklenemez
    # Bu kısıtlama veri tutarlılığını sağlar
    __table_args__ = (
        UniqueConstraint("collection_id", "movie_id", name="uq_collection_movie"),
    )
