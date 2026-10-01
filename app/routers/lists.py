from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session


from app.models.lists import ListItem
from app.models.movie import Movie
from app.schemas.movies import MovieOut
from app.core.security import get_current_user  
from app.db import SessionLocal
from app.db import get_db

# --------------------------------------------------
# LISTS ROUTER TANIMI
# --------------------------------------------------
# Tüm endpoint’ler /lists ile başlar
router = APIRouter(prefix="/lists", tags=["Lists"])

# --------------------------------------------------
# FİLMİ LİSTEYE EKLE / ÇIKAR (TOGGLE)
# --------------------------------------------------
@router.post("/toggle/{movie_id}")
def toggle_list_item(
    movie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    
    # 1. Film gerçekten var mı kontrol edilir
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(status_code=404, detail="Movie not found")
    # 2. Kullanıcının bu film için listede kaydı var mı?
    item = (
        db.query(ListItem)
        .filter(ListItem.user_id == current_user.id, ListItem.movie_id == movie_id)
        .first()
    )
   
    # 3. Film listede varsa → listeden çıkarılır
    if item:
        db.delete(item)
        db.commit()
        return {"in_list": False}
    
    # 4. Film listede yoksa → listeye eklenir
    new_item = ListItem(user_id=current_user.id, movie_id=movie_id)
    db.add(new_item)
    db.commit()
    db.refresh(new_item)

    return {"in_list": True}

# --------------------------------------------------
# KULLANICININ İZLEME LİSTESİ
# --------------------------------------------------
@router.get("/", response_model=list[MovieOut])
def my_list(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):  
    # Kullanıcının listesinde bulunan kayıtlar alınır
    items = (
        db.query(ListItem)
        .filter(ListItem.user_id == current_user.id)
        .all()
    )
     # Listede bulunan film ID’leri çıkarılır
    movie_ids = [i.movie_id for i in items]
    # Eğer liste boşsa boş dizi döndürülür
    if not movie_ids:
        return []
    
    # Film detayları tek sorgu ile alınır
    movies = (
        db.query(Movie)
        .filter(Movie.id.in_(movie_ids))
        .all()
    )
    return movies
