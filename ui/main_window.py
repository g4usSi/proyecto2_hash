import sys
import os

# Agregar la raíz del proyecto al sys.path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

import sys
from PyQt5 import QtWidgets, QtCore, QtGui
from core import HashTable, IndiceAutor, IndiceTitulo, Storage, articulo, HashUtils

class EditorDialog(QtWidgets.QDialog):
    """Ventana modal dedicada para editar archivos"""
    
    def __init__(self, parent, articulo_obj, modo='editar'):
        super().__init__(parent)
        self.articulo = articulo_obj
        self.modo = modo
        self.contenido_original = ""
        self.setupUI()
        self.cargar_contenido()
    
    def setupUI(self):
        if self.modo == 'editar':
            self.setWindowTitle(f"Editando: {self.articulo.titulo}")
        else:
            self.setWindowTitle(f"Visualizando: {self.articulo.titulo}")
        
        # Hacer la ventana modal (bloquea la ventana principal)
        self.setModal(True)
        self.setMinimumSize(800, 600)
        
        # Layout principal
        layout = QtWidgets.QVBoxLayout(self)
        
        # Información del artículo
        info_layout = QtWidgets.QHBoxLayout()
        info_label = QtWidgets.QLabel(f"<b>Autor:</b> {self.articulo.autor} | <b>Año:</b> {self.articulo.anio}")
        info_layout.addWidget(info_label)
        info_layout.addStretch()
        
        # Contador de palabras/caracteres
        self.stats_label = QtWidgets.QLabel()
        info_layout.addWidget(self.stats_label)
        layout.addLayout(info_layout)
        
        # Editor de texto
        self.text_editor = QtWidgets.QTextEdit()
        self.text_editor.setFont(QtGui.QFont("Consolas", 11))  # Fuente monoespaciada
        
        if self.modo == 'ver':
            self.text_editor.setReadOnly(True)
            self.text_editor.setStyleSheet("background-color: #f5f5f5;")
        
        # Conectar señal para actualizar estadísticas
        self.text_editor.textChanged.connect(self.actualizar_estadisticas)
        
        layout.addWidget(self.text_editor)
        
        # Botones
        buttons_layout = QtWidgets.QHBoxLayout()
        
        if self.modo == 'editar':
            btn_guardar = QtWidgets.QPushButton("💾 Guardar")
            btn_guardar.clicked.connect(self.guardar_archivo)
            btn_guardar.setStyleSheet("""
                QPushButton {
                    background-color: #4CAF50;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #45a049;
                }
            """)
            
            btn_descartar = QtWidgets.QPushButton("❌ Descartar cambios")
            btn_descartar.clicked.connect(self.descartar_cambios)
            btn_descartar.setStyleSheet("""
                QPushButton {
                    background-color: #f44336;
                    color: white;
                    border: none;
                    padding: 8px 16px;
                    border-radius: 4px;
                }
                QPushButton:hover {
                    background-color: #da190b;
                }
            """)
            
            buttons_layout.addWidget(btn_guardar)
            buttons_layout.addWidget(btn_descartar)
        
        btn_cerrar = QtWidgets.QPushButton("🚪 Cerrar")
        btn_cerrar.clicked.connect(self.reject)
        btn_cerrar.setStyleSheet("""
            QPushButton {
                background-color: #6c757d;
                color: white;
                border: none;
                padding: 8px 16px;
                border-radius: 4px;
            }
            QPushButton:hover {
                background-color: #5a6268;
            }
        """)
        
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cerrar)
        
        layout.addLayout(buttons_layout)
    
    def cargar_contenido(self):
        try:
            contenido = Storage.leer_archivo(self.articulo.archivo)
            self.contenido_original = contenido
            self.text_editor.setPlainText(contenido)
            self.actualizar_estadisticas()
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo cargar el archivo: {str(e)}")
            self.text_editor.setPlainText(f"Error al cargar: {str(e)}")
    
    def actualizar_estadisticas(self):
        texto = self.text_editor.toPlainText()
        caracteres = len(texto)
        palabras = len(texto.split()) if texto.strip() else 0
        lineas = len(texto.split('\n'))
        
        self.stats_label.setText(f"📊 {palabras} palabras, {caracteres} caracteres, {lineas} líneas")
    
    def guardar_archivo(self):
        try:
            contenido_actual = self.text_editor.toPlainText()
            Storage.actualizar_archivo(self.articulo.archivo, contenido_actual)
            
            # Mostrar mensaje de éxito
            QtWidgets.QMessageBox.information(self, "Éxito", "Archivo guardado correctamente.")
            self.accept()  # Cierra el diálogo con resultado positivo
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo guardar: {str(e)}")
    
    def descartar_cambios(self):
        contenido_actual = self.text_editor.toPlainText()
        
        if contenido_actual != self.contenido_original:
            respuesta = QtWidgets.QMessageBox.question(
                self, 
                "Descartar cambios", 
                "¿Estás seguro de que quieres descartar todos los cambios?",
                QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
            )
            
            if respuesta == QtWidgets.QMessageBox.Yes:
                self.text_editor.setPlainText(self.contenido_original)
        
    def closeEvent(self, event):
        """Interceptar el cierre de la ventana para preguntar por cambios no guardados"""
        if self.modo == 'editar':
            contenido_actual = self.text_editor.toPlainText()
            
            if contenido_actual != self.contenido_original:
                respuesta = QtWidgets.QMessageBox.question(
                    self,
                    "Cambios sin guardar",
                    "Tienes cambios sin guardar. ¿Quieres guardarlos antes de cerrar?",
                    QtWidgets.QMessageBox.Save | QtWidgets.QMessageBox.Discard | QtWidgets.QMessageBox.Cancel
                )
                
                if respuesta == QtWidgets.QMessageBox.Save:
                    self.guardar_archivo()
                    return  # guardar_archivo ya maneja el cierre
                elif respuesta == QtWidgets.QMessageBox.Cancel:
                    event.ignore()
                    return
        
        event.accept()


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
        btn_nuevo = QtWidgets.QPushButton("📄 Nuevo Artículo")
        btn_nuevo.clicked.connect(self.nuevo_articulo)
        btn_nuevo.setMinimumHeight(40)
        sidebar.addWidget(btn_nuevo)
        sidebar.addStretch()

        # --- Contenido principal ---
        content_layout = QtWidgets.QVBoxLayout()

        # Formulario búsqueda
        form_layout = QtWidgets.QFormLayout()
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_autor = QtWidgets.QLineEdit()
        self.input_anio = QtWidgets.QLineEdit()
        
        btn_aplicar_busqueda = QtWidgets.QPushButton("🔍 Aplicar Búsqueda")
        btn_aplicar_busqueda.clicked.connect(self.aplicar_busqueda)
        
        btn_limpiar = QtWidgets.QPushButton("🧹 Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_busqueda)

        form_layout.addRow("Título:", self.input_titulo)
        form_layout.addRow("Autor(es):", self.input_autor)
        form_layout.addRow("Año de Publicación:", self.input_anio)
        
        search_buttons_layout = QtWidgets.QHBoxLayout()
        search_buttons_layout.addWidget(btn_aplicar_busqueda)
        search_buttons_layout.addWidget(btn_limpiar)
        form_layout.addRow(search_buttons_layout)

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

    def limpiar_busqueda(self):
        self.input_titulo.clear()
        self.input_autor.clear()
        self.input_anio.clear()
        self.mostrar_resultados(self.tabla.listar_todos())

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
            item_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border: 1px solid #dee2e6;
                    border-radius: 5px;
                    margin: 2px;
                    padding: 5px;
                }
            """)
            
            item_layout = QtWidgets.QHBoxLayout(item_widget)

            lbl = QtWidgets.QLabel(f"<b>{art.titulo}</b><br><i>{art.autor}</i> ({art.anio})")
            lbl.setWordWrap(True)
            
            btn_ver = QtWidgets.QPushButton("👁️ Ver")
            btn_modificar = QtWidgets.QPushButton("✏️ Editar")
            btn_eliminar = QtWidgets.QPushButton("🗑️ Eliminar")

            # Estilos para botones
            btn_ver.setStyleSheet("QPushButton { background-color: #17a2b8; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")
            btn_modificar.setStyleSheet("QPushButton { background-color: #ffc107; color: black; border: none; padding: 5px 10px; border-radius: 3px; }")
            btn_eliminar.setStyleSheet("QPushButton { background-color: #dc3545; color: white; border: none; padding: 5px 10px; border-radius: 3px; }")

            btn_ver.clicked.connect(lambda _, a=art: self.ver_archivo(a))
            btn_modificar.clicked.connect(lambda _, a=art: self.editar_archivo(a))
            btn_eliminar.clicked.connect(lambda _, a=art: self.eliminar_archivo(a))

            item_layout.addWidget(lbl, 3)
            item_layout.addStretch()
            item_layout.addWidget(btn_ver)
            item_layout.addWidget(btn_modificar)
            item_layout.addWidget(btn_eliminar)

            self.resultados_scroll_layout.addWidget(item_widget)

        self.resultados_scroll_layout.addStretch()

    def nuevo_articulo(self):
        dialog = QtWidgets.QDialog(self)
        dialog.setModal(True)  # Asegurar que sea modal
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

    def ver_archivo(self, art):
        """Abrir archivo en modo solo lectura"""
        editor = EditorDialog(self, art, modo='ver')
        editor.exec_()

    def editar_archivo(self, art):
        """Abrir archivo en modo edición (modal, bloquea ventana principal)"""
        editor = EditorDialog(self, art, modo='editar')
        resultado = editor.exec_()
        
        # Si se guardaron cambios, actualizar la vista
        if resultado == QtWidgets.QDialog.Accepted:
            self.mostrar_resultados(self.tabla.listar_todos())

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