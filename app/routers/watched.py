from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user
from app.models.users import User
from app.models.movie import Movie
from app.models.watched import Watched
from app.schemas.movies import MovieOut
from app.routers.movies import convert

router = APIRouter(prefix="/watched", tags=["Watched"])


@router.post("/{movie_id}")
def mark_watched(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")
        
    existing = db.query(Watched).filter(Watched.user_id == current_user.id, Watched.movie_id == movie_id).first()
    #Eğer zaten izlendiyse → kaldır
    if existing:
        
        db.delete(existing)
        db.commit()
        return {"msg": "Film izlediklerimden kaldırıldı", "status": "removed"}
    else:
        #Daha önce izlenmediyse → ekle
        new_watched = Watched(user_id=current_user.id, movie_id=movie_id)
        db.add(new_watched)
        db.commit()
        return {"msg": "Film izlediklerim listesine eklendi", "status": "added"}

## KULLANICININ İZLEDİĞİ TÜM FİLMLERİ LİSTELE
@router.get("/", response_model=list[MovieOut])
def list_watched(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    
    items = db.query(Watched).filter(Watched.user_id == current_user.id).order_by(Watched.created_at.desc()).all()
    
    results = []
    for item in items:
        if item.movie:
            results.append(convert(item.movie))
            
    return results


@router.get("/{movie_id}/check")
def check_watched(movie_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    exists = db.query(Watched).filter(Watched.user_id == current_user.id, Watched.movie_id == movie_id).first()
    return {"is_watched": bool(exists)}
