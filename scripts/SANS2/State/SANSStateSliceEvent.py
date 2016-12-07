""" Defines the state of the event slices which should be reduced."""

import json
from SANS2.State.SANSStateBase import (SANSStateBase, sans_parameters, FloatListParameter)
from SANS2.State.SANSStateFunctions import (is_pure_none_or_not_none, validation_message)


# ------------------------------------------------
# SANSStateReduction
# ------------------------------------------------
class SANSStateSliceEvent(object):
    pass


# -----------------------------------------------
#  SANSStateReduction for ISIS
# -----------------------------------------------
@sans_parameters
class SANSStateSliceEventISIS(SANSStateSliceEvent, SANSStateBase):
    start_time = FloatListParameter()
    end_time = FloatListParameter()

    def __init__(self):
        super(SANSStateSliceEventISIS, self).__init__()

    def validate(self):
        is_invalid = dict()

        if not is_pure_none_or_not_none([self.start_time, self.end_time]):
            entry = validation_message("Missing slice times",
                                       "Makes sure that either both or none are set.",
                                       {"start_time": self.start_time,
                                        "end_time": self.end_time})
            is_invalid.update(entry)

        if self.start_time and self.end_time:
            # The length of start_time and end_time needs to be identical
            if len(self.start_time) != len(self.end_time):
                entry = validation_message("Bad relation of start and end",
                                           "Makes sure that the start time is smaller than the end time.",
                                           {"start_time": self.start_time,
                                            "end_time": self.end_time})
                is_invalid.update(entry)

            # Check that end_time is not smaller than start_time
            if not is_smaller(self.start_time, self.end_time):
                entry = validation_message("Start time larger than end time.",
                                           "Make sure that the start time is not smaller than the end time.",
                                           {"start_time": self.start_time,
                                            "end_time": self.end_time})
                is_invalid.update(entry)

        if is_invalid:
            raise ValueError("SANSStateSliceEvent: The provided inputs are illegal. "
                             "Please see: {}".format(json.dumps(is_invalid)))


def is_smaller(smaller, larger):
    return all(x <= y for x, y in zip(smaller, larger) if x != -1 and y != -1)

# -----------------------------------------------
# SANSStateSliceEvent setup for other facilities/techniques/scenarios.
# Needs to derive from SANSStateSliceEvent and SANSStateBase and fulfill its contract.
# -----------------------------------------------
