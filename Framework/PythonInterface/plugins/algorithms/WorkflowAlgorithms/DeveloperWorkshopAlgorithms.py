# pylint: disable=too-few-public-methods

""" SANSMaskWorkspace algorithm applies the masks of SANSMask state to a workspace."""

from __future__ import (absolute_import, division, print_function)
from mantid.kernel import (Direction)
from mantid.api import (DataProcessorAlgorithm, MatrixWorkspaceProperty, AlgorithmFactory, PropertyMode)


# ----------------------------------------------------------------------------------------------------------------------
# Pre-processing algorithm
# ----------------------------------------------------------------------------------------------------------------------
class DWPreProcessingAlgorithm(DataProcessorAlgorithm):
    def category(self):
        return 'Dummy\\DW'

    def summary(self):
        return 'This is a fake algorithm.'

    def PyInit(self):
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspace1", '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input),
                             doc='First input workspace')
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspace2", '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input),
                             doc='Second input workspace')

        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Output),
                             doc='Output workspace')

    def PyExec(self):
        first_workspace = self.getProperty("InputWorkspace1")
        second_workspace = self.getProperty("InputWorkspace2")

        # Add workspaces
        plus_alg = self.createChildAlgorithm("Plus")
        plus_alg.setProperty("LHSWorkspace", first_workspace)
        plus_alg.setProperty("RHSWorkspace", second_workspace)
        plus_alg.setProperty("OutputWorkspace", "out_ws")
        plus_alg.execute()
        output_workspace = plus_alg.getProperty("OutputWorkspace").value

        # Set output
        self.setProperty("OutputWorkspace", output_workspace)


# ----------------------------------------------------------------------------------------------------------------------
# Processing algorithm
# ----------------------------------------------------------------------------------------------------------------------
class DWProcessingAlgorithm(DataProcessorAlgorithm):
    def category(self):
        return 'Dummy\\DW'

    def summary(self):
        return 'This is a fake algorithm.'

    def PyInit(self):
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspace", '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Input),
                             doc='First input workspace')

        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", '',
                                                     optional=PropertyMode.Mandatory, direction=Direction.Output),
                             doc='Output workspace')

        self.declareProperty('PropertyA', 1., direction=Direction.Input, doc='Property A scales the input')
        self.declareProperty('PropertyB', 0., direction=Direction.Input, doc='Property B is added to the input')
        self.declareProperty('PropertyC', 1., direction=Direction.Input, doc='Property C scales the input')
        self.declareProperty('PropertyD', 1., direction=Direction.Input, doc='Property D scales the input')
        self.declareProperty('PropertyE', 1., direction=Direction.Input, doc='Property E scales the input')

    def PyExec(self):
        workspace = self.getProperty("InputWorkspace").value

        # Get multiplication properties
        prop_a = self.getProperty("PropertyA").value
        prop_c = self.getProperty("PropertyC").value
        prop_d = self.getProperty("PropertyD").value
        prop_e = self.getProperty("PropertyE").value
        total = prop_a * prop_c * prop_d * prop_e

        scale_alg = self.createChildAlgorithm("Scale")
        scale_alg.setProperty("InputWorkspace", workspace)
        scale_alg.setProperty("OutputWorkspace", "out_ws")
        scale_alg.setProperty("Operation", "Multiply")
        scale_alg.setProperty("Factor", total)
        scale_alg.execute()
        output_workspace = scale_alg.getProperty("OutputWorkspace").value

        # Get addition properties
        prop_b = self.getProperty("PropertyB").value
        scale_alg.setProperty("InputWorkspace", output_workspace)
        scale_alg.setProperty("Operation", "Add")
        scale_alg.setProperty("Factor", prop_b)
        scale_alg.execute()
        output_workspace = scale_alg.getProperty("OutputWorkspace").value

        # Set output
        self.setProperty("OutputWorkspace", output_workspace)


# Register algorithm with Mantid
AlgorithmFactory.subscribe(DWPreProcessingAlgorithm)
AlgorithmFactory.subscribe(DWProcessingAlgorithm)
