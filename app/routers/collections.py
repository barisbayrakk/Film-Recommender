from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session, joinedload
from pydantic import BaseModel

from app.db import get_db
from app.core.security import get_current_user
from app.models.collection import Collection, CollectionItem
from app.models.movie import Movie
from app.schemas.movies import MovieOut
# --------------------------------------------------
# COLLECTION ROUTER TANIMI
# --------------------------------------------------
# Tüm endpointler /collections ile başlar
router = APIRouter(prefix="/collections", tags=["Collections"])

# --------------------------------------------------
# REQUEST MODELLERİ
# --------------------------------------------------
class CollectionCreate(BaseModel):
    name: str

class CollectionOut(BaseModel):
    id: int
    name: str
    item_count: int
    movies: list[MovieOut]  # Koleksiyon içindeki filmler

# Movie ORM objesini response formatına dönüştüren yardımcı fonksiyon
from app.routers.movies import convert

# --------------------------------------------------
# KULLANICININ TÜM KOLEKSİYONLARINI GETİR
# --------------------------------------------------

@router.get("/", response_model=list[dict])
def get_my_collections(
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    """Kullanıcının tüm listelerini ve içindeki filmleri getirir"""
    collections = (
        db.query(Collection)
        .filter(Collection.user_id == current_user.id)
        .options(joinedload(Collection.items).joinedload(CollectionItem.movie))
        .all()
    )

    result = []
     # Her koleksiyon için response hazırlanır
    for c in collections:
        
        movie_list = []
        for item in c.items:
            
            if item.movie:
                movie_list.append(convert(item.movie))

        result.append({
            "id": c.id,
            "name": c.name,
            "movies": movie_list
        })
    return result

# --------------------------------------------------
# YENİ KOLEKSİYON OLUŞTUR
# --------------------------------------------------
@router.post("/")
def create_collection(
    data: CollectionCreate,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    
    exists = (
        db.query(Collection)
        .filter(Collection.user_id == current_user.id, Collection.name == data.name)
        .first()
    )
    if exists:
        raise HTTPException(400, "Collection with this name already exists")
    # Yeni koleksiyon oluşturulur
    new_col = Collection(user_id=current_user.id, name=data.name)
    db.add(new_col)
    db.commit()
    db.refresh(new_col)
    
    return {"id": new_col.id, "name": new_col.name, "created": True}

# --------------------------------------------------
# KOLEKSİYON SİL
# --------------------------------------------------
@router.delete("/{collection_id}")
def delete_collection(
    collection_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
     # Koleksiyon kullanıcıya ait mi kontrol edilir
    col = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if not col:
        raise HTTPException(404, "Collection not found")
    # Koleksiyon silinir (cascade sayesinde içindeki filmler de silinir) 
    db.delete(col)
    db.commit()
    return {"deleted": True}


# --------------------------------------------------
# KOLEKSİYONA FİLM EKLE
# --------------------------------------------------
@router.post("/{collection_id}/add/{movie_id}")
def add_movie_to_collection(
    collection_id: int,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
    # 1. Koleksiyon kullanıcıya ait mi?
    col = (
        db.query(Collection)
        .filter(Collection.id == collection_id, Collection.user_id == current_user.id)
        .first()
    )
    if not col:
        raise HTTPException(404, "Collection not found")

    # 2. Film var mı?
    movie = db.query(Movie).filter(Movie.id == movie_id).first()
    if not movie:
        raise HTTPException(404, "Movie not found")

    # 3. Zaten ekli mi?
    exists = (
        db.query(CollectionItem)
        .filter(CollectionItem.collection_id == collection_id, CollectionItem.movie_id == movie_id)
        .first()
    )
    if exists:
        return {"added": False, "detail": "Already in collection"}

    # 4. Ekle
    item = CollectionItem(collection_id=collection_id, movie_id=movie_id)
    db.add(item)
    db.commit()
    return {"added": True}


# --------------------------------------------------
# KOLEKSİYONDAN FİLM ÇIKAR
# --------------------------------------------------
@router.delete("/{collection_id}/remove/{movie_id}")
def remove_movie_from_collection(
    collection_id: int,
    movie_id: int,
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user),
):
     # Film gerçekten bu kullanıcıya ait koleksiyonda mı?
    item = (
        db.query(CollectionItem)
        .join(Collection)
        .filter(
            CollectionItem.collection_id == collection_id,
            CollectionItem.movie_id == movie_id,
            Collection.user_id == current_user.id
        )
        .first()
    )
    if not item:
        raise HTTPException(404, "Item not found in your collection")
     # Film koleksiyondan silinir
    db.delete(item)
    db.commit()
    return {"removed": True}
