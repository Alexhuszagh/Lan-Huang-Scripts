'''Script to extract MS2 scans within window'''

# load modules/submodules
import csv

import numpy as np

from xldlib.common import ms
from xldlib.plugins.vendors import thermo_finnigan as tf


# CONSTANTS
# ---------

MZ = 312.22900
PPM = 30
LEVEL = 2
DELIMITER = '\t'


FIELDS = [
    'Scan',
    'Present',
    'Precursor Scan',
    'Precursor m/z',
    'Precursor z',
    'm/z',
    'intensity',
]

MASS_LIST = [
    None,       # size filter
    0,          # cutoff_type
    0,          # cutoff_value
    0,          # max_peaks, 0 for all
    True        # centroid, True
]


def writer(path):
    '''Setup CSV writer to export path'''

    csvfile = open(path, 'w')
    csv_writer = csv.writer(csvfile, delimiter=DELIMITER)
    csv_writer.writerow(FIELDS)

    return csv_writer


def extract_precursor(raw, scan):
    '''Extract precursor m/z, scan number, and charge'''

    precursor = raw.get_precursor_info_from_scan_num(scan)[0]
    if precursor.charge == 0:
        precursor.charge = 1
    return {
        'Precursor Scan': precursor.scan,
        'Precursor m/z': precursor.monoisotopic_mass,
        'Precursor z': precursor.charge
    }


def extract_mz(raw, scan):
    '''Extract if target m/z value is present in scan and relevant data'''

    mass = raw.get_mass_list_from_scan_num(scan, *MASS_LIST)
    mz_arr, intensity_arr = mass.mass_list
    ppm = ms.ppm(mz_arr, 0, MZ, 0)
    indexes, = np.where(abs(ppm) < PPM)
    present = bool(indexes.size)

    if present:
        mzs = mz_arr[indexes]
        intensities = intensity_arr[indexes]
        mz = np.average(mzs, weights=intensities)
        intensity = np.sum(intensities)
    else:
        mz = MZ
        intensity = 0

    return {
        'Present': present,
        'm/z': mz,
        'intensity': intensity,
        'Scan': scan
    }


def extract_scan(raw_path, out_path):
    '''Extract scan data from raw and write to CSV'''

    out = writer(out_path)
    with tf.ThermoFinniganApi(raw_path) as raw:
        raw.set_current_controller(0, 1)
        for scan in range(1, raw.get_num_spectra()+1):
            if raw.get_ms_order_for_scan_num(scan) == LEVEL:
                data = extract_mz(raw, scan)
                data.update(extract_precursor(raw, scan))

                values = [data[i] for i in FIELDS]
                out.writerow(values)
