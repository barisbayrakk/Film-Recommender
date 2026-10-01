# --------------------------------------------------
# NLP / PROFANITY FILTER
# Kullanıcı yorumlarını küfür, argo ve
# uygunsuz içerikten arındırmak için kullanılır
# --------------------------------------------------

# Küfür ve argo tespiti için kullanılan hazır NLP kütüphanesi
from better_profanity import profanity


profanity.load_censor_words()

# --------------------------------------------------
# Türkçe özel küfür ve argo kelimeler
# Varsayılan listede olmayan kelimeler eklenir
# -------------------------------------------------
custom_bad_words = [
    "aptal", "salak", "gerizekalı", "mal", "bok","öküz", "yavşak", "piç", "amk", "aq", "sik", "siktir"
]
# Özel kelimeleri profanity filtresine ekle
profanity.add_censor_words(custom_bad_words)

# ==================================================
# METİN TEMİZLİK KONTROLÜ
# ==================================================
def is_clean(text: str) -> bool:
    
    return not profanity.contains_profanity(text)
# ==================================================
# METİN SANSÜRLEME
# ==================================================
def clean_text(text: str) -> str:
    
    return profanity.censor(text)
