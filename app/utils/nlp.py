from app.services.nlp_filter import is_clean

def is_clean_text(text: str) -> bool:
    return is_clean(text)
