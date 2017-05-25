from __future__ import (absolute_import, division, print_function)
import copy
from sans.state.data import get_data_builder
from sans.user_file.user_file_state_director import UserFileStateDirectorISIS


class GuiStateDirector(object):
    def __init__(self, table_model, state_gui_model, facility):
        super(GuiStateDirector, self).__init__()
        self._table_model = table_model
        self._state_gui_model = state_gui_model
        self._facility = facility

    def create_state(self, row):
        # 1. Get the data settings, such as sample_scatter, etc... and create the data state.
        table_index_model = self._table_model.get_table_entry(row)
        data_builder = get_data_builder(self._facility)

        self._set_data_entry(data_builder.set_sample_scatter, table_index_model.sample_scatter)
        self._set_data_entry(data_builder.set_sample_transmission, table_index_model.sample_transmission)
        self._set_data_entry(data_builder.set_sample_direct, table_index_model.sample_direct)
        self._set_data_entry(data_builder.set_can_scatter, table_index_model.can_scatter)
        self._set_data_entry(data_builder.set_can_transmission, table_index_model.can_transmission)
        self._set_data_entry(data_builder.set_can_direct, table_index_model.can_direct)

        data = data_builder.build()

        # 2. Create the rest of the state based on the builder.
        user_file_state_director = UserFileStateDirectorISIS(data)
        settings = copy.deepcopy(self._state_gui_model.settings)
        user_file_state_director.add_state_settings(settings)
        return user_file_state_director.construct()

    @staticmethod
    def _set_data_entry(func, entry):
        if entry:
            func(entry)
