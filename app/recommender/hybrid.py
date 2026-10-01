# İçerik tabanlı öneri fonksiyonu
from .content import recommend_by_content
from .collab import recommend_by_collab

def hybrid_recommend(user_id, movies, ratings, top_n=20):
    
    
     # --------------------------------------------------
    # 1. CONTENT-BASED ÖNERİLERİ AL
    # --------------------------------------------------
    # İçerik benzerliğine göre ilk 50 film alınır
    
    content_list = recommend_by_content(movies, top_n=50)

     # --------------------------------------------------
    # 2. COLLABORATIVE FILTERING ÖNERİLERİNİ AL
    # --------------------------------------------------
    # Kullanıcı benzerliğine göre ilk 50 film alınır
    collab_list = recommend_by_collab(user_id, ratings, movies, top_n=50)

    # --------------------------------------------------
    # 3. HİBRİT SKOR TABLOSU
    # --------------------------------------------------
    # scores sözlüğü:
    # { movie_id : toplam_hibrit_skor }
    scores = {}


   
    # --------------------------------------------------
    # 5. COLLABORATIVE FILTERING SKORLAMA (%40 AĞIRLIK)
    # --------------------------------------------------
    for i, m in enumerate(content_list):
        scores[m["id"]] = scores.get(m["id"], 0) + (60 - i)

    
    for i, m in enumerate(collab_list):
        scores[m["id"]] = scores.get(m["id"], 0) + (40 - i)

    # --------------------------------------------------
    # 6. TOPLAM SKORA GÖRE SIRALAMA
    # --------------------------------------------------
    # Film ID ve skor çiftleri, skora göre azalan sırada sıralanır
    ranked = sorted(scores.items(), key=lambda x: x[1], reverse=True)

    
    final = []
    for movie_id, score in ranked[:top_n]:
        for m in movies:
            if m.id == movie_id:
                final.append({
                    "id": m.id,
                    "title": m.title,
                    "poster_path": m.poster_path,
                    "overview": m.overview,
                    "vote_average": m.vote_average,
                    "popularity": m.popularity,
                    "score": score,
                })
                break

    return final
