from collections import Counter, defaultdict
from typing import Dict, List
import logging

from .ngrams import NGramModel
from .lstm_model import LSTMModel
from .trie import TrieNode
from utils.tokenizer import SpanishTokenizer

logger = logging.getLogger(__name__)


class TextPredictor:
    """
    Orquestador híbrido que combina:
    1. Autocompletado por Trie
    2. Siguiente palabra por n-gramas
    3. Re-ranking por LSTM y preferencias del usuario
    """

    def __init__(self, corpus: List[str], vocab_size: int = 1000):
        self.corpus = corpus
        self.vocab_size = vocab_size
        self.tokenizer = SpanishTokenizer()
        self.surface_forms: Dict[str, str] = {}
        self.token_frequencies = Counter()
        self.max_token_frequency = 1
        self.user_preferences = {}
        self.expression_boosts = {
            ("sin",): {"embargo": 0.34},
            ("por", "lo"): {"tanto": 0.42},
            ("tal",): {"vez": 0.28},
            ("en",): {"cambio": 0.16, "conclusion": 0.14},
            ("por",): {"eso": 0.18},
        }

        token_sequences = self._prepare_sequences(corpus)

        self.ngram_model = NGramModel(n=4)
        self.ngram_model.train(token_sequences)

        self.lstm_model = LSTMModel(vocab_size=vocab_size, sequence_length=5)
        self.lstm_model.train(token_sequences)

        self.trie = TrieNode()
        self._build_trie()

        logger.info(
            "TextPredictor inicializado con %s oraciones y %s tokens únicos",
            len(corpus),
            len(self.token_frequencies),
        )

    def _prepare_sequences(self, corpus: List[str]) -> List[List[str]]:
        sequences = []
        display_counts = defaultdict(Counter)

        for sentence in corpus:
            raw_tokens = self.tokenizer.tokenize(sentence, normalize=False)
            normalized_tokens = self.tokenizer.tokenize(sentence, normalize=True)

            if not normalized_tokens:
                continue

            sequences.append(normalized_tokens)
            self.token_frequencies.update(normalized_tokens)

            for raw_token, normalized_token in zip(raw_tokens, normalized_tokens):
                display_counts[normalized_token][raw_token] += 1

        self.surface_forms = {
            token: counts.most_common(1)[0][0]
            for token, counts in display_counts.items()
        }
        if self.token_frequencies:
            self.max_token_frequency = max(self.token_frequencies.values())

        return sequences

    def _build_trie(self):
        for token, frequency in self.token_frequencies.items():
            self.trie.insert(token, weight=frequency)

    def predict(self, text: str, max_suggestions: int = 5, user_adapter=None) -> List[Dict]:
        input_state = self.tokenizer.analyze_input(text)
        context_tokens = input_state["context_tokens"]
        current_fragment = input_state["current_fragment"]
        is_autocomplete = input_state["is_autocomplete"]

        if not context_tokens and not current_fragment:
            return []

        predictions: Dict[str, Dict] = {}

        if is_autocomplete:
            self._collect_expression_predictions(
                predictions,
                context_tokens,
                current_fragment=current_fragment,
            )
            self._collect_autocomplete_predictions(
                predictions,
                current_fragment,
                context_tokens,
                max_suggestions,
            )
        else:
            self._collect_expression_predictions(predictions, context_tokens)
            self._collect_next_word_predictions(
                predictions,
                context_tokens,
                max_suggestions,
            )

        if user_adapter:
            predictions = self._apply_user_preferences(
                predictions,
                user_adapter,
                context_tokens,
            )

        sorted_predictions = sorted(
            predictions.values(),
            key=lambda item: item["confidence"],
            reverse=True,
        )[:max_suggestions]

        return [
            {
                "word": item["word"],
                "confidence": round(min(item["confidence"], 0.99), 4),
                "source": item["source"],
            }
            for item in sorted_predictions
        ]

    def _collect_autocomplete_predictions(
        self,
        predictions: Dict[str, Dict],
        prefix: str,
        context_tokens: List[str],
        max_suggestions: int,
    ):
        trie_candidates = self.trie.search_prefix(prefix, max_results=max_suggestions * 4)

        for token, frequency in trie_candidates:
            if token == prefix:
                continue
            frequency_score = frequency / max(self.max_token_frequency, 1)
            base_score = 0.5 + min(frequency_score, 1.0) * 0.15
            self._upsert_prediction(predictions, token, base_score, "trie")

        for token, probability in self.ngram_model.predict_next(context_tokens, k=max_suggestions * 5):
            if token.startswith(prefix):
                self._upsert_prediction(predictions, token, probability * 0.35, "ngram")

        for token, probability in self.lstm_model.predict_next(context_tokens, k=max_suggestions * 5):
            if token.startswith(prefix):
                self._upsert_prediction(predictions, token, probability * 0.2, "lstm")

    def _collect_expression_predictions(
        self,
        predictions: Dict[str, Dict],
        context_tokens: List[str],
        current_fragment: str = "",
    ):
        for context_pattern, candidates in self.expression_boosts.items():
            if len(context_tokens) < len(context_pattern):
                continue

            if tuple(context_tokens[-len(context_pattern):]) != context_pattern:
                continue

            for token, score in candidates.items():
                if current_fragment and not token.startswith(current_fragment):
                    continue
                self._upsert_prediction(predictions, token, score, "expression")

    def _collect_next_word_predictions(
        self,
        predictions: Dict[str, Dict],
        context_tokens: List[str],
        max_suggestions: int,
    ):
        for token, probability in self.ngram_model.predict_next(context_tokens, k=max_suggestions * 4):
            self._upsert_prediction(predictions, token, probability * 0.65, "ngram")

        for token, probability in self.lstm_model.predict_next(context_tokens, k=max_suggestions * 4):
            self._upsert_prediction(predictions, token, probability * 0.35, "lstm")

    def _upsert_prediction(
        self,
        predictions: Dict[str, Dict],
        token: str,
        score: float,
        source: str,
    ):
        if not token:
            return

        display_word = self.surface_forms.get(token, token)
        item = predictions.get(token)

        if item is None:
            predictions[token] = {
                "token": token,
                "word": display_word,
                "confidence": float(score),
                "source": source,
                "sources": {source},
            }
            return

        item["confidence"] += float(score)
        item["sources"].add(source)
        if "ngram" in item["sources"]:
            item["source"] = "ngram"
        elif "lstm" in item["sources"]:
            item["source"] = "lstm"
        elif "expression" in item["sources"]:
            item["source"] = "expression"
        else:
            item["source"] = "trie"

    def _apply_user_preferences(
        self,
        predictions: Dict[str, Dict],
        user_adapter,
        context_tokens: List[str],
    ) -> Dict[str, Dict]:
        user_prefs = user_adapter.get_preferences()
        context_prefs = user_adapter.get_context_preferences(context_tokens)

        for token, prediction in predictions.items():
            if token not in user_prefs:
                base_boost = 1.0
            else:
                frequency = user_prefs[token]["frequency"]
                base_boost = 1 + min(frequency, 5) * 0.08

            context_boost = 1.0
            if token in context_prefs:
                context_frequency = context_prefs[token]
                context_boost += min(context_frequency, 4) * 0.14

            prediction["confidence"] *= base_boost * context_boost

        return predictions

    def update_user_preferences(self, user_id: str, selected_word: str):
        if user_id not in self.user_preferences:
            self.user_preferences[user_id] = {}

        normalized_tokens = self.tokenizer.tokenize(selected_word)
        if not normalized_tokens:
            return

        token = normalized_tokens[0]
        if token not in self.user_preferences[user_id]:
            self.user_preferences[user_id][token] = {"count": 0}

        self.user_preferences[user_id][token]["count"] += 1
