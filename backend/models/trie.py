from typing import List, Tuple


class TrieNode:
    """
    Estructura Trie para autocompletado rápido con ranking por frecuencia.
    """

    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = ""
        self.frequency = 0

    def insert(self, word: str, weight: int = 1):
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word
        node.frequency += weight

    def search_prefix(self, prefix: str, max_results: int = 10) -> List[Tuple[str, int]]:
        node = self

        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]

        results = []
        self._dfs(node, results, max_results * 3)
        results.sort(key=lambda item: (-item[1], item[0]))
        return results[:max_results]

    def _dfs(self, node: "TrieNode", results: List[Tuple[str, int]], max_results: int):
        if len(results) >= max_results:
            return

        if node.is_end:
            results.append((node.word, node.frequency))

        for char in sorted(node.children.keys()):
            self._dfs(node.children[char], results, max_results)
