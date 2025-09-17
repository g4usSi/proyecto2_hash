import sys
import os
import datetime

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from PyQt5 import QtWidgets, QtCore, QtGui
from core import HashTable, IndiceAutor, IndiceTitulo, Storage, articulo, HashUtils
from core.indices import IndiceAnio  # Asegurarse de importar IndiceAnio

class VentanaEditor(QtWidgets.QDialog):
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
        
        # Informacion del articulo
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
        
        # Conectar señal para actualizar estadisticas
        self.text_editor.textChanged.connect(self.actualizar_estadisticas)
        
        layout.addWidget(self.text_editor)
        
        # Botones
        buttons_layout = QtWidgets.QHBoxLayout()
        
        if self.modo == 'editar':
            btn_guardar = QtWidgets.QPushButton("Guardar")
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
            
            btn_descartar = QtWidgets.QPushButton("Descartar cambios")
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
        
        btn_cerrar = QtWidgets.QPushButton("Cerrar")
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
        
        self.stats_label.setText(f"{palabras} palabras, {caracteres} caracteres, {lineas} lineas")
    
    def guardar_archivo(self):
        try:
            contenido_actual = self.text_editor.toPlainText()
            Storage.actualizar_archivo(self.articulo.archivo, contenido_actual)
            
            QtWidgets.QMessageBox.information(self, "Exito", "Archivo guardado correctamente.")
            self.accept()  # Cierra el dialogo con resultado positivo
            
        except Exception as e:
            QtWidgets.QMessageBox.critical(self, "Error", f"No se pudo guardar: {str(e)}")
    
    def descartar_cambios(self):
        contenido_actual = self.text_editor.toPlainText()
        
        if contenido_actual != self.contenido_original:
            respuesta = QtWidgets.QMessageBox.question(
                self, 
                "Descartar cambios", 
                "¿Estas seguro de que quieres descartar todos los cambios?",
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
        self.setWindowTitle("Gestor de Articulos Cientificos")
        self.setGeometry(100, 100, 1000, 600)

        # --- Tabla hash e indices ---
        self.tabla = HashTable()
        self.indice_autor = IndiceAutor()
        self.indice_titulo = IndiceTitulo()
        self.indice_anio = IndiceAnio()
        self.cargar_base_datos()

        # --- Layout principal ---
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # --- Barra lateral izquierda ---
        sidebar = QtWidgets.QVBoxLayout()
        btn_nuevo = QtWidgets.QPushButton("Nuevo Articulo")
        btn_nuevo.clicked.connect(self.nuevo_articulo)
        btn_nuevo.setMinimumHeight(40)
        sidebar.addWidget(btn_nuevo)
        sidebar.addStretch()

        # --- Contenido principal ---
        content_layout = QtWidgets.QVBoxLayout()

        # Formulario busqueda
        form_layout = QtWidgets.QFormLayout()
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_autor = QtWidgets.QLineEdit()
        self.input_anio = QtWidgets.QLineEdit()
        
        btn_aplicar_busqueda = QtWidgets.QPushButton("Aplicar Busqueda")
        btn_aplicar_busqueda.clicked.connect(self.aplicar_busqueda)
        
        btn_limpiar = QtWidgets.QPushButton("Limpiar")
        btn_limpiar.clicked.connect(self.limpiar_busqueda)

        form_layout.addRow("Titulo:", self.input_titulo)
        form_layout.addRow("Autor(es):", self.input_autor)
        form_layout.addRow("Año de Publicacion:", self.input_anio)
        
        search_buttons_layout = QtWidgets.QHBoxLayout()
        search_buttons_layout.addWidget(btn_aplicar_busqueda)
        search_buttons_layout.addWidget(btn_limpiar)
        form_layout.addRow(search_buttons_layout)

        # Resultados
        self.resultados_layout = QtWidgets.QVBoxLayout()
        resultados_label = QtWidgets.QLabel("Resultados de la busqueda:")
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
        """Carga la base de datos y valida que los archivos existan"""
        articulos = Storage.cargar()
        articulos_validos = []
        articulos_huerfanos = []  # Artículos sin archivo físico
        
        for art in articulos:
            if Storage.archivo_existe(art.archivo):
                # Archivo existe, agregarlo normalmente
                self.tabla.insertar(art.hash, art)
                self.indice_autor.agregar(art)
                self.indice_titulo.agregar(art)
                self.indice_anio.agregar(art)
                articulos_validos.append(art)
            else:
                # Archivo no existe, marcarlo como huérfano
                articulos_huerfanos.append(art)
                print(f"⚠️ Archivo huérfano encontrado: {art.archivo} (Artículo: {art.titulo})")
        
        # Si hay artículos huérfanos, preguntar qué hacer
        if articulos_huerfanos:
            self.manejar_articulos_huerfanos(articulos_huerfanos)

    def manejar_articulos_huerfanos(self, articulos_huerfanos):
        """Maneja artículos que existen en la DB pero no tienen archivo físico"""
        mensaje = f"⚠️ Se encontraron {len(articulos_huerfanos)} artículo(s) en la base de datos sin archivo físico:\n\n"
        
        for art in articulos_huerfanos[:5]:  # Mostrar máximo 5
            mensaje += f"• {art.titulo} - {art.autor} ({art.archivo})\n"
        
        if len(articulos_huerfanos) > 5:
            mensaje += f"... y {len(articulos_huerfanos) - 5} más\n"
        
        mensaje += "\n¿Qué deseas hacer?"
        
        # Crear diálogo personalizado
        dialog = QtWidgets.QMessageBox(self)
        dialog.setWindowTitle("Archivos Huérfanos Detectados")
        dialog.setText(mensaje)
        
        btn_limpiar = dialog.addButton("🧹 Limpiar base de datos", QtWidgets.QMessageBox.YesRole)
        btn_ignorar = dialog.addButton("👁️ Mantener registros", QtWidgets.QMessageBox.NoRole)
        btn_ver_detalle = dialog.addButton("📋 Ver detalles", QtWidgets.QMessageBox.HelpRole)
        
        dialog.setDefaultButton(btn_ver_detalle)
        dialog.exec_()
        
        if dialog.clickedButton() == btn_limpiar:
            # Eliminar artículos huérfanos de la base de datos
            for art in articulos_huerfanos:
                Storage.eliminar_articulo_de_db(art)
            
            QtWidgets.QMessageBox.information(
                self, "Limpieza Completada", 
                f"Se eliminaron {len(articulos_huerfanos)} registro(s) huérfano(s) de la base de datos."
            )
        
        elif dialog.clickedButton() == btn_ver_detalle:
            # Mostrar detalles de todos los artículos huérfanos
            self.mostrar_detalle_huerfanos(articulos_huerfanos)

    def mostrar_detalle_huerfanos(self, articulos_huerfanos):
        """Muestra una ventana con el detalle de todos los artículos huérfanos"""
        dialog = QtWidgets.QDialog(self)
        dialog.setWindowTitle("Detalle de Archivos Huérfanos")
        dialog.setModal(True)
        dialog.resize(600, 400)
        
        layout = QtWidgets.QVBoxLayout(dialog)
        
        # Lista de artículos huérfanos
        lista = QtWidgets.QListWidget()
        for art in articulos_huerfanos:
            item_text = f"📄 {art.titulo}\n👤 {art.autor} ({art.anio})\n📁 {art.archivo}\n"
            item = QtWidgets.QListWidgetItem(item_text)
            lista.addItem(item)
        
        layout.addWidget(QtWidgets.QLabel(f"Se encontraron {len(articulos_huerfanos)} artículos sin archivo físico:"))
        layout.addWidget(lista)
        
        # Botones
        buttons_layout = QtWidgets.QHBoxLayout()
        btn_limpiar_seleccionados = QtWidgets.QPushButton("🧹 Limpiar seleccionados")
        btn_limpiar_todos = QtWidgets.QPushButton("🧹 Limpiar todos")
        btn_cerrar = QtWidgets.QPushButton("❌ Cerrar")
        
        buttons_layout.addWidget(btn_limpiar_seleccionados)
        buttons_layout.addWidget(btn_limpiar_todos)
        buttons_layout.addStretch()
        buttons_layout.addWidget(btn_cerrar)
        layout.addLayout(buttons_layout)
        
        def limpiar_todos():
            for art in articulos_huerfanos:
                Storage.eliminar_articulo_de_db(art)
            QtWidgets.QMessageBox.information(dialog, "Limpieza Completada", f"Se eliminaron {len(articulos_huerfanos)} registros.")
            dialog.accept()
        
        btn_limpiar_todos.clicked.connect(limpiar_todos)
        btn_cerrar.clicked.connect(dialog.reject)
        
        dialog.exec_()

    def limpiar_busqueda(self):
        self.input_titulo.clear()
        self.input_autor.clear()
        self.input_anio.clear()
        self.mostrar_resultados(self.tabla.listar_todos())

    def aplicar_busqueda(self):
        titulo = self.input_titulo.text().strip().lower()
        autor = self.input_autor.text().strip().lower()
        anio = self.input_anio.text().strip()
        matches = []

        if titulo:
            res = self.indice_titulo.buscar(titulo)
            # Asegurar que siempre sea lista
            if res:
                matches = res if isinstance(res, list) else [res]

        if autor:
            res = self.indice_autor.buscar(autor)
            if res:
                # unir con matches existentes sin duplicar
                res_list = res if isinstance(res, list) else [res]
                matches.extend(r for r in res_list if r not in matches)
        if anio:
            res = self.indice_anio.buscar(anio)
            if res:
                res_list = res if isinstance(res, list) else [res]
                matches.extend(r for r in res_list if r not in matches)

        if not titulo and not autor and not anio:
            matches = self.tabla.listar_todos()

        self.mostrar_resultados(matches)
        self.input_titulo.clear()
        self.input_autor.clear()
        self.input_anio.clear()

    def mostrar_resultados(self, articulos):
        # MÉTODO CORREGIDO para limpiar resultados anteriores
        def limpiar_layout(layout):
            """Limpia completamente todos los widgets de un layout"""
            while layout.count():
                child = layout.takeAt(0)
                if child.widget():
                    child.widget().deleteLater()
                elif child.layout():
                    limpiar_layout(child.layout())
        
        # Limpiar todos los widgets anteriores
        limpiar_layout(self.resultados_scroll_layout)

        # Verificar si hay artículos
        if not articulos:
            # Mostrar mensaje de "no hay coincidencias"
            no_results_widget = QtWidgets.QWidget()
            no_results_widget.setStyleSheet("""
                QWidget {
                    background-color: #f8f9fa;
                    border: 2px dashed #dee2e6;
                    border-radius: 10px;
                    margin: 20px;
                    padding: 40px;
                }
            """)
            
            no_results_layout = QtWidgets.QVBoxLayout(no_results_widget)
            
            # Ícono y mensaje
            icon_label = QtWidgets.QLabel("🔍")
            icon_label.setAlignment(QtCore.Qt.AlignCenter)
            icon_label.setStyleSheet("font-size: 48px; color: #6c757d; margin-bottom: 10px;")
            
            message_label = QtWidgets.QLabel("No se encontraron coincidencias")
            message_label.setAlignment(QtCore.Qt.AlignCenter)
            message_label.setStyleSheet("font-size: 18px; color: #6c757d; font-weight: bold; margin-bottom: 5px;")
            
            suggestion_label = QtWidgets.QLabel("Intenta con otros términos de búsqueda o limpia los filtros")
            suggestion_label.setAlignment(QtCore.Qt.AlignCenter)
            suggestion_label.setStyleSheet("font-size: 14px; color: #adb5bd;")
            
            no_results_layout.addWidget(icon_label)
            no_results_layout.addWidget(message_label)
            no_results_layout.addWidget(suggestion_label)
            
            self.resultados_scroll_layout.addWidget(no_results_widget)
            self.resultados_scroll_layout.addStretch()
            return

        # Mostrar artículos encontrados
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
            
            btn_ver = QtWidgets.QPushButton("Ver")
            btn_modificar = QtWidgets.QPushButton("Editar")
            btn_eliminar = QtWidgets.QPushButton("Eliminar")

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
        dialog.setModal(True)
        dialog.setWindowTitle("Nuevo Articulo")
        dialog.setMinimumSize(500, 400)
        layout = QtWidgets.QVBoxLayout(dialog)

        # Formulario de metadatos
        form_layout = QtWidgets.QFormLayout()
        input_titulo = QtWidgets.QLineEdit()
        input_autor = QtWidgets.QLineEdit()
        input_anio = QtWidgets.QLineEdit()
        input_archivo = QtWidgets.QLineEdit()
        
        # Boton para generar nombre automatico
        btn_generar_nombre = QtWidgets.QPushButton("Generar nombre automatico")
        archivo_layout = QtWidgets.QHBoxLayout()
        archivo_layout.addWidget(input_archivo)
        archivo_layout.addWidget(btn_generar_nombre)

        form_layout.addRow("Titulo:", input_titulo)
        form_layout.addRow("Autor(es):", input_autor)
        form_layout.addRow("Año:", input_anio)
        form_layout.addRow("Nombre archivo:", archivo_layout)
        
        layout.addLayout(form_layout)
        
        # Editor de contenido inicial
        layout.addWidget(QtWidgets.QLabel("Contenido inicial del articulo:"))
        contenido_editor = QtWidgets.QTextEdit()
        contenido_editor.setPlainText("# Titulo del articulo\n\n## Introduccion\n\n[Escribe aqui el contenido del articulo...]\n\n## Desarrollo\n\n## Conclusiones\n")
        layout.addWidget(contenido_editor)

        # Botones
        buttons_layout = QtWidgets.QHBoxLayout()
        btn_guardar = QtWidgets.QPushButton("Crear Articulo")
        btn_cancelar = QtWidgets.QPushButton("Cancelar")
        
        buttons_layout.addWidget(btn_guardar)
        buttons_layout.addWidget(btn_cancelar)
        layout.addLayout(buttons_layout)

        def generar_nombre_automatico():
            titulo = input_titulo.text().strip()
            autor = input_autor.text().strip()
            anio = input_anio.text().strip()
            
            if titulo:
                # Limpiar titulo para nombre de archivo
                nombre_limpio = "".join(c for c in titulo if c.isalnum() or c in (' ', '-', '_')).rstrip()
                nombre_limpio = nombre_limpio.replace(' ', '_')[:30]  
                
                if autor:
                    apellido = autor.split()[-1] if ' ' in autor else autor
                    nombre_archivo = f"{apellido}_{anio}_{nombre_limpio}.txt" if anio else f"{apellido}_{nombre_limpio}.txt"
                else:
                    nombre_archivo = f"{nombre_limpio}_{anio}.txt" if anio else f"{nombre_limpio}.txt"
                    
                input_archivo.setText(nombre_archivo)
            else:
                QtWidgets.QMessageBox.information(dialog, "Info", "Primero ingresa el titulo para generar el nombre automaticamente.")

        def guardar():
            titulo = input_titulo.text().strip()
            autor = input_autor.text().strip()
            anio = input_anio.text().strip()
            archivo = input_archivo.text().strip()
            contenido = contenido_editor.toPlainText()

            if not (titulo and autor and anio and archivo):
                QtWidgets.QMessageBox.warning(dialog, "Error", "Todos los campos de metadatos son obligatorios.")
                return

            #Revisar que año sea un número válido
            if not anio.isdigit() or len(anio) !=4:
                QtWidgets.QMessageBox.warning(self, "Error", "El año debe ser un número entre 1900 y 2025.")
                return
            #Validacion del año
            anio_actual = datetime.datetime.now().year
            if int(anio) > anio_actual:
                QtWidgets.QMessageBox.warning(dialog, "Error", f"El año no puede ser mayor que {anio_actual}.")
                return
            #Revisar duplicado (por título)
            for art in self.tabla.listar_todos():
                if art.titulo.lower() == titulo.lower():
                    QtWidgets.QMessageBox.warning(self, "Error", "Ya existe un artículo con este título.")
                    return

            # Asegurar que el archivo termine en .txt
            if not archivo.endswith('.txt'):
                archivo += '.txt'

            # Verificar si el archivo ya existe
            if os.path.exists(archivo):
                respuesta = QtWidgets.QMessageBox.question(
                    dialog, 
                    "Archivo existe", 
                    f"El archivo '{archivo}' ya existe. ¿Quieres sobrescribirlo?",
                    QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
                )
                if respuesta == QtWidgets.QMessageBox.No:
                    return

            try:
                # 1. Crear el objeto articulo
                art = articulo(titulo, autor, anio, archivo)
                art.hash = HashUtils.hash_text(titulo + autor + str(anio))

                # 2. Verificar que no exista en la base de datos
                if not self.tabla.insertar(art.hash, art):
                    QtWidgets.QMessageBox.warning(dialog, "Error", "Ya existe un articulo con esos datos en la base de datos.")
                    return

                # 3. CREAR EL ARCHIVO FISICO con el contenido
                with open(archivo, 'w', encoding='utf-8') as f:
                    f.write(contenido)

                # 4. Guardar en la base de datos
                self.indice_autor.agregar(art)
                self.indice_titulo.agregar(art)
                Storage.guardar_articulo(art)
                
                # 5. Actualizar la interfaz
                self.mostrar_resultados(self.tabla.listar_todos())
                
                QtWidgets.QMessageBox.information(dialog, "Exito", f"Articulo creado exitosamente:\n- Archivo: {archivo}\n- Agregado a la base de datos")
                dialog.accept()

            except Exception as e:
                QtWidgets.QMessageBox.critical(dialog, "Error", f"Error al crear el articulo: {str(e)}")
                self.tabla.eliminar(art.hash)

        btn_generar_nombre.clicked.connect(generar_nombre_automatico)
        btn_guardar.clicked.connect(guardar)
        btn_cancelar.clicked.connect(dialog.reject)
        dialog.exec_()

    def ver_archivo(self, art):
        editor = VentanaEditor(self, art, modo='ver')
        editor.exec_()

    def editar_archivo(self, art):
        editor = VentanaEditor(self, art, modo='editar')
        resultado = editor.exec_()
        
        # Si se guardaron cambios, actualizar la vista
        if resultado == QtWidgets.QDialog.Accepted:
            self.mostrar_resultados(self.tabla.listar_todos())

    def eliminar_archivo(self, art):
        confirm = QtWidgets.QMessageBox.question(
            self, "Confirmar Eliminación", 
            f"¿Estás seguro de eliminar permanentemente?\n\n"
            f"📄 Artículo: {art.titulo}\n"
            f"👤 Autor: {art.autor}\n"
            f"📁 Archivo: {art.archivo}\n\n"
            f"⚠️ Esta acción no se puede deshacer.",
            QtWidgets.QMessageBox.Yes | QtWidgets.QMessageBox.No
        )
        
        if confirm == QtWidgets.QMessageBox.Yes:
            try:
                # 1. Eliminar el archivo físico
                if Storage.archivo_existe(art.archivo):
                    Storage.eliminar_archivo(art.archivo)
                    archivo_eliminado = True
                else:
                    archivo_eliminado = False
                    print(f"Advertencia: El archivo físico '{art.archivo}' no existe")
                
                # 2. Eliminar de las estructuras de datos en memoria
                self.tabla.eliminar(art.hash)
                self.indice_autor.eliminar(art)
                self.indice_titulo.eliminar(art)
                
                # 3. Eliminar de la base de datos persistente
                Storage.eliminar_articulo_de_db(art)
                
                # 4. Actualizar la vista
                self.mostrar_resultados(self.tabla.listar_todos())
                
                # 5. Mostrar mensaje de confirmación
                if archivo_eliminado:
                    mensaje = f"✅ Artículo eliminado completamente:\n- Archivo físico eliminado\n- Metadatos eliminados de la base de datos"
                else:
                    mensaje = f"⚠️ Artículo eliminado de la base de datos:\n- El archivo físico no existía\n- Metadatos eliminados correctamente"
                
                QtWidgets.QMessageBox.information(self, "Eliminación Exitosa", mensaje)
                
            except Exception as e:
                # Si algo sale mal, intentar recargar desde la base de datos
                QtWidgets.QMessageBox.critical(self, "Error", f"Error durante la eliminación: {str(e)}")
                
                # Intentar recuperar el estado desde la base de datos
                try:
                    self.recargar_base_datos()
                    QtWidgets.QMessageBox.information(self, "Recuperación", "Se ha recargado la base de datos para mantener consistencia.")
                except Exception as e2:
                    QtWidgets.QMessageBox.critical(self, "Error Crítico", f"Error al recargar la base de datos: {str(e2)}")

    def recargar_base_datos(self):
        """Método auxiliar para recargar completamente la base de datos"""
        # Limpiar estructuras actuales
        self.tabla = HashTable()
        self.indice_autor = IndiceAutor()
        self.indice_titulo = IndiceTitulo()
        
        # Recargar desde archivo
        self.cargar_base_datos()
        
        # Actualizar vista
        self.mostrar_resultados(self.tabla.listar_todos())

if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())