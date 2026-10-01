
import requests
import sqlite3
import uuid
# --------------------------------------------------
# API & DATABASE CONFIG
# --------------------------------------------------
# Backend base URL
BASE_URL = "http://127.0.0.1:8000"
# SQLite veritabanı yolu
DB_PATH = "app/movies.db"

def verify_registration_flow():
    # --------------------------------------------------
    # 1) REGISTER İÇİN RASTGELE KULLANICI OLUŞTUR
    # --------------------------------------------------
    username = f"test_user_{uuid.uuid4().hex[:8]}"
    email = f"{username}@example.com"
    password = "testpassword123"
    
    print(f"DTO: Registering user {username}...")
    
    try:
        # --------------------------------------------------
        # REGISTER REQUEST
        # --------------------------------------------------
        response = requests.post(f"{BASE_URL}/auth/register", json={
            "username": username,
            "email": email,
            "password": password
        })
        
        # Register başarısızsa test durur
        if response.status_code != 200:
            print(f"Failed to register: {response.text}")
            return False
            
        print("Registration successful.")
        
        # --------------------------------------------------
        # 2) DATABASE KONTROLÜ
        # --------------------------------------------------
        # Kullanıcı DB'ye yazıldı mı?
        # is_verified = 0 mı?
        conn = sqlite3.connect(DB_PATH)
        cursor = conn.cursor()
        cursor.execute("SELECT is_verified, verification_token FROM users WHERE email = ?", (email,))
        user = cursor.fetchone()
        conn.close()
        
        if not user:
            print("User not found in DB!")
            return False
            
        is_verified, token = user
        print(f"DB State -> is_verified: {is_verified}, token: {token}")
        
        if is_verified != 0:
            print("❌ ERROR: User should NOT be verified automatically!")
            return False
        else:
            print("✅ SUCCESS: User is NOT verified as expected.")
            
        # --------------------------------------------------
        # 3) DOĞRULAMA OLMADAN LOGIN DENEMESİ
        # --------------------------------------------------
        login_res = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
         # Login engellenmeli
        if login_res.status_code == 400 and "doğrulayın" in login_res.text:
             print("✅ SUCCESS: Login prevented as expected.")
        else:
             print(f"❌ ERROR: Login unexpected response: {login_res.status_code} {login_res.text}")
             return False

        # --------------------------------------------------
        # 4) EMAIL DOĞRULAMA (LINK TIKLAMA SİMÜLASYONU)
        # --------------------------------------------------
        print(f"Simulating email click with token: {token}")
        verify_res = requests.get(f"{BASE_URL}/auth/verify-email?token={token}")
        
        if verify_res.status_code == 200:
            print("✅ SUCCESS: Email verification successful.")
        else:
            print(f"❌ ERROR: Verification failed: {verify_res.text}")
            return False

        # --------------------------------------------------
        # 5) DOĞRULAMADAN SONRA LOGIN
        # --------------------------------------------------
        login_res_2 = requests.post(f"{BASE_URL}/auth/login", json={
            "email": email,
            "password": password
        })
        
        if login_res_2.status_code == 200:
             print("✅ SUCCESS: Login successful after verification.")
        else:
             print(f"❌ ERROR: Login failed after verification: {login_res_2.text}")
             return False
        # Tüm akış başarılı
        return True

    except Exception as e:
        # Beklenmeyen hatalar
        print(f"Exception: {e}")
        return False
# --------------------------------------------------
# SCRIPT ENTRY POINT
# --------------------------------------------------
if __name__ == "__main__":
      # Script doğrudan çalıştırıldığında
    # registration + verification flow testini başlat
    verify_registration_flow()
