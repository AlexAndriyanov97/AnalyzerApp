import sys

import lasio
import pandas as pd
from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QTableWidgetItem

import design
import os


class AnalyzerApp(QtWidgets.QMainWindow, design.Ui_MainWindow):
    def __init__(self):
        super().__init__()
        self._final_stat = {}
        self._detailed_dictionary = {}
        self._percent_bad_data = {}
        self.setupUi(self)
        self._directory = None
        self.pushButton.clicked.connect(self.browse_folder)  # Выполнить функцию browse_folder
        # при нажатии кнопки
        self.pushButton_2.clicked.connect(self.analyzer)
        self.pushButton_3.clicked.connect(self.analyzer)
        self.checkBox.stateChanged.connect(self.clickBox)
        self.count_files = 0
        self.tableWidget.clicked.connect(self.on_click)

    def on_click(self):
        print("\n")
        for currentQTableWidgetItem in self.tableWidget.selectedItems():
            if currentQTableWidgetItem.column() == 0:
                if self._detailed_dictionary.get(currentQTableWidgetItem.text()) is not None:
                    self.openWindows(dataframe=self._detailed_dictionary[currentQTableWidgetItem.text()])
            if currentQTableWidgetItem.column() == 1:
                if self._percent_bad_data.get(
                        (self.tableWidget.item(currentQTableWidgetItem.row(), 0)).text()) is not None:
                    self.openWindows(dataframe=pd.DataFrame.from_dict(
                        self._percent_bad_data[(self.tableWidget.item(currentQTableWidgetItem.row(), 0)).text()],
                        orient='index', columns=['% плохих данных']
                    ))
        self.tableWidget.clearSelection()

    def clickBox(self, state):
        if state == QtCore.Qt.Checked:
            for iter in range(0, self.count_files):
                self.tableWidget.item(iter, 2).setCheckState(QtCore.Qt.Checked)
        else:
            for iter in range(0, self.count_files):
                self.tableWidget.item(iter, 2).setCheckState(QtCore.Qt.Unchecked)

    def browse_folder(self):
        tmp = self._directory
        self._directory = QtWidgets.QFileDialog.getExistingDirectory(self, "Выберите папку")
        self.tableWidget.setHorizontalHeaderLabels(["Имя", "Процент плохих данных", "Используемые файлы"])
        if self._directory == '':
            self._directory = tmp
            return
        self.tableWidget.clear()
        iterration = 0
        self.count_files = len(
            [name for name in os.listdir(self._directory) if os.path.isfile(os.path.join(self._directory, name))])
        self.tableWidget.setRowCount(self.count_files)
        if self._directory:  # не продолжать выполнение, если пользователь не выбрал директорию
            self._detailed_dictionary = {}
            self._percent_bad_data = {}
            self._final_stat = {}
            for file_name in os.listdir(self._directory):  # для каждого файла в директории
                self.tableWidget.setItem(iterration, 0, QTableWidgetItem(file_name))
                self.tableWidget.setItem(iterration, 1, QTableWidgetItem(""))
                chkBoxItem = QTableWidgetItem()
                chkBoxItem.setFlags(QtCore.Qt.ItemIsUserCheckable | QtCore.Qt.ItemIsEnabled)
                chkBoxItem.setCheckState(QtCore.Qt.Unchecked)
                self.tableWidget.setItem(iterration, 2, chkBoxItem)
                iterration += 1
        self.tableWidget.setHorizontalHeaderLabels(["Имя", "Процент плохих данных", "Используемые файлы"])
        self.checkBox.setChecked(False)
        self.checkBox.setVisible(True)
        self.progressBar.setValue(0)

    def analyzer(self):
        self.tableWidget_2.clear()
        self.first_file = True
        self.my_dict = {}
        self.average_percent_bad_data = {}
        self.bad_columns = {}
        self._final_stat = {}
        itter = -1
        self.progressBar.setVisible(True)
        if self._directory:
            itter = self.read_files(itter)
            itter += 1
            self.update_global_statistic(itter)

    def read_files(self, itter):
        for name in os.listdir(self._directory):
            itter += 1
            if self.tableWidget.item(itter, 2).checkState():
                self.progressBar.setValue(round(itter / self.count_files * 100))
                if os.path.isfile(os.path.join(self._directory, name)):
                    try:
                        las = lasio.read(self._directory + "/" + name)
                    except ValueError:
                        self.tableWidget.setItem(itter, 1, QTableWidgetItem('невозможно прочитать файл'))
                        continue
                    if self.first_file:
                        self.my_dict = dict.fromkeys(las.keys(), 0)
                        self.first_file = False
                    count_NaN = las.df().isnull().sum()
                    percent_bad_value = {}
                    tmp = 0
                    print(las.df().index.name)
                    for item in las.df().keys():
                        if item in self.my_dict:
                            self.my_dict[item] += 1
                        else:
                            self.my_dict[item] = 1
                        percent_bad_value[item] = round(count_NaN[item] / las[item].size * 100)
                        if percent_bad_value[item] == 100:
                            if item in self.bad_columns:
                                self.bad_columns[item] += 1
                            else:
                                self.bad_columns[item] = 1
                        if item in self.average_percent_bad_data.keys():
                            self.average_percent_bad_data[item] += percent_bad_value[item]
                        else:
                            self.average_percent_bad_data[item] = percent_bad_value[item]
                        tmp += percent_bad_value[item]
                    percent_bad_value = dict(sorted(percent_bad_value.items(), key=lambda x: x[1], reverse=True))
                    self._percent_bad_data[name] = percent_bad_value
                    self.tableWidget.setItem(itter, 1, QTableWidgetItem(str(round(tmp / len(percent_bad_value)))))
                    self._detailed_dictionary[name] = las.df().describe()
                    self.my_dict['DEPT'] += 1
            else:
                continue
        return itter

    def update_global_statistic(self, itter):
        if len(self.average_percent_bad_data) != 0:
            for item in self.average_percent_bad_data.keys():
                self.average_percent_bad_data[item] = round(self.average_percent_bad_data[item] / self.my_dict[item])
                self.my_dict[item] = str(self.my_dict[item]) + '/' + str(self.my_dict['DEPT']) + '(' + str(
                    round(self.my_dict[item] / self.my_dict['DEPT'] * 100)) + '%)'
                self._final_stat[item] = [item, self.my_dict[item], self.average_percent_bad_data[item],
                                          self.bad_columns[item] if item in self.bad_columns else 0]
            self._final_stat['DEPT'] = ['DEPT', str(self.my_dict['DEPT']) + '/' + str(self.my_dict['DEPT']) + '(' + str(
                round(self.my_dict['DEPT'] / self.my_dict['DEPT'] * 100)) + '%)', 0, 0]
            self._final_stat = dict(
                sorted(self._final_stat.items(), key=lambda x: int(x[1][1][:x[1][1].find("/")]), reverse=True))
            self.drawTable(pd.DataFrame.from_dict(self._final_stat, orient='index'))
            self.progressBar.setValue(round(itter / self.count_files * 100))


def main():
    app = QtWidgets.QApplication(sys.argv)
    window = AnalyzerApp()
    window.show()
    app.exec_()


if __name__ == '__main__':
    main()
