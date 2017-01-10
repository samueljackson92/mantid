from csv import reader
from sans.common.enums import BatchReductionEntry


class BatchCsvParser(object):
    batch_file_keywords = {"sample_sans": BatchReductionEntry.SampleScatter,
                           "output_as": BatchReductionEntry.Output,
                           "sample_trans": BatchReductionEntry.SampleTransmission,
                           "sample_direct_beam": BatchReductionEntry.SampleDirect,
                           "can_sans": BatchReductionEntry.CanScatter,
                           "can_trans": BatchReductionEntry.CanTransmission,
                           "can_direct_beam": BatchReductionEntry.CanDirect,
                           "user_file": BatchReductionEntry.UserFile}

    def __init__(self, batch_file_name):
        super(BatchCsvParser, self).__init__()
        # Get the full file path
        self._batch_file_name = batch_file_name

    def parse_batch_file(self):
        """
        Parses the batch csv file and returns the elements in a parsed form

        Returns: parsed csv elements
        """

        parsed_rows = []

        with open(self._batch_file_name, 'rb') as csvfile:
            batch_reader = reader(csvfile, delimiter=",")
            row_number = 0
            for row in batch_reader:
                # If the first element contains a # symbol then ignore it
                if "MANTID_BATCH_FILE" in row[0]:
                    continue

                # Else we perform a parse of the row
                parsed_row = self._parse_row(row, row_number)
                parsed_rows.append(parsed_row)
                row_number += 1
        return parsed_rows

    def _parse_row(self, row, row_number):
        # Clean all elements of the row
        row = map(str.strip, row)

        # Go sequentially through the row with a stride of two. The user can either leave entries away, or he can leave
        # them blank, ie ... , sample_direct_beam, , can_sans, XXXXX, ...  or even ..., , ,...
        # This means we expect an even length of entries
        if len(row) % 2 != 0:
            raise RuntimeError("We expect an even number of entries, but row {0} has {1} entries.".format(row_number,
                                                                                                          len(row)))
        output = {}
        for key, value in zip(row[::2], row[1::2]):
            if key in self.batch_file_keywords.keys():
                new_key = self.batch_file_keywords[key]
                value = value.strip()
                output.update({new_key: value})
            else:
                raise RuntimeError("The key {0} is not part of the SANS batch csv file keywords".format(key))

        # Ensure that sample_scatter was set
        if BatchReductionEntry.SampleScatter not in output or not output[BatchReductionEntry.SampleScatter]:
            raise RuntimeError("The sample_scatter entry in row {0} seems to be missing.".format(row_number))

        # Ensure that output_as was set
        if BatchReductionEntry.Output not in output or not output[BatchReductionEntry.Output]:
            raise RuntimeError("The output_as entry in row {0} seems to be missing.".format(row_number))

        # Ensure that the transmission data for the sample is specified either completely or not at all.
        has_sample_transmission = BatchReductionEntry.SampleTransmission in output and\
                                  output[BatchReductionEntry.SampleTransmission]
        has_sample_direct_beam = BatchReductionEntry.SampleDirect in output and output[BatchReductionEntry.SampleDirect]

        if (not has_sample_transmission and has_sample_direct_beam) or \
                (has_sample_transmission and not has_sample_direct_beam):
            raise RuntimeError("Inconsistent sample transmission settings in row {0}. Either both the transmission "
                               "and the direct beam run are set or none.".format(row_number))

        # Ensure that the transmission data for the can is specified either completely or not at all.
        has_can_transmission = BatchReductionEntry.CanTransmission in output and \
                               output[BatchReductionEntry.CanTransmission]
        has_can_direct_beam = BatchReductionEntry.CanDirect in output and output[BatchReductionEntry.CanDirect]

        if (not has_can_transmission and has_can_direct_beam) or \
                (has_can_transmission and not has_can_direct_beam):
            raise RuntimeError("Inconsistent can transmission settings in row {0}. Either both the transmission "
                               "and the direct beam run are set or none.".format(row_number))

        # Ensure that can scatter is specified if the transmissions are set
        has_can_scatter = BatchReductionEntry.CanScatter in output and output[BatchReductionEntry.CanScatter]
        if not has_can_scatter and has_can_transmission:
            raise RuntimeError("The can transmission was set but not the scatter file in row {0}.".format(row_number))
        return output
