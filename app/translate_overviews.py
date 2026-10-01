from googletrans import Translator
from sqlalchemy.orm import Session
from app.database import SessionLocal
from app.models.movie import Movie
import time

translator = Translator()

def translate_text(text):
    try:
        tr = translator.translate(text, src="en", dest="tr")
        return tr.text
    except Exception as e:
        print(f"Çeviri hatası: {e}. 2 saniye sonra tekrar denenecek...")
        time.sleep(2)
        try:
            tr = translator.translate(text, src="en", dest="tr")
            return tr.text
        except:
            return None

def translate_all_movies():
    db: Session = SessionLocal()

    movies = db.query(Movie).all()
    print(f"🎬 Toplam {len(movies)} film bulundu.\n")

    for movie in movies:
        if not movie.overview:
            print(f"⛔ Filmin overview'u yok: {movie.title}")
            continue

        if movie.overview_tr:
            print(f"⏩ Zaten Türkçe çeviri var: {movie.title}")
            continue

        print(f"🔄 Çevriliyor: {movie.title}")

        tr_text = translate_text(movie.overview)
        if tr_text:
            movie.overview_tr = tr_text
            db.commit()
            print(f"✅ Çevirildi: {movie.title}\n")
        else:
            print(f"❌ Çevrilemedi: {movie.title}\n")

    db.close()
    print("🎉 Tüm çeviri işlemi tamamlandı!")

if __name__ == "__main__":
    translate_all_movies()
