from __future__ import (absolute_import, division, print_function)

from isis_powder.routines.RunDetails import create_run_details_object


def get_run_details(run_number_string, inst_settings, is_vanadium_run):
    return create_run_details_object(run_number_string=run_number_string, inst_settings=inst_settings,
                                     is_vanadium_run=is_vanadium_run)
