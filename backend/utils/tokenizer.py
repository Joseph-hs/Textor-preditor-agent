import re
from typing import Dict, List

from .preprocessing import normalize_token

TOKEN_PATTERN = re.compile(r"[A-Za-zÁÉÍÓÚÜÑáéíóúüñ]+")


class SpanishTokenizer:
    """
    Tokenizador especializado para español.
    Trabaja con una representación normalizada consistente para el modelo.
    """

    def __init__(self):
        self.contractions = {
            "al": "a el",
            "del": "de el",
        }

    def _expand_contractions(self, text: str) -> str:
        expanded = text.lower()
        for contraction, expansion in self.contractions.items():
            expanded = re.sub(rf"\b{contraction}\b", expansion, expanded)
        return expanded

    def tokenize(self, text: str, normalize: bool = True) -> List[str]:
        """
        Tokeniza texto en palabras individuales.
        """
        expanded = self._expand_contractions(text)
        tokens = TOKEN_PATTERN.findall(expanded)

        if not normalize:
            return [token.lower() for token in tokens if token]

        normalized_tokens = [normalize_token(token) for token in tokens]
        return [token for token in normalized_tokens if token]

    def analyze_input(self, text: str) -> Dict[str, object]:
        """
        Separa contexto y prefijo actual para decidir entre autocompletado
        y predicción de siguiente palabra.
        """
        tokens = self.tokenize(text)
        ends_with_word = bool(text) and bool(TOKEN_PATTERN.search(text[-1]))
        current_fragment = tokens[-1] if ends_with_word and tokens else ""
        context_tokens = tokens[:-1] if current_fragment else tokens

        return {
            "tokens": tokens,
            "context_tokens": context_tokens,
            "current_fragment": current_fragment,
            "is_autocomplete": bool(current_fragment),
            "ends_with_space": bool(text) and text[-1].isspace(),
        }

    def detokenize(self, tokens: List[str]) -> str:
        return " ".join(tokens)
