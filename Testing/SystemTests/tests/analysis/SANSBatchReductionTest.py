# pylint: disable=too-many-public-methods, invalid-name, too-many-arguments

import unittest
import stresstesting

import mantid
from mantid.api import AnalysisDataService

from sans.user_file.user_file_state_director import UserFileStateDirectorISIS
from sans.state.data import get_data_builder
from sans.common.sans_type import SANSFacility, ISISReductionMode
from sans.common.constants import SANSConstants
from sans.common.general_functions import create_unmanaged_algorithm


# -----------------------------------------------
# Tests for the SANSBatchReduction algorithm
# -----------------------------------------------
class SANSBatchReductionTest(unittest.TestCase):

    def _run_batch_reduction(self, states, use_optimizations=False):
        batch_reduction_name = "SANSBatchReduction"
        batch_reduction_options = {"SANSStates": states,
                                   "UseOptimizations": use_optimizations,
                                   "OutputMode": "PublishToADS"}

        batch_reduction_alg = create_unmanaged_algorithm(batch_reduction_name, **batch_reduction_options)

        # Act
        batch_reduction_alg.execute()
        self.assertTrue(batch_reduction_alg.isExecuted())

    def _compare_workspace(self, workspace, reference_file_name):
        # Load the reference file
        load_name = "LoadNexusProcessed"
        load_options = {"Filename": reference_file_name,
                        SANSConstants.output_workspace: SANSConstants.dummy}
        load_alg = create_unmanaged_algorithm(load_name, **load_options)
        load_alg.execute()
        reference_workspace = load_alg.getProperty(SANSConstants.output_workspace).value

        # Compare reference file with the output_workspace
        # We need to disable the instrument comparison, it takes way too long
        # We need to disable the sample -- Not clear why yet
        # operation how many entries can be found in the sample logs
        compare_name = "CompareWorkspaces"
        compare_options = {"Workspace1": workspace,
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

    def test_that_batch_reduction_evaluates_LAB(self):
        # Arrange
        # Build the data information
        data_builder = get_data_builder(SANSFacility.ISIS)
        data_builder.set_sample_scatter("SANS2D00034484")
        data_builder.set_sample_transmission("SANS2D00034505")
        data_builder.set_sample_direct("SANS2D00034461")
        data_builder.set_can_scatter("SANS2D00034481")
        data_builder.set_can_transmission("SANS2D00034502")
        data_builder.set_can_direct("SANS2D00034461")

        data_builder.set_calibration("TUBE_SANS2D_BOTH_31681_25Sept15.nxs")

        data_info = data_builder.build()

        # Get the rest of the state from the user file
        user_file_director = UserFileStateDirectorISIS(data_info)
        user_file_director.set_user_file("USER_SANS2D_154E_2p4_4m_M3_Xpress_8mm_SampleChanger.txt")
        # Set the reduction mode to LAB
        user_file_director.set_reduction_builder_reduction_mode(ISISReductionMode.Lab)
        state = user_file_director.construct()

        # Act
        states = {"1": state.property_manager}
        self._run_batch_reduction(states, use_optimizations=False)

        workspace_name = "34484rear_1D1.75_16.5"
        output_workspace = AnalysisDataService.retrieve(workspace_name)

        # Evaluate it up to a defined point
        reference_file_name = "SANS2D_ws_D20_reference_LAB_1D.nxs"
        self._compare_workspace(output_workspace, reference_file_name)

        if AnalysisDataService.doesExist(workspace_name):
            AnalysisDataService.remove(workspace_name)


class SANSBatchReductionRunnerTest(stresstesting.MantidStressTest):
    def __init__(self):
        stresstesting.MantidStressTest.__init__(self)
        self._success = False

    def runTest(self):
        suite = unittest.TestSuite()
        suite.addTest(unittest.makeSuite(SANSBatchReductionTest, 'test'))
        runner = unittest.TextTestRunner()
        res = runner.run(suite)
        if res.wasSuccessful():
            self._success = True

    def requiredMemoryMB(self):
        return 2000

    def validate(self):
        return self._success


if __name__ == '__main__':
    unittest.main()
