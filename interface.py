from PyQt6 import QtWidgets, QtGui
from PyQt6.QtCore import Qt
from dialog import Ui_Dialog


class SettingsDialog(QtWidgets.QDialog):
    def __init__(self):
        super(SettingsDialog, self).__init__()
        self.ui=Ui_Dialog()
        self.ui.setupUi(self)
        self.ui.languageBox.addItem('penis', '1')
        print(self.ui.languageBox.currentData())


if __name__=='__main__':
    app = QtWidgets.QApplication([])
    app.setQuitOnLastWindowClosed(False)
    icon = QtGui.QIcon("Icon.png")
    window = SettingsDialog()
    window.show()
    app.exec()
