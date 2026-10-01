
import sys
import os
# --------------------------------------------------
# PROJECT ROOT'U sys.path'E EKLE
# --------------------------------------------------
# Bu script doğrudan çalıştırıldığında
# app/ içindeki modülleri import edebilmek için
# proje kök dizinini Python path'e ekliyoruz
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# --------------------------------------------------
# DATABASE & MODEL IMPORTLARI
# --------------------------------------------------
from app.db import SessionLocal
from app.models.movie import Movie
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.lists import ListItem
from app.models.review import Review
from app.models.rating import Rating

# ==================================================
# CAST ALANI KONTROL SCRIPTI
# ==================================================
def check_cast():
    db = SessionLocal()
    print("\n--- Checking 'cast' column format ---")
    
    
    # --------------------------------------------------
    # 1️. BELİRLİ BİR FİLM ÜZERİNDEN KONTROL
    # --------------------------------------------------
    # Örnek olarak "Yahşi Batı" içeren filmleri ara
    search_term = "%Yahşi Batı%"
    movies = db.query(Movie).filter(Movie.title.ilike(search_term)).all()
    
    if movies:
        print(f"Found {len(movies)} movies matching '{search_term}':")
        for m in movies:
            print(f"ID: {m.id}, Title: {m.title}")
            
            # Cast alanını raw haliyle yazdır
            # İlk 500 karakter yeterli olur
            print(f"Cast Raw: {m.cast[:500]}") 
    else:
        print(f"No movies found matching '{search_term}'.")
        
        # --------------------------------------------------
        # 2️.HERHANGİ BİR FİLM ÜZERİNDEN KONTROL
        # --------------------------------------------------
        # Eğer aranan film yoksa,
        # cast alanı dolu olan rastgele bir filmi al
        m = db.query(Movie).filter(Movie.cast != None).first()
        if m:
            print(f"\nRandom Movie Cast ({m.title}):")
            print(f"Cast Raw: {m.cast[:200]}")
            
    db.close()

if __name__ == "__main__":
    check_cast()
