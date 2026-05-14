from collections import defaultdict, Counter
from typing import List, Tuple
import numpy as np
import logging

logger = logging.getLogger(__name__)

class NGramModel:
    """
    Modelo de N-gramas con cadenas de Markov.
    Predice la siguiente palabra basada en patrones de secuencias.
    """
    
    def __init__(self, n: int = 3):
        """
        Args:
            n: Tamaño del n-grama (por defecto trigramas)
        """
        self.n = n
        self.ngrams = defaultdict(Counter)
        self.vocab = set()
    
    def train(self, words: List[str]):
        """
        Entrena el modelo con una lista de palabras.
        Construye tabla de frecuencias de n-gramas.
        """
        # Agregar tokens especiales
        padded_words = ["<START>"] * (self.n - 1) + words + ["<END>"]
        self.vocab = set(words)
        
        # Crear n-gramas
        for i in range(len(padded_words) - self.n + 1):
            ngram = tuple(padded_words[i:i + self.n - 1])
            next_word = padded_words[i + self.n - 1]
            self.ngrams[ngram][next_word] += 1
        
        logger.info(f"NGramModel entrenado: {len(self.ngrams)} n-gramas únicos")
    
    def predict_next(self, context: List[str], k: int = 5) -> List[Tuple[str, float]]:
        """
        Predice las siguientes k palabras más probables.
        
        Args:
            context: Lista de palabras anteriores (contexto)
            k: Número de predicciones
        
        Returns:
            Lista de tuplas (palabra, probabilidad)
        """
        # Tomar los últimos (n-1) tokens como contexto
        context = context[-(self.n - 1):]
        context_tuple = tuple(context)
        
        # Si no existe el contexto, retornar palabras frecuentes
        if context_tuple not in self.ngrams:
            return self._get_frequent_words(k)
        
        # Obtener distribución de palabras siguientes
        next_words = self.ngrams[context_tuple]
        total_count = sum(next_words.values())
        
        # Calcular probabilidades
        predictions = [
            (word, count / total_count)
            for word, count in next_words.most_common(k)
        ]
        
        return predictions
    
    def _get_frequent_words(self, k: int = 5) -> List[Tuple[str, float]]:
        """Retorna palabras más frecuentes cuando no hay contexto."""
        all_counts = Counter()
        for counter in self.ngrams.values():
            all_counts.update(counter)
        
        total = sum(all_counts.values())
        return [
            (word, count / total)
            for word, count in all_counts.most_common(k)
        ]