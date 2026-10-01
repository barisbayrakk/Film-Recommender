from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
# SQL fonksiyonları (count, avg vb.)
from sqlalchemy import func
# API request body'leri için veri doğrulama
from pydantic import BaseModel
# Opsiyonel alanlar için
from typing import Optional

from app.db import get_db
# Giriş yapmış kullanıcıyı almak için
from app.routers.auth import get_current_user
# ORM Modelleri
from app.models.users import User
from app.models.movie import Movie
from app.models.review import Review
from app.models.like import Like
from app.models.rating import Rating
from app.schemas.users import UserOut

# --------------------------------------------------
# ADMIN ROUTER TANIMI
# --------------------------------------------------
router = APIRouter(
    prefix="/admin",  # Tüm endpoint'ler /admin ile başlar
    tags=["Admin"]     # Swagger UI etiketi
)

# --------------------------------------------------
# ADMIN YETKİ KONTROLÜ
# --------------------------------------------------

def get_current_admin(current_user: User = Depends(get_current_user)):
    if current_user.is_admin != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN, 
            detail="Admin yetkisi gereklidir."
        )
    return current_user


# --------------------------------------------------
# REQUEST MODELLERİ
# --------------------------------------------------
class MovieCreate(BaseModel):
    title: str
    overview: Optional[str] = None
    release_date: Optional[str] = None
    poster_url: Optional[str] = None
    genres: Optional[str] = None

class UserRoleUpdate(BaseModel):
    is_admin: int  # 1: Admin, 0: User, 2: Moderator

# --------------------------------------------------
# DASHBOARD İSTATİSTİKLERİ
# --------------------------------------------------
@router.get("/dashboard")
def get_stats(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return {
        "total_users": db.query(User).count(),
        "total_movies": db.query(Movie).count(),
        "total_reviews": db.query(Review).count()
    }
# --------------------------------------------------
# ANALYTICS (GELİŞMİŞ İSTATİSTİKLER)
# --------------------------------------------------
@router.get("/analytics")
def get_analytics(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    from datetime import datetime, timedelta
    
    # Calculate last 7 days
    today = datetime.utcnow().date()
    dates = [today - timedelta(days=i) for i in range(6, -1, -1)]
    
    weekly_data = []
    
    for d in dates:
        # User count for this day
        # Note: SQLite stores datetime as string usually, so we compare date part
        # Or simple range filter: start of day to end of day
        start_of_day = datetime(d.year, d.month, d.day)
        end_of_day = start_of_day + timedelta(days=1)
        
        user_count = db.query(User).filter(User.created_at >= start_of_day, User.created_at < end_of_day).count()
        review_count = db.query(Review).filter(Review.created_at >= start_of_day, Review.created_at < end_of_day).count()
        
        weekly_data.append({
            "day": d.strftime("%a"), 
            "new_users": user_count,
            "new_reviews": review_count
        })

    # Coğrafi dağılım
    geography = [
            {"country": "Türkiye", "count": db.query(User).count()}, 
            {"country": "Diğer", "count": 0}
    ]
    # --------------------------------------------------
    # EN İYİ FİLMLER
    # --------------------------------------------------
    top_movies = (
        db.query(Movie)
        .order_by(Movie.vote_average.desc(), Movie.vote_count.desc())
        .limit(10)
        .all()
    )

    ## En çok yorum alan filmler
    top_commented = (
        db.query(Movie, func.count(Review.id).label('total_reviews'))
        .join(Review, Review.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.count(Review.id).desc())
        .limit(10)
        .all()
    )

     # En çok beğenilen filmler
    top_liked = (
        db.query(Movie, func.count(Like.id).label('total_likes'))
        .join(Like, Like.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.count(Like.id).desc())
        .limit(10)
        .all()
    )

    ## En yüksek puan alan filmler
    top_rated = (
        db.query(Movie, func.avg(Rating.score).label('avg_score'), func.count(Rating.id).label('count'))
        .join(Rating, Rating.movie_id == Movie.id)
        .group_by(Movie.id)
        .order_by(func.avg(Rating.score).desc())
        .limit(10)
        .all()
    )
    
    # --------------------------------------------------
    # TÜRLERE GÖRE DAĞILIM
    # --------------------------------------------------
    import json
    all_movies = db.query(Movie).all()
    genre_counts = {}
    
    genre_map = {
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
        "Western": "Western"
    }

    for m in all_movies:
        if m.genres:
            try:
                g_list = json.loads(m.genres)
                for g in g_list:
                    g_name = g['name']
                    # Translate if available, else keep original
                    g_name_tr = genre_map.get(g_name, g_name)
                    genre_counts[g_name_tr] = genre_counts.get(g_name_tr, 0) + 1
            except:
                pass
                
    genre_data = [{"name": k, "value": v} for k, v in genre_counts.items()]
    # Sort by value desc
    genre_data.sort(key=lambda x: x['value'], reverse=True)

    return {
        "weekly_activity": weekly_data, 
        "geography": geography,
        "top_movies": [{"id": m.id, "title": m.title, "rating": m.vote_average, "count": m.vote_count} for m in top_movies],
        "top_commented_movies": [{"id": m.id, "title": m.title, "review_count": count} for m, count in top_commented],
        "top_liked_movies": [{"id": m.id, "title": m.title, "like_count": count} for m, count in top_liked],
        "top_rated_movies": [{"id": m.id, "title": m.title, "avg_score": round(avg, 1), "count": count} for m, avg, count in top_rated],
        "genre_distribution": genre_data[:10], # Top 10 genres
        "active_users": get_active_users_stats(db),
        "system_health": get_system_health(db)
    }
# --------------------------------------------------
# SİSTEM SAĞLIK KONTROLÜ
# --------------------------------------------------
def get_system_health(db: Session):
    import time
    from sqlalchemy import text
    start_time = time.time()
    try:
        db.execute(text("SELECT 1"))
        latency = (time.time() - start_time) * 1000 # ms
        return {
            "status": "Online",
            "latency": round(latency, 2),
            "color": "#4caf50" # Green
        }
    except Exception as e:
        print(f"Health Check Error: {e}")
        return {
            "status": "Offline",
            "latency": 0,
            "color": "#f44336" # Red
        }

# --------------------------------------------------
# AKTİF KULLANICI ANALİZİ
# --------------------------------------------------
def get_active_users_stats(db: Session):
    
    review_counts = db.query(Review.user_id, func.count(Review.id)).group_by(Review.user_id).all()
    review_map = {user_id: count for user_id, count in review_counts}

    
    like_counts = db.query(Like.user_id, func.count(Like.id)).group_by(Like.user_id).all()
    like_map = {user_id: count for user_id, count in like_counts}

    
    users = db.query(User).all()
    
    active_users_list = []
    for user in users:
        r_count = review_map.get(user.id, 0)
        l_count = like_map.get(user.id, 0)
        total_score = r_count + l_count
        
        if total_score > 0:
            active_users_list.append({
                "id": user.id,
                "username": user.username,
                "email": user.email,
                "review_count": r_count,
                "like_count": l_count,
                "total_score": total_score
            })
            
    # Sort by total score
    active_users_list.sort(key=lambda x: x['total_score'], reverse=True)
    
    return active_users_list[:10]


@router.post("/movies")
def add_movie(movie: MovieCreate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    
    import random
    fake_tmdb_id = random.randint(1000000, 9999999)
    
    new_movie = Movie(
        tmdb_id=fake_tmdb_id,
        title=movie.title,
        overview=movie.overview,
        release_date=movie.release_date,
        poster_url=movie.poster_url,
        genres=movie.genres, 
        popularity=0,
        vote_average=0,
        vote_count=0
    )
    db.add(new_movie)
    db.commit()
    db.refresh(new_movie)
    return {"message": "Movie added", "movie_id": new_movie.id}

@router.delete("/movies/{movie_id}")
def delete_movie(movie_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
    
    db.delete(movie)
    db.commit()
    return {"message": "Movie deleted"}


@router.get("/users", response_model=list[UserOut])
def list_users(db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    return db.query(User).all()

@router.delete("/users/{user_id}")
def delete_user(user_id: int, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    
    if user.id == admin.id:
        raise HTTPException(400, "Kendinizi silemezsiniz.")

    db.delete(user)
    db.commit()
    return {"message": "User deleted"}

@router.put("/users/{user_id}/role")
def update_user_role(user_id: int, role_data: UserRoleUpdate, db: Session = Depends(get_db), admin: User = Depends(get_current_admin)):
    user = db.query(User).filter(User.id == user_id).first()
    if not user:
        raise HTTPException(404, "User not found")
    
    user.is_admin = role_data.is_admin
    db.commit()
    return {"message": "User role updated", "is_admin": user.is_admin}
