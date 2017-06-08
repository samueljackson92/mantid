try:
    from mantidplot import *
except ImportError:
    canMantidPlot = False

import ui_developer_workshop_reference_window
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
        whitelist.addElement('Scale 3', 'PropertyD', 'Scale Factor D', True, '')

        # Define a pre-processing algorithm
        pre_process_map = MantidQt.MantidWidgets.DataProcessorPreprocessMap()
        pre_process_map.addElement('Runs', 'Plus', '', '')

        # Define a blacklist
        black_list = 'PropertyA,PropertyB,PropertyC,PropertyD,InputWorkspace,OutputWorkspace'

        # Define processing algorithm
        alg = MantidQt.MantidWidgets.DataProcessorProcessingAlgorithm('DWProcessingAlgorithm', 'AlgPrefix_', black_list)

        # Add post-processing algorithm
        post_alg = MantidQt.MantidWidgets.DataProcessorPostprocessingAlgorithm('GroupWorkspaces', 'Grouped_', '')

        # Create table
        self.data_processor_table = MantidQt.MantidWidgets.QDataProcessorWidget(whitelist, pre_process_map, alg, post_alg, self)

        # Add presenter
        self.main_presenter = MainPresenter(self)
        self.data_processor_table.accept(self.main_presenter)

        # Finalise setup of table
        self.data_processor_table.runAsPythonScript.connect(self._run_python_code)
        self.data_processor_table.setInstrumentList('LOQ', 'LOQ')
        self.dw_layout.addWidget(self.data_processor_table)

        return True

    def _run_python_code(self, text):
        mantidplot.runPythonScript(text, True)

    @property
    def property_e(self):
        value = str(self.global_line_edit.text())
        return value

