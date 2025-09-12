from core.hash_utils import HashUtils

class Nodo:
    def __init__(self, key, articulo):
        self.key = key
        self.articulo = articulo
        self.siguiente = None

class HashTable:
    def __init__(self, size=1024):
        self.size = size
        self.buckets = [None] * self.size

    def _hash(self, key):
        return int(key) % self.size

    def insertar(self, key, articulo):
        index = self._hash(key)
        nodo = self.buckets[index]
        # Verificar duplicado
        while nodo:
            if nodo.key == key:
                return False  # ya existe
            nodo = nodo.siguiente
        # Insertar al inicio
        nuevo_nodo = Nodo(key, articulo)
        nuevo_nodo.siguiente = self.buckets[index]
        self.buckets[index] = nuevo_nodo
        return True

    def buscar(self, key):
        index = self._hash(key)
        nodo = self.buckets[index]
        while nodo:
            if nodo.key == key:
                return nodo.articulo
            nodo = nodo.siguiente
        return None

    def eliminar(self, key):
        index = self._hash(key)
        nodo = self.buckets[index]
        prev = None
        while nodo:
            if nodo.key == key:
                if prev:
                    prev.siguiente = nodo.siguiente
                else:
                    self.buckets[index] = nodo.siguiente
                return True
            prev = nodo
            nodo = nodo.siguiente
        return False

    def listar_todos(self):
        """Devuelve una lista con todos los articulos en la tabla hash."""
        lista = []
        for nodo in self.buckets:
            actual = nodo
            while actual:
                lista.append(actual.articulo)
                actual = actual.siguiente
        return lista
