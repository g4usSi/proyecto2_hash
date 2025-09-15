# core/__init__.py
"""
Paquete core: contiene la lógica central del gestor de artículos.
Se exponen las clases principales para importar directamente desde core.
"""

from .tabla_hash import HashTable
from .articulos import articulo
from .hash_utils import HashUtils
from .indices import IndiceAutor, IndiceTitulo
from .storage import Storage

__all__ = [
    "HashTable",
    "articulo",
    "HashUtils",
    "IndiceAutor",
    "IndiceTitulo",
    "Storage",
]
