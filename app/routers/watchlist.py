
# --------------------------------------------------
# WATCHLIST ROUTER
# Kullanıcının izleme listesine film ekleme ve
# izleme listesini görüntüleme işlemleri
# --------------------------------------------------
@router.post("/")
def add_to_watchlist(movie_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    exists = db.query(Watchlist).filter_by(user_id=user.id, movie_id=movie_id).first()
    if exists:
        raise HTTPException(400, "Already in watchlist")

    wl = Watchlist(user_id=user.id, movie_id=movie_id)
    db.add(wl)
    db.commit()
    return {"message": "Added to watchlist"}


@router.get("/")
def get_watchlist(db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    return db.query(Watchlist).filter_by(user_id=user.id).all()
