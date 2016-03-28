'''Extract reporterion counts and group my MS2 m/z values'''

# load modules/submodules
import ast
import csv

from collections import defaultdict
from functools import partial

from xldlib.common import ms


# CONSTANTS
# ---------

FIELDS = [
    'Present',
    'Precursor Mass',
    'Count',
]
DELIMITER = '\t'


def writer(path):
    '''Setup CSV writer to export path'''

    csvfile = open(path, 'w')
    csv_writer = csv.writer(csvfile, delimiter=DELIMITER)
    csv_writer.writerow(FIELDS)

    return csv_writer


def group_file(in_path, out_path):
    '''Group items by presence/abscence and reporter ion mass'''

    with open(in_path) as f:
        data = defaultdict(partial(defaultdict, int))
        reader = csv.DictReader(f, delimiter=DELIMITER)
        for row in reader:
            mz = float(row['Precursor m/z'])
            z = int(row['Precursor z'])
            mass = round(ms.mz(mz, 0, z), 1)
            data[ast.literal_eval(row['Present'])][mass] += 1

    out = writer(out_path)
    for present in [False, True]:
        for mass in sorted(data[present]):
            out.writerow([present, mass, data[present][mass]])
