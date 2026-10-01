
import sys
import os

# --------------------------------------------------
# PROJECT ROOT'U sys.path'E EKLE
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ altındaki modülleri import edebilmek için
# proje kök dizinini Python path'e ekliyoru
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------------------------
# DATABASE & MODEL IMPORTLARI
# --------------------------------------------------
from app.db import SessionLocal
from app.models.movie import Movie
# --------------------------------------------------
# DİĞER MODELLER
# --------------------------------------------------
# Bu importlar doğrudan kullanılmasa bile,
# SQLAlchemy'nin registry'sinin ve ilişkilerin
# düzgün şekilde yüklenmesi için gereklidir
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched
from app.models.like import Like
from app.models.lists import ListItem
from app.models.review import Review
from app.models.rating import Rating
# --------------------------------------------------
# NLP / EMBEDDING SERVİSİ
# --------------------------------------------------
# Film veritabanı için embedding üreten fonksiyon
from app.services.nlp_service import generate_embeddings_for_db

# ==================================================
# CHATBOT EMBEDDING GÜNCELLEME FONKSİYONU
# ==================================================
def update_embeddings():
    print("🧠 Chatbot veritabanı güncelleniyor...")
    # DB session aç
    db = SessionLocal()
    try:
        movies = db.query(Movie).all()
        print(f"📂 Toplam {len(movies)} film bulundu.")
        
        # --------------------------------------------------
        # ESKİ EMBEDDING CACHE TEMİZLE
        # --------------------------------------------------
        # nlp_service içinde cache kontrolü olsa bile,
        # tamamen temiz bir üretim yapmak için
        # pickle dosyası manuel olarak silinir
        if os.path.exists("movie_embeddings.pkl"):
            os.remove("movie_embeddings.pkl")
            print("🗑️ Eski önbellek temizlendi.")
        # --------------------------------------------------
        # YENİ EMBEDDING ÜRET
        # --------------------------------------------------
        # Tüm filmler için embedding oluşturulur
        generate_embeddings_for_db(movies)
        print("✅ Yeni filmler chatbot'a öğretildi!")
        
    except Exception as e:
        # Herhangi bir hata durumunda
        print(f"❌ Hata: {e}")
    finally:
        # DB session her durumda kapatılır
        db.close()
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
     # Script doğrudan çalıştırıldığında
    # chatbot embedding güncellemesini başlat
    update_embeddings()
