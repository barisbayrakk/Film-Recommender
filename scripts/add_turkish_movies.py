
import requests
import sqlite3
import json
import os
import sys

# --------------------------------------------------
# NOTLAR
# --------------------------------------------------
# Bu script tek seferlik (one-off) bir veri ekleme scriptidir.
# - FastAPI veya SQLAlchemy kullanılmıyor
# - Direkt TMDB API + sqlite3 kullanılıyor
# - Amaç: Türk filmlerini hızlıca DB'ye eklemek
# --------------------------------------------------


# --------------------------------------------------
# TMDB API KEY
# --------------------------------------------------
TMDB_API_KEY = "685991a80391238c318290e42a163178"

# --------------------------------------------------
# HEDEF TÜRK FİLMLERİ (SERİLER)
# --------------------------------------------------
# Arama yapılacak popüler Türk film isimleri
TARGET_SERIES = [
    "Kolpaçino",
    "Recep İvedik",
    "G.O.R.A",
    "A.R.O.G",
    "Vizontele",
    "Yahşi Batı",
    "Organize İşler",
    "Eyyvah Eyvah",
    "Çalgı Çengi",
    "Düğün Dernek",
    "Ölümlü Dünya" 
]


# --------------------------------------------------
# TMDB SEARCH (FİLM ARAMA)
# --------------------------------------------------
def get_tmdb_id(query):
    url = f"https://api.themoviedb.org/3/search/movie?api_key={TMDB_API_KEY}&query={query}&language=tr-TR"
    res = requests.get(url)
    if res.status_code == 200:
        results = res.json().get("results", [])
        return results
    return []
# --------------------------------------------------
# TMDB FİLM DETAYLARI
# --------------------------------------------------
def get_movie_details(tmdb_id):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=tr-TR&append_to_response=credits,keywords"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json()
    return None
# --------------------------------------------------
# FİLMİ VERİTABANINA EKLE
# --------------------------------------------------
def add_movie_to_db(movie_data):
    # Connect to DB
    db_path = os.path.join(os.path.dirname(__file__), "../app/movies.db")
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()

    # --------------------------------------------------
    # DUPLICATE KONTROLÜ (tmdb_id)
    # --------------------------------------------------
    cursor.execute("SELECT id FROM movies WHERE tmdb_id = ?", (movie_data['id'],))
    if cursor.fetchone():
        print(f"✅ Zaten var: {movie_data['title']}")
        conn.close()
        return

    # --------------------------------------------------
    # TEMEL FİLM ALANLARI
    # --------------------------------------------------
    title = movie_data['title']
    original_title = movie_data['original_title']
    overview = movie_data['overview']
    poster_path = movie_data['poster_path']
    backdrop_path = movie_data['backdrop_path']
    release_date = movie_data['release_date']
    rating = movie_data['vote_average']
    vote_count = movie_data['vote_count']
    popularity = movie_data['popularity']
    
    
    genres = json.dumps([{"id": g['id'], "name": g['name']} for g in movie_data.get('genres', [])])
    
   
    cast = []
    credits = movie_data.get('credits', {})
    for c in credits.get('cast', [])[:15]:
        cast.append({
            "id": c['id'],
            "name": c['name'],
            "character": c['character'],
            "profile_path": c['profile_path']
        })
    cast_json = json.dumps(cast)
    
    
    directors = []
    for c in credits.get('crew', []):
        if c['job'] == 'Director':
            directors.append({"id": c['id'], "name": c['name']})
    directors_json = json.dumps(directors)

    
    try:
        cursor.execute("""
            INSERT INTO movies (
                tmdb_id, title, overview, overview_tr, 
                poster_path, release_date, vote_average, vote_count, popularity,
                genres, cast, directors
            ) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            movie_data['id'], title, overview, overview, 
            poster_path, release_date, rating, vote_count, popularity,
            genres, cast_json, directors_json
        ))
        conn.commit()
        print(f"🎬 Eklendi: {title}")
    except Exception as e:
        print(f"❌ Hata ({title}): {e}")
    
    conn.close()

# --------------------------------------------------
# TMDB DISCOVER (TÜRK FİLMLERİ)
# --------------------------------------------------
def discover_turkish_movies(page=1):
    url = f"https://api.themoviedb.org/3/discover/movie?api_key={TMDB_API_KEY}&language=tr-TR&sort_by=popularity.desc&with_original_language=tr&primary_release_date.gte=2010-01-01&page={page}"
    res = requests.get(url)
    if res.status_code == 200:
        return res.json().get("results", [])
    return []

def main():
    print("🚀 2010 Sonrası Popüler Türk Filmleri Ekleniyor...")
    
    # 5 sayfa (top 100 film) çekelim
    for page in range(1, 6):
        print(f"\n📄 Sayfa {page} işleniyor...")
        movies = discover_turkish_movies(page)
        
        for m in movies:
            # Detayları çek (cast, director vs için)
            details = get_movie_details(m['id'])
            if details:
                add_movie_to_db(details)
            else:
                print(f"⏩ Detay alınamadı: {m['title']}")

if __name__ == "__main__":
    main()
