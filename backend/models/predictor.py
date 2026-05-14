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
    def __init__(self, corpus: List[str], vocab_size: int = 500):
        self.corpus = corpus
        self.vocab_size = vocab_size
        self.tokenizer = SpanishTokenizer()
        self.ngram_model = NGramModel(n=3)
        self.ngram_model.train(corpus)
        self.lstm_model = LSTMModel(vocab_size=vocab_size, embedding_dim=128)
        self.lstm_model.train(corpus)
        self.trie = TrieNode()
        self._build_trie(corpus)
        self.user_preferences = {}
        logger.info(f"TextPredictor inicializado con corpus de {len(corpus)} palabras")
    
    def _build_trie(self, words: List[str]):
        for word in words:
            self.trie.insert(word)
    
    def predict(self, text: str, max_suggestions: int = 5, user_adapter=None) -> List[Dict]:
        cleaned = clean_text(text)
        tokens = self.tokenizer.tokenize(cleaned)
        if not tokens:
            return []
        last_token = tokens[-1] if tokens else ""
        predictions = {}
        
        if last_token:
            trie_completions = self.trie.search_prefix(last_token)
            for word in trie_completions[:max_suggestions]:
                predictions[word] = {"word": word, "confidence": 0.7, "source": "trie"}
        
        if len(tokens) >= 1:
            ngram_predictions = self.ngram_model.predict_next(tokens[-3:], k=max_suggestions)
            for word, prob in ngram_predictions:
                if word not in predictions:
                    predictions[word] = {"word": word, "confidence": float(prob), "source": "ngram"}
                else:
                    predictions[word]["confidence"] = (predictions[word]["confidence"] + float(prob)) / 2
        
        lstm_predictions = self.lstm_model.predict_next(tokens, k=max_suggestions)
        for word, prob in lstm_predictions:
            if word not in predictions:
                predictions[word] = {"word": word, "confidence": float(prob), "source": "lstm"}
            else:
                predictions[word]["confidence"] = (predictions[word]["confidence"] * 0.4 + float(prob) * 0.6)
        
        if user_adapter:
            predictions = self._apply_user_preferences(predictions, user_adapter, cleaned)
        
        sorted_predictions = sorted(predictions.values(), key=lambda x: x["confidence"], reverse=True)[:max_suggestions]
        return sorted_predictions
    
    def _apply_user_preferences(self, predictions: Dict, user_adapter, text: str) -> Dict:
        user_prefs = user_adapter.get_preferences()
        for word in predictions:
            if word in user_prefs:
                weight = user_prefs[word]["frequency"]
                predictions[word]["confidence"] *= (1 + weight * 0.2)
        return predictions
    
    def update_user_preferences(self, user_id: str, selected_word: str):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}
        if selected_word not in self.user_preferences[user_id]:
            self.user_preferences[user_id][selected_word] = {"count": 0}
        self.user_preferences[user_id][selected_word]["count"] += 1