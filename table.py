import PandasModel
from PyQt5 import QtCore, QtGui, QtWidgets

class Ui_OtherWindow(QtWidgets.QWidget):
    def __init__(self,MainWindow,dataframe=None,parent=None):
        QtWidgets.QWidget.__init__(self, parent=None)
        MainWindow.resize(850, 400)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.horizontalLayout = QtWidgets.QHBoxLayout(self.centralwidget)
        self.verticalLayout = QtWidgets.QVBoxLayout()
        self.tableView = QtWidgets.QTableView(self.centralwidget)
        self.verticalLayout.addWidget(self.tableView)
        self.horizontalLayout.addLayout(self.verticalLayout)
        MainWindow.setCentralWidget(self.centralwidget)
        model=PandasModel.PandasModel(dataframe)
        self.tableView.resizeColumnsToContents()
        self.tableView.resizeRowsToContents()
        self.tableView.setModel(model)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

