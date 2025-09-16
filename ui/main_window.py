import sys
import os

# Agregar la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
#import temporalmente el path para desarrollo local solo para pruebas de UI

import sys
from PyQt5 import QtWidgets
from core import HashTable, IndiceAutor, IndiceTitulo, Storage, articulo, HashUtils

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Artículos Científicos")
        self.setGeometry(100, 100, 1000, 600)

        # --- Tabla hash e índices ---
        self.tabla = HashTable()
        self.indice_autor = IndiceAutor()
        self.indice_titulo = IndiceTitulo()
        self.cargar_base_datos()

        # --- Layout principal ---
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # --- Barra lateral izquierda ---
        sidebar = QtWidgets.QVBoxLayout()
        btn_nuevo = QtWidgets.QPushButton("Nuevo Artículo")
        btn_nuevo.clicked.connect(self.nuevo_articulo)
        sidebar.addWidget(btn_nuevo)
        sidebar.addStretch()

        # --- Contenido principal ---
        content_layout = QtWidgets.QVBoxLayout()

        # Formulario búsqueda
        form_layout = QtWidgets.QFormLayout()
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_autor = QtWidgets.QLineEdit()
        self.input_anio = QtWidgets.QLineEdit()
        btn_aplicar_busqueda = QtWidgets.QPushButton("Aplicar Búsqueda")
        btn_aplicar_busqueda.clicked.connect(self.aplicar_busqueda)

        form_layout.addRow("Título:", self.input_titulo)
        form_layout.addRow("Autor(es):", self.input_autor)
        form_layout.addRow("Año de Publicación:", self.input_anio)
        form_layout.addRow(btn_aplicar_busqueda)

        # Resultados
        self.resultados_layout = QtWidgets.QVBoxLayout()
        resultados_label = QtWidgets.QLabel("Resultados de la búsqueda:")
        self.resultados_layout.addWidget(resultados_label)

        # Scroll con coincidencias
        self.scroll_area = QtWidgets.QScrollArea()
        self.scroll_area.setWidgetResizable(True)
        self.resultados_widget = QtWidgets.QWidget()
        self.resultados_scroll_layout = QtWidgets.QVBoxLayout(self.resultados_widget)
        self.scroll_area.setWidget(self.resultados_widget)
        self.resultados_layout.addWidget(self.scroll_area)

        # Agregar formulario y resultados al contenido principal
        content_layout.addLayout(form_layout)
        content_layout.addLayout(self.resultados_layout)

        # Agregar sidebar y contenido al layout principal
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 4)

        # Mostrar todos al inicio
        self.mostrar_resultados(self.tabla.listar_todos())

    def cargar_base_datos(self):
        articulos = Storage.cargar()
        for art in articulos:
            self.tabla.insertar(art.hash, art)
            self.indice_autor.agregar(art)
            self.indice_titulo.agregar(art)

    def aplicar_busqueda(self):
        titulo = self.input_titulo.text().strip().lower()
        autor = self.input_autor.text().strip().lower()

        if titulo:
            matches = self.indice_titulo.buscar(titulo)
        elif autor:
            matches = self.indice_autor.buscar(autor)
        else:
            matches = self.tabla.listar_todos()

        self.mostrar_resultados(matches)

    def mostrar_resultados(self, articulos):
        for i in reversed(range(self.resultados_scroll_layout.count())):
            widget = self.resultados_scroll_layout.itemAt(i).widget()
            if widget:
                widget.setParent(None)

        for art in articulos:
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)

            lbl = QtWidgets.QLabel(f"{art.titulo} - {art.autor} ({art.anio})")
            btn_modificar = QtWidgets.QPushButton("Editar archivo")
            btn_eliminar = QtWidgets.QPushButton("Eliminar archivo")
            btn_ver = QtWidgets.QPushButton("Ver archivo")

            btn_modificar.clicked.connect(lambda _, a=art: self.editar_archivo(a))
            btn_eliminar.clicked.connect(lambda _, a=art: self.eliminar_archivo(a))
            btn_ver.clicked.connect(lambda _, a=art: self.ver_archivo(a))

            item_layout.addWidget(lbl)
            item_layout.addStretch()
            item_layout.addWidget(btn_modificar)
            item_layout.addWidget(btn_eliminar)
            item_layout.addWidget(btn_ver)

            self.resultados_scroll_layout.addWidget(item_widget)

        self.resultados_scroll_layout.addStretch()

    def nuevo_articulo(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Nuevo Artículo")
        layout = QtWidgets.QFormLayout(dialog)

        input_titulo = QtWidgets.QLineEdit()
        input_autor = QtWidgets.QLineEdit()
        input_anio = QtWidgets.QLineEdit()
        input_archivo = QtWidgets.QLineEdit()

        layout.addRow("Título:", input_titulo)
        layout.addRow("Autor(es):", input_autor)
        layout.addRow("Año:", input_anio)
        layout.addRow("Archivo:", input_archivo)

        btn_guardar = QtWidgets.QPushButton("Guardar")
        layout.addRow(btn_guardar)

        def guardar():
            titulo = input_titulo.text().strip()
            autor = input_autor.text().strip()
            anio = input_anio.text().strip()
            archivo = input_archivo.text().strip()

            if not (titulo and autor and anio and archivo):
                QtWidgets.QMessageBox.warning(dialog, "Error", "Todos los campos son obligatorios.")
                return

            art = articulo(titulo, autor, anio, archivo)
            art.hash = HashUtils.hash_text(titulo + autor + str(anio))

            if self.tabla.insertar(art.hash, art):
                self.indice_autor.agregar(art)
                self.indice_titulo.agregar(art)
                Storage.guardar_articulo(art)
                self.mostrar_resultados(self.tabla.listar_todos())
                dialog.accept()
            else:
                QtWidgets.QMessageBox.warning(dialog, "Error", "El artículo ya existe.")

        btn_guardar.clicked.connect(guardar)
        dialog.exec_()

    # --- CRUD de archivos en UI ---
    def ver_archivo(self, art):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(f"Ver: {art.titulo}")
        layout = QtWidgets.QVBoxLayout(dlg)
        txt = QtWidgets.QTextEdit()
        txt.setReadOnly(True)
        try:
            txt.setText(Storage.leer_archivo(art.archivo))
        except Exception as e:
            txt.setText(f"Error: {e}")
        layout.addWidget(txt)
        dlg.exec_()

    def editar_archivo(self, art):
        dlg = QtWidgets.QDialog(self)
        dlg.setWindowTitle(f"Editar: {art.titulo}")
        layout = QtWidgets.QVBoxLayout(dlg)
        txt = QtWidgets.QTextEdit()
        try:
            txt.setText(Storage.leer_archivo(art.archivo))
        except Exception as e:
            txt.setText(f"Error: {e}")
        layout.addWidget(txt)
        btn_guardar = QtWidgets.QPushButton("Guardar cambios")
        layout.addWidget(btn_guardar)

        def guardar():
            try:
                Storage.actualizar_archivo(art.archivo, txt.toPlainText())
                dlg.accept()
            except Exception as e:
                QtWidgets.QMessageBox.warning(dlg, "Error", str(e))

        btn_guardar.clicked.connect(guardar)
        dlg.exec_()

    def eliminar_archivo(self, art):
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirmar", f"¿Eliminar el archivo '{art.archivo}'?",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        if confirm == QtWidgets.QMessageBox.Yes:
            try:
                Storage.eliminar_archivo(art.archivo)
                self.tabla.eliminar(art.hash)
                self.indice_autor.eliminar(art)
                self.indice_titulo.eliminar(art)
                self.mostrar_resultados(self.tabla.listar_todos())
                QtWidgets.QMessageBox.information(self, "Éxito", "Archivo eliminado.")
            except Exception as e:
                QtWidgets.QMessageBox.warning(self, "Error", str(e))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())
