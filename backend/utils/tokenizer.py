import re
from typing import List

class SpanishTokenizer:
    """
    Tokenizador especializado para español.
    Maneja puntuación, contracciones y caracteres especiales.
    """
    
    def __init__(self):
        # Contracciones en español
        self.contractions = {
            "al": "a el",
            "del": "de el",
        }
    
    def tokenize(self, text: str) -> List[str]:
        """
        Tokeniza texto en palabras individuales.
        
        Args:
            text: Texto a tokenizar
        
        Returns:
            Lista de tokens (palabras)
        """
        # Convertir a minúsculas
        text = text.lower()
        
        # Expandir contracciones
        for contraction, expansion in self.contractions.items():
            text = re.sub(r'\b' + contraction + r'\b', expansion, text)
        
        # Separar por espacios y puntuación
        tokens = re.findall(r'\b\w+\b', text)
        
        return [t for t in tokens if len(t) > 0]
    
    def detokenize(self, tokens: List[str]) -> str:
        """
        Convierte tokens de vuelta a texto.
        """
        return " ".join(tokens)