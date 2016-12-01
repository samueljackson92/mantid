# pylint: disable=too-few-public-methods

""" Converts a workspace from wavelengths to momentum transfer."""

from mantid.kernel import (Direction, StringListValidator, PropertyManagerProperty, CompositeValidator)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory, PropertyMode, Progress,
                        WorkspaceUnitValidator)

from SANS2.Common.SANSConstants import SANSConstants
from SANS2.Common.SANSType import (ReductionDimensionality, RangeStepType)
from SANS2.State.SANSStateBase import create_deserialized_sans_state_from_property_manager
from SANS2.Common.SANSFunctions import (create_unmanaged_algorithm, append_to_sans_file_tag)
from SANS2.ConvertToQ.QResolutionCalculator import QResolutionCalculatorFactory


class SANSConvertToQ(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\ConvertToQ'

    def summary(self):
        return 'Converts a SANS workspace to momentum transfer.'

    def PyInit(self):
        # ----------
        # INPUT
        # ----------
        # State
        self.declareProperty(PropertyManagerProperty('SANSState'),
                             doc='A property manager which fulfills the SANSState contract.')

        # Main workspace
        workspace_validator = CompositeValidator()
        workspace_validator.add(WorkspaceUnitValidator("Wavelength"))
        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.input_workspace, '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input,
                                                     validator=workspace_validator),
                             doc='The main input workspace.')

        # Adjustment workspaces
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspaceWavelengthAdjustment", '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input,
                                                     validator=workspace_validator),
                             doc='The workspace which contains only wavelength-specific adjustments, ie which affects '
                                 'all spectra equally.')
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspacePixelAdjustment", '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input,
                                                     validator=workspace_validator),
                             doc='The workspace which contains only pixel-specific adjustments, ie which affects '
                                 'all bins within a spectrum equally.')
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspaceWavelengthAndPixelAdjustment", '',
                                                     optional=PropertyMode.Optional, direction=Direction.Input,
                                                     validator=workspace_validator),
                             doc='The workspace which contains wavelength- and pixel-specific adjustments.')

        self.declareProperty('OutputParts', defaultValue=False,
                             direction=Direction.Input,
                             doc='Set to true to output two additional workspaces which will have the names '
                                 'OutputWorkspace_sumOfCounts OutputWorkspace_sumOfNormFactors. The division '
                                 'of _sumOfCounts and _sumOfNormFactors equals the workspace returned by the '
                                 'property OutputWorkspace (default is false).')

        # ----------
        # Output
        # ----------
        self.declareProperty(MatrixWorkspaceProperty(SANSConstants.output_workspace, '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Output),
                             doc="The reduced workspace")

    def PyExec(self):
        # Read the state
        state_property_manager = self.getProperty("SANSState").value
        state = create_deserialized_sans_state_from_property_manager(state_property_manager)

        # Perform either a 1D reduction or a 2D reduction
        convert_to_q = state.convert_to_q
        reduction_dimensionality = convert_to_q.reduction_dimensionality
        if reduction_dimensionality is ReductionDimensionality.OneDim:
            output_workspace, sum_of_counts_workspace, sum_of_norms_workspace = self._run_q_1d(state)
        else:
            output_workspace, sum_of_counts_workspace, sum_of_norms_workspace = self._run_q_2d(state)

        # Set the output
        append_to_sans_file_tag(output_workspace, "_convertq")
        self.setProperty(SANSConstants.output_workspace, output_workspace)
        if sum_of_counts_workspace and sum_of_norms_workspace:
            self._set_partial_workspaces(sum_of_counts_workspace, sum_of_norms_workspace)

    def _run_q_1d(self, state):
        data_workspace = self.getProperty(SANSConstants.input_workspace).value
        wavelength_adjustment_workspace = self.getProperty("InputWorkspaceWavelengthAdjustment").value
        pixel_adjustment_workspace = self.getProperty("InputWorkspacePixelAdjustment").value
        wavelength_and_pixel_adjustment_workspace = self.getProperty("InputWorkspaceWavelengthAndPixelAdjustment").value

        # Get QResolution
        convert_to_q = state.convert_to_q
        q_resolution_factory = QResolutionCalculatorFactory()
        q_resolution_calculator = q_resolution_factory.create_q_resolution_calculator(state)
        q_resolution_workspace = q_resolution_calculator.get_q_resolution_workspace(convert_to_q, data_workspace)

        output_parts = True

        # Extract relevant settings
        q_binning = self._get_q1d_binning(convert_to_q)
        use_gravity = convert_to_q.use_gravity
        gravity_extra_length = convert_to_q.gravity_extra_length
        radius_cutoff = convert_to_q.radius_cutoff / 1000.  # Q1D2 expects the radius cutoff to be in mm
        wavelength_cutoff = convert_to_q.wavelength_cutoff

        q1d_name = "Q1D"
        q1d_options = {"DetBankWorkspace": data_workspace,
                       SANSConstants.output_workspace: SANSConstants.dummy,
                       "OutputBinning": q_binning,
                       "AccountForGravity": use_gravity,
                       "RadiusCut": radius_cutoff,
                       "WaveCut": wavelength_cutoff,
                       "OutputParts": output_parts,
                       "ExtraLength": gravity_extra_length}
        if wavelength_adjustment_workspace:
            q1d_options.update({"WavelengthAdj": wavelength_adjustment_workspace})
        if pixel_adjustment_workspace:
            q1d_options.update({"PixelAdj": pixel_adjustment_workspace})
        if wavelength_and_pixel_adjustment_workspace:
            q1d_options.update({"WavePixelAdj": wavelength_and_pixel_adjustment_workspace})
        if q_resolution_workspace:
            q1d_options.update({"QResolution": q_resolution_workspace})

        q1d_alg = create_unmanaged_algorithm(q1d_name, **q1d_options)
        q1d_alg.execute()
        reduced_workspace = q1d_alg.getProperty(SANSConstants.output_workspace).value

        # Get the partial workspaces
        sum_of_counts_workspace, sum_of_norms_workspace = self._get_partial_output(output_parts, q1d_alg,
                                                                                   do_clean=False)

        return reduced_workspace, sum_of_counts_workspace, sum_of_norms_workspace

    def _run_q_2d(self, state):
        """
        This methods performs a 2D data reduction on our workspace.

        Note that it does not perform any q resolution calculation, nor any wavelength-and-pixel adjustment. The
        output workspace contains two numerical axes.
        @param state: a SANSState object
        @return: the reduced workspace, the sum of counts workspace, the sum of norms workspace or
                 the reduced workspace, None, None
        """
        data_workspace = self.getProperty(SANSConstants.input_workspace).value
        wavelength_adjustment_workspace = self.getProperty("InputWorkspaceWavelengthAdjustment").value
        pixel_adjustment_workspace = self.getProperty("InputWorkspacePixelAdjustment").value

        output_parts = True

        # Extract relevant settings
        convert_to_q = state.convert_to_q
        max_q_xy = convert_to_q.q_xy_max
        delta_q_prefix = -1 if convert_to_q.q_xy_step_type is RangeStepType.Log else 1
        delta_q = delta_q_prefix*convert_to_q.q_xy_step
        radius_cutoff = convert_to_q.radius_cutoff / 1000.  # Qxy expects the radius cutoff to be in mm
        wavelength_cutoff = convert_to_q.wavelength_cutoff
        use_gravity = convert_to_q.use_gravity
        gravity_extra_length = convert_to_q.gravity_extra_length

        qxy_name = "Qxy"
        qxy_options = {SANSConstants.input_workspace: data_workspace,
                       SANSConstants.output_workspace: SANSConstants.dummy,
                       "MaxQxy": max_q_xy,
                       "DeltaQ": delta_q,
                       "AccountForGravity": use_gravity,
                       "RadiusCut": radius_cutoff,
                       "WaveCut": wavelength_cutoff,
                       "OutputParts": output_parts,
                       "ExtraLength": gravity_extra_length}
        if wavelength_adjustment_workspace:
            qxy_options.update({"WavelengthAdj": wavelength_adjustment_workspace})
        if pixel_adjustment_workspace:
            qxy_options.update({"PixelAdj": pixel_adjustment_workspace})

        qxy_alg = create_unmanaged_algorithm(qxy_name, **qxy_options)
        qxy_alg.execute()

        reduced_workspace = qxy_alg.getProperty(SANSConstants.output_workspace).value
        reduced_workspace = self._replace_special_values(reduced_workspace)

        # Get the partial workspaces
        sum_of_counts_workspace, sum_of_norms_workspace = self._get_partial_output(output_parts, qxy_alg, do_clean=True)

        return reduced_workspace, sum_of_counts_workspace, sum_of_norms_workspace

    def _get_q1d_binning(self, convert_to_q):
        """
        Get the binning for the Q1D algorithm.

        The binning can be of a simple form with start, step, stop or of a complex form with start, step1, mid,
        step2, stop
        @param convert_to_q: a SANSStateConvertToQ object.
        @return: a binning string.
        """
        # Check if the binning is complex or simple binning
        # complex binning is start, step, mid, step2, stop
        # simple binning is start, step, stop
        is_complex_binning = convert_to_q.q_mid is not None and convert_to_q.q_step2 is not None and\
                             convert_to_q.q_step_type2 is not None

        start = convert_to_q.q_min
        stop = convert_to_q.q_max
        prefix = -1 if convert_to_q.q_step_type is RangeStepType.Log else 1
        step = convert_to_q.q_step
        step *= prefix
        if is_complex_binning:
            step2 = convert_to_q.q_step2
            prefix2 = -1 if convert_to_q.q_step_type2 is RangeStepType.Log else 1
            step2 *= prefix2
            mid = convert_to_q.q_mid
            binning = "{0},{1},{2},{3},{4}".format(start, step, mid, step2, stop)
        else:
            binning = "{0},{1},{2}".format(start, step, stop)
        return binning

    def _get_partial_output(self, output_parts, alg, do_clean=False):
        if output_parts:
            sum_of_counts_workspace = alg.getProperty("SumOfCounts").value
            sum_of_norms_workspace = alg.getProperty("sumOfNormFactors").value
            if do_clean:
                sum_of_counts_workspace = self._replace_special_values(sum_of_counts_workspace)
                sum_of_norms_workspace = self._replace_special_values(sum_of_norms_workspace)
        else:
            sum_of_counts_workspace = None
            sum_of_norms_workspace = None
        return sum_of_counts_workspace, sum_of_norms_workspace

    def _set_partial_workspaces(self, sum_of_counts_workspace, sum_of_norms_workspace):
        """
        Sets the partial output, ie the sum of the counts workspace and the sum of the normalization workspace
        @param sum_of_counts_workspace: the sum of the counts workspace
        @param sum_of_norms_workspace: the sum of the normalization workspace
        """
        self.declareProperty(MatrixWorkspaceProperty("SumOfCounts", '',
                                                     optional=PropertyMode.Optional, direction=Direction.Output),
                             doc="The sum of the counts workspace.")
        self.declareProperty(MatrixWorkspaceProperty("SumOfNormFactors", '',
                                                     optional=PropertyMode.Optional, direction=Direction.Output),
                             doc="The sum of the normalizations workspace.")

        output_name = self.getProperty(SANSConstants.output_workspace).name
        sum_of_counts_workspace_name = output_name + "_sumOfCounts"
        sum_of_norms_workspace_name = output_name + "_sumOfNormFactors"

        self.setPropertyValue("SumOfCounts", sum_of_counts_workspace_name)
        self.setPropertyValue("SumOfNormFactors", sum_of_norms_workspace_name)

        self.setProperty("SumOfCounts", sum_of_counts_workspace)
        self.setProperty("SumOfNormFactors", sum_of_norms_workspace)

    def _replace_special_values(self, workspace):
        replace_name = "ReplaceSpecialValues"
        replace_options = {SANSConstants.input_workspace: workspace,
                           SANSConstants.output_workspace: SANSConstants.dummy,
                           "NaNValue": 0.,
                           "InfinityValue": 0.}
        replace_alg = create_unmanaged_algorithm(replace_name, **replace_options)
        replace_alg.execute()
        return replace_alg.getProperty(SANSConstants.output_workspace).value

    def validateInputs(self):
        errors = dict()
        # Check that the input can be converted into the right state object
        state_property_manager = self.getProperty("SANSState").value
        try:
            state = create_deserialized_sans_state_from_property_manager(state_property_manager)
            state.property_manager = state_property_manager
            state.validate()
        except ValueError as err:
            errors.update({"SANSSConvertToQ": str(err)})
        return errors


# Register algorithm with Mantid
AlgorithmFactory.subscribe(SANSConvertToQ)
