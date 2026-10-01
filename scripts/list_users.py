import sqlite3
import os

# --------------------------------------------------
# DATABASE PATH
# --------------------------------------------------
# Kullanıcıların tutulduğu SQLite veritabanı dosyası
DB_PATH = "app/movies.db"

# ==================================================
# KULLANICILARI LİSTELE
# ==================================================
def list_users():
    # Veritabanı dosyası var mı kontrol et
    if not os.path.exists(DB_PATH):
        print(f"❌ Veritabanı dosyası bulunamadı: {DB_PATH}")
        return

    try:
        # SQLite bağlantısı aç
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        # Kullanıcı bilgilerini çek
        cursor.execute("SELECT id, username, email, is_verified, is_admin FROM users")
        users = cursor.fetchall()
        
        # --------------------------------------------------
        # TABLO BAŞLIĞI
        # --------------------------------------------------
        print(f"\n{'='*60}")
        print(f"{'ID':<5} {'KULLANICI ADI':<20} {'E-POSTA':<30} {'ONAY':<5} {'ADMIN'}")
        print(f"{'-'*60}")
        
        # --------------------------------------------------
        # KULLANICI SATIRLARI
        # --------------------------------------------------
        for user in users:
            user_id, username, email, is_verified, is_admin = user
            # Doğrulama durumu (emoji ile)
            verified_status = "✅" if is_verified else "❌"
            # Admin durumu (emoji ile)
            admin_status = "👑" if is_admin else "👤"
             # Kullanıcı satırını yazdır
            print(f"{user_id:<5} {username:<20} {email:<30} {verified_status:<5} {admin_status}")
        # --------------------------------------------------
        # ÖZET BİLGİ
        # --------------------------------------------------
        print(f"{'='*60}\n")
        print(f"Toplam Kullanıcı: {len(users)}\n")
         
          # DB bağlantısını kapat
        conn.close()
    except Exception as e:
        # Herhangi bir DB / SQL hatası
        print(f"❌ Hata oluştu: {e}")

# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında
    # kullanıcı listesini yazdır
    list_users()
