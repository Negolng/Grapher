import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QMessageBox
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
import math as mt
from datetime import datetime


# КТО ПРОЕКТ ТРОНЕТ - В ЖОПУ ВЫЕБУ

OPERANDS = '/*-+^ '
NUMBERS = '123456789'
KEY_WORDS = {'sin', 'tan', 'mod', 'cos'}
ALLOWED = OPERANDS + NUMBERS + 'x'


def mod(x, y):
    return x % y


def sin(x):
    return mt.sin(x)


def cos(x):
    return mt.cos(x)


def tan(x):
    return mt.tan(x)


def write_log(log):
    with open('logs.txt', 'a') as f:
        f.write(f'[{datetime.now()}] {log}\n')


def is_it_safe(line):
    one = 'y' in line or 'f(x)' in line or 'x' in line
    two = all([symbol in ALLOWED for symbol in line])
    return one or two


class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('log_gui.ui', self)
        self.updateButton.clicked.connect(self.read_logs)
        self.clearButton.clicked.connect(self.remove_logs)
        self.read_logs()
        write_log('Logs window started successfully')

    def read_logs(self):
        self.logArea.clear()
        logs = open('logs.txt', 'r')
        self.logArea.addItems(logs.readlines())
        logs.close()

    def remove_logs(self):
        with open('logs.txt', 'w') as f:
            f.write('')
        self.read_logs()
        msg = QMessageBox(self)
        msg.setText('Logs have been removed')
        msg.show()


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_gui.ui', self)

        self.graph = Plot(self)
        self.graph.move(200, 35)

        self.log_window = LogWindow()

        self.plotButton.clicked.connect(self.calc_and_plot)
        self.clearButton.clicked.connect(self.clear_plot)
        self.logButton.clicked.connect(self.log_window.show)
        self.calc_and_plot()
        write_log('Application started successfully')
        self.show()

    def function_interpreter(self):
        line = self.functionInput.text().lower()
        left_part, right_part = line.split('=')
        if is_it_safe(right_part):
            return right_part.replace('^', '**')
        write_log('Error with function interpretation')
        self.statusLabel.setText('Error')

    def func(self):
        ret = self.function_interpreter()
        if ret:
            return lambda x: eval(ret)
        return lambda x: x

    def calc_and_plot(self):
        self.clear_plot()
        xdata, ydata = self.calculate_data(self.func())
        if xdata is not None:
            self.plot_data(xdata, ydata)

    def calculate_data(self, func):
        write_log(f'Started calculating function {self.functionInput.text()}')
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
            write_log('Calculated data successfully')
        except ValueError:
            xdata, ydata = None, None
            write_log('Calculation error')
            self.statusLabel.setText('Error')
        return xdata, ydata

    def plot_data(self, xdata, ydata):
        self.graph.ax.plot(xdata, ydata)
        write_log('Plotted data successfully')
        self.graph.draw()

    def clear_plot(self):
        self.graph.ax.cla()
        self.graph.draw()
        write_log('Cleared plot successfully')


class Plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True)
        self.setParent(parent)


application = QApplication(sys.argv)
window = MainWindow()
sys.exit(application.exec())
