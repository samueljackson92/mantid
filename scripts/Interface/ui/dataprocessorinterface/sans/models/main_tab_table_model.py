from model_base import StringParameter


class MainTabTableModelItem(object):
    sample_scatter = StringParameter()
    sample_transmission = StringParameter()
    sample_direct = StringParameter()
    can_scatter = StringParameter()
    can_transmission = StringParameter()
    can_direct = StringParameter()
    output_name = StringParameter()
    user_file = StringParameter()

    def __init__(self):
        super(MainTabTableModelItem, self).__init__()


class MainTabTableModel(object):
    def __init__(self):
        super(MainTabTableModel, self).__init__()
        self._main_tab_model_items = []
        self._index_to_parameter_map = {0: "sample_scatter",
                                        1: "sample_transmission",
                                        2: "sample_direct",
                                        3: "can_scatter",
                                        4: "can_transmission",
                                        5: "can_direct",
                                        6: "output_name",
                                        7: "user_file"}

    def update_model_item(self, item_index, parameter_index, value):
        # Check that the model is valid
        self._check_item_access(item_index)

        # Check that the parameter is valid
        self._check_parameter_access(parameter_index)

        # Set the parameter
        setattr(self._main_tab_model_items[item_index], self._index_to_parameter_map[parameter_index], value)

    def add_new_item(self, model_item):
        self._main_tab_model_items.append(model_item)

    def get_model_item(self, item_index):
        self._check_item_access(item_index)

    def get_number_of_paramters(self):
        7

    def _check_item_access(self, item_index):
        if item_index > len(self._main_tab_model_items):
            raise RuntimeError("There are {0} models. You requested the {1}nth"
                               " one".format(len(self._main_tab_model_items), item_index))

    def _check_parameter_access(self, parameter_index):
        if parameter_index > len(self._index_to_parameter_map):
            raise RuntimeError("There are {0} parameters. You requested the {1}nth"
                               " one".format(len(self._index_to_parameter_map), parameter_index))
