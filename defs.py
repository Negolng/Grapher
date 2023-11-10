from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from PyQt5.QtWidgets import QMainWindow, QMessageBox
from matplotlib.figure import Figure
from PyQt5.QtGui import QPixmap
from datetime import datetime
from PyQt5 import uic
import math as mt
import sqlite3


class MathFunctions:
    @staticmethod
    def mod(x, y):
        return x % y

    @staticmethod
    def sin(x):
        return mt.sin(x)

    @staticmethod
    def cos(x):
        return mt.cos(x)

    @staticmethod
    def tan(x):
        return mt.tan(x)


class UsefulTools:
    OPERANDS = '/*-+^ '
    NUMBERS = '123456789'
    KEY_WORDS = {'sin', 'tan', 'mod', 'cos'}
    ALLOWED = OPERANDS + NUMBERS + 'x'

    @staticmethod
    def write_log(log):
        with open('logs.txt', 'a') as f:
            f.write(f'[{datetime.now()}] {log}\n')

    @staticmethod
    def is_it_safe(line):
        one = 'y' in line or 'f(x)' in line or 'x' in line
        two = all([symbol in UsefulTools.ALLOWED for symbol in line])
        return one or two


# Windows
class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        uic.loadUi('Guis/main_gui.ui', self)
        self.lg = Language()
        self.lgF = False
        self.graph = Plot(self)
        self.graph.move(200, 35)
        self.log_window = LogWindow()
        self.load_window = LoadWindow(self)
        self.save_window = SaveWindow(self)
        self.lg.switch_russian()
        self.load_window.lg.switch_russian()
        self.log_window.lg.switch_russian()
        self.save_window.lg.switch_russian()
        self.set_lang()
        self.load_window.set_lang()
        self.log_window.set_lang()
        self.save_window.set_lang()
        pixmap = QPixmap("Guis/Image.png")
        self.imageLb.setPixmap(pixmap)
        self.plotButton.clicked.connect(self.calc_and_plot)
        self.clearButton.clicked.connect(self.clear_plot)
        self.logButton.clicked.connect(self.log_window.show)
        self.saveButton.clicked.connect(self.save_func)
        self.loadButton.clicked.connect(self.load_window.show)
        self.langButton.clicked.connect(self.switch_lang)
        self.calc_and_plot()
        UsefulTools.write_log('Application started successfully')
        self.show()

    def set_lang(self):
        self.plotButton.setText(self.lg.plotB)
        self.clearButton.setText(self.lg.plotC)
        self.logButton.setText(self.lg.logsB)
        self.saveButton.setText(self.lg.saveB)
        self.loadButton.setText(self.lg.loadB)
        self.formulaLb.setText(self.lg.formulaLb)
        self.startLb.setText(self.lg.beginL)
        self.endLb.setText(self.lg.endL)
        self.stepLb.setText(self.lg.stepL)

    def switch_lang(self):
        if self.lgF:
            self.lg.switch_russian()
            self.load_window.lg.switch_russian()
            self.log_window.lg.switch_russian()
            self.save_window.lg.switch_russian()
            self.lgF = False
        else:
            self.lg.switch_english()
            self.load_window.lg.switch_english()
            self.log_window.lg.switch_english()
            self.save_window.lg.switch_english()
            self.lgF = True
        self.set_lang()
        self.load_window.set_lang()
        self.log_window.set_lang()
        self.save_window.set_lang()
        UsefulTools.write_log('Language changed successfully')

    def function_interpreter(self, line=None):
        if not line:
            line = self.functionInput.text().lower()
        if '=' in line:
            left_part, right_part = line.split('=')
            if UsefulTools.is_it_safe(right_part):
                return right_part.replace('^', '**')
        UsefulTools.write_log('Error with function interpretation')
        self.statusLabel.setText(self.lg.error)

    def func(self, ret=None):
        if not ret:
            ret = self.function_interpreter()
        try:
            if ret:
                return lambda x: eval(ret)
            return lambda x: x
        except EOFError:
            UsefulTools.write_log('Error with function interpretation')
            self.statusLabel.setText(self.lg.error)

    def calc_and_plot(self):
        self.clear_plot()
        xdata, ydata = self.calculate_data(self.func())
        if xdata is not None:
            self.plot_data(xdata, ydata)

    def calculate_data(self, func):
        UsefulTools.write_log(f'Started calculating function {self.functionInput.text()}')
        ydata = []
        xdata = []
        try:
            end = float(self.endXInput.text())
            start = float(self.startXInput.text())
            step = float(self.stepInput.text())
            number_of_iterations = mt.floor((end - start) / step) + 1
            for _ in range(number_of_iterations):
                ydata.append(func(start))
                xdata.append(start)
                start += step
            self.statusLabel.setText(self.lg.successL)
            UsefulTools.write_log('Calculated data successfully')
        except ValueError:
            xdata, ydata = None, None
            UsefulTools.write_log('Calculation error')
            self.statusLabel.setText(self.lg.error)
        except EOFError:
            UsefulTools.write_log('Error with function interpretation')
            self.statusLabel.setText(self.lg.error)
        return xdata, ydata

    def plot_data(self, xdata, ydata):
        self.graph.ax.plot(xdata, ydata)
        UsefulTools.write_log('Plotted data successfully')
        self.graph.draw()

    def clear_plot(self):
        self.graph.ax.cla()
        self.graph.draw()
        UsefulTools.write_log('Cleared plot successfully')

    def save_func(self):
        self.save_window.set_data(self.functionInput.text())
        self.save_window.show()


class LoadWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.lg = Language()
        self.main_w = parent
        uic.loadUi('Guis/load_gui.ui', self)
        self.loadButton.clicked.connect(self.load_by_name)
        self.deleteButton.clicked.connect(self.delete)
        self.updateButton.clicked.connect(self.get_list)
        UsefulTools.write_log('Loaded load window successfully')
        self.get_list()

    def set_lang(self):
        self.loadButton.setText(self.lg.loadB)
        self.deleteButton.setText(self.lg.delB)
        self.updateButton.setText(self.lg.loadUpB)
        self.loadLb.setText(self.lg.loadL)
        UsefulTools.write_log('Language set successfully')

    def get_list(self):
        self.listWidget.clear()
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        request = '''
                        SELECT * FROM functions
                    '''
        new_list = []
        result = cursor.execute(request).fetchall()
        connection.close()
        for line in result:
            number, name, formula, group = line
            final_string = f'№{number} | Name: {name}, Formula: {formula}, Group: {group}'
            new_list.append(final_string)
        UsefulTools.write_log('got list of functions successfully')
        self.listWidget.addItems(new_list)

    def load_by_name(self):
        name = self.nameInput.text()
        if name:
            connection = sqlite3.connect('database.sqlite')
            cursor = connection.cursor()
            names = set(map(''.join, cursor.execute('SELECT name FROM functions').fetchall()))
            if name in names:
                request = f'''
                SELECT formula FROM functions
                WHERE name = "{name}"
                '''
                formula = str(''.join(*cursor.execute(request).fetchall()))
                connection.close()
                self.main_w.functionInput.setText(formula)
                UsefulTools.write_log('Loaded a function successfully')
                self.hide()
                self.nameInput.clear()
            else:
                msg = QMessageBox(self)
                msg.setText(self.lg.nonameMsg)
                msg.setWindowTitle(self.lg.error)
                UsefulTools.write_log('Error, no function found')
                msg.exec()

    def delete(self):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        request = f'''
                DELETE FROM functions
                WHERE name = "{self.nameInput.text()}"
                '''
        cursor.execute(request).fetchall()
        connection.commit()
        connection.close()
        msg = QMessageBox(self)
        msg.setText(self.lg.delMsg)
        msg.setWindowTitle(self.lg.delB)
        msg.exec()
        UsefulTools.write_log('Deleted a function successfully')
        self.get_list()
        self.nameInput.clear()


class SaveWindow(QMainWindow):
    def __init__(self, parent):
        super().__init__()
        self.main_w = parent
        uic.loadUi('Guis/save_gui.ui', self)
        self.lg = Language()
        self.saveButton.clicked.connect(self.save_or_update)
        UsefulTools.write_log('Loaded save window successfully')

    def set_data(self, formula):
        self.functionInput.setText(formula)
        
    def set_lang(self):
        self.saveButton.setText(self.lg.saveB)
        self.formulaLb.setText(self.lg.formulaLb)
        self.nameLb.setText(self.lg.loadL)
        self.groupLb.setText(self.lg.group)
        UsefulTools.write_log('Language set successfully')

    @staticmethod
    def new_group(n):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        req = f'''
        INSERT INTO groups(group) VALUES({n})
        '''
        cursor.execute(req).fetchall()
        connection.commit()
        connection.close()
        UsefulTools.write_log('new group created successfully')

    @staticmethod
    def is_group_there(n):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        req = f'''
                SELECT numberG FROM groups
                '''
        groups = list(map(lambda x: x[0], cursor.execute(req).fetchall()))
        connection.commit()
        connection.close()
        return n in groups

    def save_or_update(self):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        names = set(map(''.join, cursor.execute('SELECT name FROM functions').fetchall()))
        name = self.nameInput.text()
        try:
            if name:
                group = int(self.groupInput.text())
                if SaveWindow.is_group_there(group):
                    if name in names:
                        msg = QMessageBox(self)
                        msg.setText(self.lg.existMsg)
                        msg.setWindowTitle(self.lg.existMsgT)
                        msg.exec()
                        self.update_old_function(name)

                    else:
                        self.save_new_funtion(name)
                    self.hide()
                else:
                    cursor.execute(f'''INSERT INTO groups(numberG) VALUES({group})''').fetchall()
                    connection.commit()
                    self.save_or_update()
            else:
                msg = QMessageBox(self)
                msg.setText(self.lg.nameMsg)
                msg.setWindowTitle(self.lg.nameMsgT)
                msg.exec()
                UsefulTools.write_log('No name error successfully')
            connection.close()

        except ValueError:
            self.errorLb.setText(self.lg.error)
            UsefulTools.write_log('Error with group name while checking')

    def update_old_function(self, name):
        try:
            connection = sqlite3.connect('database.sqlite')
            cursor = connection.cursor()
            request = f'''
                        UPDATE functions
                        SET formula = "{self.functionInput.text()}", group={int(self.groupInput.text())}
                        WHERE name = "{name}"
                     '''
            cursor.execute(request).fetchall()
            self.errorLb.setText(self.lg.successL)
            connection.commit()
            connection.close()
            UsefulTools.write_log('Save updated successfully')
        except ValueError:
            self.errorLb.setText(self.lg.error)
            UsefulTools.write_log('Error with group name while updating')

    def save_new_funtion(self, name):
        connection = sqlite3.connect('database.sqlite')
        cursor = connection.cursor()
        try:
            request = f'''
            INSERT INTO functions(name, formula, numberG) VALUES("{name}", "{self.functionInput.text()}", 
{int(self.groupInput.text())})
             '''
            cursor.execute(request).fetchall()
            print('a')
            connection.commit()
            connection.close()
            self.errorLb.setText(self.lg.successL)
            UsefulTools.write_log('Saved a function successfully')
        except ValueError:
            self.errorLb.setText(self.lg.error)
            UsefulTools.write_log('Error with group name while saving')


class LogWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.lg = Language()
        uic.loadUi('Guis/log_gui.ui', self)
        self.updateButton.clicked.connect(self.read_logs)
        self.clearButton.clicked.connect(self.remove_logs)
        self.read_logs()
        UsefulTools.write_log('Logs window started successfully')

    def set_lang(self):
        self.updateButton.setText(self.lg.logsUpB)
        self.clearButton.setText(self.lg.logsClB)
        UsefulTools.write_log('Language set successfully')

    def read_logs(self):
        self.logArea.clear()
        logs = open('logs.txt', 'r')
        self.logArea.addItems(logs.readlines())
        logs.close()
        UsefulTools.write_log('Logs loaded successfully')

    def remove_logs(self):
        with open('logs.txt', 'w') as f:
            f.write('')
        self.read_logs()
        msg = QMessageBox(self)
        msg.setText(self.lg.logsMsg)
        msg.setWindowTitle(self.lg.logsB)
        msg.show()


class Plot(FigureCanvas):
    def __init__(self, parent=None, width=5, height=5, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        super().__init__(self.fig)
        self.ax = self.figure.add_subplot(111)
        self.ax.grid(True)
        self.setParent(parent)
        UsefulTools.write_log('Axes created successfully')


class Language:
    def __init__(self):
        self.plotB = ''
        self.plotC = ''
        self.formulaLb = ''
        self.saveB = ''
        self.loadB = ''
        self.logsB = ''
        self.beginL = ''
        self.endL = ''
        self.stepL = ''
        self.loadL = ''
        self.loadUpB = ''
        self.delB = ''
        self.logsUpB = ''
        self.logsClB = ''
        self.existMsg = ''
        self.existMsgT = ''
        self.nonameMsg = ''
        self.error = ''
        self.delMsg = ''
        self.logsMsg = ''
        self.successL = ''
        self.checkT = ''
        self.nameMsg = ""
        self.nameMsgT = ''
        self.group = ''

    def switch_english(self):
        self.plotB = 'Plot'
        self.plotC = 'Clear plot'
        self.formulaLb = 'Formula:'
        self.saveB = 'Save'
        self.loadB = 'Load'
        self.logsB = 'Logs'
        self.beginL = 'begin with x = '
        self.endL = 'end with x = '
        self.stepL = 'step ='
        self.loadL = "Choose funtion's name:"
        self.loadUpB = 'Update list'
        self.delB = 'Delete'
        self.logsUpB = 'Update logs'
        self.logsClB = 'Clear logs'
        self.existMsg = 'This function exists already, it will be updated'
        self.existMsgT = 'Update'
        self.nonameMsg = 'There is no such name in the list'
        self.error = 'Error'
        self.delMsg = 'Deleted successfully'
        self.logsMsg = 'Logs have been cleared'
        self.successL = 'Success!'
        self.checkT = 'Save points'
        self.nameMsg = "Choose function's name, please"
        self.nameMsgT = 'Error'
        self.group = 'Group: '

    def switch_russian(self):
        self.plotB = 'Начертить'
        self.plotC = 'Отчистить плоскость'
        self.formulaLb = 'Формула:'
        self.saveB = 'Сохранить'
        self.loadB = 'Загрузить'
        self.logsB = 'Логи'
        self.beginL = 'Начать с x = '
        self.endL = 'Закончить с x = '
        self.stepL = 'Шаг ='
        self.loadL = "Выберите имя функции:"
        self.loadUpB = 'Обновить список'
        self.delB = 'Удалить'
        self.logsUpB = 'Обновить логи'
        self.logsClB = 'Очистить логи'
        self.existMsg = 'Эта функция уже существует, так что она будет обновлена'
        self.existMsgT = 'Обновить'
        self.nonameMsg = 'В списке нет такого имеи'
        self.error = 'Ошибка'
        self.delMsg = 'Удалено успешно'
        self.logsMsg = 'Логи были очищены'
        self.successL = 'Успех!'
        self.checkT = 'Сохранить точки'
        self.nameMsg = "Выберите имя функции, пожалуйста"
        self.nameMsgT = 'Ошибка'
        self.group = 'Группа: '
