import re
import unicodedata

def clean_text(text: str) -> str:
    text = remove_accents(text)
    text = text.lower()
    text = re.sub(r'[^a-z\s]', '', text)
    text = re.sub(r'\s+', ' ', text)
    text = text.strip()
    return text

def remove_accents(text: str) -> str:
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])