import numpy as np
from typing import List, Dict
import logging
from .ngrams import NGramModel
from .lstm_model import LSTMModel
from .trie import TrieNode
from utils.tokenizer import SpanishTokenizer
from utils.preprocessing import clean_text

logger = logging.getLogger(__name__)

class TextPredictor:
    """
    Orquestador híbrido que combina 3 modelos:
    1. N-gramas (rápido, base)
    2. LSTM (contexto profundo)
    3. Trie (autocompletado)
    """
    
    def __init__(self, corpus: List[str], vocab_size: int = 500):
        self.corpus = corpus
        self.vocab_size = vocab_size
        self.tokenizer = SpanishTokenizer()
        
        # Inicializar modelos
        self.ngram_model = NGramModel(n=3)
        self.ngram_model.train(corpus)
        
        self.lstm_model = LSTMModel(vocab_size=vocab_size, embedding_dim=128)
        self.lstm_model.train(corpus)
        
        self.trie = TrieNode()
        self._build_trie(corpus)
        
        # Almacenar preferencias de usuario
        self.user_preferences = {}
        
        logger.info(f"TextPredictor inicializado con corpus de {len(corpus)} palabras")
    
    def _build_trie(self, words: List[str]):
        """Construye estructura Trie para autocompletado."""
        for word in words:
            self.trie.insert(word)
    
    def predict(self, text: str, max_suggestions: int = 5, 
                user_adapter=None) -> List[Dict]:
        """
        Realiza predicción mediante enfoque híbrido.
        
        Args:
            text: Texto ingresado por el usuario
            max_suggestions: Número de sugerencias a retornar
            user_adapter: Adaptador de usuario para personalización
        
        Returns:
            Lista de predicciones con confianza
        """
        # Limpiar y tokenizar
        cleaned = clean_text(text)
        tokens = self.tokenizer.tokenize(cleaned)
        
        if not tokens:
            return []
        
        # Obtener palabra parcial (última palabra incompleta)
        last_token = tokens[-1] if tokens else ""
        
        predictions = {}
        
        # 1. Predicción por Trie (autocompletado)
        if last_token:
            trie_completions = self.trie.search_prefix(last_token)
            for word in trie_completions[:max_suggestions]:
                predictions[word] = {
                    "word": word,
                    "confidence": 0.7,  # Trie tiene confianza alta
                    "source": "trie"
                }
        
        # 2. Predicción por N-gramas
        if len(tokens) >= 1:
            ngram_predictions = self.ngram_model.predict_next(
                tokens[-3:],  # Últimas 3 palabras
                k=max_suggestions
            )
            for word, prob in ngram_predictions:
                if word not in predictions:
                    predictions[word] = {
                        "word": word,
                        "confidence": float(prob),
                        "source": "ngram"
                    }
                else:
                    # Combinar confianzas
                    predictions[word]["confidence"] = \
                        (predictions[word]["confidence"] + float(prob)) / 2
        
        # 3. Predicción por LSTM
        lstm_predictions = self.lstm_model.predict_next(tokens, k=max_suggestions)
        for word, prob in lstm_predictions:
            if word not in predictions:
                predictions[word] = {
                    "word": word,
                    "confidence": float(prob),
                    "source": "lstm"
                }
            else:
                # Combinar confianzas (LSTM tiene más peso)
                predictions[word]["confidence"] = \
                    (predictions[word]["confidence"] * 0.4 + float(prob) * 0.6)
        
        # 4. Aplicar adaptación de usuario
        if user_adapter:
            predictions = self._apply_user_preferences(
                predictions, 
                user_adapter,
                cleaned
            )
        
        # Ordenar por confianza y limitar
        sorted_predictions = sorted(
            predictions.values(),
            key=lambda x: x["confidence"],
            reverse=True
        )[:max_suggestions]
        
        return sorted_predictions
    
    def _apply_user_preferences(self, predictions: Dict, 
                                user_adapter, text: str) -> Dict:
        """Aplica preferencias personales del usuario."""
        user_id = user_adapter.user_id
        user_prefs = user_adapter.get_preferences()
        
        # Ajustar confianzas según histórico del usuario
        for word in predictions:
            if word in user_prefs:
                # Aumentar confianza si el usuario ha usado esta palabra antes
                weight = user_prefs[word]["frequency"]
                predictions[word]["confidence"] *= (1 + weight * 0.2)
        
        return predictions
    
    def update_user_preferences(self, user_id: str, selected_word: str):
        """Actualiza preferencias cuando el usuario selecciona una palabra."""
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        
        if selected_word not in self.user_preferences[user_id]:
            self.user_preferences[user_id][selected_word] = {"count": 0}
        
        self.user_preferences[user_id][selected_word]["count"] += 1