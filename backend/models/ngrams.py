from collections import Counter, defaultdict
from typing import Dict, List, Tuple
import logging

logger = logging.getLogger(__name__)

START_TOKEN = "<START>"
END_TOKEN = "<END>"


class NGramModel:
    """
    Modelo de n-gramas con backoff para aprovechar mejor el contexto.
    """

    def __init__(self, n: int = 3):
        self.n = n
        self.ngrams: Dict[int, defaultdict] = {
            order: defaultdict(Counter) for order in range(1, n)
        }
        self.vocab = set()
        self.unigram_counts = Counter()

    def train(self, sequences: List[List[str]]):
        """
        Entrena el modelo con una lista de secuencias de tokens.
        """
        for tokens in sequences:
            if not tokens:
                continue

            padded = [START_TOKEN] * (self.n - 1) + tokens + [END_TOKEN]
            self.vocab.update(tokens)
            self.unigram_counts.update(tokens)

            for order in range(1, self.n):
                for index in range(len(padded) - order):
                    context = tuple(padded[index:index + order])
                    next_word = padded[index + order]
                    self.ngrams[order][context][next_word] += 1

        logger.info(
            "NGramModel entrenado: %s contextos y %s tokens de vocabulario",
            sum(len(model) for model in self.ngrams.values()),
            len(self.vocab),
        )

    def predict_next(self, context: List[str], k: int = 5) -> List[Tuple[str, float]]:
        """
        Predice las siguientes palabras más probables usando backoff.
        """
        if not self.unigram_counts:
            return []

        scores = Counter()
        max_order = min(self.n - 1, len(context))

        for order in range(max_order, 0, -1):
            context_tuple = tuple(context[-order:])
            if context_tuple not in self.ngrams[order]:
                continue

            next_words = self.ngrams[order][context_tuple]
            total_count = sum(next_words.values())
            distance = max_order - order
            weight = 1.0 if distance == 0 else 0.18 / distance

            for word, count in next_words.items():
                if word == END_TOKEN:
                    continue
                scores[word] += weight * (count / total_count)

        if not scores:
            return self._get_frequent_words(k)

        if len(scores) < k:
            for word, prob in self._get_frequent_words(k * 2):
                scores[word] += prob * 0.04

        return self._normalize_scores(scores, k)

    def _get_frequent_words(self, k: int = 5) -> List[Tuple[str, float]]:
        total = sum(self.unigram_counts.values())
        if total == 0:
            return []

        return [
            (word, count / total)
            for word, count in self.unigram_counts.most_common(k)
        ]

    def _normalize_scores(self, scores: Counter, k: int) -> List[Tuple[str, float]]:
        total_score = sum(scores.values())
        if total_score <= 0:
            return []

        return [
            (word, score / total_score)
            for word, score in scores.most_common(k)
        ]
