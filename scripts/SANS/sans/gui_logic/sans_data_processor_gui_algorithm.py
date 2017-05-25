from mantid.kernel import (Direction, Property)
from mantid.api import (DataProcessorAlgorithm, AlgorithmFactory, MatrixWorkspaceProperty, PropertyMode)
from sans.common.enums import (SANSFacility, OutputMode)
from collections import namedtuple
from sans.gui_logic.presenter.property_manager_service import PropertyManagerService
from sans.sans_batch import SANSBatchReduction

# ----------------------------------------------------------------------------------------------------------------------
# Globals
# ----------------------------------------------------------------------------------------------------------------------
SANS_DUMMY_INPUT_ALGORITHM_PROPERTY_NAME = '__sans_dummy_gui_workspace'
SANS_DUMMY_OUTPUT_ALGORITHM_PROPERTY_NAME = '__sans_dummy_gui_workspace'


# ----------------------------------------------------------------------------------------------------------------------
# Set up the white list and black list properties of the data algorithm
# ----------------------------------------------------------------------------------------------------------------------
algorithm_list_entry = namedtuple('algorithm_list_entry', 'column_name, algorithm_property, description, '
                                                          'show_value, default, prefix')


def get_white_list_entries():
    white_list_properties = [algorithm_list_entry(column_name="SampleScatter",
                                                  algorithm_property="SampleScatter",
                                                  description='The run number of the scatter sample',
                                                  show_value=False,
                                                  default='',
                                                  prefix=''),
                             algorithm_list_entry(column_name="SampleTransmission",
                                                  algorithm_property="SampleTransmission",
                                                  description='The run number of the transmission sample',
                                                  show_value=False,
                                                  default='',
                                                  prefix=''),
                             algorithm_list_entry(column_name="SampleDirect",
                                                  algorithm_property="SampleDirect",
                                                  description='The run number of the direct sample',
                                                  show_value=False,
                                                  default='',
                                                  prefix=''),
                             algorithm_list_entry(column_name="CanScatter",
                                                  algorithm_property="CanScatter",
                                                  description='The run number of the scatter can',
                                                  show_value=False,
                                                  default='',
                                                  prefix=''),
                             algorithm_list_entry(column_name="CanTransmission",
                                                  algorithm_property="CanTransmission",
                                                  description='The run number of the transmission can',
                                                  show_value=False,
                                                  default='',
                                                  prefix=''),
                             algorithm_list_entry(column_name="CanDirect",
                                                  algorithm_property="CanDirect",
                                                  description='The run number of the direct can',
                                                  show_value=False,
                                                  default='',
                                                  prefix='')]
    return white_list_properties


def get_black_list_entries():
    # black_list_properties = [algorithm_list_entry(column_name="",
    #                                               algorithm_property="UseOptimizations",
    #                                               description='If optimzations should be used.',
    #                                               show_value=False,
    #                                               default=1,
    #                                               prefix='')
    #                         ]
    return []


def get_gui_algorithm_name(facility):
    if facility is SANSFacility.ISIS:
        algorithm_name = "SANSGuiDataProcessorAlgorithm"
        AlgorithmFactory.subscribe(SANSGuiDataProcessorAlgorithm)
    else:
        raise RuntimeError("The facility is currently not supported")
    return algorithm_name


class SANSGuiDataProcessorAlgorithm(DataProcessorAlgorithm):
    def category(self):
        return 'SANS\\Gui'

    def summary(self):
        return 'Dynamic SANS Gui algorithm.'

    def PyInit(self):
        # ------------------------------------------------------------
        # Dummy workspace properties.
        # ------------------------------------------------------------
        self.declareProperty(MatrixWorkspaceProperty("InputWorkspace", SANS_DUMMY_INPUT_ALGORITHM_PROPERTY_NAME,
                                                     optional=PropertyMode.Optional, direction=Direction.Input),
                             doc='The input workspace (which is not used)')

        self.declareProperty(MatrixWorkspaceProperty("OutputWorkspace", SANS_DUMMY_OUTPUT_ALGORITHM_PROPERTY_NAME,
                                                     optional=PropertyMode.Optional, direction=Direction.Output),
                             doc='The output workspace (which is not used)')

        # ------------------------------------------------------------
        # White list properties. They will be visible in the table
        # ------------------------------------------------------------
        white_list_entries = get_white_list_entries()
        for entry in white_list_entries:
            self.declareProperty(entry.algorithm_property, entry.default,
                                 direction=Direction.Input, doc=entry.description)

        # ------------------------------------------------------------
        # Black list properties. They will not be visible in the table
        # ------------------------------------------------------------
        black_list_entries = get_black_list_entries()
        for entry in black_list_entries:
            self.declareProperty(entry.algorithm_property, entry.default, option=PropertyMode.Optional,
                                 direction=Direction.Input, doc=entry.description)

        # ------------------------------------------------------------
        # Index of the row
        # ------------------------------------------------------------
        self.declareProperty("RowIndex", Property.EMPTY_INT, direction=Direction.Input,
                             doc='The row index (which is automatically populated by the GUI)')
        self.declareProperty('UseOptimizations', defaultValue=False, direction=Direction.Input, doc='Use optimizations')
        self.declareProperty('OutputMode', defaultValue=OutputMode.to_string(OutputMode.PublishToADS),
                             direction=Direction.Input, doc='Use optimizations')

    def PyExec(self):
        # 1. Get the index of the batch reduction
        index = self.getProperty("RowIndex").value

        if index == Property.EMPTY_INT:
            return

        # 2. Get the state for the index from the PropertyManagerDataService
        property_manager_service = PropertyManagerService()
        state = property_manager_service.get_single_state_from_pmds(index_to_retrieve=index)

        # 3. Get some global settings
        use_optimizations = self.getProperty("UseOptimizations").value
        output_mode_as_string = self.getProperty("OutputMode").value
        output_mode = OutputMode.from_string(output_mode_as_string)

        # 3. Run the sans_batch script
        sans_batch = SANSBatchReduction()
        sans_batch(states=state, use_optimizations=use_optimizations, output_mode=output_mode)
