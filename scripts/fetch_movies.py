import requests
import json
from dotenv import load_dotenv
import os
import time

# --------------------------------------------------
# ENV DOSYASINI YÜKLE
# --------------------------------------------------
# .env içindeki TMDB_V4_TOKEN gibi gizli bilgileri alır
load_dotenv()

# --------------------------------------------------
# TMDB V4 TOKEN
# --------------------------------------------------
# TMDB'nin modern (Bearer) authentication token'ı
API_V4_TOKEN = os.getenv("TMDB_V4_TOKEN")


# Debug amaçlı kontroller
print("DEBUG — Working directory:", os.getcwd())
print("DEBUG — V4 TOKEN loaded:", API_V4_TOKEN is not None)

# --------------------------------------------------
# TMDB BASE URL
# --------------------------------------------------
BASE_URL = "https://api.themoviedb.org/3"

# --------------------------------------------------
# TMDB REQUEST HEADER
# --------------------------------------------------
# Bearer token ile kimlik doğrulama yapılır
HEADERS = {
    "accept": "application/json",
    "Authorization": f"Bearer {API_V4_TOKEN}"
}

# ==================================================
# GÜVENLİ TMDB JSON FETCH
# ==================================================
def get_json(url):
    """TMDB isteklerini güvenli şekilde yapan fonksiyon."""
    while True:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
             # Rate limit yediysek biraz bekle
            if r.status_code == 429:
                print("⏳ Rate limit! Bekleniyor...")
                time.sleep(2)
                continue
            return r.json()
        except:
             # Network / timeout hatası
            print("⚠️ Tekrar deneniyor...")
            time.sleep(1)

# ==================================================
# POPÜLER FİLMLERİ ÇEK
# ==================================================
def fetch_popular_movies(total=1000):
    print(f"\n🎬 {total} popüler film çekiliyor…")
    movies = []
    page = 1

    while len(movies) < total:
        url = f"{BASE_URL}/movie/popular?page={page}"
        data = get_json(url)
  
        # Her sayfadaki filmleri ekle
        for m in data.get("results", []):
            movies.append(m)
            if len(movies) >= total:
                break

        page += 1

    return movies


# ==================================================
# TÜRK FİLMLERİNİ ÇEK
# ==================================================
def fetch_turkish_movies(total=500):
    print(f"\n🎬 {total} Türk filmi çekiliyor…")
    movies = []
    page = 1

    while len(movies) < total:
        url = (
            f"{BASE_URL}/discover/movie?"
            f"with_origin_country=TR&sort_by=popularity.desc&page={page}"
        )
        data = get_json(url)

        for m in data.get("results", []):
            movies.append(m)
            if len(movies) >= total:
                break

        page += 1

    return movies

# ==================================================
# TEK FİLMİ ZENGİNLEŞTİR
# ==================================================
def enrich_movie(movie_id):
    """Poster | oyuncular | yönetmen bilgilerini alır."""
    details = get_json(f"{BASE_URL}/movie/{movie_id}")
    credits = get_json(f"{BASE_URL}/movie/{movie_id}/credits")

    cast = credits.get("cast", [])
    crew = credits.get("crew", [])
      # Crew içinden yönetmenleri ayıkla
    directors = [c for c in crew if c.get("job") == "Director"]

    return {
        "tmdb_id": movie_id,
        "title": details.get("title"),
        "overview": details.get("overview"),
        "release_date": details.get("release_date"),
        "genres": details.get("genres"),
        "poster_path": details.get("poster_path"),
        "vote_average": details.get("vote_average"),
        "popularity": details.get("popularity"),
        "cast": cast[:10],       # ilk 10 oyuncu
        "directors": directors,  # yönetmen(ler)
    }

# ==================================================
# TÜM FİLMLERİ ZENGİNLEŞTİR
# ==================================================
def enrich_all_movies(movie_list):
    print("\n✨ Filmler zenginleştiriliyor…")
    final_data = []

    for i, m in enumerate(movie_list, 1):
        print(f"→ {i}/{len(movie_list)}: {m.get('title')}")
        enriched = enrich_movie(m["id"])
        final_data.append(enriched)
         # Rate-limit'e yakalanmamak için kısa bekleme
        time.sleep(0.25)  

    return final_data

# ==================================================
# MAIN
# ==================================================
def main():
    print("\n🚀 Film dataset oluşturuluyor...")

    pop_movies = fetch_popular_movies(1000)
    tr_movies = fetch_turkish_movies(500)

    combined = pop_movies + tr_movies
    print(f"\n📌 Toplam film: {len(combined)}")

    enriched_data = enrich_all_movies(combined)
    
    # JSON dosyasına yaz
    with open("movies_1500.json", "w", encoding="utf-8") as f:
        json.dump(enriched_data, f, ensure_ascii=False, indent=4)

    print("\n🎉 TAMAMLANDI! → movies_1500.json oluşturuldu.")

# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    main()
