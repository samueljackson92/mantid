# pylint: disable=too-few-public-methods

""" SANSConvertToWavelength converts to wavelength units """

from mantid.kernel import (Direction, StringListValidator, Property, PropertyManagerProperty)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory, PropertyMode)
from SANS2.Common.SANSConstants import SANSConstants
from SANS2.Common.SANSFunctions import (create_unmanaged_algorithm, append_to_sans_file_tag)
from SANS2.Common.SANSType import (convert_rebin_type_to_string, convert_range_step_type_to_string)
from SANS2.State.SANSStateBase import create_deserialized_sans_state_from_property_manager


class SANSConvertToWavelength(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\Wavelength'

    def summary(self):
        return 'Convert the units of a SANS workspace to wavelength'

    def PyInit(self):
        # State
        self.declareProperty(PropertyManagerProperty('SANSState'),
                             doc='A property manager which fulfills the SANSState contract.')

        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.input_workspace, '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input),
                             doc='The workspace which is to be converted to wavelength')

        self.declareProperty(MatrixWorkspaceProperty('OutputWorkspace', '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Output),
                             doc='The output workspace.')

    def PyExec(self):
        # State
        state_property_manager = self.getProperty("SANSState").value
        state = create_deserialized_sans_state_from_property_manager(state_property_manager)
        wavelength_state = state.wavelength

        # Input workspace
        workspace = self.getProperty(SANSConstants.input_workspace).value

        wavelength_name = "ConvertToWavelength"
        wavelength_options = {SANSConstants.input_workspace: workspace,
                              SANSConstants.output_workspace: SANSConstants.dummy,
                              "WavelengthLow": wavelength_state.wavelength_low,
                              "WavelengthHigh": wavelength_state.wavelength_high,
                              "WavelengthStep": wavelength_state.wavelength_step,
                              "WavelengthStepType": convert_range_step_type_to_string(
                                  wavelength_state.wavelength_step_type),
                              "RebinMode": convert_rebin_type_to_string(wavelength_state.rebin_type)}
        wavelength_alg = create_unmanaged_algorithm(wavelength_name, **wavelength_options)
        wavelength_alg.execute()
        converted_workspace = wavelength_alg.getProperty(SANSConstants.output_workspace).value
        self.setProperty(SANSConstants.output_workspace, converted_workspace)

    def validateInputs(self):
        errors = dict()
        # Check that the input can be converted into the right state object
        state_property_manager = self.getProperty("SANSState").value
        try:
            state = create_deserialized_sans_state_from_property_manager(state_property_manager)
            state.property_manager = state_property_manager
            state.validate()
        except ValueError as err:
            errors.update({"SANSSMove": str(err)})
        return errors


# Register algorithm with Mantid
AlgorithmFactory.subscribe(SANSConvertToWavelength)
