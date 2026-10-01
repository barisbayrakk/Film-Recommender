
from fastapi import APIRouter, Depends, HTTPException, Body
from sqlalchemy.orm import Session
from app.db import get_db
from app.core.security import get_current_user_optional
from app.services.nlp_filter import is_clean
from app.services.recommendation import recommend_personal, recommend_by_genre, recommend_by_actor
from app.models.movie import Movie
from sqlalchemy import or_
from app.services.nlp_service import generate_embeddings_for_db, semantic_search, hybrid_search
from app.db import SessionLocal
from thefuzz import process
import random

router = APIRouter(prefix="/chatbot", tags=["Chatbot"])





from app.models.movie import Movie
from sqlalchemy import or_

## Türkçe ekleri temizlemek için kullanılan basit suffix listesi
# Amaç: "tarantino'nun" -> "tarantino"
suffixes = ["nın", "nin", "nun", "nün", "den", "dan", "ten", "tan"]

stopwords = {
    "filmleri", "filmi", "oynadığı", "yönettiği", "yönetmen", "kimdir", "öner", "bana", "hakkında", "izle",
    "var", "mi", "mı", "mu", "mü", "film", "benzer", "tarzı", "gibi", "ile", "ve", "veya", "olan", "yapan", "listele", "göster", "getir", "bul",
    "filmii", "flimi", "fılm", "fılmı", "oner", "hngi", "yapım", 
    "hani", "şöyle", "böyle", "işte", "falan", "filan", "yani", "acaba", "şey", "diyorlar",
    "farklı", "değişik", "başka", "daha",
    "filim", "filimler", "filimlerini", "filimlerin", "filmlerini", "filmlerin",
    "yönetmeni", "yonetmen", "yonetmeni", "yönetmeninin",
    "oyuncu", "oyuncusu", "oyuncuları", "oyuncusunun",
    "tüm", "bütün", "hepsi", "hepsini", "tamamı"
}

# Kullanıcıya daha önce ne önerildiğini tutan global oturum hafızası
# Amaç:
# - Aynı filmi tekrar önermemek
# - "Başka?", "Daha?" gibi devam sorularını anlayabilmek
SESSION_MEMORY = {}

# Kullanıcıların isimleri yanlış yazmasına karşı eşleştirme tablosu
# Örn: "cm yılmaz" -> "Cem Yılmaz"
CELEBRITY_ALIASES = {
    # Cem Yılmaz 
    "cm yılmaz": "Cem Yılmaz",
    "cem yılmz": "Cem Yılmaz",
    "cemyılmaz": "Cem Yılmaz",
    "cem yilmaz": "Cem Yılmaz",
    "cm yilmaz": "Cem Yılmaz",
    "cmylmz": "Cem Yılmaz",
    
    # Şahan Gökbakar 
    "şahan": "Şahan Gökbakar",
    "sahan": "Şahan Gökbakar",
    "gökbakar": "Şahan Gökbakar",
    "sahan gokbakar": "Şahan Gökbakar",
    "recep ivedik": "Şahan Gökbakar",
    
    # Kenan İmirzalıoğlu
    "kenan": "Kenan İmirzalıoğlu",
    "imirzalıoğlu": "Kenan İmirzalıoğlu",
    "kenan imirzalioglu": "Kenan İmirzalıoğlu",
    
    # Ata Demirer
    "ata": "Ata Demirer",
    "demirer": "Ata Demirer",
    
    # Yılmaz Erdoğan
    "yılmaz erdoğan": "Yılmaz Erdoğan",
    "yilmaz erdogan": "Yılmaz Erdoğan",
    
    # Directors
    "tarantino": "Quentin Tarantino",
    "nolan": "Christopher Nolan",
    "scorsese": "Martin Scorsese",
    "spielberg": "Steven Spielberg",
    "kubrick": "Stanley Kubrick",
    "hitchcock": "Alfred Hitchcock",
    "fincher": "David Fincher",
    "villeneuve": "Denis Villeneuve",
    
    # Famous actors
    "dicaprio": "Leonardo DiCaprio",
    "leo": "Leonardo DiCaprio",
    "deniro": "Robert De Niro",
    "de niro": "Robert De Niro",
    "pacino": "Al Pacino",
    "brad pitt": "Brad Pitt",
    "pitt": "Brad Pitt",
    "tom hanks": "Tom Hanks",
    "hanks": "Tom Hanks",
    "morgan freeman": "Morgan Freeman",
    "freeman": "Morgan Freeman",
    "keanu": "Keanu Reeves",
    "keanu reeves": "Keanu Reeves",
}

def clean_tokens(query):
    # 1. Tokenize
    tokens = query.split()
    cleaned_tokens = []
    for t in tokens:
        
        if t in stopwords: continue
        
       
        # "tarantino'nun" -> "tarantino"
        candidate = t
        for s in suffixes:
            if t.endswith(s) and len(t) > len(s) + 2: 
                candidate = t[:-len(s)]
                break
        
        cleaned_tokens.append(candidate)
        
    return " ".join(cleaned_tokens).strip()


def generate_search_variants(q):
    variants = {q, q.lower(), q.upper()}
    
   
    def tr_title_case(text):
        words = text.lower().split()
        cap_words = []
        for w in words:
            if not w: continue
            first = w[0]
            rest = w[1:]
            if first == "i": first = "İ"
            elif first == "ı": first = "I"
            else: first = first.upper()
            cap_words.append(first + rest)
        return " ".join(cap_words)
    
    titled = tr_title_case(q)
    variants.add(titled)
    
    # (Türkçe karakterleri temizle)
    tr_map = {
        "ı": "i", "ğ": "g", "ü": "u", "ş": "s", "ö": "o", "ç": "c",
        "İ": "I", "Ğ": "G", "Ü": "U", "Ş": "S", "Ö": "O", "Ç": "C"
    }
    anglicized = "".join(tr_map.get(c, c) for c in q)
    variants.add(anglicized)
    variants.add(anglicized.lower())
    variants.add(anglicized.title())
    
    
    swapped_i = q.replace("i", "İ").replace("I", "ı")
    variants.add(swapped_i)
    swapped_i2 = q.replace("İ", "i").replace("ı", "I") 
    variants.add(swapped_i2)

   
    try:
            import json
            escaped = json.dumps(q).strip('"')
            variants.add(escaped)
            escaped_titled = json.dumps(titled).strip('"')
            variants.add(escaped_titled)
    except:
            pass
    
    return list(variants)

# 🌟 ICONIC CHARACTERS MAPPING
ICONIC_CHARACTERS = {
    "al pacino": ["Michael Corleone", "Tony Montana"],
    "marlon brando": ["Vito Corleone"],
    "robert de niro": ["Travis Bickle", "Vito Corleone"],
    "christian bale": ["Batman", "Bruce Wayne"],
    "heath ledger": ["Joker"],
    "johnny depp": ["Jack Sparrow"],
    "daniel radcliffe": ["Harry Potter"],
    "elijah wood": ["Frodo"],
    "viggo mortensen": ["Aragorn"]
}


def search_people(query, db, exclude_ids=None):
    if len(query) < 2: return None
    
    variants = generate_search_variants(query)
    
    
    query_lower_check = query.lower()
    matched_chars = []
    for actor, chars in ICONIC_CHARACTERS.items():
        if actor in query_lower_check: 
            variants.extend(chars)
            matched_chars.extend(chars)
    
    filters = []
    
    filters.append(Movie.cast.ilike(f"%{query}%"))
    filters.append(Movie.directors.ilike(f"%{query}%"))
    
    for v in variants:
        filters.append(Movie.cast.ilike(f"%{v}%"))
        filters.append(Movie.directors.ilike(f"%{v}%"))
        
    base_query = db.query(Movie).filter(or_(*filters))
    
    if exclude_ids:
        ex_list = list(exclude_ids)
        
        base_query = base_query.filter(Movie.id.not_in(ex_list))
        
    res = base_query.order_by(Movie.popularity.desc()).limit(5).all() 
    return res

@router.on_event("startup")
def load_embeddings():
    db = SessionLocal()
    movies = db.query(Movie).all()
    generate_embeddings_for_db(movies)
    
    
    from app.services.nlp_service import get_popular_people
    
    global POPULAR_PEOPLE
    POPULAR_PEOPLE = get_popular_people()
    
    print(f"🧶 Fuzzy Search için {len(POPULAR_PEOPLE)} kişi hafızaya alındı (Cache).")
    
    
    db.close()

@router.post("/ask")
async def ask_chatbot(
    msg: dict = Body(...),
    db: Session = Depends(get_db),
    current_user=Depends(get_current_user_optional)
):
    try:
        return await ask_chatbot_impl(msg, db, current_user)
    except Exception as e:
        import traceback
        trace = traceback.format_exc()
        print(f"Chatbot Error: {trace}")
        return {"reply": "Üzgünüm, şu anda yanıt veremiyorum. Lütfen biraz sonra tekrar deneyin.", "action": "none"}

async def ask_chatbot_impl(
    msg: dict,
    db: Session,
    current_user
):
    text = msg.get("message", "").strip()
    if not text:
        return {"reply": "...", "action": "none"}

    
    session_id = msg.get("session_id")
    if current_user:
        session_id = f"user_{current_user.id}"
        
    context = SESSION_MEMORY.setdefault(session_id, {}) if session_id else {}

    
    affirmation_keywords = ["tamam", "olur", "peki", "evet", "tabii", "öner", "göster", "neden olmasın", "olabilir", "aynen", "tabi"]
    if text.lower().strip(".,!") in affirmation_keywords:
        pending = context.get("pending_suggestion")
        if pending:
             print(f"✅ Suggestion Accepted: {pending}")
             text = pending # Transform "tamam" -> "Komedi filmleri"
             context["pending_suggestion"] = None # Consume it

    
    import re

    text = re.sub(r'[^\w\s,.?!\'\"]', '', text).strip()
    
    # 0. GİRDİ UZUNLUĞU VE ANLAMSIZLIK KONTROLÜ
    if len(text) < 3:
        return {"reply": "Anlayamadım, biraz daha detay verebilir misin?", "action": "none"}

    # Eğer girdi çok uzun ama içinde boşluk yoksa (rastgele harf dizisi)
    if len(text) > 15 and " " not in text:
        return {"reply": "Girdiğin metni tam anlayamadım. Film ismi veya tür mü yazmıştın?", "action": "none"}
    
    text_lower = text.lower()

    if not is_clean(text_lower):
        context["pending_suggestion"] = "Komedi ve aksiyon filmleri"
        return {
            "reply": "Üslubunuza dikkat etmenizi rica ediyorum 😔. Modunuzu değiştirmek için güzel bir film izlemeye ne dersiniz? Size komedi veya aksiyon önerebilirim 🎬",
            "action": "none"
        }

    # 1. SOHBET / CHITTER CHATTER
    greetings = ["merhaba", "selam", "hi", "hello", "naber", "günaydın", "iyi akşamlar", "selamlar", "mrb", "slm"]
    
    
    best_greet = process.extractOne(text_lower, greetings)
    if best_greet and best_greet[1] >= 80:
        return {
            "reply": "Merhaba! Ben FilmRec asistanıyım. Sana film önerebilir, teknik destek verebilir veya hesabınla ilgili yardımcı olabilirim. Ne istersin?",
            "action": "none"
        }

    if any(x in text_lower for x in ["nasılsın", "nasıl gidiyor", "ne haber"]):
        return {"reply": "Harikayım! Film izlemek (daha doğrusu önermek) beni mutlu ediyor. Sen nasılsın?"}
    
    
    mood_responses = [
        "iyiyim", "iyiym", "iyi", "süperim", "harikayım", "bomba gibiyim", 
        "fena değil", "idare eder", "kötüyüm", "modum düşük", "pek iyi değilim", "moralim bozuk",
        "hissediyorum", "mutsuzum", "canım sıkkın", "üzgünüm", "keyfim yok"
    ]

    # "iyi" gibi kelimeler film aramalarında da geçebileceği için (iyi film öner), arama niyeti yoksa cevapla
    if any(x in text_lower for x in mood_responses) and not any(k in text_lower for k in ["film", "öner", "izle"]):
        if any(neg in text_lower for neg in ["kötü", "değilim", "düşük", "bozuk", "fenayım"]):
            context["pending_suggestion"] = "Komedi filmleri"
            return {"reply": "Bunu duyduğuma üzüldüm. Belki seni neşelendirecek bir komedi filmi modunu düzeltebilir? 🎬", "action": "none"}
        else:
            return {"reply": "Bunu duyduğuma sevindim! 😊 Sana nasıl bir film önermemi istersin? 🤖", "action": "none"}

    if any(x in text_lower for x in ["teşekkür", "tesekkür", "sağol", "eyvallah"]):
        return {"reply": "Rica ederim! İyi seyirler 🍿"}

    if any(x in text_lower for x in ["kimsin", "adın ne", "sen kimsin"]):
        return {"reply": "Ben FilmRec Asistanı. Senin film zevkini çözüp nokta atışı öneriler yapmak için buradayım."}

  
    personal_keywords = ["zevkime", "beğendiklerim", "bana özel", "kütüphanem"]
    if any(k in text_lower for k in personal_keywords):
        if not current_user:
             return {"reply": "Kütüphanene göre öneri yapabilmem için giriş yapmalısın. 😉", "action": "login_redirect"}
        
        
        genre_tr_map = {
            "Action": "Aksiyon", "Comedy": "Komedi", "Drama": "Dram",
            "Science Fiction": "Bilim Kurgu", "Horror": "Korku", "Thriller": "Gerilim",
            "Crime": "Suç", "Adventure": "Macera", "Romance": "Romantik",
            "Animation": "Animasyon", "Family": "Aile", "War": "Savaş",
            "History": "Tarih", "Mystery": "Gizem", "Western": "Western",
            "Documentary": "Belgesel", "Music": "Müzik", "Fantasy": "Fantastik"
        }
        
        
        lib_context = context.get("library_rec", {})
        previously_recommended = set(lib_context.get("recommended_ids", []))
        
        
        movies, top_genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
        
        if movies and top_genres:
            tr_genres = [genre_tr_map.get(g, g) for g in top_genres]
            reply = f"🎬 Sevdiğin türlere ({', '.join(tr_genres)}) göre bunları seçtim:"
        elif movies:
            reply = "🎬 Beğendiğin filmlere göre önerilerim:"
        else:
            return {"reply": "Kütüphanen henüz boş veya yeterli veri yok. Biraz film beğenip tekrar gel! ⭐", "action": "none"}
        
        
        new_recommended_ids = list(previously_recommended) + [m.id for m in movies]
        if len(new_recommended_ids) > 100:
            new_recommended_ids = new_recommended_ids[-100:]  
        
        if session_id:
            context["library_rec"] = {"recommended_ids": new_recommended_ids}
            SESSION_MEMORY[session_id] = context
        
        return {
            "reply": reply,
            "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
        }

    # 1.5 UPCOMING / YAKINDA OLANLAR
    # "Yakındaki filmler" butonu veya benzer sorgular için
    upcoming_keywords = ["yakında", "gelecek", "vizyon", "ne zaman", "geliyor"]
   
    if any(k in text_lower for k in upcoming_keywords):
        from datetime import date
        today = date.today().isoformat()
        
        # Gelecek filmleri bul (Release date > today)
        # release_date string format YYYY-MM-DD usually.
        upcoming_movies = (db.query(Movie)
                           .filter(Movie.release_date > today)
                           .order_by(Movie.release_date.asc())
                           .limit(5).all())
        
        if upcoming_movies:
             return {
                "reply": "Yakında vizyona girecek şu filmleri buldum:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in upcoming_movies]
            }
        else:
            return {
                "reply": "Şu an için veritabanımda yakın tarihli bir film görünmüyor."
            }

    # 1.5 "BEĞENDİKLERİME GÖRE ÖNER" - Genre-based from Liked Movies
    liked_based_keywords = ["beğendiklerime", "sevdiklerime", "beğenilerime", "liked", "favorilerime"]
    if any(k in text_lower for k in liked_based_keywords):
        print(f"❤️ Beğendiklerime Göre Öner tetiklendi: {text}")
        
        # 1. LOGIN CHECK
        if not current_user:
            popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
            return {
                "reply": "Beğenilerine göre öneri yapabilmem için giriş yapmalısın! 🔐 Şimdilik en popüler filmlere göz at:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
            }
        
        
        liked_context = context.get("liked_recommendation", {})
        previously_recommended = set(liked_context.get("recommended_ids", []))
        
        print(f"📊 Liked Context: excluded={len(previously_recommended)}")
        
        # 3. GET TOP 2 GENRES FROM LIKED MOVIES
        # Use recommend_by_genre which already does this analysis
        movies, top_genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
        
        # 4. TRANSLATE GENRES TO TURKISH
        genre_tr_map = {
            "Action": "Aksiyon", "Comedy": "Komedi", "Drama": "Dram",
            "Science Fiction": "Bilim Kurgu", "Horror": "Korku", "Thriller": "Gerilim",
            "Crime": "Suç", "Adventure": "Macera", "Romance": "Romantik",
            "Animation": "Animasyon", "Family": "Aile", "War": "Savaş",
            "History": "Tarih", "Mystery": "Gizem", "Western": "Western",
            "Documentary": "Belgesel", "Music": "Müzik", "Fantasy": "Fantastik"
        }
        
        if movies and top_genres:
            # Show only top 2 genres
            tr_genres = [genre_tr_map.get(g, g) for g in top_genres[:2]]
            genre_names = ", ".join(tr_genres)
            
            # Update session memory with recommended IDs
            new_recommended_ids = list(previously_recommended) + [m.id for m in movies]
            
            # Keep only last 50 to avoid memory bloat
            if len(new_recommended_ids) > 50:
                new_recommended_ids = new_recommended_ids[-50:]
            
            if session_id:
                if session_id not in SESSION_MEMORY:
                    SESSION_MEMORY[session_id] = {}
                SESSION_MEMORY[session_id]["liked_recommendation"] = {
                    "recommended_ids": new_recommended_ids
                }
            
            print(f"🎯 Liked Recommendation: genres={top_genres[:2]}, count={len(movies)}, total_excluded={len(new_recommended_ids)}")
            
            return {
                "reply": f"🎬 {genre_names} türünde sana özel seçtiklerim:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
            }
        
        # 5. FALLBACK: No liked movies or genres exhausted -> Popular movies
        popular_query = db.query(Movie).filter(~Movie.id.in_(previously_recommended))
        popular = popular_query.order_by(Movie.popularity.desc()).limit(5).all()
        
        if popular:
            new_recommended_ids = list(previously_recommended) + [m.id for m in popular]
            if len(new_recommended_ids) > 50:
                new_recommended_ids = new_recommended_ids[-50:]
            
            if session_id:
                if session_id not in SESSION_MEMORY:
                    SESSION_MEMORY[session_id] = {}
                SESSION_MEMORY[session_id]["liked_recommendation"] = {
                    "recommended_ids": new_recommended_ids
                }
            
            return {
                "reply": "Beğenilerine göre önerilerim tükendi! 🎬 Popüler filmlerden devam edelim:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
            }
        else:
            return {
                "reply": "Tüm filmleri önerdim! 🎉 Biraz mola verelim mi?",
                "movies": []
            }

    # 2. GENRE DETECTION (En yüksek öncelik - "Komedi filmi aç" deyince komedi gelmeli)
    genres_map = {
        "aksiyon": "Action", "komedi": "Comedy", "dram": "Drama",
        "bilim": "Science Fiction", "kurgu": "Science Fiction", "teknoloji": "Science Fiction",
        "korku": "Horror", "gerilim": "Thriller", "suç": "Crime",
        "macera": "Adventure", "romantik": "Romance", 
        "animasyon": "Animation", "aile": "Family", "savaş": "War",
        "tarih": "History", "gizem": "Mystery", "western": "Western"
    }

    # Keywords for "New / Latest"
    new_intent_keywords = ["yeni", "son", "2024", "2025", "güncel", "en yeni", "yakın"]
    is_new_intent = any(k in text_lower for k in new_intent_keywords)

    # Context is already loaded at start


    # Keywords for "Refinement / Continuation"
    refinement_keywords = ["daha", "başka", "yenileri", "eskileri", "peki", "ya", "değil"]
    is_refinement = any(k in text_lower for k in refinement_keywords) and len(text.split()) < 5
    
    # Merge Context if Refinement
    if is_refinement and context:
        print(f"🧠 Context Merging Triggered for {session_id}: {context}")
        
        # If user says "Daha yenileri", keep genre but change sort intent
        if "yenileri" in text_lower or "yeni" in text_lower:
            is_new_intent = True
            
        # If user says "Peki aksiyon?", override genre
        # We let standard detection run first, if it finds a new genre, it overrides.
        
    # 2. GENRE DETECTION (Positive & Negative)
    found_genres = set()     # (name, db_value)
    excluded_genres = set()  # db_value only
    
    negative_keywords = ["olmasın", "istemiyorum", "hariç", "sevmem", "nefret", "değil", "yok"]
    
    # Yardımcı: Bir genre metinde geçiyor mu ve negatif mi?
    def analyze_genre_intent(text, genre_name, genre_val):
        idx = text.find(genre_name)
        if idx == -1: return False
        
        # Kelime sınırlarını kontrol et (optional but good)
        # Şimdilik basit context check
        
        # Context window: 5 chars before, 25 chars after
        start = max(0, idx - 10)
        end = min(len(text), idx + len(genre_name) + 25)
        context_str = text[start:end]
        
        is_negative = any(nk in context_str for nk in negative_keywords)
        return is_negative

    # Yardımcı: Bir kişi ismi metinde geçiyor mu ve negatif mi?
    def analyze_person_intent(text, person_name):
        idx = text.find(person_name)
        if idx == -1: return False
        
        # Context window
        start = max(0, idx - 15) # Biraz daha geniş geriye bak
        end = min(len(text), idx + len(person_name) + 25)
        context_str = text[start:end]
        
        is_negative = any(nk in context_str for nk in negative_keywords)
        return is_negative

    # 2.1 Exact Match Check
    for k, v in genres_map.items():
        if k in text_lower:
            if analyze_genre_intent(text_lower, k, v):
                excluded_genres.add(v)
                print(f"🚫 Negative Genre Detected: {k}")
            else:
                found_genres.add((k, v))
            
    # 2.2 Fuzzy Match (if needed - skipping logic for simplicity or can adapt)
    # ... (Keep existing fuzzy logic but add negation check if you want, usually exact covers it)
    
    # ... (Existing fuzzy loop logic - simplified for brevity in this replacement) ...
     
    tokens = text_lower.split()
    genre_keys = list(genres_map.keys())
    for t in tokens:
        if len(t) < 4: continue
        if any(k in t for k in genre_keys): continue
        match = process.extractOne(t, genre_keys)
        if match:
            best_match, score = match
            if score >= 80:
            
                if analyze_genre_intent(text_lower, t, genres_map[best_match]):
                     excluded_genres.add(genres_map[best_match])
                     print(f"🚫 Fuzzy Negative: {best_match}")
                else:
                     found_genres.add((best_match, genres_map[best_match]))

   
    last_intent = context.get("last_intent")
    should_restore_genre = (
        not found_genres and 
        not excluded_genres and 
        context.get("last_genres") and 
        (is_refinement or len(text.split()) < 4) and
        last_intent != "person"  
    )
    
    if should_restore_genre:
         
         found_genres = set(tuple(x) for x in context['last_genres'])

    unique_genre_values = set()
    display_genre_names = []
    
    for k, v in found_genres:
        if v not in unique_genre_values:
            unique_genre_values.add(v)
            display_genre_names.append(k.capitalize())

    is_pure_genre_query = False
    
    
    if unique_genre_values or excluded_genres:
        
        turkish_keywords = ["türk", "yerli", "türkçe"]
        is_turkish_intent = any(k in text_lower for k in turkish_keywords)

        foreign_keywords = ["yabancı"]
        is_foreign_intent = any(k in text_lower for k in foreign_keywords)
        
        noise = ["filmleri", "filmi", "film", "öner", "listele", "aç", "getir", "var", "mı", "boşluk", "bana", "ve", "ile", "daha", "yenileri", "olan"] 
        all_noise = noise + new_intent_keywords + negative_keywords + turkish_keywords + foreign_keywords # Add keywords to noise
        
        clean_t = text_lower
        for k, v in found_genres: clean_t = clean_t.replace(k, "")
        
     
        for k in genres_map:
            if k in clean_t: clean_t = clean_t.replace(k, "")
            
        for n in all_noise:
            clean_t = clean_t.replace(n, "").strip() # Remove noise
            
        if len(clean_t) < 4 or (context.get("last_genres") and not is_refinement == False):
            is_pure_genre_query = True

    if is_pure_genre_query and (unique_genre_values or excluded_genres):
        
        if session_id:
            if session_id not in SESSION_MEMORY: SESSION_MEMORY[session_id] = {"recommended_ids": set()}
            if "recommended_ids" not in SESSION_MEMORY[session_id]: SESSION_MEMORY[session_id]["recommended_ids"] = set()
            
           
            if found_genres:
                SESSION_MEMORY[session_id]["last_genres"] = list(found_genres)
            SESSION_MEMORY[session_id]["last_intent"] = "genre"
            
    
        query_base = db.query(Movie)
        
        
        if is_turkish_intent:
            query_base = query_base.filter(Movie.original_language == 'tr')
        elif is_foreign_intent:
            query_base = query_base.filter(Movie.original_language != 'tr')
        
    
        for g_val in unique_genre_values:
            query_base = query_base.filter(Movie.genres.like(f"%{g_val}%"))
            
        
        for g_val in excluded_genres:
            query_base = query_base.filter(~Movie.genres.like(f"%{g_val}%")) # NOT LIKE

        
        if session_id:
            excluded_ids = SESSION_MEMORY[session_id].get("recommended_ids", set())
            if excluded_ids:
                query_base = query_base.filter(Movie.id.not_in(excluded_ids))

        
        if is_new_intent:
             movies = query_base.order_by(Movie.release_date.desc()).limit(5).all()
             joined_names = " - ".join(display_genre_names) if display_genre_names else "Genel"
             reply_msg = f"İşte senin için en yeni {joined_names} filmleri"
        else:
            
             candidates = query_base.order_by(Movie.vote_average.desc()).limit(50).all()
             if candidates:
                 movies = random.sample(candidates, min(len(candidates), 5))
             else:
                 movies = []
             
             joined_names = " - ".join(display_genre_names) if display_genre_names else "Önerilen"
             
             if not movies and session_id:
                 
                 SESSION_MEMORY[session_id]["recommended_ids"] = set()
                 
                 query_base_retry = db.query(Movie)
                 for g_val in unique_genre_values: query_base_retry = query_base_retry.filter(Movie.genres.like(f"%{g_val}%"))
                 for g_val in excluded_genres: query_base_retry = query_base_retry.filter(~Movie.genres.like(f"%{g_val}%"))
                 movies = query_base_retry.order_by(Movie.vote_average.desc()).limit(5).all()
                 reply_msg = f"Tüm seçenekleri gösterdim! İşte tekrar:"
             else:
                 reply_msg = f"İşte {joined_names} filmleri:"

        if excluded_genres:
             reply_msg += " (İstemediğin türleri çıkardım 🚫)"

        # 5. SAVE IDs
        if session_id and movies:
            current_ids = {m.id for m in movies}
            SESSION_MEMORY[session_id]["recommended_ids"].update(current_ids)

        return {
            "reply": reply_msg,
            "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
        }

    # 3. YARDIMCI FONKSİYONLAR VE ARAMA HAZIRLIĞI
    search_query = clean_tokens(text_lower)
    print(f"🕵️ CHATBOT DEBUG: text_lower='{text_lower}' -> clean_tokens='{search_query}'")
    
    import json
    from sqlalchemy import or_

    import json
    from sqlalchemy import or_



    def search_title(query):
        if len(query) < 2: return None
        variants = generate_search_variants(query)
        filters = []
        for v in variants:
            filters.append(Movie.title.ilike(f"%{v}%"))
        res = db.query(Movie).filter(or_(*filters)).order_by(Movie.popularity.desc()).limit(5).all()
        return res

    
    theme_keywords = [
        "mafya", "gangster", "çete", "suç örgütü", "yeraltı",
        "savaş", "asker", "ordu", "cephe",
        "uzay", "galaksi", "gezegen", "astronot",
        "zombi", "vampir", "hayalet", "cin", "doğaüstü",
        "intikam", "öç", "felaket", "kıyamet",
        "dedektif", "cinayet", "soruşturma",
        "hapishane", "mahkum", "kaçış",
        "ağlatan", "hüzünlü", "duygusal", "romantik", "aşk",
        "komik", "güldüren", "eğlenceli",
        "korkunç", "ürkütücü", "gerilimli"
    ]
    
    
    has_theme_keyword = False
    for kw in theme_keywords:
        
        pattern = r"(?<!\w)" + re.escape(kw) + r"(?!\w)"
        if re.search(pattern, text_lower):
            has_theme_keyword = True
            break
    
    if has_theme_keyword:
        print(f"🎬 Theme keyword detected, triggering semantic search: {text}")
        semantic_results = hybrid_search(text, top_k=5, score_threshold=0.45)
        if semantic_results:
            return {
                "reply": "Aradığın konuya uygun şunları buldum:",
                "movies": semantic_results
            }
        
        
        print(f"🔍 Semantic failed, trying overview keyword search for: {text}")
        theme_keyword_found = None
        for kw in theme_keywords:
            if kw in text_lower:
                theme_keyword_found = kw
                break
        
        if theme_keyword_found:
           
            overview_results = (db.query(Movie)
                .filter(or_(
                    Movie.overview_tr.ilike(f"%{theme_keyword_found}%"),
                    Movie.overview.ilike(f"%{theme_keyword_found}%")
                ))
                .order_by(Movie.popularity.desc())
                .limit(5).all())
            
            if overview_results:
                return {
                    "reply": f"'{theme_keyword_found}' konulu filmler:",
                    "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in overview_results]
                }
    
   
    # "BAŞKA" INTENT
    person_query = search_query 
    
    continuation_keywords = ["başka", "daha", "farklı", "yenileri", "peki", "sıradaki", "devam", "değişik"]
    is_continuation = any(k in text_lower for k in continuation_keywords)
    
    last_person_query = context.get("last_person_query")
    
    if is_continuation and last_person_query:
        
         temp_clean = text_lower
         for ck in continuation_keywords:
             temp_clean = temp_clean.replace(ck, "")
         
         
         # E.g. "Peki başka?" -> " ?" -> short
         if len(temp_clean.strip()) < 5: 
             person_query = last_person_query
             search_query = person_query # Update display name to the person, not "Peki başka"
             print(f"🔄 Bağlam Korundu ({text}): {person_query} için yeni sonuçlar aranıyor...")
    
    # NEW: Handle continuation without context (User says "farklı" but no previous search)
    elif is_continuation and not last_person_query:
         temp_clean = text_lower
         for ck in continuation_keywords:
             temp_clean = temp_clean.replace(ck, "")
         
         if len(temp_clean.strip()) < 4:
             return {
                 "reply": "Henüz bir arama yapmadın. Önce bir oyuncu, yönetmen veya film türü söylemelisin. 😉",
                 "action": "none"
             }


    
    should_search_people = len(person_query) > 2 and (not has_theme_keyword or (is_continuation and last_person_query))
    
    if should_search_people:
        
        exclude_ids = set()
        
        if session_id and session_id in SESSION_MEMORY and is_continuation:
             exclude_ids = SESSION_MEMORY[session_id].get("recommended_ids", set())

        
        is_negative_person = analyze_person_intent(text_lower, person_query)
        if is_negative_person:
             print(f"🚫 Negative Person Intent Detected: {person_query}. Skipping People Search.")
             people_res = [] 
        else:
             
             alias_match = CELEBRITY_ALIASES.get(text_lower) or CELEBRITY_ALIASES.get(person_query)
             if alias_match:
                 print(f"🎭 Alias Match Found: '{text_lower}' -> '{alias_match}'")
                 people_res = search_people(alias_match, db, exclude_ids)
                 if people_res:
                     search_query = alias_match  
             else:
                 people_res = []
             
             
             if not people_res:
                 people_res = search_people(text_lower if not is_continuation else person_query, db, exclude_ids)
             
            
             if not people_res and person_query != text_lower:
                 people_res = search_people(person_query, db, exclude_ids)
                 
             
             if not people_res and "'" in person_query:
                 cleaned = person_query.split("'")[0].strip()
                 people_res = search_people(cleaned, db, exclude_ids)
    
             #
             if not people_res:
                 cleaned = person_query
                 for s in suffixes:
                     if cleaned.endswith(s):
                         
                         candidate = cleaned[:-len(s)].strip()
                         
                         if len(candidate) > 2:
                               if not analyze_person_intent(text_lower, candidate):
                                   people_res = search_people(candidate, db, exclude_ids)
                                   if people_res: 
                                       search_query = candidate 
                                       break
                               else:
                                   print(f"🚫 Negative Person Intent on Suffix Candidate: {candidate}") 

        
        if not people_res:
             
             global POPULAR_PEOPLE
             try:
                 POPULAR_PEOPLE
             except NameError:
                 POPULAR_PEOPLE = [] 
             
             
             people_list = list(POPULAR_PEOPLE) if POPULAR_PEOPLE else []
             print(f"🔍 DEBUG Fuzzy: Query='{text_lower}', POPULAR_PEOPLE count={len(people_list)}")
             
             if people_list:
                 match = process.extractOne(text_lower if not is_continuation else person_query, people_list)
                 print(f"🔍 DEBUG Fuzzy Match Result: {match}")
                 if match:
                     best_name, score = match
                     if score >= 70: 
                         
                         if analyze_person_intent(text_lower, best_name) or analyze_person_intent(text_lower, person_query):
                             print(f"🚫 Negative Person Intent on Fuzzy Match: {best_name}")
                         else:
                             print(f"🧶 Fuzzy Person Match: '{person_query}' -> '{best_name}' ({score}%)")
                             people_res = search_people(best_name, db, exclude_ids)
                             search_query = best_name # Update for display 

        
        if not people_res and is_continuation and last_person_query and exclude_ids:
             
             name_display = last_person_query.title()
             return {
                "reply": f"{name_display} için veritabanımızda başka film kalmadı! Önerilerim bu kadar.",
                "movies": [] 
             }

        if people_res:
             
             if session_id:
                 if session_id not in SESSION_MEMORY: SESSION_MEMORY[session_id] = {"recommended_ids": set()}
                 if "recommended_ids" not in SESSION_MEMORY[session_id]: SESSION_MEMORY[session_id]["recommended_ids"] = set()
                 
                 
                 if not is_continuation:
                     SESSION_MEMORY[session_id]["recommended_ids"] = set()
                     print(f"🧹 Session history cleared for new search: {search_query}")

                 SESSION_MEMORY[session_id]["last_person_query"] = search_query 
                 SESSION_MEMORY[session_id]["last_intent"] = "person"
                 
                 current_ids = {m.id for m in people_res}
                 SESSION_MEMORY[session_id]["recommended_ids"].update(current_ids)

            
             name_display = search_query.title()
             if "'" in name_display: name_display = name_display.split("'")[0]
             
             reply_prefix = f"'{name_display}' (oyuncu/yönetmen) ile ilgili şunları buldum:"
             if is_continuation: 
                  reply_prefix = f"{name_display} için diğer önerilerim:"  
             
             return {
                "reply": reply_prefix,
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in people_res]
            }

   
    similarity_keywords = ["gibi", "benzer", "tarzı", "tarzında", "benzeri"]
    has_similarity_intent = any(k in text_lower for k in similarity_keywords)
    
    if has_similarity_intent:
        print(f"🎯 Similarity Intent Detected for: {text}")
        
    
        title_candidate = text_lower
        for kw in similarity_keywords:
            if kw in title_candidate:
                title_candidate = title_candidate.split(kw)[0].strip()
                break
        
       
        noise_words = ["film", "filmi", "bir", "bana", "öner"]
        for nw in noise_words:
            title_candidate = title_candidate.replace(nw, "").strip()
        
        
        primary_movie = None
        if len(title_candidate) > 2:
            title_match = db.query(Movie).filter(Movie.title.ilike(f"%{title_candidate}%")).first()
            if title_match:
                primary_movie = title_match
                print(f"🎬 Primary Title Found: {primary_movie.title}")
        
        
        semantic_basis = primary_movie.title if primary_movie else text
        semantic_results = hybrid_search(semantic_basis, top_k=4)
        
        
        if primary_movie and semantic_results:
            semantic_results = [m for m in semantic_results if m.get("id") != primary_movie.id]
        
        if primary_movie:
            
            movies_list = [{"id": primary_movie.id, "title": primary_movie.title, "poster": primary_movie.poster_url or primary_movie.poster_path}]
            
            reply_text = f"'{primary_movie.title}' filmini bulduk!"
            if semantic_results:
                reply_text += " Bu filme benzer diğer önerilerim:"
                movies_list.extend(semantic_results)
            
            return {
                "reply": reply_text,
                "movies": movies_list
            }
        elif semantic_results:
            
            return {
                "reply": "Aradığın türde şunları buldum:",
                "movies": semantic_results
            }
    
    recommendation_keywords = ["öner", "tavsiye", "ne izle", "zevkim", "benim için", "mood"]
    if any(k in text_lower for k in recommendation_keywords) and not found_genres and not is_continuation:

        if not current_user:
            # Login yoksa popüler filmleri verelim
            popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
            return {
                "reply": "Sana özel zevkine göre öneri yapabilmem için giriş yapmalısın. Ama şimdilik en popüler şu filmlere göz at:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
            }
        

        
       
        rec_context = context.get("recommendation", {})
        last_rec_type = rec_context.get("last_type", None)
        previously_recommended = set(rec_context.get("recommended_ids", []))
        
    
        if last_rec_type == "genre":
            
            movies, actors = recommend_by_actor(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
            rec_type = "actor"
            if movies and actors:
                actor_names = ", ".join(actors[:2])
                reply = f"🎭 {actor_names} gibi oyuncuların başka filmleri:"
            else:
               
                movies, genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
                rec_type = "genre"
                
                
                genre_tr_map = {
                    "Action": "Aksiyon", "Comedy": "Komedi", "Drama": "Dram",
                    "Science Fiction": "Bilim Kurgu", "Horror": "Korku", "Thriller": "Gerilim",
                    "Crime": "Suç", "Adventure": "Macera", "Romance": "Romantik",
                    "Animation": "Animasyon", "Family": "Aile", "War": "Savaş",
                    "History": "Tarih", "Mystery": "Gizem", "Western": "Western",
                    "Documentary": "Belgesel", "Music": "Müzik", "Fantasy": "Fantastik"
                }
                tr_genres = [genre_tr_map.get(g, g) for g in genres[:2]]
                genre_names = ", ".join(tr_genres)
                reply = f"🎬 {genre_names} türünde sana özel seçtiklerim:"
        else:
            
            movies, genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
            rec_type = "genre"
            
            
            genre_tr_map = {
                "Action": "Aksiyon", "Comedy": "Komedi", "Drama": "Dram",
                "Science Fiction": "Bilim Kurgu", "Horror": "Korku", "Thriller": "Gerilim",
                "Crime": "Suç", "Adventure": "Macera", "Romance": "Romantik",
                "Animation": "Animasyon", "Family": "Aile", "War": "Savaş",
                "History": "Tarih", "Mystery": "Gizem", "Western": "Western",
                "Documentary": "Belgesel", "Music": "Müzik", "Fantasy": "Fantastik"
            }
            
            if movies and genres:
                tr_genres = [genre_tr_map.get(g, g) for g in genres[:2]]
                genre_names = ", ".join(tr_genres)
                reply = f"🎬 {genre_names} türünde sana özel seçtiklerim:"
            else:
               
                movies, actors = recommend_by_actor(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
                rec_type = "actor"
                reply = "Beğendiğin filmlerdeki oyuncuların diğer filmleri:"
        
        if movies:
            
            new_recommended_ids = list(previously_recommended) + [m.id for m in movies]
            
            
            if len(new_recommended_ids) > 50:
                new_recommended_ids = new_recommended_ids[-50:]
            
            if session_id:
                SESSION_MEMORY[session_id] = {
                    **context,
                    "recommendation": {
                        "last_type": rec_type,
                        "recommended_ids": new_recommended_ids
                    }
                }
            
            return {
                "reply": reply,
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
            }
        
       
        popular_query = db.query(Movie).filter(~Movie.id.in_(previously_recommended))
        popular = popular_query.order_by(Movie.popularity.desc()).limit(5).all()
        
        if popular:
             
             new_recommended_ids = list(previously_recommended) + [m.id for m in popular]
             if len(new_recommended_ids) > 50: new_recommended_ids = new_recommended_ids[-50:]
             
             if session_id:
                SESSION_MEMORY[session_id] = {
                    **context,
                    "recommendation": {
                        "last_type": "popular",
                        "recommended_ids": new_recommended_ids
                    }
                }
             
             return {
                "reply": "Özel önerilerim tükendi ama popüler filmlerden devam edelim:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
             }
        else:
             
             return {
                 "reply": "Veritabanımdaki tüm filmleri dolaştık! Biraz mola verelim mi? 🎬",
                 "movies": []
             }

    theme_keywords = [
        # Emotions
        "ağlatan", "hüzünlü", "komik", "korkunç", "sürükleyici", "duygusal", "romantik",
        "güldüren", "düşündüren", "heyecanlı", "gerilimli", "ürkütücü",
        # Topics/Themes
        "mafya", "gangster", "çete", "suç örgütü", "yeraltı",
        "savaş", "asker", "ordu", "cephe",
        "uzay", "galaksi", "gezegen", "astronot", "bilim kurgu",
        "zombi", "vampir", "hayalet", "cin", "doğaüstü",
        "aşk", "evlilik", "ilişki", "romantizm",
        "intikam", "öç", "adaletsizlik",
        "hayatta kalma", "survival", "felaket", "kıyamet",
        "dedektif", "cinayet", "gizem", "soruşturma",
        "spor", "futbol", "boks", "basketbol",
        "müzik", "şarkıcı", "konser", "rock", "dans",
        "tarih", "osmanlı", "antik", "ortaçağ", "dünya savaşı",
        "hayal", "rüya", "fantezi", "büyü", "sihir",
        "yapay zeka", "robot", "teknoloji", "hacker",
        "kaçış", "hapishane", "mahkum",
        "aile", "çocuk", "ebeveyn", "çocukluk",
        
        "umut", "samimi", "içten", "dokunaklı", "etkileyici", "ağla", "psikolojik", "derin", "felsefi",
        "hayat", "yaşam", "biyografi", "gerçek", "sanat", "ödüllü"
    ]
    
    is_semantic_likely = len(text.split()) > 3 or any(kw in text_lower for kw in theme_keywords)
    
    #  "Ağlatan dram filmi" 
    should_run_semantic = is_semantic_likely
    
    if found_genres and len(text.split()) < 4 and not any(kw in text_lower for kw in theme_keywords):
        
        should_run_semantic = False

    if should_run_semantic:
        print(f"🧠 Semantic/Theme Search Triggered for: {text}")
        semantic_results = hybrid_search(text, top_k=5, score_threshold=0.4) # 0.4
        if semantic_results:
             return {
                "reply": "Aradığın duyguya veya konuya göre şunları buldum:",
                "movies": semantic_results
            }

    
    if len(search_query) > 2:
        title_res = search_title(search_query)
        # Sadece iyi bir eşleşme varsa dön, yoksa Semantic'e veya Recommendation'a bırak
        if title_res:
             return {
                "reply": f"Bunu mu arıyorsun?",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in title_res]
            }

    # 5. (Rotasyonlu Akıllı Öneri)
    recommendation_keywords = ["öner", "tavsiye", "ne izle", "zevkim", "benim için", "mood"]
    if any(k in text_lower for k in recommendation_keywords):
        if not current_user:
            # Login yoksa popüler filmleri verelim
            popular = db.query(Movie).order_by(Movie.popularity.desc()).limit(5).all()
            return {
                "reply": "Sana özel zevkine göre öneri yapabilmem için giriş yapmalısın. Ama şimdilik en popüler şu filmlere göz at:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
            }
        

        
        
        rec_context = context.get("recommendation", {})
        last_rec_type = rec_context.get("last_type", None)
        previously_recommended = set(rec_context.get("recommended_ids", []))
        
       
        if last_rec_type == "genre":
            # This time: Actor-based
            movies, actors = recommend_by_actor(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
            rec_type = "actor"
            if movies and actors:
                actor_names = ", ".join(actors[:2])
                reply = f"🎭 {actor_names} gibi oyuncuların başka filmleri:"
            else:
                
                movies, genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
                rec_type = "genre"
                reply = "Beğendiğin türlerde şunları önerebilirim:"
        else:
            
            movies, genres = recommend_by_genre(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
            rec_type = "genre"
            if movies and genres:
                genre_names = ", ".join(genres[:2])
                reply = f"🎬 {genre_names} türünde sana özel seçtiklerim:"
            else:
                
                movies, actors = recommend_by_actor(db, current_user.id, exclude_ids=list(previously_recommended), limit=5)
                rec_type = "actor"
                reply = "Beğendiğin filmlerdeki oyuncuların diğer filmleri:"
        
        if movies:
            
            new_recommended_ids = list(previously_recommended) + [m.id for m in movies]
            
            
            if len(new_recommended_ids) > 50:
                new_recommended_ids = new_recommended_ids[-50:]
            
            if session_id:
                SESSION_MEMORY[session_id] = {
                    **context,
                    "recommendation": {
                        "last_type": rec_type,
                        "recommended_ids": new_recommended_ids
                    }
                }
            
            print(f"🎯 Smart Recommendation: type={rec_type}, count={len(movies)}, excluded={len(previously_recommended)}")
            
            return {
                "reply": reply,
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in movies]
            }
        
        
        popular_query = db.query(Movie).filter(~Movie.id.in_(previously_recommended))
        popular = popular_query.order_by(Movie.popularity.desc()).limit(5).all()
        
        if popular:
             
             new_recommended_ids = list(previously_recommended) + [m.id for m in popular]
             if len(new_recommended_ids) > 50: new_recommended_ids = new_recommended_ids[-50:]
             
             if session_id:
                SESSION_MEMORY[session_id] = {
                    **context,
                    "recommendation": {
                        "last_type": "popular",
                        "recommended_ids": new_recommended_ids
                    }
                }
             
             return {
                "reply": "Özel önerilerim tükendi ama popüler filmlerden devam edelim:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular]
             }
        else:
            
             return {
                 "reply": "Veritabanımdaki tüm filmleri dolaştık! Biraz mola verelim mi? 🎬",
                 "movies": []
             }

    if "rastgele" in text_lower or "şans" in text_lower:
        from sqlalchemy.sql.expression import func
        random_movie = db.query(Movie).order_by(func.random()).first()
        if random_movie:
             return {
                "reply": f"Şansına bu çıktı: {random_movie.title}",
                "movies": [{"id": random_movie.id, "title": random_movie.title, "poster": random_movie.poster_url or random_movie.poster_path}]
            }

    
    
    fallback_semantic = hybrid_search(text, top_k=3, score_threshold=0.45)
    if fallback_semantic:
         return {
            "reply": "Tam anlayamadım ama belki şunlar ilgini çeker:",
            "movies": fallback_semantic
        }

    
    
    keywords = [w for w in text_lower.split() if len(w) > 3 and w not in stopwords]
    if keywords:
        keyword_filters = [Movie.title.ilike(f"%{kw}%") for kw in keywords]
        keyword_filters += [Movie.overview_tr.ilike(f"%{kw}%") for kw in keywords]
        keyword_filters += [Movie.genres.ilike(f"%{kw}%") for kw in keywords]
        
        keyword_results = (db.query(Movie)
                            .filter(or_(*keyword_filters))
                            .order_by(Movie.popularity.desc())
                            .limit(5).all())
        
        if keyword_results:
            return {
                "reply": f"'{text}' için tam sonuç bulamadım ama şunlara bakabilirsin:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in keyword_results]
            }
    
    
    # Sadece harf değil, gerçek bir kelimeyse popülerleri öner
    if len(search_query) > 3:
        popular_fallback = db.query(Movie).order_by(Movie.popularity.desc()).limit(3).all()
        if popular_fallback:
            return {
                "reply": "Aradığını bulamadım, ama en popüler filmlere göz atabilirsin:",
                "movies": [{"id": m.id, "title": m.title, "poster": m.poster_url or m.poster_path} for m in popular_fallback]
            }
    
    return {
        "reply": "Bunu tam anlayamadım. 'Komedi filmleri' gibi bir arama yapabilirsin.",
        "action": "none"
    }

    return {
        "reply": "Bunu tam anlayamadım. 'Komedi filmleri', 'Cem Yılmaz', 'Ağlatan filmler' gibi aramalar yapabilirsin.",
        "action": "none"
    }
