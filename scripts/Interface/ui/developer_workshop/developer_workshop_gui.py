try:
    from mantidplot import *
except ImportError:
    canMantidPlot = False

import ui_developer_workshop_window
from PyQt4 import QtGui
canMantidPlot = True

from mantidqtpython import MantidQt


class MainPresenter(MantidQt.MantidWidgets.DataProcessorMainPresenter):
    def __init__(self, gui):
        super(MantidQt.MantidWidgets.DataProcessorMainPresenter, self).__init__()
        self.gui = gui

    def getPreprocessingOptionsAsString(self):
        return ""

    def getProcessingOptions(self):
        property_e = self.gui.property_e
        option = "PropertyE={}".format(property_e) if property_e else ""
        return option

    def getPostprocessingOptions(self):
        return ""

    def notifyADSChanged(self, workspace_list):
        print("was called")



class DeveloperWorkshopGui(QtGui.QMainWindow, ui_developer_workshop_window.Ui_MainWindow):
    data_processor_table = None
    main_presenter = None

    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.setupUi(self)

    def setup_layout(self):
        return True

