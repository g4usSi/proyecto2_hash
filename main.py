import os
import json
from core.tabla_hash import HashTable
from core.articulos import articulo
from core.hash_utils import HashUtils

class Main:
    def __init__(self):
        self.tabla = HashTable()
        self.indice_autor = {}
        self.cargar_base_datos()
        self.ejecutar_menu()

    def cargar_base_datos(self):
        if not os.path.exists("articulos_db.txt"):
            return 
        with open("articulos_db.txt", "r", encoding="utf-8") as f:
            for linea in f:
                linea = linea.strip()
                if not linea:
                    continue
                try:
                    data = json.loads(linea)
                    art = articulo.from_dict(data)
                    self.tabla.insertar(art.hash, art)
                    if art.autor in self.indice_autor:
                        self.indice_autor[art.autor].append(art)
                    else:
                        self.indice_autor[art.autor] = [art]
                except Exception as e:
                    print(f"⚠️ Error al cargar línea de la base de datos: {e}")

    def ejecutar_menu(self):
        while True:
            print("\n=== GESTIÓN DE ARTÍCULOS ===")
            print("1. Insertar artículo")
            print("2. Buscar artículo por título")
            print("3. Eliminar artículo por título")
            print("4. Listar todos los artículos")
            print("5. Salir")

            opcion = input("Seleccione una opción: ")

            match opcion:
                case "1":
                    self.insertar_articulo()
                case "2":
                    self.buscar_articulo()
                case "3":
                    self.eliminar_articulo()
                case "4":
                    self.listar_articulos()
                case "5":
                    print("Saliendo del programa...")
                    break
                case _:
                    print("Opción inválida. Intente de nuevo.")

    def insertar_articulo(self):
        titulo = input("Título: ").strip()
        autor = input("Autor(es): ").strip()
        anio = input("Año: ").strip()
        archivo = input("Nombre del archivo (ejemplo: articulo.txt): ").strip()

        art = articulo(titulo, autor, anio, archivo)

        if archivo and os.path.exists(archivo):
            try:
                key = HashUtils.hash_file(archivo, use_fnv=True)
                print("Hash calculado desde archivo.")
            except Exception as e:
                print(f"No se pudo leer el archivo ({e}). Se usará metadata para hashear.")
                key = HashUtils.hash_text(titulo + autor + str(anio))
        else:
            key = HashUtils.hash_text(titulo + autor + str(anio))

        art.hash = key
        if self.tabla.insertar(key, art):
            print("Artículo insertado correctamente.")
                    # Índice por autor
            if art.autor in self.indice_autor:
                self.indice_autor[art.autor].append(art)
            else:
                self.indice_autor[art.autor] = [art]
            with open("articulos_db.txt", "a", encoding="utf-8") as f:
                f.write(json.dumps(art.to_dict()) + "\n")
        else:
            print("El artículo ya existe en la tabla.")

    def buscar_articulo(self):
        consulta = input("Ingrese el título (o parte del título) a buscar: ").strip().lower()
        todos = self.tabla.listar_todos()
        matches = [art for art in todos if consulta in (art.titulo or "").lower()]

        if not matches:
            print("No se encontraron artículos con ese título.")
            return

        print(f"{len(matches)} artículo(s) encontrado(s):")
        for art in matches:
            print(f"Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")

    def eliminar_articulo(self):
        consulta = input("Ingrese el título (o parte del título) del artículo a eliminar: ").strip().lower()
        todos = self.tabla.listar_todos()
        matches = [art for art in todos if consulta in (art.titulo or "").lower()]

        if not matches:
            print("No se encontraron artículos con ese título.")
            return
        
        if len(matches) > 1:
            print("Se encontraron múltiples artículos")
            for i, art in enumerate(matches):
                print(f"{i + 1}. Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")
            seleccion = input("Ingrese el número del artículo a eliminar: ").strip()
            art = matches[int(seleccion) - 1]
        else:
            art = matches[0]

        if art.hash is None:
            print("Artículo no exitente")
            return
        
        if self.tabla.eliminar(art.hash):
            print(f"Artículo '{art.titulo}' eliminado.")
        # Quitar del índice por autor
        if art.autor in self.indice_autor:
            self.indice_autor[art.autor] = [a for a in self.indice_autor[art.autor] if a.hash != art.hash]
            if not self.indice_autor[art.autor]:
                del self.indice_autor[art.autor]

            try:
                with open("articulos_db.txt", r, encoding="utf-8") as f:
                    lineas = f.readlines()
                
                with open("articulos_db.txt", "w", encoding="utf-8") as f:
                    for linea in lineas:
                        data = json.loads(linea.strip())
                        if data.get("hash") != art.hash:
                            f.write(json.dumps(data) + "\n")
            except FileNotFoundError:
                print("Archivo no encontrado. No se pudo actualizar.")
            except Exception as e:
                print(f"Error al actualizar la base de datos: {e}")

        else:
            print("Error al eliminar el artículo.")

    def listar_articulos(self, articulos):
        print("Seleccione cómo listar los artículos:")
        print("1. Por título (alfabéticamente)")
        print("2. Por autor (alfabéticamente)")

        opcion = input("Opción: ").strip()
        match opcion:
            case "1":
                articulos.sort(key=lambda x: x.titulo.lower() if x.titulo else "")
            case "2":
                articulos.sort(key=lambda x: x.autor.lower() if x.autor else "")
            case _:
                print("Opción inválida. Listando por título por defecto.")
                articulos.sort(key=lambda x: x.titulo if x.titulo else "")

        for i, art in enumerate(articulos, 1):
            print(f"{i}. Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")

if __name__ == "__main__":
    Main()
