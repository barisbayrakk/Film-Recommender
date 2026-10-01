# Test ortamında kullanılan SQLAlchemy session
from app.tests.conftest import TestingSessionLocal
# Testler için yedek (backup) model tanımları
from app import models_backup

def seed_movies():
     # Test DB session oluştur
    db = TestingSessionLocal()
    
    # --------------------------------------------------
    # MEVCUT MOVIE KAYITLARINI TEMİZLE
    # --------------------------------------------------
    # Önceki testlerden kalan veriler varsa silinir
    db.query(models_backup.Movie).delete()
    
     # --------------------------------------------------
    # ÖRNEK FİLMLER OLUŞTUR
    # --------------------------------------------------
    movie1 = models_backup.Movie(
        title="Inception",
        genre="Sci-Fi",
        description="A mind-bending movie about dreams within dreams.",
    )
    movie2 = models_backup.Movie(
        title="The Matrix",
        genre="Sci-Fi",
        description="A hacker discovers the nature of his reality.",
    )
    
     # --------------------------------------------------
    # VERİTABANINA EKLE
    # --------------------------------------------------
    # İki filmi tek seferde ekle
    db.add_all([movie1, movie2])
     # Değişiklikleri kaydet
    db.commit()
     # --------------------------------------------------
    # ID VE DB STATE'İ GÜNCELLE
    # --------------------------------------------------
    # Commit sonrası otomatik oluşan ID'leri almak için refresh
    db.refresh(movie1)
    db.refresh(movie2)
     # Session'ı kapat
    db.close()
  # Testlerde kullanılmak üzere movie objelerini döndür
    return movie1, movie2
