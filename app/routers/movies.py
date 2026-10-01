# app/routers/movies.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
import json

from app.models.movie import Movie
from app.schemas.movies import MovieOut
from app.db import get_db
from app.utils.tmdb import get_movie_details, get_movie_stats
from app.services.tmdb_import import fetch_upcoming_movies

router = APIRouter(prefix="/movies", tags=["Movies"])

# --------------------------------------------------
# GENRE (TÜR) ÇEVİRİ TABLOSU
# İngilizce türleri Türkçeye çevirmek için kullandık
# --------------------------------------------------

GENRE_TRANSLATION = {
    "Action": "Aksiyon",
    "Adventure": "Macera",
    "Animation": "Animasyon",
    "Comedy": "Komedi",
    "Crime": "Suç",
    "Documentary": "Belgesel",
    "Drama": "Dram",
    "Family": "Aile",
    "Fantasy": "Fantastik",
    "History": "Tarih",
    "Horror": "Korku",
    "Music": "Müzik",
    "Mystery": "Gizem",
    "Romance": "Romantik",
    "Science Fiction": "Bilim Kurgu",
    "TV Movie": "TV Filmi",
    "Thriller": "Gerilim",
    "War": "Savaş",
    "Western": "Vahşi Batı"
}

def convert(movie: Movie, tmdb_extra=None):

    # DIRECTOR
    if tmdb_extra and tmdb_extra.get("director"):
        directors = [{"name": tmdb_extra["director"]}]
    else:
        
        try:
            directors = json.loads(movie.directors) if movie.directors else [{"name": "Bilinmiyor"}]
        except:
            directors = [{"name": "Bilinmiyor"}]

    # CAST
    if tmdb_extra and tmdb_extra.get("cast"):
        cast = tmdb_extra["cast"]
    else:
        
        try:
            cast = json.loads(movie.cast) if movie.cast else []
        except:
            cast = []

    # GENRES
    try:
        raw_genres = json.loads(movie.genres) if movie.genres else []
    except:
        raw_genres = []

    # Tür formatı string mi dict mi kontrol edilir
    if raw_genres and isinstance(raw_genres, list) and len(raw_genres) > 0:
        if isinstance(raw_genres[0], str):
            genres = [{"id": 0, "name": GENRE_TRANSLATION.get(g, g)} for g in raw_genres]
        elif isinstance(raw_genres[0], dict):
            genres = []
            for item in raw_genres:
                new_item = item.copy()
                if "name" in new_item:
                    new_item["name"] = GENRE_TRANSLATION.get(new_item["name"], new_item["name"])
                genres.append(new_item)
        else:
            genres = raw_genres
    else:
        genres = raw_genres

    return MovieOut(
        id=movie.id,

        # Başlık
        title=(
            tmdb_extra.get("title")
            if (tmdb_extra and tmdb_extra.get("title"))
            else movie.title
        ),

        
        overview=(
            tmdb_extra.get("overview")
            if (tmdb_extra and tmdb_extra.get("overview"))
            else movie.overview
        ),

       
        overview_tr=movie.overview_tr,      

        poster_path=movie.poster_path,
        poster_url=movie.poster_url,
        trailer_url=getattr(movie, "trailer_url", None), 
        backdrop_path=getattr(movie, "backdrop_path", None), 

        release_date=(
            tmdb_extra.get("release_date")
            if (tmdb_extra and tmdb_extra.get("release_date"))
            else movie.release_date
        ),

        original_language=(
            tmdb_extra.get("original_language")
            if (tmdb_extra and tmdb_extra.get("original_language"))
            else movie.original_language
        ),

        vote_average=movie.vote_average,
        vote_count=movie.vote_count,
        popularity=movie.popularity,

        genres=genres,
        cast=cast,
        directors=directors,
    )



# --------------------------------------------------
# TÜM FİLMLER
# --------------------------------------------------
@router.get("/all", response_model=list[MovieOut])
def all_movies(db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(Movie.popularity.desc()).all()
    return [convert(m) for m in movies]


## --------------------------------------------------
# POPÜLER FİLMLER
# --------------------------------------------------
@router.get("/popular", response_model=list[MovieOut])
def popular(db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(Movie.popularity.desc()).limit(20).all()
    return [convert(m) for m in movies]



# --------------------------------------------------
# EN YÜKSEK PUANLI FİLMLER
# --------------------------------------------------
@router.get("/top", response_model=list[MovieOut])
def top_rated(db: Session = Depends(get_db)):
    movies = db.query(Movie).order_by(Movie.vote_average.desc()).limit(20).all()
    return [convert(m) for m in movies]




# --------------------------------------------------
# YAKINDA VİZYONA GİRECEK FİLMLER (TMDB)
# --------------------------------------------------
@router.get("/upcoming", response_model=list[MovieOut])
def upcoming():
    upcoming = fetch_upcoming_movies()

    return [
        MovieOut(
            id=m["id"],              
            title=m["title"],
            overview=m.get("overview", ""),
            overview_tr=None,        
            poster_path=m.get("poster_path"),
            poster_url=None,
            release_date=m.get("release_date"),
            vote_average=0.0, 
            vote_count=0, 
            popularity=m.get("popularity"),
            genres=[],
            cast=[],
            directors=[],
        )
        for m in upcoming
    ]



# --------------------------------------------------
# FİLM ARAMA
# --------------------------------------------------
@router.get("/search/{query}", response_model=list[MovieOut])
def search(query: str, db: Session = Depends(get_db)):
    from sqlalchemy import or_
    import json
    

    def generate_search_variants(q):
        variants = {q, q.lower(), q.upper()}
        
        
        def tr_title_case(text):
            words = text.lower().split()
            cap_words = []
            for w in words:
                if not w: continue
                first = w[0]
                rest = w[1:]
                if first == "i": first = "İ"
                elif first == "ı": first = "I"
                else: first = first.upper()
                cap_words.append(first + rest)
            return " ".join(cap_words)
        
        titled = tr_title_case(q)
        variants.add(titled)
        
        # (Türkçe karakterleri temizle)
        tr_map = {
            "ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c",
            "İ": "I", "Ğ": "G", "Ü": "U", "Ş": "S", "Ö": "O", "Ç": "C"
        }
        anglicized = "".join(tr_map.get(c, c) for c in q)
        variants.add(anglicized)
        variants.add(anglicized.lower())
        variants.add(anglicized.title())
        
 
        swapped_i = q.replace("i", "İ").replace("I", "ı")
        variants.add(swapped_i)
        swapped_i2 = q.replace("İ", "i").replace("ı", "I") 
        variants.add(swapped_i2)

        
        try:
             escaped = json.dumps(q).strip('"')
             variants.add(escaped)
             escaped_titled = json.dumps(titled).strip('"')
             variants.add(escaped_titled)
        except:
             pass
        
        return list(variants)

    
    simple_movies = db.query(Movie).filter(
        or_(
            Movie.title.ilike(f"%{query}%"),
            Movie.cast.ilike(f"%{query}%"),
            Movie.directors.ilike(f"%{query}%")
        )
    ).limit(50).all()
    
    if simple_movies:
        return [convert(m) for m in simple_movies]

    # Varyasyonları üret 
    search_variants = generate_search_variants(query)

    filters = []
    for v in search_variants:
        filters.append(Movie.title.ilike(f"%{v}%"))
        filters.append(Movie.cast.ilike(f"%{v}%"))
        filters.append(Movie.directors.ilike(f"%{v}%"))
        filters.append(Movie.genres.ilike(f"%{v}%"))

    
    tr_to_en_genre = {v.lower(): k for k, v in GENRE_TRANSLATION.items()}
    query_lower = query.lower()
    if query_lower in tr_to_en_genre:
        english_genre = tr_to_en_genre[query_lower]
        filters.append(Movie.genres.ilike(f"%{english_genre}%"))

    # Sorguyu çalıştır
    movies = db.query(Movie).filter(or_(*filters)).all()
    return [convert(m) for m in movies]



# YAKINDA: TEK FİLM DETAY (TMDB)

@router.get("/upcoming/detail/{tmdb_id}")
def upcoming_detail(tmdb_id: int):
    detail = get_movie_details(tmdb_id)   
    stats = get_movie_stats(tmdb_id)

    return {
        "id": tmdb_id,
        "title": detail.get("title"),
        "overview": detail.get("overview"),
        "overview_tr": None,
        "poster_path": detail.get("poster_path"),
        "release_date": detail.get("release_date"),
        "vote_average": stats.get("vote_average"),
        "vote_count": stats.get("vote_count"),
        "cast": detail.get("cast"),
        "directors": [{"name": detail.get("director")}],
    }



# VERİTABANI FİLM DETAY

@router.get("/{movie_id}", response_model=MovieOut)
def get_movie(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()

    if not movie:
        raise HTTPException(404, "Movie not found")

    
    
    tmdb_extra = get_movie_details(movie.tmdb_id)
    stats = get_movie_stats(movie.tmdb_id)
  # Türkçe olmayan filmler için TMDB başlığını ezme
    if movie.original_language != "tr":
        tmdb_extra.pop("title", None)
  # Güncel oy bilgileri senkronize edilir
    if stats.get("vote_count") is not None:
        movie.vote_count = stats["vote_count"]

    if stats.get("vote_average") is not None:
        movie.vote_average = stats["vote_average"]

    db.commit()

    return convert(movie, tmdb_extra)

# --------------------------------------------------
# BENZER FİLMLER (CONTENT-BASED)
# --------------------------------------------------
@router.get("/{movie_id}/similar", response_model=list[MovieOut])
def similar_movies(movie_id: int, db: Session = Depends(get_db)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")

   
    from app.recommender.content import recommend_by_content
    
  
    
    all_movies_pool = db.query(Movie).all()
    
    recommendations = recommend_by_content(all_movies_pool, seed_movie=movie, top_n=6)
    
    
    results = []
    for r in recommendations:
        
        m_obj = next((m for m in all_movies_pool if m.id == r['id']), None)
        if m_obj:
            results.append(convert(m_obj))
            
    return results
