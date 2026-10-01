import os
# HTTP istekleri yapmak için
import requests
# .env dosyasından environment variable yüklemek için
from dotenv import load_dotenv

# --------------------------------------------------
# ENV AYARLARI
# --------------------------------------------------
# .env dosyasını yükle
load_dotenv()

TMDB_API_KEY = os.getenv("TMDB_API_KEY")

# ======================================================
#  TÜRKÇE DETAY + OYUNCULAR + YÖNETMEN
# ======================================================
def get_movie_details(tmdb_id: int):
    if not tmdb_id:
        return {"director": "Bilinmiyor", "cast": [], "overview": None}

    base = f"https://api.themoviedb.org/3/movie/{tmdb_id}"

    # Film detayı
    detail_url = f"{base}?api_key={TMDB_API_KEY}&language=tr-TR"

    # Oyuncular + yönetmen
    credits_url = f"{base}/credits?api_key={TMDB_API_KEY}&language=tr-TR"

    detail_res = requests.get(detail_url).json()
    credits_res = requests.get(credits_url).json()

    # ----- Yönetmen -----
    director = next(
        (c.get("name") for c in credits_res.get("crew", []) if c.get("job") == "Director"),
        "Bilinmiyor"
    )

    # ----- Oyuncular -----
    cast_list = []
    for c in credits_res.get("cast", [])[:15]:
        cast_list.append({
            "name": c.get("name"),
            "character": c.get("character"),
            "profile_path": c.get("profile_path"),
        })

    return {
        "director": director,
        "cast": cast_list,
        "overview": detail_res.get("overview"),
        "title": detail_res.get("title"),
        "poster_path": detail_res.get("poster_path"),
        "release_date": detail_res.get("release_date"),
        "original_language": detail_res.get("original_language"),
    }


# ======================================================
#  IMDb Rating + Oy Sayısı
# ======================================================
def get_movie_stats(tmdb_id: int):
    url = f"https://api.themoviedb.org/3/movie/{tmdb_id}?api_key={TMDB_API_KEY}&language=tr-TR"
    res = requests.get(url).json()
    return {
        "vote_count": res.get("vote_count"),
        "vote_average": res.get("vote_average"),
    }


# ======================================================
#  Poster Bulma (Yedek)
# ======================================================
def get_poster_url(title: str):
    """Film başlığına göre poster URL bulur. (V3 API Key kullanır)"""
    if not TMDB_API_KEY:
        print("❌ TMDB_API_KEY bulunamadı!")
        return None

    url = "https://api.themoviedb.org/3/search/movie"
    
    params = {
        "query": title, 
        "language": "en-US",
        "api_key": TMDB_API_KEY 
    }

    try:
        r = requests.get(url, params=params)
        r.raise_for_status()

        data = r.json().get("results", [])
        if not data:
            return None

        poster_path = data[0].get("poster_path")
        
        if poster_path:
            return f"https://image.tmdb.org/t/p/w500{poster_path}" 
        
    except Exception as e:
        print(f"❌ Poster API hatası: {e}")

    return None
