import sqlite3
import datetime

# --------------------------------------------------
# DATABASE PATH
# --------------------------------------------------
# SQLite veritabanı dosyasının yolu
DB_PATH = "app/movies.db"
# ==================================================
# DATABASE GÜNCELLEME FONKSİYONU
# ==================================================
def update_db():
    # Veritabanına bağlan
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    # --------------------------------------------------
    # USERS TABLOSU GÜNCELLEME
    # --------------------------------------------------
    try:
        
        print("Updating users table...")
        cursor.execute("ALTER TABLE users ADD COLUMN created_at TIMESTAMP")
         # Mevcut tüm kullanıcılar için created_at set et
        now = datetime.datetime.utcnow()
        cursor.execute("UPDATE users SET created_at = ?", (now,))
        print("Success: users table updated.")
    except sqlite3.OperationalError as e:
        # Sütun zaten varsa veya tablo yoksa buraya düşer
        print(f"Skipped users: {e}")
    # --------------------------------------------------
    # REVIEWS TABLOSU GÜNCELLEME
    # --------------------------------------------------
    try:
        
        print("Updating reviews table...")
        # created_at sütununu ekle
        cursor.execute("ALTER TABLE reviews ADD COLUMN created_at TIMESTAMP")
         # Mevcut tüm review'lar için created_at set et
        now = datetime.datetime.utcnow()
        cursor.execute("UPDATE reviews SET created_at = ?", (now,))
        print("Success: reviews table updated.")
    except sqlite3.OperationalError as e:
         # Sütun zaten varsa veya tablo yoksa
        print(f"Skipped reviews: {e}")
    # --------------------------------------------------
    # DEĞİŞİKLİKLERİ KAYDET VE KAPAT
    # -------------------------------------------------
    conn.commit()
    conn.close()
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
     # Script doğrudan çalıştırıldığında
    # veritabanı güncellemesini başlat
    update_db()
