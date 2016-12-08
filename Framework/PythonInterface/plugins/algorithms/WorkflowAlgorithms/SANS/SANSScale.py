# pylint: disable=too-few-public-methods

""" Multiplies a SANS workspace by an absolute scale and divides it by the sample volume. """

from mantid.kernel import (Direction, PropertyManagerProperty, StringListValidator,
                           FloatArrayProperty)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory, PropertyMode, Progress)

from sans.state.state_base import create_deserialized_sans_state_from_property_manager
from sans.common.constants import SANSConstants
from sans.algorithm_detail.scale_helpers import (DivideByVolumeFactory, MultiplyByAbsoluteScaleFactory)
from sans.common.sans_type import (convert_reduction_data_type_to_string, convert_string_to_reduction_data_type,
                                   DataType)
from sans.common.general_functions import (append_to_sans_file_tag)


class SANSScale(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\Scale'

    def summary(self):
        return 'Multiplies a SANS workspace by an absolute scale and divides it by the sample volume.'

    def PyInit(self):
        # State
        self.declareProperty(PropertyManagerProperty('SANSState'),
                             doc='A property manager which fulfills the SANSState contract.')

        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.input_workspace, '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input),
                             doc='The input workspace')

        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.output_workspace, '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Output),
                             doc='The scaled output workspace')

        # The data type
        allowed_data = StringListValidator([convert_reduction_data_type_to_string(DataType.Sample),
                                            convert_reduction_data_type_to_string(DataType.Can)])
        self.declareProperty("DataType", convert_reduction_data_type_to_string(DataType.Sample),
                             validator=allowed_data, direction=Direction.Input,
                             doc="The component of the instrument which is to be reduced.")

    def PyExec(self):
        state_property_manager = self.getProperty("SANSState").value
        state = create_deserialized_sans_state_from_property_manager(state_property_manager)

        # Get the correct SANS move strategy from the SANSMaskFactory
        workspace = self.getProperty(SANSConstants.input_workspace).value

        progress = Progress(self, start=0.0, end=1.0, nreports=3)

        # Divide by the sample volume
        progress.report("Dividing by the sample volume.")
        data_type_as_string = self.getProperty("DataType").value
        data_type = convert_string_to_reduction_data_type(data_type_as_string)

        workspace = self._divide_by_volume(workspace, state, data_type)

        # Multiply by the absolute scale
        progress.report("Applying absolute scale.")
        workspace = self._multiply_by_absolute_scale(workspace, state)

        append_to_sans_file_tag(workspace, "_scale")
        self.setProperty(SANSConstants.output_workspace, workspace)
        progress.report("Finished applying absolute scale")

    def _divide_by_volume(self, workspace, state, data_type):
        divide_factory = DivideByVolumeFactory()
        divider = divide_factory.create_divide_by_volume(state, data_type)
        scale_info = state.scale
        return divider.divide_by_volume(workspace, scale_info)

    def _multiply_by_absolute_scale(self, workspace, state):
        multiply_factory = MultiplyByAbsoluteScaleFactory()
        multiplier = multiply_factory.create_multiply_by_absolute(state)
        scale_info = state.scale
        return multiplier.multiply_by_absolute_scale(workspace, scale_info)


# Register algorithm with Mantid
AlgorithmFactory.subscribe(SANSScale)
