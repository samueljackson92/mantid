try:
    from mantidplot import *
except ImportError:
    canMantidPlot = False

import ui_developer_workshop_window
from PyQt4 import QtGui
canMantidPlot = True


class DeveloperWorkshopGui(QtGui.QMainWindow, ui_developer_workshop_window.Ui_MainWindow):
    data_processor_table = None
    main_presenter = None

    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.setupUi(self)

    def setup_layout(self):
        return True

