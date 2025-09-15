import os
import json
from core.tabla_hash import HashTable
from core.articulos import articulo
from core.hash_utils import HashUtils
from core.indices import IndiceAutor, IndiceTitulo
from core.storage import Storage


class Main:
    def __init__(self):
        self.tabla = HashTable()
        self.indice_autor = IndiceAutor()
        self.indice_titulo = IndiceTitulo()
        self.cargar_base_datos()
        self.ejecutar_menu()

    def cargar_base_datos(self):
        articulos = Storage.cargar()
        for art in articulos:
            self.tabla.insertar(art.hash, art)
            self.indice_autor.agregar(art)
            self.indice_titulo.agregar(art)

    def ejecutar_menu(self):
        while True:
            print("\n=== GESTIÓN DE ARTÍCULOS ===")
            print("1. Insertar artículo")
            print("2. Buscar artículo por título")
            print("3. Eliminar artículo por título")
            print("4. Listar todos los artículos")
            print("5. Ver archivo")
            print("6. Editar archivo")
            print("7. Eliminar archivo")
            print("8. Salir")

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
                    self.ver_archivo()
                case "6":
                    self.editar_archivo()
                case "7":
                    self.eliminar_archivo()
                case "8":
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

        if self.tabla.insertar(key, art):  # se inserta ya en la tabla
            print("Artículo insertado correctamente.")
            # Agregar a índices
            self.indice_autor.agregar(art)
            self.indice_titulo.agregar(art)
            Storage.guardar(art)
        else:
            print("El artículo ya existe en la tabla.")

    def buscar_articulo(self):
        print("Búsqueda de artículos")
        tipo = input("Buscar por (1) Título o (2) Autor: ").strip()
        consulta = input("Ingrese el texto de búsqueda: ").strip().lower()

        if tipo == "1":
            matches = self.indice_titulo.buscar(consulta)
        elif tipo == "2":
            matches = self.indice_autor.buscar(consulta)
        else:
            print("Opción inválida. Mostrando todos los artículos.")
            matches = self.tabla.listar_todos()

        if not matches:
            print("No se encontraron artículos.")
            return

        print(f"{len(matches)} artículo(s) encontrado(s):")
        for art in matches:
            print(
                f"Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")

    def eliminar_articulo(self):
        consulta = input("Ingrese el título (o parte del título) del artículo a eliminar: ").strip().lower()
        matches = self.indice_titulo.buscar(consulta)

        if not matches:
            print("No se encontraron artículos con ese título.")
            return

        if len(matches) > 1:
            print("Se encontraron múltiples artículos")
            for i, art in enumerate(matches):
                print(
                    f"{i + 1}. Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")
            seleccion = int(input("Ingrese el número del artículo a eliminar: ").strip())
            art = matches[seleccion - 1]
        else:
            art = matches[0]

        if art.hash is None:
            print("Artículo no exitente")
            return

        # Quitar del índice por autor
        if self.tabla.eliminar(art.hash):
            print(f"Atículo '{art.titulo}' eliminado.")
            self.indice_autor.eliminar(art)
            self.indice_titulo.eliminar(art)

            arts_restantes = self.tabla.listar_todos()
            with open("articulos_db.txt", "w", encoding="utf-8") as f:
                for a in arts_restantes:
                    f.write(json.dumps(a.to_dict()) + "\n")
        else:
            print("Error al eliminar el artículo.")

    def listar_articulos(self):
        articulos = self.tabla.listar_todos()
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
            print(
                f"{i}. Hash: {art.hash} | Título: {art.titulo} | Autor(es): {art.autor} | Año: {art.anio} | Archivo: {art.archivo}")

    # --- CRUD de archivos ---
    def ver_archivo(self):
        archivo = input("Nombre del archivo a ver: ").strip()
        try:
            contenido = Storage.leer_archivo(archivo)
            print("\n--- Contenido ---")
            print(contenido)
        except Exception as e:
            print(f"Error: {e}")

    def editar_archivo(self):
        archivo = input("Nombre del archivo a editar: ").strip()
        try:
            contenido = Storage.leer_archivo(archivo)
            print("\n--- Contenido actual ---")
            print(contenido)
            nuevo = input("\nNuevo contenido:\n")
            Storage.actualizar_archivo(archivo, nuevo)
            print("Archivo actualizado.")
        except Exception as e:
            print(f"Error: {e}")

    def eliminar_archivo(self):
        archivo = input("Nombre del archivo a eliminar: ").strip()
        try:
            Storage.eliminar_archivo(archivo)
            print("Archivo eliminado.")
        except Exception as e:
            print(f"Error: {e}")


if __name__ == "__main__":
    Main()
