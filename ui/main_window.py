import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon


class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Gestor de Articulos Cientificos")
        self.setGeometry(100, 100, 1000, 600)

        # --- Widget central ---
        central_widget = QtWidgets.QWidget()
        self.setCentralWidget(central_widget)
        main_layout = QtWidgets.QHBoxLayout(central_widget)

        # --- Barra lateral izquierda ---
        sidebar = QtWidgets.QVBoxLayout()
        btn_nuevo = QtWidgets.QPushButton("Nuevo Articulo")
        btn_buscar = QtWidgets.QPushButton("Buscar")
        btn_ver = QtWidgets.QPushButton("Ver")
        btn_editar = QtWidgets.QPushButton("Editar")

        sidebar.addWidget(btn_nuevo)
        sidebar.addWidget(btn_buscar)
        sidebar.addWidget(btn_ver)
        sidebar.addWidget(btn_editar)
        sidebar.addStretch()

        # --- Contenido principal ---
        content_layout = QtWidgets.QVBoxLayout()

        # Formulario busqueda
        form_layout = QtWidgets.QFormLayout()
        self.input_titulo = QtWidgets.QLineEdit()
        self.input_autor = QtWidgets.QLineEdit()
        self.input_anio = QtWidgets.QLineEdit()
        btn_aplicar_busqueda = QtWidgets.QPushButton("Aplicar Busqueda")

        form_layout.addRow("Titulo:", self.input_titulo)
        form_layout.addRow("Autor(es):", self.input_autor)
        form_layout.addRow("Año de Publicacion:", self.input_anio)
        form_layout.addRow(btn_aplicar_busqueda)

        # Resultados
        resultados_layout = QtWidgets.QVBoxLayout()
        resultados_label = QtWidgets.QLabel("Resultados de la busqueda:")
        resultados_layout.addWidget(resultados_label)

        # Scroll con coincidencias
        scroll_area = QtWidgets.QScrollArea()
        scroll_area.setWidgetResizable(True)
        resultados_widget = QtWidgets.QWidget()
        resultados_scroll_layout = QtWidgets.QVBoxLayout(resultados_widget)

        # Ejemplo de coincidencia
        for i in range(3):  # tres coincidencias 
            item_widget = QtWidgets.QWidget()
            item_layout = QtWidgets.QHBoxLayout(item_widget)

            lbl = QtWidgets.QLabel(f"Articulo {i+1}: Titulo de ejemplo")
            btn_modificar = QtWidgets.QPushButton("Modificar")
            btn_eliminar = QtWidgets.QPushButton("Eliminar")
            btn_ver = QtWidgets.QPushButton("Ver")

            item_layout.addWidget(lbl)
            item_layout.addStretch()
            item_layout.addWidget(btn_modificar)
            item_layout.addWidget(btn_eliminar)
            item_layout.addWidget(btn_ver)

            resultados_scroll_layout.addWidget(item_widget)

        resultados_scroll_layout.addStretch()
        scroll_area.setWidget(resultados_widget)
        resultados_layout.addWidget(scroll_area)

        # Agregar formulario y resultados al contenido principal
        content_layout.addLayout(form_layout)
        content_layout.addLayout(resultados_layout)

        # Agregar sidebar y contenido al layout principal
        main_layout.addLayout(sidebar, 1)
        main_layout.addLayout(content_layout, 4)


# Ventanas auxiliares para Ver y Editar
class VerWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Ver Articulo")
        self.setGeometry(200, 200, 400, 300)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("aca se muestran los detalles del articulo."))


class EditarWindow(QtWidgets.QDialog):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Editar Articulo")
        self.setGeometry(200, 200, 400, 300)
        layout = QtWidgets.QVBoxLayout(self)
        layout.addWidget(QtWidgets.QLabel("aca se podra editar el articulo."))


if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    window = MainWindow()
    window.show()
    sys.exit(app.exec_())