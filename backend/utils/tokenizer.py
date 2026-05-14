import re
from typing import List

class SpanishTokenizer:
    def __init__(self):
        self.contractions = {"al": "a el", "del": "de el"}
    
    def tokenize(self, text: str) -> List[str]:
        text = text.lower()
        for contraction, expansion in self.contractions.items():
            text = re.sub(r'\b' + contraction + r'\b', expansion, text)
        tokens = re.findall(r'\b\w+\b', text)
        return [t for t in tokens if len(t) > 0]
    
    def detokenize(self, tokens: List[str]) -> str:
        return " ".join(tokens)