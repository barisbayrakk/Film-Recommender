from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from app.models.comment import Comment
from app.models.users import User
from app.utils.nlp import is_toxic
from app.core.security import get_current_user
from app.db import get_db


# --------------------------------------------------
# COMMENTS ROUTER TANIMI
# --------------------------------------------------
# Tüm endpointler /comments ile başlar
router = APIRouter(prefix="/comments", tags=["Comments"])

# --------------------------------------------------
# YORUM EKLEME ENDPOINT'I
# --------------------------------------------------
@router.post("/")
def add_comment(movie_id: int, text: str, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    # Yorum metni uygunsuz / toksik dil içeriyor mu kontrol edilir
    if is_toxic(text):
        raise HTTPException(status_code=400, detail="Toxic or inappropriate language detected.")
    
    # Yeni yorum nesnesi oluşturulur
    comment = Comment(text=text, movie_id=movie_id, user_id=user.id)
    
    # Yorum veritabanına eklenir
    db.add(comment)
    db.commit()
    db.refresh(comment)

    return {"message": "Comment added", "comment": comment}

# --------------------------------------------------
# YORUM SİLME ENDPOINT'I
# --------------------------------------------------
@router.delete("/{comment_id}")
def delete_comment(comment_id: int, db: Session = Depends(get_db), user: User = Depends(get_current_user)):
    
    # Yorum gerçekten var mı kontrol edilir
    comment = db.query(Comment).filter(Comment.id == comment_id).first()

    if not comment:
        raise HTTPException(status_code=404, detail="Yorum bulunamadı")
    
    # Kullanıcının yetkisi kontrol edilir: Yorum sahibi veya Admin silebilir
    if comment.user_id != user.id and user.is_admin != 1:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="Bu yorumu silme yetkiniz bulunmuyor."
        )

    # Yorum silinir
    db.delete(comment)
    db.commit()

    return {"message": "Comment deleted"}
