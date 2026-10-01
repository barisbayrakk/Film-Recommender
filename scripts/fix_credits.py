
import os
import sys
import sqlite3
import json
import requests
import time

# --------------------------------------------------
# PROJECT ROOT'U sys.path'E EKLE
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ içindeki modülleri import edebilmek için
# proje kök dizinini Python path'e ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

# --------------------------------------------------
# ENV & TMDB TOKEN
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()
# TMDB V4 Bearer Token (.env içinden)
API_V4_TOKEN = os.getenv("TMDB_V4_TOKEN")

# --------------------------------------------------
# DATABASE & API AYARLARI
# --------------------------------------------------
# SQLite veritabanı yolu
DB_PATH = "app/movies.db"
# TMDB base URL
BASE_URL = "https://api.themoviedb.org/3"

# TMDB API request header (Bearer auth)
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_V4_TOKEN}"
}

# ==================================================
# GENEL JSON FETCH FONKSİYONU
# ==================================================
def get_json(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        return r.json()
    except Exception as e:
        print(f"Error fetching {url}: {e}")
        return {}

# ==================================================
# FİLM CREDITS (CAST + DIRECTOR)
# ==================================================
def fetch_credits(tmdb_id):
    url = f"{BASE_URL}/movie/{tmdb_id}/credits"
    data = get_json(url)
    
    cast = data.get("cast", [])
    crew = data.get("crew", [])
    
   
    # --------------------------------------------------
    # CAST (İLK 10 OYUNCU)
    # --------------------------------------------------
    final_cast = []
    for c in cast[:10]:
        final_cast.append({
            "name": c.get("name"),
            "character": c.get("character"),
            "profile_path": c.get("profile_path")
        })
        
    # --------------------------------------------------
    # DIRECTORS (YÖNETMENLER)
    # --------------------------------------------------
    final_directors = []
    for c in crew:
        if c.get("job") == "Director":
             final_directors.append({
                "name": c.get("name"),
                "profile_path": c.get("profile_path")
            })
            
    return final_cast, final_directors
# ==================================================
# CAST / DIRECTORS BOŞ FİLMLERİ DÜZELT
# ==================================================
def fix_movies():
    # SQLite bağlantısı
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    # --------------------------------------------------
    # EKSİK CAST / DIRECTOR OLAN FİLMLER
    # --------------------------------------------------
    # NULL
    # boş string
    # '[]' (boş JSON array)
    c.execute("""
        SELECT id, tmdb_id, title, "cast", directors 
        FROM movies 
        WHERE "cast" IS NULL OR "cast" = '' OR "cast" = '[]' 
           OR directors IS NULL OR directors = '' OR directors = '[]'
    """)
    movies = c.fetchall()
    
    print(f"Found {len(movies)} movies with missing credits.")
    
    updated_count = 0
    for m in movies:
        mid, tmdb_id, title, cast_val, dir_val = m
        
        print(f"Fetching credits for: {title} (TMDB {tmdb_id})...")
        # TMDB'den yeni credits al
        new_cast, new_directors = fetch_credits(tmdb_id)
        
       # JSON'a serialize et
        cast_json = json.dumps(new_cast, ensure_ascii=False)
        dir_json = json.dumps(new_directors, ensure_ascii=False)
        
        if not new_cast and not new_directors:
              # TMDB'de bile yoksa
            print(f"❌ No credits found on TMDB for {title} either.")
        else:
             # DB güncelle
            c.execute("UPDATE movies SET cast = ?, directors = ? WHERE id = ?", (cast_json, dir_json, mid))
            updated_count += 1
            print(f"✅ Updated {title}: {len(new_cast)} cast, {len(new_directors)} directors.")
        # Rate limit'e yakalanmamak için küçük bekleme
        time.sleep(0.1) 
        # Her 10 güncellemede bir commit
        if updated_count % 10 == 0:
            conn.commit()
    # Final commit & close
    conn.commit()
    conn.close()
    print(f"\n🎉 Done! Fixed {updated_count} movies.")
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında
    # eksik cast / director kayıtlarını düzelt
    fix_movies()
