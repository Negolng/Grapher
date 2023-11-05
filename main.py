import sys
from PyQt5.QtWidgets import QApplication, QMainWindow
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor

# https://pythonspot.com/pyqt5-matplotlib/
# https://www.pythonguis.com/tutorials/plotting-matplotlib/
# https://matplotlib.org/stable/



OPERANDS = {'/', '+', '-', '^', '*'}


class FormulaError(Exception):
    pass


class MathFunc:
    def __init__(self):
        self.things_to_do = []

    @staticmethod
    def multiply(x, y):
        return x * y

    @staticmethod
    def divide(x, y):
        return x / y

    @staticmethod
    def add(x, y):
        return x + y

    @staticmethod
    def sub(x, y):
        return x - y

    @staticmethod
    def pow(x, y):
        return x**y

    @staticmethod
    def root(x, y):
        return x**(1 / y)

    def add_f(self, function):
        self.things_to_do.append(function)

# TODO: eval


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('gui.ui', self)

        self.graph = Plot(self)
        self.graph.move(200, 35)

        self.plotButton.clicked.connect(self.calc_and_plot)
        self.clearButton.clicked.connect(self.clear_plot)
        self.clear_plot()
        self.show()

    def function_interpreter(self):
        line = self.functionInput.text().lower()
        func = MathFunc()

        left_part, right_part = line.split('=')
        if 'y' in left_part or 'f(x)' in left_part or 'x' in left_part:
            for i, symbol in enumerate(right_part):
                if symbol == ' ':
                    continue
                if symbol == 'x':
                    operand = right_part[i]
                    while operand not in OPERANDS:
                        i += 1
                        operand = right_part[i]
                    

        else:
            raise FormulaError

    def calc_and_plot(self):
        func = lambda x: eval(self.function_interpreter())
        self.clear_plot()
        xdata, ydata = self.calculate_data(func)
        if xdata is not None:
            self.plot_data(xdata, ydata)

    def calculate_data(self, func):
        ydata = []
        xdata = []
        try:
            end = float(self.endXInput.text())
            start = float(self.startXInput.text())
            step = float(self.stepInput.text())
            number_of_iterations = floor((end - start) / step) + 1
            for _ in range(number_of_iterations):
                ydata.append(func(start))
                xdata.append(start)
                start += step
            self.statusLabel.setText('Success')
        except ValueError:
            xdata, ydata = None, None
            self.statusLabel.setText('Error')
        return xdata, ydata

    def plot_data(self, xdata, ydata):
        self.graph.ax.plot(xdata, ydata)
        self.graph.draw()

    def clear_plot(self):
        self.graph.ax.cla()
        self.graph.draw()


class Plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True)
        self.ax.set_title('Kurwa')
        self.setParent(parent)


application = QApplication(sys.argv)
window = MainWindow()
sys.exit(application.exec())
