# app/routers/ratings.py
from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError
from app.db import get_db
from app.core.security import get_current_user
from app.models.rating import Rating
from app.models.users import User
from app.schemas.ratings import RatingCreate

# --------------------------------------------------
# ROUTER TANIMI
# --------------------------------------------------
# Tüm endpoint’ler /ratings ile başlar
router = APIRouter(prefix="/ratings", tags=["Ratings"])

# --------------------------------------------------
# PUAN EKLE / GÜNCELLE
# --------------------------------------------------
@router.post("/add", status_code=status.HTTP_201_CREATED)
def add_rating(
    data: RatingCreate,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    """
    Belirli bir filme, giriş yapmış kullanıcı için puan ekler.
    Varsa günceller (Upsert mantığı daha mantıklı olabilir ama şimdilik yeni ekleme/hata).
    """
    
    # --------------------------------------------------
    # 1. Kullanıcının bu film için daha önce puanı var mı?
    # --------------------------------------------------
    existing = db.query(Rating).filter(Rating.user_id == current_user.id, Rating.movie_id == data.movie_id).first()
    # --------------------------------------------------
    # 2. Eğer daha önce puan verilmişse → güncelle
    # --------------------------------------------------
    if existing:
        
        existing.score = data.score
        db.commit()
        return {"message": "Puan güncellendi", "id": existing.id, "score": existing.score}
    # --------------------------------------------------
    # 3. Daha önce puan yoksa → yeni puan oluştur
    # --------------------------------------------------
    new_rating = Rating(
        score=data.score,
        movie_id=data.movie_id,
        user_id=current_user.id,
    )
    db.add(new_rating)
      # --------------------------------------------------
    # 4. Veritabanına kaydetme işlemi
    # --------------------------------------------------
    try:
        db.commit()
        db.refresh(new_rating)
    except Exception as e:
          # Hata durumunda transaction geri alınır
        db.rollback()
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"Sunucu hatası: {e}",
        )

    return {"message": "Rating added", "id": new_rating.id, "score": new_rating.score}

# --------------------------------------------------
# KULLANICININ BELİRLİ BİR FİLME VERDİĞİ PUANI GETİR
# --------------------------------------------------
@router.get("/{movie_id}/my-rating")
def get_my_rating(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user: User = Depends(get_current_user),
):
    rating = db.query(Rating).filter(Rating.user_id == current_user.id, Rating.movie_id == movie_id).first()
      # Kullanıcı henüz puan vermemişse
    if not rating:
        return {"has_rated": False, "score": 0}
    # Kullanıcı puan vermişse
    return {"has_rated": True, "score": rating.score}
