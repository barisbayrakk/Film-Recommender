from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.models.like import Like
from app.models.movie import Movie
from app.core.security import get_current_user
from app.db import SessionLocal
from app.db import get_db


# --------------------------------------------------
# LIKES ROUTER TANIMI
# --------------------------------------------------
# Tüm endpoint’ler /likes ile başlar
router = APIRouter(prefix="/likes", tags=["Likes"])

# --------------------------------------------------
# LIKE TOGGLE ENDPOINT'I
# --------------------------------------------------
@router.post("/toggle/{movie_id}")
def toggle_like(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. Film gerçekten var mı kontrol edilir
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")

    like = (
        db.query(Like)
        .filter(Like.user_id == current_user.id, Like.movie_id == movie_id)
        .first()
    )
    # 3. Eğer daha önce beğenilmişse -> beğeni silinir
    if like:
        db.delete(like)
        db.commit()
        return {"liked": False}

    new_like = Like(user_id=current_user.id, movie_id=movie_id)
    db.add(new_like)
    db.commit()
    db.refresh(new_like)

    return {"liked": True}


@router.get("/me")
def my_likes(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    likes = (
        db.query(Like)
        .filter(Like.user_id == current_user.id)
        .all()
    )
    return {"movie_ids": [l.movie_id for l in likes]}


from app.routers.movies import convert
# --------------------------------------------------
# KULLANICININ TÜM BEĞENDİĞİ FİLMLERİN ID'LERİ
# --------------------------------------------------
@router.get("/me/details")
def my_likes_details(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    likes = (
        db.query(Like)
        .filter(Like.user_id == current_user.id)
        .all()
    )
    
    movies = []
      # Her beğeni için ilgili film bilgisi alınır
    for l in likes:
        m = db.query(Movie).filter(Movie.id == l.movie_id).first()
        if m:
            movies.append(convert(m))
    
    return movies

