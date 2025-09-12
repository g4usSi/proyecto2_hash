import sys
from PyQt5 import QtWidgets
from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon

class MainWindow(QtWidgets.QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("My Application")
        self.setGeometry(100, 100, 800, 600)
        self.setWindowIcon(QIcon('path/to/icon.png'))  # asegúrate de que exista ese archivo
        
        self.central_widget = QtWidgets.QWidget()
        self.setCentralWidget(self.central_widget)
        
        self.layout = QtWidgets.QVBoxLayout()
        self.central_widget.setLayout(self.layout)
        
        self.label = QtWidgets.QLabel("Hello, World!")
        self.label.setAlignment(Qt.AlignCenter)
        self.layout.addWidget(self.label)
        
        self.button = QtWidgets.QPushButton("Click Me")
        self.button.clicked.connect(self.on_button_click)
        self.layout.addWidget(self.button)
        
    def on_button_click(self):
        self.label.setText("Button Clicked!")
    
if __name__ == "__main__":
    app = QtWidgets.QApplication(sys.argv)
    main_window = MainWindow()
    main_window.show()
    sys.exit(app.exec_())
