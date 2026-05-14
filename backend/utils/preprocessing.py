import re
import unicodedata

def clean_text(text: str) -> str:
    """
    Limpia y normaliza el texto.
    
    Args:
        text: Texto a limpiar
    
    Returns:
        Texto limpio
    """
    # Eliminar acentos
    text = remove_accents(text)
    
    # Convertir a minúsculas
    text = text.lower()
    
    # Eliminar caracteres especiales (mantener espacios y letras)
    text = re.sub(r'[^a-záéíóúñ\s]', '', text)
    
    # Eliminar espacios múltiples
    text = re.sub(r'\s+', ' ', text)
    
    # Eliminar espacios al inicio y final
    text = text.strip()
    
    return text

def remove_accents(text: str) -> str:
    """
    Elimina acentos del texto.
    """
    nfkd_form = unicodedata.normalize('NFKD', text)
    return ''.join([c for c in nfkd_form if not unicodedata.combining(c)])