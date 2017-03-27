from __future__ import (absolute_import, division, print_function)

advanced_variables = {
    "grouping_file_name": "IMAT_Grouping.cal",
    "spline_coefficient": 10,
    "raw_tof_cropping_values": (5000, 19990)

}

focused_cropping_values = [(5050, 19900),  # Bank 1
                           (5050, 19900)   # Bank 2
                           ]

vanadium_cropping_values = [(5010, 19950),  # Bank 1
                            (5010, 19950)   # Bank 2
                            ]


def get_all_adv_variables():
    adv_config_dict = {
        "cropping_values": advanced_variables,
        "focused_cropping_values": focused_cropping_values,
        "vanadium_cropping_values": vanadium_cropping_values,
    }

    return adv_config_dict
