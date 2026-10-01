from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from sqlalchemy.orm import relationship
from app.db import Base

# --------------------------------------------------
# USER (KULLANICI) TABLOSU
# --------------------------------------------------

class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)

    
    # --------------------------------------------------
    # KULLANICI BİLGİLERİ
    # --------------------------------------------------

    # Kullanıcı adı
    # unique=True ile aynı kullanıcı adının tekrar kullanılması engellenir
    username = Column(String, unique=True, index=True, nullable=False)
    # Kullanıcının e-posta adresi
    # unique=True ile aynı e-posta ile birden fazla hesap açılması engellenir
    email = Column(String, unique=True, index=True, nullable=False)
    name = Column(String, nullable=True)
    # Kullanıcı profil fotoğrafı URL bilgisi 
    avatar_url = Column(String, nullable=True) 


    # --------------------------------------------------
    # GÜVENLİK BİLGİLERİ
    # --------------------------------------------------

    # Kullanıcı şifresi düz metin olarak tutulmaz
    # Güvenlik amacıyla hashlenmiş şekilde saklanır
    hashed_password = Column(String, nullable=False)
    
    # Kullanıcının admin yetkisi olup olmadığını belirtir
    # 0: normal kullanıcı, 1: admin
    is_admin = Column(Integer, default=0)
    # Kullanıcının sisteme kayıt olduğu tarih
    created_at = Column(DateTime, default=datetime.utcnow)
    
    
    # --------------------------------------------------
    # HESAP DOĞRULAMA (VERIFICATION)
    # --------------------------------------------------

    # Kullanıcının e-posta doğrulama durumu
    # 0: doğrulanmamış, 1: doğrulanmış
    is_verified = Column(Integer, default=0) 
    # E-posta doğrulama işlemi için kullanılan token
    verification_token = Column(String, nullable=True)

    
    # --------------------------------------------------
    # ORM İLİŞKİLERİ (KULLANICI ETKİLEŞİMLERİ)
    # --------------------------------------------------

    # User ↔ Review ilişkisi
    # Bir kullanıcı birden fazla yorum yazabilir
    reviews = relationship("Review", back_populates="user", cascade="all, delete-orphan")
     # User ↔ Rating ilişkisi
    # Bir kullanıcı birden fazla filme puan verebilir
    ratings = relationship("Rating", back_populates="user", cascade="all, delete-orphan")
     # User ↔ ListItem (izleme listesi) ilişkisi
    # Kullanıcı birçok filmi izleme listesine ekleyebilir
    lists = relationship("ListItem", back_populates="user", cascade="all, delete-orphan")
    # User ↔ Like (beğeni) ilişkisi
    # Kullanıcı birçok filmi beğenebilir
    likes = relationship("Like", back_populates="user", cascade="all, delete-orphan")
     # User ↔ Collection ilişkisi
    # Kullanıcı birden fazla koleksiyon oluşturabilir
    collections = relationship("Collection", back_populates="user", cascade="all, delete-orphan")
    watched = relationship("Watched", back_populates="user", cascade="all, delete-orphan") 
