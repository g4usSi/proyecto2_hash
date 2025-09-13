import os
from core.tabla_hash import HashTable
from core.articulos import articulo
from core.hash_utils import HashUtils

class Main:
    def __init__(self):
        self.tabla = HashTable()
        self.ejecutar_menu()

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

        art = matches[0]
        if art.hash is None:
            print("Artículo no tiene hash asignado; no se puede eliminar vía hash.")
            return
        if self.tabla.eliminar(art.hash):
            print(f"Artículo '{art.titulo}' eliminado.")
        else:
            print("Error al eliminar el artículo.")

    def listar_articulos(self):
        articulos = self.tabla.listar_todos()
        if not articulos:
            print("No hay artículos en la tabla.")
        else:
            print("\n=== LISTA DE ARTÍCULOS ===")
            for art in articulos:
                print(f"Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")


if __name__ == "__main__":
    Main()
