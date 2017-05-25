import os


class TableModel(object):
    def __init__(self):
        super(TableModel, self).__init__()
        self._user_file = ""
        self._batch_file = ""
        self._table_entries = {}

    @staticmethod
    def _validate_file_name(file_name):
        if not file_name:
            return
        if not os.path.exists(file_name):
            raise ValueError("The file {} does not seem to exist.".format(file_name))

    @property
    def user_file(self):
        return self._user_file

    @user_file.setter
    def user_file(self, value):
        self._validate_file_name(value)
        self._user_file = value

    @property
    def batch_file(self):
        return self._batch_file

    @batch_file.setter
    def batch_file(self, value):
        self._validate_file_name(value)
        self._batch_file = value

    def get_table_entry(self, index):
        if index not in self._table_entries:
            raise ValueError("The {}th row entry does not exist".format(index))
        return self._table_entries[index]

    def add_table_entry(self, row, table_index_model):
        self._table_entries.update({row: table_index_model})

    def clear_table_entries(self):
        self._table_entries = {}


class TableIndexModel(object):
    def __init__(self, index, sample_scatter, sample_transmission, sample_direct,
                 can_scatter, can_transmission, can_direct):
        super(TableIndexModel, self).__init__()
        self.index = index
        self.sample_scatter = sample_scatter
        self.sample_transmission = sample_transmission
        self.sample_direct = sample_direct

        self.can_scatter = can_scatter
        self.can_transmission = can_transmission
        self.can_direct = can_direct

        self.user_file = ""
        self.output_name = ""
