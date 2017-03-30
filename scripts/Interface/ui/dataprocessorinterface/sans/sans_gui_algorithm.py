# pylint: disable=too-few-public-methods

""" Crops a selected component from a SANS."""

from __future__ import (absolute_import, division, print_function)
from mantid.kernel import (Direction)
from mantid.api import (DataProcessorAlgorithm)

from sans_property_names import (SAMPLE_SCATTER)

class SANSGuiAlgorithm(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\GUI'

    def summary(self):
        return 'Algorithm to run the SANS Gui.'

    def PyInit(self):
        # ----------
        # Data Input
        # ----------
        self.declareProperty("sample_scatter", "", direction=Direction.Input, doc="The scatter sample.")

    def PyExec(self):
        pass
