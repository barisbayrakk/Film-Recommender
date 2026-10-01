
import sqlite3
import os
import requests
import time
from dotenv import load_dotenv

# --------------------------------------------------
# ENV & API KEY
# --------------------------------------------------
# .env dosyasından TMDB_API_KEY'i yükle
load_dotenv()
TMDB_API_KEY = os.getenv("TMDB_API_KEY")
# SQLite veritabanı yolu
DB_PATH = "app/movies.db"

# ==================================================
# FİLM BAŞLIKLARINI TÜRKÇEYE GÜNCELLE
# ==================================================
def update_titles():
    print(f"🚀 Starting Title Localization Script...")
    
    # --------------------------------------------------
    # GÜVENLİK KONTROLLERİ
    # ---------------------------------------------
    if not TMDB_API_KEY:
        print("❌ Error: TMDB_API_KEY not found.")
        return

    if not os.path.exists(DB_PATH):
        print(f"❌ Error: Database not found at {DB_PATH}")
        return
    
    # --------------------------------------------------
    # DB BAĞLANTISI
    # --------------------------------------------------
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()

    try:
        # --------------------------------------------------
        # TÜM FİLMLERİ ÇEK
        # --------------------------------------------------
        cursor.execute("SELECT id, tmdb_id, title FROM movies")
        movies = cursor.fetchall()
        total = len(movies)
        print(f"📊 Found {total} movies to check.")

        updated_count = 0
        # --------------------------------------------------
        # FİLMLER ÜZERİNDE GEZ
        # --------------------------------------------------
        for i, (db_id, tmdb_id, current_title) in enumerate(movies, 1):
            # TMDB ID yoksa geç
            if not tmdb_id:
                continue

            try:
                # --------------------------------------------------
                # TMDB'DEN TÜRKÇE FİLM DETAYI ÇEK
                # --------------------------------------------------
                url = f"https://api.themoviedb.org/3/movie/{tmdb_id}"
                params = {"api_key": TMDB_API_KEY, "language": "tr-TR"}
                
                response = requests.get(url, params=params, timeout=5)
                
                if response.status_code == 200:
                    data = response.json()
                    tr_title = data.get("title")
                    # --------------------------------------------------
                    # BAŞLIK FARKLIYSA GÜNCELLE
                    # --------------------------------------------------
                    if tr_title and tr_title != current_title:
                        cursor.execute("UPDATE movies SET title = ? WHERE id = ?", (tr_title, db_id))
                        updated_count += 1
                        print(f"✅ [{i}/{total}] Updated: '{current_title}' -> '{tr_title}'")
                    else:
                        # Opsiyonel ilerleme logu
                        if i % 50 == 0:
                            print(f"🔹 [{i}/{total}] Skipped (Already match): {current_title}")
                else:
                    # API hata kodları
                    print(f"❌ [{i}/{total}] API Error {response.status_code} for ID {tmdb_id}")

                # --------------------------------------------------
                # PERİYODİK COMMIT
                # --------------------------------------------------
                # Her 50 güncellemede bir commit
                if updated_count > 0 and updated_count % 50 == 0:
                    conn.commit()
                
               # API'ye nazik olmak için kısa bekleme
                time.sleep(0.02)

            except Exception as e:
                 # Tek filmde hata olursa script durmaz
                print(f"💥 Error on movie {db_id}: {e}")
                
        # --------------------------------------------------
        # FINAL COMMIT
        # --------------------------------------------------
        conn.commit()
        print(f"\n🎉 Finished! Updated {updated_count} titles to Turkish.")

    except Exception as e:
        # Script seviyesinde kritik hata
        print(f"❌ Script Fatal Error: {e}")
    finally:
        # DB bağlantısını kapat
        conn.close()
        
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında
    # başlık lokalizasyonunu başlat
    update_titles()
