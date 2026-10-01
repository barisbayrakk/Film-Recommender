import requests
import json

# --------------------------------------------------
# CHATBOT API ENDPOINT
# --------------------------------------------------
# FastAPI chatbot servisinin lokal endpoint’i
URL = "http://localhost:8000/chatbot/ask"

# --------------------------------------------------
# TEST EDİLECEK SORULAR
# --------------------------------------------------
# Chatbot'un farklı senaryolardaki davranışını görmek için
# çeşitli türde kullanıcı mesajları
QUERIES = [
    "Komedi",
    "Cem Yılmaz",
    "Beni ağlatan bir film öner",
    "Nasılsın",
    "Harry Potter",
    "Aksiyon filmleri",
    "Rastgele film"
]
# ==================================================
# CHATBOT TEST FONKSİYONU
# ==================================================
def test_chatbot():
    print(f"Testing Chatbot at {URL}...\n")
    # Her test sorgusu için ayrı ayrı istek at
    for q in QUERIES:
        print(f"🔹 QUERY: '{q}'")
        try:
             # Chatbot endpoint’ine POST isteği
            resp = requests.post(URL, json={"message": q}, timeout=30)
            if resp.status_code == 200:
                # JSON response parse edilir
                data = resp.json()
                 # Botun metin cevabı
                reply = data.get("reply", "NO REPLY")
                 # Önerilen filmler (varsa)
                movies = data.get("movies", [])
                print(f"🔸 REPLY: {reply}")
                 # Eğer film listesi geldiyse
                if movies:
                    print(f"🔸 MOVIES Found: {len(movies)}")
                    # İlk 2 filmi örnek olarak göster
                    for m in movies[:2]: 
                        print(f"   - {m.get('title')} (ID: {m.get('id')})")
            else:
                 # 4xx / 5xx hataları
                print(f"❌ ERROR: {resp.status_code} - {resp.text}")
        except Exception as e:
            # Network / timeout / connection hataları
            print(f"❌ EXCEPTION: {e}")
        print("-" * 40)
# ==================================================
# SCRIPT ENTRY POINT
# ==================================================
if __name__ == "__main__":
    # Script doğrudan çalıştırıldığında
    # chatbot testlerini başlat
    test_chatbot()
