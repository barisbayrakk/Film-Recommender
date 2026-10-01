
import os
import sys
import time

# --------------------------------------------------
# PROJECT ROOT'U sys.path'E EKLE
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ klasörü altındaki modülleri import edebilmek için
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------------------------
# DATABASE & ORM IMPORTLARI
# --------------------------------------------------
from sqlalchemy.orm import Session
from app.db import SessionLocal
# Modeller
from app.models.users import User
from app.models.movie import Movie
from app.models.collection import Collection
from app.models.review import Review
from app.models.like import Like
from app.models.lists import ListItem
from app.models.watched import Watched
from app.models.rating import Rating
# TMDB yardımcı fonksiyonları
from app.utils.tmdb import get_movie_details 
# HTTP istekleri
import requests
# Google Translate (otomatik çeviri)
from deep_translator import GoogleTranslator

# --------------------------------------------------
# ENV & TMDB API KEY
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# ==================================================
# TMDB'DEN TÜRKÇE OVERVIEW ÇEK
# ==================================================
def fetch_tmdb_tr(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
    try:
        res = requests.get(url, params=params).json()
        return res.get("overview", "")
    except:
        return ""
# ==================================================
# TMDB'DEN TÜRKÇE BAŞLIK ÇEK (KULLANILMIYOR)
# ==================================================
def fetch_tmdb_tr_title(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
    params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
    try:
        res = requests.get(url, params=params).json()
        return res.get("title", "")
    except:
        return ""
# ==================================================
# FİLMLERİ TÜRKÇEYE ÇEVİR
# ==================================================
def translate_movies():
      # DB session
    db: Session = SessionLocal()
    # Tüm filmleri al
    movies = db.query(Movie).all()
    # Google Translate instance
    translator = GoogleTranslator(source='auto', target='tr')
    
    count = 0
    updated = 0
    
    print(f"Checking {len(movies)} movies...")
    
    for m in movies:
        # Mevcut Türkçe overview (varsa)
        current_tr = m.overview_tr
        
         # --------------------------------------------------
        # 1️. TMDB TÜRKÇE OVERVIEW DENEMESİ
        # --------------------------------------------------
        tmdb_overview = fetch_tmdb_tr(m.tmdb_id)
        
        final_tr = ""
        # TMDB Türkçe overview yeterince uzunsa kullan
        if tmdb_overview and len(tmdb_overview) > 10:
            final_tr = tmdb_overview
        
        
         # --------------------------------------------------
        # (OPSİYONEL) TÜRKÇE BAŞLIK GÜNCELLEME
        # --------------------------------------------------
        # tmdb_title = fetch_tmdb_tr_title(m.tmdb_id)
        # if tmdb_title and tmdb_title != m.title:
        #      print(f"  Title Change: {m.title} -> {tmdb_title}")
        #      m.title = tmdb_title
        #      updated += 1

        # --------------------------------------------------
        # 2️. GOOGLE TRANSLATE FALLBACK
        # --------------------------------------------------
        if not final_tr:
           
            english_ov = m.overview
            if english_ov and len(english_ov) > 5:
                try:
                    translated = translator.translate(english_ov)
                    final_tr = translated
                except Exception as e:
                    print(f"Translation failed for {m.title}: {e}")
                    
        # --------------------------------------------------
        # 3️. DB GÜNCELLE
        # --------------------------------------------------
        if final_tr:
             # Türkçe overview alanı
            m.overview_tr = final_tr
             # Ayrıca overview alanı da Türkçe ile overwrite ediliyor
            m.overview = final_tr 
            updated += 1
            print(f"✅ Translated Overview: {m.title[:20]}...")
            
        count += 1
        # --------------------------------------------------
        # PERİYODİK COMMIT
        # --------------------------------------------------
        if count % 10 == 0:
            db.commit()
            print(f"--- Processed {count} movies ---")
            
        if count % 10 == 0:
            db.commit()
            print(f"--- Processed {count} movies ---")
        
        time.sleep(0.5)

    db.commit()
    print(f"🎉 Done! Updated {updated} movies.")
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında
    # film açıklamalarını Türkçeleştir
    translate_movies()
