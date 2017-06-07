try:
    from mantidplot import *
except ImportError:
    canMantidPlot = False

import ui_developer_workshop_reference_window
from PyQt4 import QtGui
canMantidPlot = True

from mantidqtpython import MantidQt


class DeveloperWorkshopReferenceGui(QtGui.QMainWindow, ui_developer_workshop_reference_window.Ui_MainWindow):
    data_processor_table = None
    main_presenter = None

    def __init__(self):
        super(QtGui.QMainWindow, self).__init__()
        self.setupUi(self)
        self.data_processor_table = None

    def setup_layout(self):
        # Define white list
        whitelist = MantidQt.MantidWidgets.DataProcessorWhiteList()
        whitelist.addElement('Runs', 'InputWorkspace', 'The run to reduce', True, '')
        whitelist.addElement('Scale 1', 'PropertyA', 'Scale Factor A', False, '')
        whitelist.addElement('Offset', 'PropertyB', 'Offset B', False, '')
        whitelist.addElement('Scale 2', 'PropertyC', 'Scale Factor C', True, 'scale_')
        whitelist.addElement('Scale 3', 'PropertyD', 'Scale Factor A', True, '')

        # Define processing algorithm
        alg = MantidQt.MantidWidgets.DataProcessorProcessingAlgorithm('DWProcessingAlgorithm', 'AlgPrefix_', '')

        # Create table
        self.data_processor_table = MantidQt.MantidWidgets.QDataProcessorWidget(whitelist, alg, self)
        self.data_processor_table.runAsPythonScript.connect(self._run_python_code)
        self.dw_layout.addWidget(self.data_processor_table)

        return True

    def _run_python_code(self, text):
        mantidplot.runPythonScript(text, True)