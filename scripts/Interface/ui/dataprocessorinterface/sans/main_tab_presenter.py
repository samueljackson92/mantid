from models.main_tab_table_model import MainTabTableModel


class MainTabPresenter(object):
    def __init__(self, view):
        super(MainTabPresenter, self).__init__()
        self._view = view
        self._model = MainTabTableModel()

    def update_models(self):
        """
        Iterate over each reduction and update the models
        """
        # TODO how do I get the number of rows?

        item_index = 0
        self._update_model_for_single_reduction(item_index)

    def _update_model_for_single_reduction(self, item_index):
        pass

    def get_number_of_reductions(self):
        return 1

