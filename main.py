import sys
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QGridLayout, QLabel
from PyQt5 import uic
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
from math import floor
from datetime import datetime

# https://pythonspot.com/pyqt5-matplotlib/
# https://www.pythonguis.com/tutorials/plotting-matplotlib/
# https://matplotlib.org/stable/


OPERANDS = '/*-+^'
NUMBERS = '123456789'
SPECIALS = OPERANDS + NUMBERS


class FormulaError(Exception):
    pass


class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('log_gui.ui')
        layout = QGridLayout()
        for i in range(10):
            label = QLabel(self)
            label.setText(i)
            print('!!!')
            layout.addWidget(label)
            print('a')
        log_widget = QWidget()
        log_widget.setLayout(layout)
        self.logArea.setWidgt(log_widget)



def is_it_safe(line):
    safe = True
    if not ('y' in line or 'f(x)' in line or 'x' in line):
        safe = False
    return safe


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('main_gui.ui', self)

        self.graph = Plot(self)
        self.graph.move(200, 35)

        self.plotButton.clicked.connect(self.calc_and_plot)
        self.clearButton.clicked.connect(self.clear_plot)
        self.logButton.clicked.connect(self.show_logs)
        self.calc_and_plot()
        self.show()

    def function_interpreter(self):
        line = self.functionInput.text().lower()
        left_part, right_part = line.split('=')
        if is_it_safe(left_part):
            return right_part.replace('^', '**')

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
            with open('logs.txt', 'a') as f:
                f.write(f'[{datetime.now()}] Calculated data Successfully!\n')
        except ValueError:
            xdata, ydata = None, None
            with open('logs.txt', 'a') as f:
                f.write(f'[{datetime.now()}] Calculation error\n')
            self.statusLabel.setText('Error')
        return xdata, ydata

    def plot_data(self, xdata, ydata):
        self.graph.ax.plot(xdata, ydata)
        self.graph.draw()

    def clear_plot(self):
        self.graph.ax.cla()
        self.graph.draw()

    def show_logs(self):
        self.log_window = LogWindow()
        self.log_window.show()


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
