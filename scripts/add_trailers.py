
import os
import sys
import sqlite3
import requests
import re
import urllib.parse

# --------------------------------------------------
# PROJECT ROOT PATH EKLEME
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ içindeki modülleri import edebilmek için
# proje kök dizinini sys.path'e ekliyoruz
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------------------------
# ENV & API KEY
# --------------------------------------------------
from dotenv import load_dotenv
load_dotenv()
# TMDB API anahtarı (.env içinden)
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# SQLite veritabanı yolu
DB_PATH = "app/movies.db"

# ==================================================
# TMDB ÜZERİNDEN TRAILER BULMA
# ==================================================
def fetch_trailer_from_tmdb(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}/videos"
    params = {"api_key": TMDB_API_KEY} 
    try:
        res = requests.get(url, params=params, timeout=5).json()
        results = res.get("results", [])
        
        # 1. Turkish Trailer
        tr = next((v for v in results if v["iso_639_1"] == "tr" and v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if tr: return f"https://www.youtube.com/watch?v={tr['key']}"
            
        # 2. English Trailer
        en = next((v for v in results if v["iso_639_1"] == "en" and v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if en: return f"https://www.youtube.com/watch?v={en['key']}"
            
        # 3. Any Trailer
        any_t = next((v for v in results if v["type"] == "Trailer" and v["site"] == "YouTube"), None)
        if any_t: return f"https://www.youtube.com/watch?v={any_t['key']}"

        return None
    except:
        return None


# ==================================================
# YOUTUBE SCRAPE (FALLBACK)
# ==================================================
def fetch_trailer_from_youtube_scrape(title):
    try:
        # Arama sorgusu (Türkçe + İngilizce karışık)
        query_string = urllib.parse.quote(f"{title} fragman trailer")
        url = "https://www.youtube.com/results?search_query=" + query_string
        
          # Bot tespitine takılmamak için fake User-Agent
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, timeout=5)
        html = response.text
        
        # --------------------------------------------------
        # VIDEO ID BULMA
        # --------------------------------------------------
        # YouTube HTML içindeki JSON’da sıkça geçen pattern:
        # "videoId":"XXXXXXXX"
        video_ids = re.findall(r'"videoId":"(.*?)"', html)
        
        if video_ids:
           
            return f"https://www.youtube.com/watch?v={video_ids[0]}"
            
    except Exception as e:
        print(f"YT Scrape error for {title}: {e}")
    return None
# ==================================================
# DATABASE GÜNCELLEME
# ==================================================
def update_movies():
    # SQLite bağlantısı
    conn = sqlite3.connect(DB_PATH)
    c = conn.cursor()
    
    
    # --------------------------------------------------
    # TRAILER'I OLMAYAN FİLMLER
    # --------------------------------------------------
    c.execute("SELECT id, tmdb_id, title FROM movies WHERE trailer_url IS NULL OR trailer_url = ''")
    movies = c.fetchall()
    
    print(f"Checking fallbacks for {len(movies)} missing trailers...")
    
    count = 0
    updated = 0
    
    for m in movies:
        mid, tmdb_id, title = m
        
         # 1️.Önce TMDB tekrar dene
        trailer = fetch_trailer_from_tmdb(tmdb_id)
        
        # 2️.TMDB başarısızsa → YouTube scrape
        if not trailer:
             print(f"🔍 Searching YouTube for: {title}")
             trailer = fetch_trailer_from_youtube_scrape(title)
        
        # Trailer bulunduysa DB'yi güncelle
        if trailer:
            c.execute("UPDATE movies SET trailer_url = ? WHERE id = ?", (trailer, mid))
            updated += 1
            print(f"✅ Found: {title[:20]} -> {trailer}")
        else:
            print(f"❌ Still no trailer for {title[:20]}")
            
        count += 1
            # Her 10 kayıtta bir commit (performans için)s
        if count % 10 == 0:
            conn.commit()
            
    conn.commit()
    conn.close()
    print(f"🎉 Done! Filled {updated} gaps.")

if __name__ == "__main__":
    update_movies()
