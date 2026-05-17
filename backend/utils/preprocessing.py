import re

SPANISH_REPLACEMENTS = str.maketrans({
    "á": "a",
    "é": "e",
    "í": "i",
    "ó": "o",
    "ú": "u",
    "ü": "u",
    "Á": "a",
    "É": "e",
    "Í": "i",
    "Ó": "o",
    "Ú": "u",
    "Ü": "u",
})


def normalize_spanish(text: str) -> str:
    """Normaliza tildes manteniendo la distinción de la letra ñ."""
    return text.translate(SPANISH_REPLACEMENTS).lower()


def normalize_token(token: str) -> str:
    """Normaliza un token individual para uso interno del modelo."""
    normalized = normalize_spanish(token)
    normalized = re.sub(r"[^a-zñ]", "", normalized)
    return normalized.strip()


def clean_text(text: str) -> str:
    """
    Limpia y normaliza el texto preservando tokens útiles para el modelo.
    """
    normalized = normalize_spanish(text)
    normalized = re.sub(r"[^a-zñ\s]", " ", normalized)
    normalized = re.sub(r"\s+", " ", normalized)
    return normalized.strip()
