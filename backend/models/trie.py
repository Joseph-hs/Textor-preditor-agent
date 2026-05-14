from typing import List

class TrieNode:
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = ""
    
    def insert(self, word: str):
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word
    
    def search_prefix(self, prefix: str, max_results: int = 10) -> List[str]:
        node = self
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        results = []
        self._dfs(node, results, max_results)
        return results
    
    def _dfs(self, node, results: List[str], max_results: int):
        if len(results) >= max_results:
            return
        if node.is_end:
            results.append(node.word)
        for child in node.children.values():
            self._dfs(child, results, max_results)