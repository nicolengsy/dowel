"""A `dowel.logger.LogOutput` for CSV files."""
import csv
import warnings

from dowel import TabularInput
from dowel.simple_outputs import FileOutput
from dowel.utils import colorize


class CsvOutput(FileOutput):
    """CSV file output for logger.

    :param file_name: The file this output should log to.
    """

    def __init__(self, file_name):
        super().__init__(file_name)
        self._writer = None
        self._fieldnames = None
        self._file_name = file_name

    @property
    def types_accepted(self):
        """Accept TabularInput objects only."""
        return (TabularInput, )

    def record(self, data, prefix=''):
        """Log tabular data to CSV."""
        if isinstance(data, TabularInput):
            to_csv = data.as_primitive_dict

            if not to_csv.keys() and not self._writer:
                return

            if not self._writer:
                self._fieldnames = set(to_csv.keys())
                self._writer = csv.DictWriter(
                    self._log_file,
                    fieldnames=self._fieldnames,
                    extrasaction='ignore')
                self._writer.writeheader()

            if to_csv.keys() != self._fieldnames:
                # Get data from current csv
                with open(self._file_name, 'r') as f:
                    reader = csv.DictReader(f)

                    # Add new fields to self._fieldnames
                    for key in to_csv.keys():
                        if key not in self._fieldnames:
                            self._fieldnames.add(key)
                    
                    # Write back to csv with new fieldnames
                    self._writer = csv.DictWriter(
                        self._log_file,
                        fieldnames=self._fieldnames,
                        extrasaction='raise')

                    self._log_file.seek(0)
                    self._writer.writeheader()
                    self._writer.writerows(reader)

            self._writer.writerow(to_csv)

            for k in to_csv.keys():
                data.mark(k)
        else:
            raise ValueError('Unacceptable type.')

