# -*- coding: utf-8 -*-

# Form implementation generated from reading ui file '.\QTDesigner\MainWindow.ui'
#
# Created by: PyQt5 UI code generator 5.15.10
#
# WARNING: Any manual changes made to this file will be lost when pyuic5 is
# run again.  Do not edit this file unless you know what you are doing.


from PyQt5 import QtCore, QtGui, QtWidgets


class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        MainWindow.setWindowIcon(QtGui.QIcon("C:/Users/Duck/Codes/Udito/QTDesigner/CampariIcon.png"))

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(800, 600)
        MainWindow.setStyleSheet("background-color: #605678;")

        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")

        self.progressBar = QtWidgets.QProgressBar(self.centralwidget)
        self.progressBar.setGeometry(QtCore.QRect(70, 40, 71, 231))
        self.progressBar.setMinimum(-40)
        self.progressBar.setMaximum(-10)
        self.progressBar.setProperty("value", -24)
        self.progressBar.setTextVisible(False)
        self.progressBar.setOrientation(QtCore.Qt.Vertical)
        self.progressBar.setInvertedAppearance(False)
        self.progressBar.setTextDirection(QtWidgets.QProgressBar.TopToBottom)
        self.progressBar.setObjectName("progressBar")
        self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: #8ABFA3; }")

        self.label = QtWidgets.QLabel(self.centralwidget)
        self.label.setGeometry(QtCore.QRect(70, 290, 64, 23))  
        self.label.setStyleSheet("QLabel { background-color: #605678; color: #FFBF61;}") 
        #self.label.setAlignment(QtCore.Qt.AlignCenter)  # 중앙 정렬
        
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 800, 21))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "Udito"))

    def update_progress(self,value):
        valueForDisplay=round(value,2)
        valueForBar=int(valueForDisplay)

        self.progressBar.setValue(valueForBar)
        self.label.setText(f"{valueForDisplay}")
        # Change color based on value
        if valueForBar > -15: # red
            self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: #FF0000; }")
        elif valueForBar > -20: # yellow
            self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: #FFE6A5; }")
        else: # green
            self.progressBar.setStyleSheet("QProgressBar::chunk { background-color: #8ABFA3; }")


if __name__ == "__main__":
    import sys
    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
