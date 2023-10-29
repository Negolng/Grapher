import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import random

# https://pythonspot.com/pyqt5-matplotlib/
# https://www.pythonguis.com/tutorials/plotting-matplotlib/
# https://matplotlib.org/stable/


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)

        self.graph = Plot(self)
        self.graph.move(200, 35)

        self.randomButton.clicked.connect(self.calc_and_plot)
        self.clearButton.clicked.connect(self.clear_plot)
        self.clear_plot()
        self.show()

    def calc_and_plot(self):
        data = self.calculate_data()
        if data is not None:
            self.plot_data(data)

    def calculate_data(self):
        try:
            data = [random.random() for _ in range(int(self.startXInput.text()), int(self.endXInput.text()) + 1)]
            self.statusLabel.setText('Success')
        except Exception:
            data = None
            self.statusLabel.setText('Error')
        return data

    def plot_data(self, data):

        self.graph.ax.plot(data)
        self.graph.draw()

    def clear_plot(self):
        self.graph.ax.cla()
        self.graph.draw()


class Plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.figure.add_subplot(111)
        self.ax.set_title('Kurwa')
        self.setParent(parent)


application = QApplication(sys.argv)
window = MainWindow()
sys.exit(application.exec())
