import os, json
from core.articulos import articulo

class Storage:
    File = "articulos_db.txt"

    @staticmethod
    def cargar():
        articulos = []
        if not os.path.exists(Storage.File):
            return articulos
        with open(Storage.File, "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    data = json.loads(linea)
                    art = articulo.from_dict(data)
                    articulos.append(art)
                except Exception as e:
                    print(f"Error al cargar linea de la base de datos: {e}")
        return articulos

    @staticmethod
    def guardar_articulo(art):
        with open(Storage.File, "a", encoding="utf-8") as f:
            f.write(json.dumps(art.to_dict()) + "\n")

    # --- CRUD de archivos ---
    @staticmethod
    def crear_archivo(nombre_archivo, contenido_inicial=""):
        """Crea un nuevo archivo con contenido inicial"""
        if os.path.exists(nombre_archivo):
            raise FileExistsError(f"El archivo '{nombre_archivo}' ya existe")
        
        # Crear directorios padre si no existen
        directorio = os.path.dirname(nombre_archivo)
        if directorio and not os.path.exists(directorio):
            os.makedirs(directorio)
        
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(contenido_inicial)
        
        return True

    @staticmethod
    def leer_archivo(nombre_archivo):
        if not os.path.exists(nombre_archivo):
            raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")
        with open(nombre_archivo, "r", encoding="utf-8") as f:
            return f.read()

    @staticmethod
    def actualizar_archivo(nombre_archivo, nuevo_contenido):
        if not os.path.exists(nombre_archivo):
            raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")
        with open(nombre_archivo, "w", encoding="utf-8") as f:
            f.write(nuevo_contenido)

    @staticmethod
    def eliminar_archivo(nombre_archivo):
        if os.path.exists(nombre_archivo):
            os.remove(nombre_archivo)
        else:
            raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")

    @staticmethod
    def archivo_existe(nombre_archivo):
        """Verifica si un archivo existe"""
        return os.path.exists(nombre_archivo)

    @staticmethod
    def obtener_info_archivo(nombre_archivo):
        """Obtiene informacion del archivo (tamaño, fecha modificacion, etc.)"""
        if not os.path.exists(nombre_archivo):
            raise FileNotFoundError(f"El archivo '{nombre_archivo}' no existe")
        
        stats = os.stat(nombre_archivo)
        return {
            'tamaño': stats.st_size,
            'modificado': stats.st_mtime,
            'creado': stats.st_ctime,
            'ruta_completa': os.path.abspath(nombre_archivo)
        }