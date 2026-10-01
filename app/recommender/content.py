import numpy as np
from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer
import json

def recommend_by_content(movies, seed_movie=None, top_n=20):
    """
    movies         : tüm Movie objeleri
    seed_movie     : belirli bir filme göre öneri olsun istiyorsan Movie objesi
    top_n          : kaç öneri istiyorsun
    """

    if not movies:
        return []

   
    # 1)  (title + overview + GENRES + DIRECTORS + CAST)
   
    corpus = []
    
    for m in movies:
        
        genre_str = ""
        try:
            if m.genres:
                g_list = json.loads(m.genres) if isinstance(m.genres, str) else m.genres
                if isinstance(g_list, list):
                      # Türler 5 kez tekrar edilerek ağırlığı artırılır
                    genre_str = " ".join([g.get('name', '') if isinstance(g, dict) else str(g) for g in g_list] * 5)
        except:
             # JSON parse hataları sistemin çökmesini engellemek için yakalanır
            pass

        
        director_str = ""
        try:
            if m.directors:
                d_list = json.loads(m.directors) if isinstance(m.directors, str) else m.directors
                if isinstance(d_list, list):
                    # Yönetmen isimleri boşluksuz yazılır ve 3 kez tekrar edilir
                    director_str = " ".join([d.get('name', '').replace(" ", "") for d in d_list] * 3)
        except:
            pass

        cast_str = ""
        try:
            if m.cast:
                c_list = json.loads(m.cast) if isinstance(m.cast, str) else m.cast
                if isinstance(c_list, list):
                    # Sadece ilk 3 oyuncu alınır, 2 kez tekrar edilir
                    cast_str = " ".join([c.get('name', '').replace(" ", "") for c in c_list[:3]] * 2)
        except:
            pass
        
        # -----------------------------
        # TÜM METİNLERİ BİRLEŞTİR
        # -----------------------------
            
        text = f"{m.title} {m.overview or ''} {genre_str} {director_str} {cast_str}"
        corpus.append(text)

   
     # --------------------------------------------------
    # 2. TF-IDF VEKTÖRLEŞTİRME
    # --------------------------------------------------
    # Stop words: İngilizce anlamsız kelimeler çıkarılır
    tfidf = TfidfVectorizer(stop_words="english")
    try:
        # Metinler sayısal vektörlere dönüştürülür
        matrix = tfidf.fit_transform(corpus)
    except ValueError:
        # Tüm metinler boşsa hata oluşabilir
        return []

    
    
    
    if seed_movie:
        try:
            anchor_index = movies.index(seed_movie)
        except ValueError:
            anchor_index = np.argmax([m.popularity for m in movies])
    else:
        anchor_index = np.argmax([m.popularity for m in movies])

    
    # --------------------------------------------------
    # 4. COSINE SIMILARITY HESABI
    # --------------------------------------------------
    # Referans film ile tüm filmler arasındaki benzerlik hesaplanır
    similarities = cosine_similarity(matrix[anchor_index:anchor_index + 1], matrix).flatten()

    # Filmin kendisi önerilmesin diye similarity değeri düşürülür
    similarities[anchor_index] = -1  

    # En benzer top_n film index'i bulunur
    indices = similarities.argsort()[::-1][:top_n]

     # --------------------------------------------------
    # 5. JSON FORMATINDA SONUÇ DÖNDÜRME
    # --------------------------------------------------
    
    recommended = []
    for idx in indices:
        m = movies[idx]
        recommended.append({
            "id": m.id,
            "title": m.title,
            "poster_path": m.poster_path,
            "overview": m.overview,
            "vote_average": m.vote_average,
            "popularity": m.popularity,
        })

    return recommended
