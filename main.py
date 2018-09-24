import sys

import lasio
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

import design
import os


class AnalyzerApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        # Это здесь нужно для доступа к переменным, методам
        # и т.д. в файле design.py
        super().__init__()
        self.setupUi(self)  # Это нужно для инициализации нашего дизайна
        self._directory = None
        self.pushButton.clicked.connect(self.browse_folder)  # Выполнить функцию browse_folder
        # при нажатии кнопки
        self.pushButton_2.clicked.connect(self.analyzer)
        self.checkBox.stateChanged.connect(self.clickBox)
        self.count_files = 0

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            for iter in range(0, self.count_files):
                self.tableWidget.item(iter, 2).setCheckState(QtCore.Qt.Checked)
        else:
            for iter in range(0, self.count_files):
                self.tableWidget.item(iter, 2).setCheckState(QtCore.Qt.Unchecked)

    def browse_folder(self):
        self.tableWidget.clear()  # На случай, если в списке уже есть элементы
        self._directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        # открыть диалог выбора директории и установить значение переменной
        # равной пути к выбранной директории
        iterration = 0
        self.count_files = len(
            [name for name in os.listdir(self._directory) if os.path.isfile(os.path.join(self._directory, name))])
        self.tableWidget.setRowCount(self.count_files)
        if self._directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            for file_name in os.listdir(self._directory):  # для каждого файла в директории
                self.tableWidget.setItem(iterration, 0, QTableWidgetItem(file_name))  # добавить файл в listWidget
                self.tableWidget.setItem(iterration, 1, QTableWidgetItem(""))
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                self.tableWidget.setItem(iterration, 2, chkBoxItem)
                iterration += 1
        self.tableWidget.setHorizontalHeaderLabels(["Имя", "Процент плохих данных", "Используемые файлы"])
        self.checkBox.setVisible(True)

    def analyzer(self):
        first_file = True
        my_dict = {}
        bad_files = []
        i = 0
        if self._directory:
            for name in os.listdir(self._directory):
                if self.tableWidget.item(i, 2).checkState():
                    print(name)
                    if os.path.isfile(os.path.join(self._directory, name)):
                        try:
                            las = lasio.read(self._directory + "/" + name)
                        except ValueError:
                            bad_files.append(name)
                            i += 1
                            continue
                        if first_file:
                            my_dict = dict.fromkeys(las.keys(), 0)
                            first_file = False
                        count_NaN = las.df().isnull().sum()
                        percent_bad_value = {}
                        tmp = 0
                        for item in las.df().keys():
                            if item in my_dict:
                                my_dict[item] += 1
                            else:
                                my_dict[item] = 1
                            percent_bad_value[item] = round(count_NaN[item] / las[item].size, 2)
                            tmp += percent_bad_value[item]
                        self.tableWidget.setItem(i, 1, QTableWidgetItem(str(round(tmp / len(percent_bad_value), 2))))
                        print(i)
                    i += 1
                else:
                    i += 1
                    continue
                my_dict['DEPT'] = self.count_files
                print(sorted(my_dict.items(), key=lambda x: x[1], reverse=True))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AnalyzerApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
