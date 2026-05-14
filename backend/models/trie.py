from typing import List

class TrieNode:
    """
    Estructura Trie (árbol de prefijos) para autocompletado rápido.
    Búsqueda en O(m) donde m es la longitud del prefijo.
    """
    
    def __init__(self):
        self.children = {}
        self.is_end = False
        self.word = ""
    
    def insert(self, word: str):
        """
        Inserta una palabra en el Trie.
        
        Args:
            word: Palabra a insertar
        """
        node = self
        for char in word:
            if char not in node.children:
                node.children[char] = TrieNode()
            node = node.children[char]
        node.is_end = True
        node.word = word
    
    def search_prefix(self, prefix: str, max_results: int = 10) -> List[str]:
        """
        Busca todas las palabras que comienzan con el prefijo dado.
        
        Args:
            prefix: Prefijo a buscar
            max_results: Número máximo de resultados
        
        Returns:
            Lista de palabras que coinciden
        """
        node = self
        
        # Navegar hasta el prefijo
        for char in prefix:
            if char not in node.children:
                return []
            node = node.children[char]
        
        # Obtener todas las palabras con este prefijo
        results = []
        self._dfs(node, results, max_results)
        return results
    
    def _dfs(self, node: 'TrieNode', results: List[str], max_results: int):
        """
        Búsqueda en profundidad para encontrar todas las palabras.
        """
        if len(results) >= max_results:
            return
        
        if node.is_end:
            results.append(node.word)
        
        for child in node.children.values():
            self._dfs(child, results, max_results)