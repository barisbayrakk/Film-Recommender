
# --------------------------------------------------
# EMBEDDING TABANLI SEMANTIC & HYBRID SEARCH MODÜLÜ
# --------------------------------------------------
# Bu modül:
# - Film verilerini embedding vektörlerine dönüştürür
# - Anlam (semantic) bazlı arama yapar
# - Popülerlik ve IMDb puanı ile hibrit skor üretir
# --------------------------------------------------
import os
import pickle
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
import numpy as np


_model = None
_movie_embeddings = {}  # {movie_id: vector}
_movie_metadata = {}    # {movie_id: {title, poster}}
_popular_people = set()   # Oyuncu / yönetmen isimleri (cache)

# --------------------------------------------------
# MULTILINGUAL EMBEDDING MODEL
# --------------------------------------------------
# Türkçe ve İngilizce metinlerde yüksek başarı sağlar
MODEL_NAME = "paraphrase-multilingual-MiniLM-L12-v2"
# Embeddinglerin disk üzerinde saklandığı dosya
EMBEDDING_FILE = "movie_embeddings.pkl" 

def load_model():
    global _model
    if _model is None:
        print("🧠 NLP Model Yükleniyor (Bu işlem ilk seferde biraz sürebilir)...")
        _model = SentenceTransformer(MODEL_NAME)
        print("✅ NLP Model Yüklendi!")
    return _model

def generate_embeddings_for_db(movies):
    """
    Veritabanındaki filmlerin özetlerini (overview_tr veya overview) vektöre çevirir.
    Cache mekanizması eklendi: Pickle dosyasından okur, yoksa oluşturup kaydeder.
    """
    global _movie_embeddings, _movie_metadata, _model, _popular_people
    
    # --------------------------------------------------
    # 1 CACHE (ÖNBELLEK) KONTROLÜ
    # --------------------------------------------------
    if os.path.exists(EMBEDDING_FILE):
        print(f"📂 Embedding önbelleği bulundu: {EMBEDDING_FILE}")
        try:
            with open(EMBEDDING_FILE, "rb") as f:
                data = pickle.load(f)
                _movie_embeddings = data.get("embeddings", {})
                _movie_metadata = data.get("metadata", {})
                _popular_people = data.get("popular_people", set())
                print(f"✅ {_len(_movie_embeddings)} film ve {_len(_popular_people)} kişi önbellekten yüklendi!")
                
                 # Eğer film sayısı yeterliyse tekrar hesaplama yapma
                if len(_movie_embeddings) >= len(movies) and _popular_people:
                    return
                print("⚠ Yeni filmler var veya kişi listesi eksik, tekrar hazırlanıyor...")
        except Exception as e:
            print(f"❌ Önbellek okuma hatası: {e}")

    # --------------------------------------------------
    # 2️. EMBEDDING ÜRETİMİ
    # --------------------------------------------------
    model = load_model()
    
    print(f"🔄 {len(movies)} film için embedding hazırlanıyor...")
    
    texts = []
    ids = []
    
    _movie_embeddings = {}
    _movie_metadata = {}

    for m in movies:
        # Öncelik Türkçe özet, yoksa İngilizce, o da yoksa başlık
        summary = m.overview_tr if m.overview_tr else (m.overview if m.overview else "")
        
        import json
        
        cast_str = ""
        try:
            if m.cast:
                
                cast_data = json.loads(m.cast) if isinstance(m.cast, str) else m.cast
                if isinstance(cast_data, list):
                    names = [p.get("name", "") for p in cast_data if p.get("name")]
                    cast_str = ", ".join(names[:5]) 
                    
                    
                    for p in cast_data[:10]:
                        if p.get("name"): _popular_people.add(p["name"])
        except:
            cast_str = str(m.cast)

        director_str = ""
        try:
            if m.directors:
                dir_data = json.loads(m.directors) if isinstance(m.directors, str) else m.directors
                if isinstance(dir_data, list):
                    names = [d.get("name", "") for d in dir_data if d.get("name")]
                    director_str = ", ".join(names)
                    
                   
                    for d in names:
                        _popular_people.add(d)
        except:
             director_str = str(m.directors)

        # --------------------------------------------------
        # ZENGİNLEŞTİRİLMİŞ METİN OLUŞTURMA
        # --------------------------------------------------
        # Title, genre ve overview tekrar edilerek
        # embedding içinde daha fazla ağırlık kazanır
        rich_text = f"Film: {m.title}. {m.title}. " 
        if m.genres: rich_text += f"Tür: {m.genres}. {m.genres}. " 
        if director_str: rich_text += f"Yönetmen: {director_str}. "
        if cast_str: rich_text += f"Oyuncular: {cast_str}. "
       
        rich_text += f"Özet: {summary}. {summary}" 
        
        texts.append(rich_text)
        ids.append(m.id)
        
        _movie_metadata[m.id] = {
            "title": m.title,
            "poster": m.poster_url or m.poster_path,
            "vote_average": m.vote_average or 0,
            "popularity": m.popularity or 0
        }

    if texts:
        embeddings = model.encode(texts, convert_to_numpy=True)
        
        for i, movie_id in enumerate(ids):
            _movie_embeddings[movie_id] = embeddings[i]
            
        # 3. Save to Cache
        try:
            with open(EMBEDDING_FILE, "wb") as f:
                pickle.dump({
                    "embeddings": _movie_embeddings,
                    "metadata": _movie_metadata,
                    "popular_people": _popular_people
                }, f)
            print("💾 Embeddingler diske kaydedildi.")
        except Exception as e:
            print(f"❌ Kaydetme hatası: {e}")
            
    print("✅ Embedding işlemi tamamlandı!")

def _len(d):
    return len(d) if d else 0

def get_popular_people():
    global _popular_people
    return _popular_people

def semantic_search(query, top_k=3, score_threshold=0.5):
    """
    Kullanıcının sorgusunu (örn: 'beni ağlatan film') vektöre çevirip
    en yakın filmleri bulur.
    
    Args:
        query: Search query text
        top_k: Maximum number of results
        score_threshold: Minimum cosine similarity score (0-1). Default 0.5
    """

    global _movie_embeddings, _movie_metadata, _model
    
    model = load_model()
    
    if not _movie_embeddings:
        return []

    # Sorgu vektörü
    query_vec = model.encode([query], convert_to_numpy=True)
    
    # Tüm film vektörleri
    movie_ids = list(_movie_embeddings.keys())
    movie_vecs = np.array(list(_movie_embeddings.values()))
    
    if len(movie_vecs) == 0:
        return []

    # Benzerlik hesabı (Cosine Similarity)
    scores = cosine_similarity(query_vec, movie_vecs)[0]
    
    # En yüksek skorlu indexler
    top_indices = np.argsort(scores)[::-1][:top_k]
    
    results = []
    for idx in top_indices:
        score = scores[idx]
        if score < score_threshold: 
            continue # Eşik altındakileri atla
        
        m_id = movie_ids[idx]
        meta = _movie_metadata.get(m_id)
        if meta:
            results.append({
                "id": m_id,
                "title": meta["title"],
                "poster": meta["poster"],
                "score": float(score)
            })
            
    return results


def hybrid_search(query, top_k=5, score_threshold=0.35):
    """
    Semantic search + Popülerlik/Kalite skorlaması.
    Hibrit skor = semantic_score * (1 + quality_boost)
    
    Args:
        query: Search query text
        top_k: Maximum number of results
        score_threshold: Minimum semantic similarity score
    """
    import math
    from difflib import SequenceMatcher
    global _movie_metadata
    
    # 1. Semantic sonuçları al (geniş havuz, düşük eşik)
    raw_results = semantic_search(query, top_k=50, score_threshold=0.3)
    
    if not raw_results:
        return []
    
    # 2. Her sonuç için hibrit skor hesapla
    for r in raw_results:
        meta = _movie_metadata.get(r["id"], {})
        vote = meta.get("vote_average", 5)
        pop = meta.get("popularity", 10)
        
        
        pop_normalized = min(math.log10(pop + 1) / 3, 1)  
        vote_normalized = vote / 10                        
        
        
        quality_boost = (vote_normalized * 0.6) + (pop_normalized * 0.4)
        
        
        # Eğer sorgu = film başlığı ise (veya çok yakınsa), puanı uçur.
        title_lower = meta.get("title", "").lower()
        query_lower = query.lower()
        
        match_ratio = SequenceMatcher(None, query_lower, title_lower).ratio()
        
        title_boost = 0
        if match_ratio > 0.9: # Neredeyse aynı (%90+)
            title_boost = 3.0 # semantic score (genelde 0-1 arası) yanında devasa bir boost
        elif match_ratio > 0.7: # Benziyor
             title_boost = 0.5
        elif query_lower in title_lower: # İçinde geçiyor
             title_boost = 0.2

        # Hibrit skor: semantic * (1 + quality_boost) + title_boost
        r["hybrid_score"] = (r["score"] * (1 + quality_boost)) + title_boost
    
    # 3. Hibrit skora göre sırala
    raw_results.sort(key=lambda x: x["hybrid_score"], reverse=True)
    
    # 4. Eşik üstündekileri döndür
    filtered = [r for r in raw_results if r["score"] >= score_threshold]
    
    return filtered[:top_k]
