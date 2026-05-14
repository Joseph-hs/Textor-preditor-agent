from typing import Dict, List
from datetime import datetime
import logging

logger = logging.getLogger(__name__)

class UserAdapter:
    def __init__(self, user_id: str):
        self.user_id = user_id
        self.word_frequency = {}
        self.selection_history = []
        self.total_predictions = 0
        self.correct_selections = 0
        self.last_update = datetime.now().isoformat()
    
    def register_selection(self, context: str, selected_word: str):
        if selected_word not in self.word_frequency:
            self.word_frequency[selected_word] = 0
        self.word_frequency[selected_word] += 1
        self.selection_history.append({"context": context, "selected": selected_word, "timestamp": datetime.now().isoformat()})
        self.correct_selections += 1
        self.last_update = datetime.now().isoformat()
        logger.info(f"Seleccion registrada para {self.user_id}: '{selected_word}'")
    
    def get_preferences(self) -> Dict[str, Dict]:
        return {word: {"frequency": freq} for word, freq in self.word_frequency.items()}
    
    def get_statistics(self) -> Dict:
        accuracy = (self.correct_selections / max(self.total_predictions, 1)) if self.total_predictions > 0 else 0
        return {"words_learned": len(self.word_frequency), "total_predictions": self.total_predictions, "correct_selections": self.correct_selections, "accuracy": accuracy, "last_update": self.last_update}
    
    def increment_prediction_count(self):
        self.total_predictions += 1