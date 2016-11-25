# pylint: disable=invalid-name

""" SANSReductionCore algorithm runs the sequence of reduction steps which are necessary to reduce a data set."""

from mantid.kernel import (Direction, PropertyManagerProperty, StringListValidator)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory, PropertyMode,
                        IEventWorkspace)

from SANS2.Common.SANSConstants import SANSConstants
from SANS2.State.SANSStateBase import create_deserialized_sans_state_from_property_manager
from SANS2.Common.SANSFunctions import create_unmanaged_algorithm
from SANS2.Common.SANSType import (DetectorType, convert_detector_type_to_string,
                                           convert_reduction_data_type_to_string, DataType)


class SANSReductionCore(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\Reduction'

    def summary(self):
        return ' Runs the the core reduction elements.'

    def PyInit(self):
        # ----------
        # INPUT
        # ----------
        self.declareProperty(PropertyManagerProperty('SANSState'),
                             doc='A property manager which fulfills the SANSState contract.')

        # WORKSPACES
        # Scatter Workspaces
        self.declareProperty(MatrixWorkspaceProperty('ScatterWorkspace', '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input),
                             doc='The scatter workspace. This workspace does not contain monitors.')
        self.declareProperty(MatrixWorkspaceProperty('ScatterMonitorWorkspace', '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input),
                             doc='The scatter monitor workspace. This workspace only contains monitors.')

        # Transmission Workspace
        self.declareProperty(MatrixWorkspaceProperty('TransmissionWorkspace', '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input),
                             doc='The transmission workspace.')

        # Direct Workspace
        self.declareProperty(MatrixWorkspaceProperty('DirectWorkspace', '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input),
                             doc='The direct workspace.')

        self.setPropertyGroup("ScatterWorkspace", 'Data')
        self.setPropertyGroup("ScatterMonitorWorkspace", 'Data')
        self.setPropertyGroup("TransmissionWorkspace", 'Data')
        self.setPropertyGroup("DirectWorkspace", 'Data')

        self.declareProperty("UseOptimizations", True, direction=Direction.Input,
                             doc="When enabled the ADS is being searched for already loaded and reduced workspaces. "
                                 "Depending on your concrete reduction, this could provide a significant"
                                 " performance boost")

        # The component
        allowed_detectors = StringListValidator([convert_detector_type_to_string(DetectorType.Lab),
                                                 convert_detector_type_to_string(DetectorType.Hab)])
        self.declareProperty("Component", convert_detector_type_to_string(DetectorType.Lab),
                             validator=allowed_detectors, direction=Direction.Input,
                             doc="The component of the instrument which is to be reduced.")

        # The data type
        allowed_data = StringListValidator([convert_reduction_data_type_to_string(DataType.Sample),
                                            convert_reduction_data_type_to_string(DataType.Can)])
        self.declareProperty("DataType", convert_reduction_data_type_to_string(DataType.Sample),
                             validator=allowed_data, direction=Direction.Input,
                             doc="The component of the instrument which is to be reduced.")

        # ----------
        # OUTPUT
        # ----------
        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.output_workspace, '', direction=Direction.Output),
                             doc='The output workspace.')

        self.declareProperty(MatrixWorkspaceProperty('SumOfCounts', '', optional=PropertyMode.Optional,
                                                     direction=Direction.Output),
                             doc='The sum of the counts of the output workspace.')

        self.declareProperty(MatrixWorkspaceProperty('SumOfNormFactors', '', optional=PropertyMode.Optional,
                                                     direction=Direction.Output),
                             doc='The sum of the counts of the output workspace.')

    def PyExec(self):
        # Get the input
        state = self._get_state()
        component_as_string = self.getProperty("Component").value

        # --------------------------------------------------------------------------------------------------------------
        # 1. Crop workspace by detector name
        #    This will create a reduced copy of the original workspace with only those spectra which are relevant
        #    for this particular reduction.
        # --------------------------------------------------------------------------------------------------------------
        workspace = self._get_cropped_workspace(component_as_string)

        # --------------------------------------------------------------------------------------------------------------
        # 2. Perform dark run subtraction
        #    This will subtract a dark background from the scatter workspace. Note that dark background subtraction
        #    will also affect the transmission calculation later on.
        # --------------------------------------------------------------------------------------------------------------

        # --------------------------------------------------------------------------------------------------------------
        # 3. Create event slice
        #    If we are dealing with an event workspace as input, this will cut out a time-based (use-defined) slice.
        #    In case of a histogram workspace, nothing happens.
        # --------------------------------------------------------------------------------------------------------------
        monitor_workspace = self._get_monitor_workspace()
        workspace, monitor_workspace, slice_event_factor = self._slice(state, workspace, monitor_workspace)

        # ------------------------------------------------------------
        # 4. Move the workspace into the correct position
        #    The detectors in the workspaces are set such that the beam centre is at (0,0). The position is
        #    a user-specified value which can be obtained with the help of the beam centre finder.
        # ------------------------------------------------------------
        workspace = self._move(state, workspace, component_as_string)

        # **************************************************
        # ONLY FOR DEVELOPMENT AND TESTING -- BEGIN
        # **************************************************
        # We convert the workspace here to a histogram workspace, since we cannot otherwise compare the results between
        # the old and the new reduction workspace in a meaningful manner. The old one is histogram and the new one
        # is event.
        rebin_name = "Rebin"
        rebin_option = {SANSConstants.input_workspace: workspace,
                        SANSConstants.output_workspace: SANSConstants.dummy,
                        "Params": "8000,-0.025,100000",
                        "PreserveEvents": False}

        rebin_alg = create_unmanaged_algorithm(rebin_name, **rebin_option)
        rebin_alg.execute()
        workspace = rebin_alg.getProperty(SANSConstants.output_workspace).value
        # **************************************************
        # ONLY FOR DEVELOPMENT AND TESTING -- END
        # **************************************************

        # --------------------------------------------------------------------------------------------------------------
        # 5. Apply masking (pixel masking and time masking)
        # --------------------------------------------------------------------------------------------------------------
        workspace = self._mask(state, workspace, component_as_string)

        # --------------------------------------------------------------------------------------------------------------
        # 6. Convert to Wavelength
        # --------------------------------------------------------------------------------------------------------------
        workspace = self._convert_to_wavelength(state, workspace)

        # --------------------------------------------------------------------------------------------------------------
        # 7. Multiply by volume and absolute scale
        # --------------------------------------------------------------------------------------------------------------
        data_type_as_string = self.getProperty("DataType").value
        workspace = self._scale(state, workspace, data_type_as_string)

        # --------------------------------------------------------------------------------------------------------------
        # 8. Create adjustment workspaces, those are
        #     1. pixel-based adjustments
        #     2. wavelength-based adjustments
        #     3. pixel-and-wavelength-based adjustments
        # Note that steps 4 to 7 could run in parallel if we don't use wide angle correction. If we do then the
        # creation of the adjustment workspaces requires the sample workspace itself and we have to run it sequentially.
        # We could consider to have a serial and a parallel strategy here, depending on the wide angle correction
        # settings. On the other hand it is not clear that this would be an advantage with the GIL.
        # --------------------------------------------------------------------------------------------------------------
        wavelength_adjustment_workspace, pixel_adjustment_workspace, wavelength_and_pixel_adjustment_workspace =\
            self._adjustment(state, workspace, monitor_workspace, component_as_string, data_type_as_string)

        # ------------------------------------------------------------
        # 9. Convert event workspaces to histogram workspaces
        # ------------------------------------------------------------
        workspace = self._convert_to_histogram(workspace)

        # ------------------------------------------------------------
        # 10. Convert to Q
        # ------------------------------------------------------------
        workspace, sum_of_counts, sum_of_norms = self._convert_to_q(state,
                                                                    workspace,
                                                                    wavelength_adjustment_workspace,
                                                                    pixel_adjustment_workspace,
                                                                    wavelength_and_pixel_adjustment_workspace)

        # ------------------------------------------------------------
        # Populate the output
        self.setProperty(SANSConstants.output_workspace, workspace)
        # ------------------------------------------------------------


        # ------------------------------------------------------------
        # Diagnostic output
        # ------------------------------------------------------------
        # We abuse output fields for testing at this point
        if sum_of_counts:
            self.setProperty("SumOfCounts", sum_of_counts)
        if sum_of_norms:
            self.setProperty("SumOfNormFactors", sum_of_norms)

        # TODO: Publish temporary workspaces if required
        # This includes partial workspaces of Q1D and unfitted transmission data

    def _get_cropped_workspace(self, component):
        scatter_workspace = self.getProperty("ScatterWorkspace").value
        crop_name = "SANSCrop"
        crop_options = {SANSConstants.input_workspace: scatter_workspace,
                        SANSConstants.output_workspace: SANSConstants.dummy,
                        "Component": component}
        crop_alg = create_unmanaged_algorithm(crop_name, **crop_options)
        crop_alg.execute()
        return crop_alg.getProperty(SANSConstants.output_workspace).value

    def _slice(self, state, workspace, monitor_workspace):
        state_serialized = state.property_manager
        slice_name = "SANSSliceEvent"
        slice_options = {"SANSState": state_serialized,
                         SANSConstants.input_workspace: workspace,
                         "InputWorkspaceMonitor": monitor_workspace,
                         SANSConstants.output_workspace: SANSConstants.dummy,
                         "OutputWorkspaceMonitor": "dummy2"}
        slice_alg = create_unmanaged_algorithm(slice_name, **slice_options)
        slice_alg.execute()

        workspace = slice_alg.getProperty(SANSConstants.output_workspace).value
        monitor_workspace = slice_alg.getProperty("OutputWorkspaceMonitor").value
        slice_event_factor = slice_alg.getProperty("SliceEventFactor").value
        return workspace, monitor_workspace, slice_event_factor

    def _move(self, state, workspace, component):
        # First we set the workspace to zero, since it might have been moved around by the user in the ADS
        # Second we use the initial move to bring the workspace into the correct position
        state_serialized = state.property_manager
        move_name = "SANSMove"
        move_options = {"SANSState": state_serialized,
                        SANSConstants.workspace: workspace,
                        "MoveType": "SetToZero",
                        "Component": ""}
        move_alg = create_unmanaged_algorithm(move_name, **move_options)
        move_alg.execute()
        workspace = move_alg.getProperty(SANSConstants.workspace).value

        # Do the initial move
        move_alg.setProperty("MoveType", "InitialMove")
        move_alg.setProperty("Component", component)
        move_alg.setProperty(SANSConstants.workspace, workspace)
        move_alg.execute()
        return move_alg.getProperty(SANSConstants.workspace).value

    def _mask(self, state, workspace, component):
        state_serialized = state.property_manager
        mask_name = "SANSMaskWorkspace"
        mask_options = {"SANSState": state_serialized,
                        SANSConstants.workspace: workspace,
                        "Component": component}
        mask_alg = create_unmanaged_algorithm(mask_name, **mask_options)
        mask_alg.execute()
        return mask_alg.getProperty(SANSConstants.workspace).value

    def _convert_to_wavelength(self, state, workspace):
        state_serialized = state.property_manager
        wavelength_name = "SANSConvertToWavelength"
        wavelength_options = {"SANSState": state_serialized,
                              SANSConstants.input_workspace: workspace,
                              SANSConstants.output_workspace: SANSConstants.dummy}
        wavelength_alg = create_unmanaged_algorithm(wavelength_name, **wavelength_options)
        wavelength_alg.execute()
        return wavelength_alg.getProperty(SANSConstants.output_workspace).value

    def _scale(self, state, workspace, data_type):
        state_serialized = state.property_manager
        scale_name = "SANSScale"
        scale_options = {"SANSState": state_serialized,
                         SANSConstants.input_workspace: workspace,
                         SANSConstants.output_workspace: SANSConstants.dummy,
                         "DataType": data_type}
        scale_alg = create_unmanaged_algorithm(scale_name, **scale_options)
        scale_alg.execute()
        return scale_alg.getProperty(SANSConstants.output_workspace).value

    def _adjustment(self, state, workspace, monitor_workspace, component, data_type):
        transmission_workspace = self._get_transmission_workspace()
        direct_workspace = self._get_direct_workspace()

        state_serialized = state.property_manager
        adjustment_name = "SANSCreateAdjustmentWorkspaces"
        adjustment_options = {"SANSState": state_serialized,
                              "Component": component,
                              "DataType": data_type,
                              "MonitorWorkspace": monitor_workspace,
                              "SampleData": workspace,
                              "OutputWorkspaceWavelengthAdjustment": SANSConstants.dummy,
                              "OutputWorkspacePixelAdjustment": SANSConstants.dummy,
                              "OutputWorkspaceWavelengthAndPixelAdjustment": SANSConstants.dummy}
        if transmission_workspace:
            adjustment_options.update({"TransmissionWorkspace": transmission_workspace})
        if direct_workspace:
            adjustment_options.update({"DirectWorkspace": direct_workspace})
        adjustment_alg = create_unmanaged_algorithm(adjustment_name, **adjustment_options)
        adjustment_alg.execute()

        wavelength_adjustment = adjustment_alg.getProperty("OutputWorkspaceWavelengthAdjustment").value
        pixel_adjustment = adjustment_alg.getProperty("OutputWorkspacePixelAdjustment").value
        wavelength_and_pixel_adjustment = adjustment_alg.getProperty(
                                           "OutputWorkspaceWavelengthAndPixelAdjustment").value
        return wavelength_adjustment, pixel_adjustment, wavelength_and_pixel_adjustment

    def _convert_to_histogram(self, workspace):
        if isinstance(workspace, IEventWorkspace):
            convert_name = "RebinToWorkspace"
            convert_options = {"WorkspaceToRebin": workspace,
                               "WorkspaceToMatch": workspace,
                               SANSConstants.output_workspace: SANSConstants.output_workspace,
                               "PreserveEvents": False}
            convert_alg = create_unmanaged_algorithm(convert_name, **convert_options)
            convert_alg.execute()
            workspace = convert_alg.getProperty(SANSConstants.output_workspace).value
        return workspace

    def _convert_to_q(self, state, workspace, wavelength_adjustment_workspace, pixel_adjustment_workspace,
                      wavelength_and_pixel_adjustment_workspace):
        """
        A conversion to momentum transfer is performed in this step.

        The conversion can be either to the modulus of Q in which case the output is a 1D workspace, or it can
        be a 2D reduction where the y axis is Qy, ie it is a numeric axis.
        @param state: a SANSState object
        @param workspace: the workspace to convert to momentum transfer.
        @param wavelength_adjustment_workspace: the wavelength adjustment workspace.
        @param pixel_adjustment_workspace: the pixel adjustment workspace.
        @param wavelength_and_pixel_adjustment_workspace: the wavelength and pixel adjustment workspace.
        @return: a reduced workspace
        """
        state_serialized = state.property_manager
        convert_name = "SANSConvertToQ"
        convert_options = {SANSConstants.input_workspace: workspace,
                           SANSConstants.output_workspace: SANSConstants.dummy,
                           "SANSState": state_serialized,
                           "OutputParts": True}
        if wavelength_adjustment_workspace:
            convert_options.update({"InputWorkspaceWavelengthAdjustment": wavelength_adjustment_workspace})
        if pixel_adjustment_workspace:
            convert_options.update({"InputWorkspacePixelAdjustment": pixel_adjustment_workspace})
        if wavelength_and_pixel_adjustment_workspace:
            convert_options.update({"InputWorkspaceWavelengthAndPixelAdjustment":
                                        wavelength_and_pixel_adjustment_workspace})
        convert_alg = create_unmanaged_algorithm(convert_name, **convert_options)
        convert_alg.execute()
        data_workspace = convert_alg.getProperty(SANSConstants.output_workspace).value
        sum_of_counts = convert_alg.getProperty("SumOfCounts").value
        sum_of_norms = convert_alg.getProperty("SumOfNormFactors").value
        return data_workspace, sum_of_counts, sum_of_norms

    def validateInputs(self):
        errors = dict()
        # Check that the input can be converted into the right state object
        try:
            state = self._get_state()
            state.validate()
        except ValueError as err:
            errors.update({"SANSSingleReduction": str(err)})
        return errors

    def _get_state(self):
        state_property_manager = self.getProperty("SANSState").value
        state = create_deserialized_sans_state_from_property_manager(state_property_manager)
        state.property_manager = state_property_manager
        return state

    def _get_transmission_workspace(self):
        transmission_workspace = self.getProperty("TransmissionWorkspace").value
        return self._get_cloned_workspace(transmission_workspace) if transmission_workspace else None

    def _get_direct_workspace(self):
        direct_workspace = self.getProperty("DirectWorkspace").value
        return self._get_cloned_workspace(direct_workspace) if direct_workspace else None

    def _get_monitor_workspace(self):
        monitor_workspace = self.getProperty("ScatterMonitorWorkspace").value
        return self._get_cloned_workspace(monitor_workspace)

    def _get_cloned_workspace(self, workspace):
        clone_name = "CloneWorkspace"
        clone_options = {SANSConstants.input_workspace: workspace,
                         SANSConstants.output_workspace: SANSConstants.dummy}
        clone_alg = create_unmanaged_algorithm(clone_name, **clone_options)
        clone_alg.execute()
        return clone_alg.getProperty(SANSConstants.output_workspace).value

# Register algorithm with Mantid
AlgorithmFactory.subscribe(SANSReductionCore)
