from collections import Counter, defaultdict
from datetime import datetime
from pathlib import Path
from typing import Dict, List
import json
import logging
import re

from .preprocessing import normalize_token
from .tokenizer import SpanishTokenizer

logger = logging.getLogger(__name__)

DATA_DIR = Path(__file__).resolve().parent.parent / "data" / "user_profiles"


class UserAdapter:
    """
    Adapta las predicciones según el estilo de escritura del usuario.
    Guarda preferencias globales y por contexto para reforzar el aprendizaje.
    """

    def __init__(self, user_id: str):
        self.user_id = user_id
        self.tokenizer = SpanishTokenizer()
        self.word_frequency: Dict[str, int] = {}
        self.context_frequency: Dict[str, Dict[str, int]] = defaultdict(dict)
        self.selection_history: List[Dict] = []
        self.total_predictions = 0
        self.correct_selections = 0
        self.last_update = datetime.now().isoformat()
        self.profile_path = DATA_DIR / f"{self._safe_user_id(user_id)}.json"
        self._load()

    def _safe_user_id(self, user_id: str) -> str:
        safe = re.sub(r"[^a-zA-Z0-9_-]", "_", user_id)
        return safe or "default_user"

    def _load(self):
        if not self.profile_path.exists():
            return

        try:
            data = json.loads(self.profile_path.read_text(encoding="utf-8"))
        except (OSError, json.JSONDecodeError) as error:
            logger.warning("No pude cargar perfil de usuario %s: %s", self.user_id, error)
            return

        self.word_frequency = {
            str(token): int(count)
            for token, count in data.get("word_frequency", {}).items()
        }
        self.context_frequency = defaultdict(
            dict,
            {
                str(context): {
                    str(token): int(count)
                    for token, count in token_counts.items()
                }
                for context, token_counts in data.get("context_frequency", {}).items()
            },
        )
        self.selection_history = list(data.get("selection_history", []))[-200:]
        self.total_predictions = int(data.get("total_predictions", 0))
        self.correct_selections = int(data.get("correct_selections", 0))
        self.last_update = data.get("last_update", self.last_update)

    def _save(self):
        DATA_DIR.mkdir(parents=True, exist_ok=True)
        payload = {
            "user_id": self.user_id,
            "word_frequency": self.word_frequency,
            "context_frequency": dict(self.context_frequency),
            "selection_history": self.selection_history[-200:],
            "total_predictions": self.total_predictions,
            "correct_selections": self.correct_selections,
            "last_update": self.last_update,
        }
        self.profile_path.write_text(
            json.dumps(payload, ensure_ascii=False, indent=2),
            encoding="utf-8",
        )

    def register_selection(self, context: str, selected_word: str):
        normalized_word = normalize_token(selected_word)
        if not normalized_word:
            return

        self.word_frequency[normalized_word] = self.word_frequency.get(normalized_word, 0) + 1

        context_tokens = self.tokenizer.tokenize(context)
        for window_size in (1, 2):
            if len(context_tokens) < window_size:
                continue
            context_key = " ".join(context_tokens[-window_size:])
            context_bucket = self.context_frequency.setdefault(context_key, {})
            context_bucket[normalized_word] = context_bucket.get(normalized_word, 0) + 1

        self.selection_history.append({
            "context": context,
            "selected": selected_word,
            "normalized_selected": normalized_word,
            "timestamp": datetime.now().isoformat()
        })
        self.selection_history = self.selection_history[-200:]

        self.correct_selections += 1
        self.last_update = datetime.now().isoformat()
        self._save()

        logger.info(f"Selección registrada para {self.user_id}: '{selected_word}'")

    def get_preferences(self) -> Dict[str, Dict]:
        return {
            word: {"frequency": freq}
            for word, freq in self.word_frequency.items()
        }

    def get_context_preferences(self, context_tokens: List[str]) -> Dict[str, int]:
        scores = Counter()

        for window_size, weight in ((1, 1.0), (2, 1.35)):
            if len(context_tokens) < window_size:
                continue

            context_key = " ".join(context_tokens[-window_size:])
            for token, frequency in self.context_frequency.get(context_key, {}).items():
                scores[token] += int(frequency * weight)

        return dict(scores)

    def get_statistics(self) -> Dict:
        acceptance_rate = (
            self.correct_selections / max(self.total_predictions, 1)
        ) if self.total_predictions > 0 else 0

        return {
            "words_learned": len(self.word_frequency),
            "total_predictions": self.total_predictions,
            "correct_selections": self.correct_selections,
            "accuracy": min(acceptance_rate, 1.0),
            "last_update": self.last_update
        }

    def increment_prediction_count(self):
        self.total_predictions += 1
        self.last_update = datetime.now().isoformat()
        self._save()
