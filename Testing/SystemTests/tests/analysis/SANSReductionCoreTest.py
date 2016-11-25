# pylint: disable=too-many-public-methods, invalid-name, too-many-arguments

import unittest
import os
import stresstesting

import mantid
from mantid.api import AlgorithmManager

from SANS2.State.StateBuilder.SANSStateDataBuilder import get_data_builder
from SANS2.Common.SANSType import (DetectorType, DetectorType, convert_detector_type_to_string, DataType,
                                           convert_reduction_data_type_to_string, SANSFacility)
from SANS2.UserFile.UserFileStateDirector import UserFileStateDirectorISIS
from SANS2.Common.SANSConstants import SANSConstants
from SANS2.Common.SANSFunctions import create_unmanaged_algorithm


# -----------------------------------------------
# Tests for the SANSReductionCore algorithm
# -----------------------------------------------
class SANSReductionCoreTest(unittest.TestCase):
    def _load_workspace(self, state):
        load_alg = AlgorithmManager.createUnmanaged("SANSLoad")
        load_alg.setChild(True)
        load_alg.initialize()

        state_dict = state.property_manager
        load_alg.setProperty("SANSState", state_dict)
        load_alg.setProperty("PublishToCache", False)
        load_alg.setProperty("UseCached", False)
        load_alg.setProperty("MoveWorkspace", False)
        load_alg.setProperty("SampleScatterWorkspace", "dummy")
        load_alg.setProperty("SampleScatterMonitorWorkspace", "dummy")
        load_alg.setProperty("SampleTransmissionWorkspace", "dummy")
        load_alg.setProperty("SampleDirectWorkspace", "dummy")

        # Act
        load_alg.execute()
        self.assertTrue(load_alg.isExecuted())
        sample_scatter = load_alg.getProperty("SampleScatterWorkspace").value
        sample_scatter_monitor_workspace = load_alg.getProperty("SampleScatterMonitorWorkspace").value
        transmission_workspace = load_alg.getProperty("SampleTransmissionWorkspace").value
        direct_workspace = load_alg.getProperty("SampleDirectWorkspace").value
        return sample_scatter, sample_scatter_monitor_workspace, transmission_workspace, direct_workspace

    def _run_reduction_core(self, state, workspace, monitor, transmission=None, direct=None,
                            detector_type=DetectorType.Lab, component=DataType.Sample):
        reduction_core_alg = AlgorithmManager.createUnmanaged("SANSReductionCore")
        reduction_core_alg.setChild(True)
        reduction_core_alg.initialize()

        state_dict = state.property_manager
        reduction_core_alg.setProperty("SANSState", state_dict)
        reduction_core_alg.setProperty("ScatterWorkspace", workspace)
        reduction_core_alg.setProperty("ScatterMonitorWorkspace", monitor)

        if transmission:
            reduction_core_alg.setProperty("TransmissionWorkspace", transmission)

        if direct:
            reduction_core_alg.setProperty("DirectWorkspace", direct)

        reduction_core_alg.setProperty("Component", convert_detector_type_to_string(detector_type))
        reduction_core_alg.setProperty("DataType", convert_reduction_data_type_to_string(component))

        reduction_core_alg.setProperty(SANSConstants.output_workspace, SANSConstants.dummy)

        # Act
        reduction_core_alg.execute()
        self.assertTrue(reduction_core_alg.isExecuted())
        return reduction_core_alg

    def _compare_workspace(self, workspace, reference_file_name):
        # Load the reference file
        load_name = "LoadNexusProcessed"
        load_options = {"Filename": reference_file_name,
                        SANSConstants.output_workspace: SANSConstants.dummy}
        load_alg = create_unmanaged_algorithm(load_name, **load_options)
        load_alg.execute()
        reference_workspace = load_alg.getProperty(SANSConstants.output_workspace).value

        # Save the workspace out and reload it again. This makes equalizes it with the reference workspace
        f_name = os.path.join(mantid.config.getString('defaultsave.directory'),
                              'SANS_temp_single_core_reduction_testout.nxs')

        save_name = "SaveNexus"
        save_options = {"Filename": f_name,
                        "InputWorkspace": workspace}
        save_alg = create_unmanaged_algorithm(save_name, **save_options)
        save_alg.execute()
        load_alg.setProperty("Filename", f_name)
        load_alg.setProperty(SANSConstants.output_workspace, SANSConstants.dummy)
        load_alg.execute()

        ws = load_alg.getProperty(SANSConstants.output_workspace).value

        from mantid.api import AnalysisDataService
        from mantid.simpleapi import SaveNexusProcessed
        AnalysisDataService.addOrReplace("test", ws)
        AnalysisDataService.addOrReplace("test2", reference_workspace)
        SaveNexusProcessed(Filename="C:/Users/pica/Desktop/new_data.nxs", InputWorkspace="test")
        SaveNexusProcessed(Filename="C:/Users/pica/Desktop/old_data.nxs", InputWorkspace="test2")

        # Compare reference file with the output_workspace
        # We need to disable the instrument comparison, it takes way too long
        # We need to disable the sample -- Not clear why yet
        # operation how many entries can be found in the sample logs
        compare_name = "CompareWorkspaces"
        compare_options = {"Workspace1": ws,
                           "Workspace2": reference_workspace,
                           "Tolerance": 1e-6,
                           "CheckInstrument": False,
                           "CheckSample": False,
                           "ToleranceRelErr": True,
                           "CheckAllData": True,
                           "CheckMasking": True,
                           "CheckType": True,
                           "CheckAxes": True,
                           "CheckSpectraMap": True}
        compare_alg = create_unmanaged_algorithm(compare_name, **compare_options)
        compare_alg.setChild(False)
        compare_alg.execute()
        result = compare_alg.getProperty("Result").value
        self.assertTrue(result)

        # Remove file
        if os.path.exists(f_name):
            os.remove(f_name)

    def test_that_reduction_core_evaluates_LAB(self):
        # Arrange
        # Build the data information
        data_builder = get_data_builder(SANSFacility.ISIS)
        data_builder.set_sample_scatter("SANS2D00034484")
        data_builder.set_sample_transmission("SANS2D00034505")
        data_builder.set_sample_direct("SANS2D00034461")
        data_builder.set_calibration("TUBE_SANS2D_BOTH_31681_25Sept15.nxs")
        data_info = data_builder.build()

        # Get the rest of the state from the user file
        user_file_director = UserFileStateDirectorISIS(data_info)
        user_file_director.set_user_file("USER_SANS2D_154E_2p4_4m_M3_Xpress_8mm_SampleChanger.txt")
        state = user_file_director.construct()

        # Load the sample workspaces
        workspace, workspace_monitor, transmission_workspace, direct_workspace = self._load_workspace(state)

        # Act
        reduction_core_alg = self._run_reduction_core(state, workspace, workspace_monitor,
                                                      transmission_workspace, direct_workspace)
        output_workspace = reduction_core_alg.getProperty(SANSConstants.output_workspace).value
        wavelength_adjustment_workspace = reduction_core_alg.getProperty("SumOfCounts").value
        wavelength_and_pixel_adjustment_workspace = reduction_core_alg.getProperty("SumOfNormFactors").value

        # Evaluate it up to a defined point
        reference_file_name = "SANS2D_ws_D20_reference.nxs"
        self._compare_workspace(output_workspace, reference_file_name)
        self.assertTrue(wavelength_and_pixel_adjustment_workspace is None)
        reference_file_name_wavelength_adjustment = "SANS2D_ws_D20_wavelength_adjustment_reference.nxs"
        self._compare_workspace(wavelength_adjustment_workspace, reference_file_name_wavelength_adjustment)


class SANSReductionCoreRunnerTest(stresstesting.MantidStressTest):
    def __init__(self):
        stresstesting.MantidStressTest.__init__(self)
        self._success = False

    def runTest(self):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SANSReductionCoreTest, 'test'))
        runner = unittest.TextTestRunner()
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True

    def requiredMemoryMB(self):
        return 1000

    def validate(self):
        return self._success


if __name__ == '__main__':
    unittest.main()
