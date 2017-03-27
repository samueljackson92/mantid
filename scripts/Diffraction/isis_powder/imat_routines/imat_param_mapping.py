from __future__ import (absolute_import, division, print_function)

from isis_powder.routines.ParamMapEntry import ParamMapEntry
#                 Maps friendly user name (ext_name) -> script name (int_name)

attr_mapping = \
    [
     ParamMapEntry(ext_name="absorb_corrections",       int_name="do_absorb_corrections"),
     ParamMapEntry(ext_name="calibration_dir",          int_name="calibration_dir"),
     ParamMapEntry(ext_name="calibration_mapping_file", int_name="cal_mapping_path"),
     ParamMapEntry(ext_name="focused_cropping_values",  int_name="focused_cropping_values"),
     ParamMapEntry(ext_name="grouping_file_name",       int_name="grouping_file_name"),
     ParamMapEntry(ext_name="output_dir",               int_name="output_dir"),
     ParamMapEntry(ext_name="raw_tof_cropping_values",  int_name="raw_tof_cropping_values"),
     ParamMapEntry(ext_name="run_in_range",             int_name="run_in_range"),
     ParamMapEntry(ext_name="run_number",               int_name="run_number"),
     ParamMapEntry(ext_name="spline_coefficient",       int_name="spline_coeff"),
     ParamMapEntry(ext_name="user_name",                int_name="user_name"),
     ParamMapEntry(ext_name="vanadium_cropping_values", int_name="vanadium_cropping_values"),
     ParamMapEntry(ext_name="vanadium_normalisation",   int_name="do_van_norm")
    ]
