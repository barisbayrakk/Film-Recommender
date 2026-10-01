from sqlalchemy import Column, Integer, String, Text, Float
from sqlalchemy.orm import relationship
from app.db import Base
from app.models.like import Like
from app.models.lists import ListItem

# --------------------------------------------------
# MOVIE (FİLM) TABLOSU
# --------------------------------------------------

class Movie(Base):
    __tablename__ = "movies"

    id = Column(Integer, primary_key=True, index=True)
    # TMDB üzerindeki benzersiz film kimliği
    # unique=True ile aynı filmin tekrar eklenmesi engellenir
    tmdb_id = Column(Integer, unique=True, index=True, nullable=False)

    title = Column(String, nullable=False)
    # Filmin orijinal dildeki özeti
    overview = Column(Text)
    # Filmin Türkçe özeti
    # Çok dilli içerik desteği sağlamak amacıyla eklenmiştir
    overview_tr = Column(Text)  

   
    poster_path = Column(String)
    # Poster için tam URL adresi
    poster_url = Column(String)
     # Film fragmanının (trailer) video bağlantısı
    trailer_url = Column(String) 
    

    # Filmin çıkış tarihi
    release_date = Column(String)
     # Filmin orijinal dili (örn: en, tr)
    original_language = Column(String) 

    # --------------------------------------------------
    # İÇERİK TABANLI ÖNERİ SİSTEMİ İÇİN KULLANILAN ALANLAR
    # --------------------------------------------------

    # Filmin tür bilgileri (örn: Action, Drama)
    # Metinsel formatta tutulur ve embedding üretiminde kullanılır
    genres = Column(Text)      
    # Filmde oynayan oyuncular (cast bilgisi)
    cast = Column(Text)       
    # Filmin yönetmen(ler)i
    directors = Column(Text)  
    
    # --------------------------------------------------
    # POPÜLERLİK ve PUANLAMA BİLGİLERİ
    # --------------------------------------------------
    # Filmin popülerlik skoru 
    popularity = Column(Float)
     # Kullanıcılar tarafından verilen ortalama puan
    vote_average = Column(Float)
      # Toplam oy sayısı
    vote_count = Column(Integer)

    
    # --------------------------------------------------
    # ORM İLİŞKİLERİ
    # (Bu alanlar kullanıcı etkileşimlerini temsil eder)
    # --------------------------------------------------

    # Movie ↔ Rating ilişkisi
    # Bir film birden fazla puan alabilir
    ratings = relationship("Rating", back_populates="movie")
     # Movie ↔ Review ilişkisi
    # Bir film birden fazla yoruma sahip olabilir
    reviews = relationship("Review", back_populates="movie")
    # Movie ↔ Like ilişkisi
    # Bir film birçok kullanıcı tarafından beğenilebilir
    # Film silinirse, ona ait beğeniler de otomatik olarak silinir
    likes = relationship("Like", back_populates="movie", cascade="all, delete-orphan")
     # Movie ↔ ListItem ilişkisi
    # Bir film birçok kullanıcının izleme listesinde yer alabilir
    # Film silinirse, ilgili liste kayıtları da otomatik silinir
    listed_by = relationship("ListItem", back_populates="movie", cascade="all, delete-orphan")
