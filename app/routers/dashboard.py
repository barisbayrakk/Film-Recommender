from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from sqlalchemy import func
from app.db import get_db
# Giriş yapmış kullanıcıyı almak için
from app.core.security import get_current_user
from app.models.users import User
from app.models.like import Like
from app.models.rating import Rating
from app.models.movie import Movie
from app.models.watched import Watched
# Giriş yapmış kullanıcıyı almak için
from app.recommender.content import recommend_by_content
import json

# --------------------------------------------------
# DASHBOARD ROUTER TANIMI
# --------------------------------------------------
# Tüm endpointler /dashboard ile başlar
router = APIRouter(
    prefix="/dashboard",
    tags=["Dashboard"]
)
# --------------------------------------------------
# KULLANICI DASHBOARD ENDPOINT'I
# --------------------------------------------------
@router.get("/user")
def get_user_dashboard(
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user)
):
    # --------------------------------------------------
    # 1. KULLANICI İSTATİSTİKLERİ
    # --------------------------------------------------
    # Kullanıcının toplam beğeni (like) sayısı
    total_likes = db.query(Like).filter(Like.user_id == current_user.id).count()
    # Kullanıcının izledi olarak işaretlediği film sayısı
    total_watched = db.query(Watched).filter(Watched.user_id == current_user.id).count()
    
    # --------------------------------------------------
    # 2. SON BEĞENİLEN FİLMLER (EN SON 5 ADET)
    # --------------------------------------------------
    # Kullanıcının son beğendiği filmler ve film bilgileri
    recent_likes = (
        db.query(Like, Movie)
        .join(Movie, Like.movie_id == Movie.id)
        .filter(Like.user_id == current_user.id)
        .order_by(Like.created_at.desc())
        .limit(5)
        .all()
    )
     # Frontend için sade film listesi hazırlanır
    recent_movies_data = []
    for like, movie in recent_likes:
        recent_movies_data.append({
            "id": movie.id,
            "title": movie.title,
            "poster_path": movie.poster_path,
            "poster_url": movie.poster_url
        })
       
        
   # --------------------------------------------------
    # 3. FAVORİ TÜRLERİN BELİRLENMESİ
    # --------------------------------------------------
    # Kullanıcının beğendiği filmler üzerinden tür analizi yapılır
    liked_movies = (
        db.query(Movie)
        .join(Like, Movie.id == Like.movie_id)
        .filter(Like.user_id == current_user.id)
        .all()
    )
    
    #Türlere göre sayaç
    genre_counts = {}
    for m in liked_movies:
        if m.genres:
            try:
                # Türler JSON string olarak saklanıyor:
                # [{"id": 1, "name": "Action"}, ...]
                genres_list = json.loads(m.genres)
                for g in genres_list:
                    g_name = g['name']
                    genre_counts[g_name] = genre_counts.get(g_name, 0) + 1
            except:
                 # JSON parse hataları sistemin çalışmasını bozmaz
                pass
                
   # En çok beğenilen ilk 3 tür alınır
    top_genres = sorted(genre_counts.items(), key=lambda item: item[1], reverse=True)[:3]
    top_genres_list = [{"name": name, "count": count} for name, count in top_genres]
    
     # --------------------------------------------------
    # 4. KİŞİSELLEŞTİRİLMİŞ FİLM ÖNERİLERİ
    # --------------------------------------------------
    recommendations = []
    seed_info = None
    
    # Eğer kullanıcının daha önce beğendiği film varsa
    if recent_likes:
        # En son beğenilen film referans (anchor / seed) alınır
        last_liked_movie = recent_likes[0][1] 
        seed_info = {
            "title": last_liked_movie.title,
            "id": last_liked_movie.id
        }
        
        all_movies = db.query(Movie).all()
        # İçerik tabanlı öneri sistemi çalıştırılır
        recs = recommend_by_content(all_movies, seed_movie=last_liked_movie, top_n=10)
        
       # Referans filmin kendisi önerilerden çıkarılır 
        recommendations = [r for r in recs if r['id'] != last_liked_movie.id]
    else:
        # --------------------------------------------------
        # FALLBACK: HİÇ BEĞENİ YOKSA
        # --------------------------------------------------
        # Kullanıcı yeni ise popüler filmler önerilir
        popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(10).all()
        recommendations = [
             {
                "id": m.id,
                "title": m.title,
                "poster_path": m.poster_path,
                "poster_url": m.poster_url,
                "vote_average": m.vote_average
            } for m in popular
        ]
        seed_info = None # Popüler öneri yapıldığını belirtir
    # --------------------------------------------------
    # DASHBOARD RESPONSE
    # --------------------------------------------------
    return {
        "user_profile": {
            "username": current_user.username,
            "joined_at": current_user.created_at,
            "total_likes": total_likes,
            "total_watched": total_watched
        },
        "recent_likes": recent_movies_data,
        "favorite_genres": top_genres_list,
        "recommendations": recommendations,
        "recommendation_seed": seed_info
    }
