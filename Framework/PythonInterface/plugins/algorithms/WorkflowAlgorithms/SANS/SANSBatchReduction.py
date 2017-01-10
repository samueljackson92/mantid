# pylint: disable=invalid-name

""" SANBatchReduction algorithm is the starting point for any new type reduction, event single reduction"""

from mantid.kernel import (Direction, PropertyManagerProperty, StringListValidator)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory,
                        PropertyMode, AnalysisDataService)

from sans.state.state_base import create_deserialized_sans_state_from_property_manager
from sans.algorithm_detail.batch_execution import (single_reduction_for_batch)
from sans.common.enums import (OutputMode)


class SANSBatchReduction(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\Reduction'

    def summary(self):
        return 'Performs a batch reduction of SANS data.'

    def PyInit(self):
        # ----------
        # INPUT
        # ----------
        self.declareProperty(PropertyManagerProperty('SANSStates'),
                             doc='This is a dictionary of SANSStates. Note that the key is irrelevant here. '
                                 'Each SANSState in the dictionary corresponds to a single reduction.')

        self.declareProperty("UseOptimizations", True, direction=Direction.Input,
                             doc="When enabled the ADS is being searched for already loaded and reduced workspaces. "
                                 "Depending on your concrete reduction, this could provide a significant"
                                 " performance boost")

        allowed_detectors = StringListValidator([OutputMode.to_string(OutputMode.PublishToADS),
                                                 OutputMode.to_string(OutputMode.SaveToFile),
                                                 OutputMode.to_string(OutputMode.Both)])
        self.declareProperty("OutputMode", "PublishToADS", validator=allowed_detectors, direction=Direction.Input,
                             doc="There are two output modes available./n"
                                 "PublishToADS: publishes the workspaces to the ADS. /n"
                                 "SaveToFile: Saves the workspaces to file.")

    def PyExec(self):
        # Read the states.
        states = self._get_states()

        # Check if optimizations are to be used
        use_optimizations = self.getProperty("UseOptimizations").value

        # Check how the output is to be handled
        output_mode = self._get_output_mode()

        # We now iterate over each state, load the data and perform the reduction
        for state in states:
            single_reduction_for_batch(state, use_optimizations, output_mode)

    def validateInputs(self):
        errors = dict()
        # Check that the input can be converted into the right state object
        try:
            states = self._get_states()
            for state in states:
                state.validate()
        except ValueError as err:
            errors.update({"SANSBatchReduction": str(err)})
        return errors

    def _get_output_mode(self):
        output_mode_as_string = self.getProperty("OutputMode").value
        return OutputMode.from_string(output_mode_as_string)

    def _get_states(self):
        # The property manager contains a collection of states
        outer_property_manager = self.getProperty("SANSStates").value
        keys = outer_property_manager.keys()
        sans_states = []
        for key in keys:
            inner_property_manager = outer_property_manager.getProperty(key).value
            state = create_deserialized_sans_state_from_property_manager(inner_property_manager)
            state.property_manager = inner_property_manager
            sans_states.append(state)
        return sans_states


# Register algorithm with Mantid
AlgorithmFactory.subscribe(SANSBatchReduction)
