# app/routers/reviews.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.review import Review
from app.models.movie import Movie
from app.models.users import User
from app.utils.nlp import is_clean_text
# JWT tabanlı kullanıcı doğrulama
from app.core.jwt import get_current_user
# NLP tabanlı içerik temizliği / uygunsuz dil kontrolü
from app.services.nlp_filter import is_clean
from app.db import SessionLocal
from app.db import get_db

# --------------------------------------------------
# ROUTER TANIMI
# --------------------------------------------------
# Tüm endpoint’ler /reviews ile başlar
router = APIRouter(prefix="/reviews", tags=["Reviews"])

# --------------------------------------------------
# YORUM EKLE
# --------------------------------------------------
@router.post("/add/{movie_id}")
def add_review(movie_id: int, text: str, 
               is_spoiler: bool = False, 
               db: Session = Depends(get_db),
               current_user: User = Depends(get_current_user)):
    # --------------------------------------------------
    # 1. NLP TABANLI UYGUNSUZ İÇERİK KONTROLÜ
    # --------------------------------------------------
    if not is_clean(text):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Yorumunuz argo veya uygunsuz içerik barındırıyor."
        )
    # --------------------------------------------------
    # 2. FİLM VAR MI KONTROLÜ
    # --------------------------------------------------
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status.HTTP_404_NOT_FOUND, "Film bulunamadı")
    # --------------------------------------------------
    # 3. YORUM OLUŞTURMA
    # --------------------------------------------------
    review = Review(
        text=text, 
        user_id=current_user.id, 
        movie_id=movie_id,
        is_spoiler=is_spoiler # spoiler bilgisi ayrıca tutulur
    )
    db.add(review)
    db.commit()
    db.refresh(review)

    return {"message": "Yorum eklendi", "review": review}

# --------------------------------------------------
# KULLANICININ KENDİ YORUMLARI
# --------------------------------------------------
@router.get("/my-reviews")
def get_my_reviews(db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    reviews = db.query(Review).filter(
        Review.user_id == current_user.id
    ).order_by(Review.created_at.desc()).all()
    
    results = []
    # Her yorum için ilgili film bilgisi eklenir
    for r in reviews:
        movie = db.query(Movie).filter(Movie.id == r.movie_id).first()
        results.append({
            "id": r.id,
            "text": r.text,
            "created_at": r.created_at,
            "movie": {
                "id": movie.id if movie else 0,
                "title": movie.title if movie else "Unknown Movie",
                "poster_path": movie.poster_path if movie else ""
            }
        })
    return results

# --------------------------------------------------
# BELİRLİ BİR FİLME AİT TÜM YORUMLAR
# --------------------------------------------------
@router.get("/{movie_id}")
def get_movie_reviews(movie_id: int, db: Session = Depends(get_db)):
    reviews = db.query(Review).filter(
        Review.movie_id == movie_id
    ).order_by(Review.created_at.desc()).all()
    
    
    results = []
     # Yorum sahibinin kullanıcı adı da eklenir
    for r in reviews:
        user = db.query(User).filter(User.id == r.user_id).first()
        results.append({
            "id": r.id,
            "text": r.text,
            "is_spoiler": r.is_spoiler, 
            "created_at": r.created_at, 
            "user": {
                "username": user.username if user else "Anonim"
            }
        })
    return results
# --------------------------------------------------
# YORUM SİL
# --------------------------------------------------
@router.delete("/delete/{review_id}")
def delete_review(review_id: int, db: Session = Depends(get_db), current_user: User = Depends(get_current_user)):
    review = db.query(Review).filter(
        Review.id == review_id,
        Review.user_id == current_user.id
    ).first()

    if not review:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND, 
            detail="Yorum bulunamadı veya silme yetkiniz yok"
        )
    
    db.delete(review)
    db.commit()
    return {"message": "Yorum silindi"}
