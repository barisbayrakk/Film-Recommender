
import os
import sys
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
# --------------------------------------------------
# PROJECT ROOT'U sys.path'E EKLE
# --------------------------------------------------
# Script doğrudan çalıştırıldığında
# app/ içindeki modülleri ve ayarları kullanabilmek için
# proje kök dizini Python path'e eklenir
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
# --------------------------------------------------
# ENV & DATABASE CONNECTION
# --------------------------------------------------
# .env dosyasını yükle
load_dotenv()

DATABASE_URL = os.getenv("DATABASE_URL")
engine = create_engine(DATABASE_URL)

# --------------------------------------------------
# SİLİNECEK FİLM ID'LERİ
# --------------------------------------------------
# Manuel olarak belirlenen problemli / yanlış kayıtlar
ids_to_delete = [1548, 1301, 1259, 1282] 
# --------------------------------------------------
# DELETE İŞLEMİ
# --------------------------------------------------
with engine.connect() as connection:
    print(f"Deleting movies with IDs: {ids_to_delete}")
    
    # Her ID için tek tek kontrol ve silme işlemi
    for movie_id in ids_to_delete:
         # Önce film var mı diye kontrol et
        result = connection.execute(text("SELECT title FROM movies WHERE id = :id"), {"id": movie_id}).fetchone()
        if result:
            # Film varsa sil
            connection.execute(text("DELETE FROM movies WHERE id = :id"), {"id": movie_id})
            # Değişikliği commit et
            connection.commit()
            print(f"Deleted: {result.title} (ID: {movie_id})")
        else:
             # Film bulunamazsa (zaten silinmiş olabilir)
            print(f"Movie ID {movie_id} not found (already deleted?)")

print("Deletion complete.")
