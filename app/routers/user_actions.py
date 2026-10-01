from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models.user_collections import UserWatchList
from app.models.like import Like
from app.models.movie import Movie

router = APIRouter(prefix="/user", tags=["User Actions"])


# BEĞEN
@router.post("/like/{movie_id}")
def like_movie(movie_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Film bulunamadı")

    exists = db.query(Like).filter_by(
        user_id=user.id, movie_id=movie_id
    ).first()

    if exists:
        return {"message": "Zaten beğenmişsin ❤️"}

    new_like = Like(user_id=user.id, movie_id=movie_id)
    db.add(new_like)
    db.commit()

    return {"message": "Beğenildi ❤️"}


#  LİSTEYE EKLE
@router.post("/watchlist/{movie_id}")
def add_watchlist(movie_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):

    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Film bulunamadı")

    exists = db.query(UserWatchList).filter_by(
        user_id=user.id, movie_id=movie_id
    ).first()

    if exists:
        return {"message": "Zaten listede 📌"}

    new_item = UserWatchList(user_id=user.id, movie_id=movie_id)
    db.add(new_item)
    db.commit()

    return {"message": "Listeye eklendi 📌"}


#  LİSTEDEN ÇIKAR
@router.delete("/watchlist/{movie_id}")
def remove_watchlist(movie_id: int, user=Depends(get_current_user), db: Session = Depends(get_db)):
    item = db.query(UserWatchList).filter_by(
        user_id=user.id, movie_id=movie_id
    ).first()

    if not item:
        raise HTTPException(404, "Film listede değil")

    db.delete(item)
    db.commit()

    return {"message": "Listeden çıkarıldı"}


#  TÜM KOLEKSİYONLAR (BEĞENİLEN + İZLEME LİSTESİ + İZLENENLER)
from app.routers.movies import convert
from app.models.watched import Watched

@router.get("/collections")
def user_collections(user=Depends(get_current_user), db: Session = Depends(get_db)):

    # Beğenilenler
    liked_items = db.query(Like).filter(Like.user_id == user.id).all()
    liked_movies = []
    for item in liked_items:
        movie = db.query(Movie).filter(Movie.id == item.movie_id).first()
        if movie:
            liked_movies.append(convert(movie))

    # İzleme Listesi
    watchlist_items = db.query(UserWatchList).filter(UserWatchList.user_id == user.id).all()
    watchlist_movies = []
    for item in watchlist_items:
        movie = db.query(Movie).filter(Movie.id == item.movie_id).first()
        if movie:
            watchlist_movies.append(convert(movie))

    # İzlenenler (Watched)
    watched_items = db.query(Watched).filter(Watched.user_id == user.id).order_by(Watched.created_at.desc()).all()
    watched_movies = []
    
    from app.models.rating import Rating  
    
    for item in watched_items:
        if item.movie:
            movie_obj = convert(item.movie)
            movie_dict = movie_obj.dict()
            
            
            rating = db.query(Rating).filter(
                Rating.user_id == user.id, 
                Rating.movie_id == item.movie_id
            ).first()
            
            movie_dict["user_rating"] = rating.score if rating else 0
            watched_movies.append(movie_dict)

    # İzlenen filmler, kullanıcının verdiği puana göre sıralanır
    watched_movies.sort(key=lambda x: x["user_rating"], reverse=True)

    return {
        "liked": liked_movies,
        "watchlist": watchlist_movies,
        "watched": watched_movies
    }
