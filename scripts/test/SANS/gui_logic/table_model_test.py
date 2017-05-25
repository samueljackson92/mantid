from __future__ import (absolute_import, division, print_function)
import unittest
import mantid
from sans.gui_logic.models.table_model import (TableModel, TableIndexModel)


class TableModelTest(unittest.TestCase):
    def test_user_file_can_be_set(self):
        self._do_test_file_setting(self._user_file_wrapper, "user_file")

    def test_batch_file_can_be_set(self):
        self._do_test_file_setting(self._batch_file_wrapper, "batch_file")

    def test_that_raises_if_table_index_does_not_exist(self):
        table_model = TableModel()
        table_index_model = TableIndexModel(0, "", "", "",
                                            "", "", "")
        table_model.add_table_entry(0, table_index_model)
        self.assertRaises(ValueError, table_model.get_table_entry, 1)

    def test_that_can_get_table_index_model_for_valid_index(self):
        table_model = TableModel()
        table_index_model = TableIndexModel(0, "", "", "",
                                            "", "", "")
        table_model.add_table_entry(0, table_index_model)
        returned_model = table_model.get_table_entry(0)
        self.assertTrue(returned_model.index == 0)

    def _do_test_file_setting(self, func, prop):
        # Test that can set to empty string
        table_model = TableModel()
        try:
            setattr(table_model, prop, "")
            has_raised = False
        except:
            has_raised = True
        self.assertFalse(has_raised)

        # Test raises for non-existent file path
        self.assertRaises(ValueError, func, "/home/test")

        # Test that can be set to valid value
        setattr(table_model, prop, __file__)
        self.assertTrue(getattr(table_model, prop) == __file__)

    @staticmethod
    def _batch_file_wrapper(value):
        table_model = TableModel()
        table_model.batch_file = value

    @staticmethod
    def _user_file_wrapper(value):
        table_model = TableModel()
        table_model.user_file = value

if __name__ == '__main__':
    unittest.main()
