""" Main presenter for the SANS interface """
from main_tab_presenter import MainTabPresenter


class SANSPresenter(object):
    def __init__(self, main_tab_view):
        super(SANSPresenter, self).__init__()

        # Main tab
        self._main_tab_presenter = MainTabPresenter(main_tab_view)

        # Settings tab

        # State builder
        self._state_builder = None

    def reduce(self):
        # 1. Get the number of reductions that need to be performed
        # 2. For each row:
        #   i. Create a state for a reduction and execute the reduction
        # 3. For each row:
        #   i. Execute the reduction.
        #   ii. Update the output workspace name
        pass

    def _get_number_of_reductions(self):
        return self._main_tab_presenter.get_number_of_reductions()

    def _create_reduction_for_single_reduction(self, row):
        row = 0
        self._main_tab_view.get_cell(row, 1)

    def _reduce(self, state, row):
        pass

    def _update_output_workspace_name(self, output_workspace_name, row):
        pass
