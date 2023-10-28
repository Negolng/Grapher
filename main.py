import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)

        self.graph = Plot(self)
        self.graph.move(200, 35)

        self.randomButton.clicked.connect(self.plot_data)
        self.clearButton.clicked.connect(self.clear_plot)

        self.show()

    def plot_data(self):
        data = [random.random() for i in range(1, 10)]

        self.graph.ax.plot(data, 'r-')
        self.graph.draw()

    def clear_plot(self):
        pass
    # ДОДЕЛАТЬ ОТЧИСТКУ ВСЕГО ЭТОГО ГОВНА БЛЯТЬ
    # https://pythonspot.com/pyqt5-matplotlib/
    # https://www.pythonguis.com/tutorials/plotting-matplotlib/
    # https://matplotlib.org/stable/


class Plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.setParent(parent)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Kurwa')



application = QApplication(sys.argv)
window = MainWindow()
sys.exit(application.exec())
