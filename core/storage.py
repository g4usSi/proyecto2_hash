import os, json
from core.articulos import articulo

class Storage:
    File = "articulos_db.txt"

    @staticmethod
    def cargar():
        articulos = []
        if not os.path.exists(Storage.File):
            return articulos
        with open (Storage.File, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    data = json.loads(linea)
                    art = articulo.from_dict(data)
                    articulos.append(art)
                except Exception as e:
                    print(f"Error al cargar línea de la base de datos: {e}")
        return articulos
    
    @staticmethod
    def guardar(art):
        with open(Storage.File, "a", encoding="utf-8") as f:
            f.write(json.dumps(art.to_dict()) + "\n")