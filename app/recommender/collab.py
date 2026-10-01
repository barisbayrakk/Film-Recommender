import numpy as np
#Sözlük yapısını otomatik başlatmak için
#Boş key hatalarını önler
from collections import defaultdict

def recommend_by_collab(user_id, ratings, movies, top_n=20):
    """
    ratings: List[Rating] ORM objeleri
    movies: List[Movie]
    """

    # --------------------------------------------------
    # 1. KULLANICININ PUANLADIĞI FİLMLERİ BUL
    # --------------------------------------------------
    # user_ratings sözlüğü şu yapıya sahiptir:
    # { movie_id : rating }
    user_ratings = {r.movie_id: r.rating for r in ratings if r.user_id == user_id}
    
    # Eğer kullanıcı hiç puan vermemişse (cold start problemi),
    # collaborative filtering çalıştırılamaz

    if not user_ratings:
        return []   

    # --------------------------------------------------
    # 2. HER FİLMİ HANGİ KULLANICILAR PUANLAMIŞ?
    # --------------------------------------------------
    # movie_to_users sözlüğü şu yapıya sahiptir:
    # { movie_id : { user_id : rating } }
    movie_to_users = defaultdict(dict)
    for r in ratings:
        movie_to_users[r.movie_id][r.user_id] = r.rating

     # --------------------------------------------------
    # 3. KULLANICI BENZERLİKLERİNİ HESAPLA
    # --------------------------------------------------
    # similarities sözlüğü:
    # { other_user_id : similarity_score }
    similarities = defaultdict(float)
    
    # Sistemdeki tüm kullanıcılar üzerinde dolaş

    for other_user in set(r.user_id for r in ratings):
        
        # Kullanıcının kendisiyle karşılaştırılması anlamsızdır,
        # bu nedenle atlanır
        if other_user == user_id:
            continue

       
        # --------------------------------------------------
        # 4. ORTAK PUANLANAN FİLMLERİ BUL
        # --------------------------------------------------
        # İki kullanıcının da puan verdiği filmler
        common_movies = [
            m for m in user_ratings if m in movie_to_users and other_user in movie_to_users[m]
        ]
        
        # Ortak film yoksa benzerlik hesaplanamaz

        if not common_movies:
            continue
        
        # --------------------------------------------------
        # 5. PUAN VEKTÖRLERİNİ OLUŞTUR
        # --------------------------------------------------
        # Hedef kullanıcının puan vektörü
        v1 = np.array([user_ratings[m] for m in common_movies])
        # Diğer kullanıcının puan vektörü
        v2 = np.array([movie_to_users[m][other_user] for m in common_movies])

         # --------------------------------------------------
        # 6. COSINE SIMILARITY HESABI
        # --------------------------------------------------
        # Cosine similarity formülü:
        # (v1 · v2) / (||v1|| * ||v2||)
        sim = np.dot(v1, v2) / (np.linalg.norm(v1) * np.linalg.norm(v2))
         # Hesaplanan benzerlik skoru kaydedilir
        similarities[other_user] = sim

      # Eğer hiçbir kullanıcıyla benzerlik bulunamadıysa
    if not similarities:
        return []
 
    # --------------------------------------------------
    # 7. EN BENZER KULLANICIYI BUL
    # --------------------------------------------------
    # En yüksek cosine similarity değerine sahip kullanıcı seçilir
    top_user = max(similarities, key=similarities.get)

     # --------------------------------------------------
    # 8. BENZER KULLANICININ SEVDİĞİ AMA
    #    HEDEF KULLANICININ İZLEMEDİĞİ FİLMLER
    # --------------------------------------------------
    recs = []
    for movie_id, rating in movie_to_users.items():
        if top_user in rating and movie_id not in user_ratings:
            recs.append(movie_id)

    results = []
    for m in movies:
        if m.id in recs:
            results.append({
                "id": m.id,
                "title": m.title,
                "poster_path": m.poster_path,
                "overview": m.overview,
                "vote_average": m.vote_average,
                "popularity": m.popularity,
            })

    return results[:top_n]
