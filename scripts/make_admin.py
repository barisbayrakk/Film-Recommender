import sys
import os
from dotenv import load_dotenv

load_dotenv()

# --------------------------------------------------
# PYTHON PATH AYARI
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ klasörünü import edebilmek için
# mevcut çalışma dizinini sys.path'e ekle
sys.path.append(os.getcwd())

# --------------------------------------------------
# DATABASE & MODEL IMPORTLARI
# --------------------------------------------------
from app.db import SessionLocal
from app.models.users import User
from app.models.collection import Collection
from app.models.watched import Watched # 🔥 Fix for Watched relation
# ==================================================
# KULLANICIYI ADMIN YAPMA FONKSİYONU
# ==================================================
def make_admin():
   # DB session aç
    db = SessionLocal()
    print("--- User List ---")
     # Tüm kullanıcıları çek
    users = db.query(User).all()
     # Hiç kullanıcı yoksa uyar
    if not users:
        print("No users found in database!")
        print("Please register a user first via the Frontend.")
        return
    # --------------------------------------------------
    # KULLANICILARI LİSTELE
    # --------------------------------------------------
    for u in users:
        print(f"ID: {u.id} | Username: {u.username} | Admin: {u.is_admin}")
    
    # --------------------------------------------------
    # ADMIN YAPILACAK KULLANICIYI AL
    # --------------------------------------------------
    username = input("\nEnter username to make ADMIN (or 'q' to quit): ")
    # Çıkış seçeneği
    if username.lower() == 'q':
        return
    
     # --------------------------------------------------
    # KULLANICIYI BUL VE GÜNCELLE
    # --------------------------------------------------
    user = db.query(User).filter(User.username == username).first()
    if user:
            # Admin flag set edilir
        user.is_admin = 1
        db.commit()
        print(f"User '{username}' is now an ADMIN (is_admin=1).")
    else:
        print("User not found!")
# DB session kapat
    db.close()
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
     # Script doğrudan çalıştırıldığında
    # admin yapma fonksiyonunu başlat
    make_admin()
