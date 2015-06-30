#!/usr/bin/env python

# load modules
import argparse
import copy
import math
import os
from collections import defaultdict

# constants
PATH = os.path.dirname(os.path.realpath(__file__))

# process arguments
PARSER = argparse.ArgumentParser()
PARSER.add_argument("-t", "--TPP", help="TPP File",
                    type=str)
PARSER.add_argument("-p", "--PAVA", help="PAVA File",
                    type=str)
PARSER.add_argument("-o", "--output", help="Output File Name (Optional)",
                    type=str)
ARGS = PARSER.parse_args()
# parse arguments
if not ARGS.TPP or not ARGS.PAVA:
    raise argparse.ArgumentTypeError("Please include both a PAVA file and "
                                     "TPP file in the working directory")
TPP_PATH = os.path.join(PATH, ARGS.TPP)
PAVA_PATH = os.path.join(PATH, ARGS.PAVA)
BASE_NAME = ARGS.PAVA[:-4] + "_corrected.txt"
OUT_PATH = os.path.join(PATH, BASE_NAME)
if ARGS.output:
    OUT_PATH = os.path.join(PATH, ARGS.output)

# ------------------
#        I/O
# ------------------

# output
try:
    with open(TPP_PATH, 'r') as fileobj:
        MGF_SCANS = fileobj.read()
except IOError:
    raise argparse.ArgumentTypeError("MGF File not found. Make sure it is "
                                     "in the current working directory.")

# process input
try:
    with open(PAVA_PATH, 'r') as fileobj:
        PAVA_SCANS = fileobj.read()
except IOError:
    raise argparse.ArgumentTypeError("PAVA File not found. Make sure it is "
                                     "in the current working directory.")

# ------------------
#       UTILS
# ------------------

def paired_start_end(value, start_sub, end_sub):
    '''Extract substring from string'''

    start = value.find(start_sub) + len(start_sub)
    end = value.find(end_sub, value.find(start_sub))
    return start, end

def find_all_shift_sub(value, sub):
    """Find all occurrences within a string"""

    start = 0
    while True:
        start = value.find(sub, start)
        if start == -1:
            return
        start += len(sub)
        yield start

# ------------------
#     PARSERS
# ------------------

class ParseScans(object):
    '''Core scan parser object'''

    _split_length = 100000

    def __init__(self, ms_scans, start_sub, end_sub):
        super(ParseScans, self).__init__()

        self.msscans = ms_scans
        self.start_sub = start_sub
        self.end_sub = end_sub

    def run(self):
        '''Splitting length'''

        generator = self.split_file()
        start, end = self.find_all_positions(generator)
        return self.find_scans(start, end)

    def split_file(self):
        '''Splits a file and iteratively corrects it'''

        # grab scan count to iter over
        scan_count = len(self.msscans)
        num = int(math.ceil(scan_count/self._split_length))+1
        # iteratively split
        for start in range(0, num, self._split_length):
            end = start + self._split_length
            yield self.msscans[start:end]

    def find_all_positions(self, generator):
        '''Find all scan start and end positions within the generator'''

        # init return
        scan_start = []
        scan_end = []
        # remainder counter for everything leftover from a split
        remainder = ''
        for index, scan in enumerate(generator):
            counter = index*self._split_length - len(remainder)
            tmp_scan_str = remainder+scan

            start_value = list(find_all_shift_sub(tmp_scan_str,
                                                  self.start_sub))
            end_value = list(find_all_shift_sub(tmp_scan_str, self.end_sub))

            try:
                last_idx = max(start_value + end_value)
            except ValueError:
                # In case none are found, then the scan is expanded
                last_idx = 0
            remainder = (tmp_scan_str)[last_idx:]
            scan_start += [i+counter for i in start_value]
            scan_end += [i+counter for i in end_value]
        import pdb
        pdb.set_trace()
        return scan_start, scan_end

    def find_scans(self, scan_start, scan_end):
        '''Returns a generator for each scan string within the file'''

        for i, start in enumerate(scan_start):
            end = scan_end[i]
            yield self.msscans[start:end]

class ParseMGF(ParseScans):
    '''Parses an MGF-type file format'''

    _start_sub = 'BEGIN IONS'
    _end_sub = 'END IONS'
    _pava_parse = {
        'num':['TITLE=Scan ', ' (rt='],
        'retentionTime':[' (rt=', ') [']
    }
    _tpp_parse = {
        'num':['scan=', '"\n'],
        'retentionTime':['RTINSECONDS=', '\n']
    }
    _pep_mass = {
        'start' : 'PEPMASS=',
        'end': '\n'
    }
    _charge = {
        'start': 'CHARGE=',
        'end': '+'
    }

    def __init__(self, scans):
        super(ParseMGF, self).__init__(scans, self._start_sub, self._end_sub)

        # bind instance attributes
        self.scans = self.run()
        self.scan_data = defaultdict(dict)
        self.process_scan_nums_to_data()

    # ------------------
    #       MAIN
    # ------------------

    def process_scan_nums_to_data(self):
        '''Processes each scan by number'''

        # Extract all spectra values per scan
        for scan in self.scans:
            data = self.extract_scan_mgf(scan)
            num = data.get('num')
            self.scan_data['%s' %num] = data

    def extract_scan_mgf(self, scan):
        '''Extracts data from all MGF scans'''

        # split header and spectra, extract metadata
        header, spectra = self.find_header_spectra(scan)
        data = self.extract_header_mgf(header)
        # process peaklists
        peaks = self.process_spectra(spectra)
        # store data and return object
        data['type'] = 'MGF'
        data['peaks'] = peaks
        return data

    # ------------------
    #   EXTRACT UTILS
    # ------------------

    @staticmethod
    def find_header_spectra(scan):
        '''Finds and extracts the header from the scan'''

        scan = scan.splitlines()[1:-1]
        #import pdb; pdb.set_trace()
        scan_index = None
        # In each spectra scan, first line that starts with a float
        for index, row in enumerate(scan):
            # number is the start of the spectral data
            try:
                float(row.split()[0])
                scan_index = index
                break
            except ValueError:
                pass
        # If no scans, set the scan list to be blank,
        if scan_index is None:
            # and the header to be the rest
            header = scan
            spectra = []
            return '\n'.join(header), '\n'.join(spectra)
        else:
            header = '\n'.join(scan[:scan_index])
            spectra = '\n'.join(scan[scan_index:])
            return header, spectra

    def extract_header_mgf(self, header):
        '''Extracts data from the MGF header'''

        # Unique substring for a PAVA-style MGF file
        if '(rt=' in header:
            return self.extract_pava_header(header)
        # Substring for TPP-compatible MGF file
        elif 'RTINSECONDS=' in header:
            return self.extract_tpp_header(header)

        else:
            return

    def extract_pava_header(self, header):
        '''Extracts the metadata from the PAVA header'''

        # init return
        data = {}
        parse = copy.deepcopy(self._pava_parse)
        if 'MS2_SCAN_NUMBER' in header:
            parse.update({'precursorScanNum':['MS2_SCAN_NUMBER= ', '\n']})
        # update scan dictionary
        self.parse_header(header, parse, data)
        self.parse_pep_mass(header, data)
        self.parse_charge(header, data)

        return data

    def extract_tpp_header(self, header):
        '''Extracts the metadata from the TPP header'''

        data = {}
        self.parse_header(header, self._tpp_parse, data)
        self.parse_pep_mass(header, data)
        self.parse_charge(header, data)

        if 'retentionTime' in data:
            retention_time = data.get('retentionTime')
            min_seconds = 60
            data['retentionTime'] = round(float(retention_time)/min_seconds, 3)

        return data

    # ------------------
    #    PARSE UTILS
    # ------------------

    @staticmethod
    def parse_header(header, parse_subs, data):
        '''Parses and extracts the metadata from the scan header'''

        for key in parse_subs:
            start_sub, end_sub = parse_subs.get(key)
            start, end = paired_start_end(header, start_sub, end_sub)
            value = header[start:end]
            data[key] = value

    def parse_pep_mass(self, header, data):
        '''Process the peptide mass'''

        start, end = paired_start_end(header, self._pep_mass['start'],
                                      self._pep_mass['end'])
        row = header[start:end]
        pep_mass = row.split()
        # only one entry in header
        if len(pep_mass) == 1:
            precursor_mz = pep_mass[0]
            data['precursorMz'] = precursor_mz
        # mz/intensity pair in header
        elif len(pep_mass) == 2:
            precursor_mz, precursor_intensity = pep_mass
            data['precursorMz'] = precursor_mz
            data['precursorIntensity'] = precursor_intensity

    def parse_charge(self, header, data):
        '''Processes the peptide charges'''

        precursor_charge = 1
        if 'CHARGE=' in header:
            start, end = paired_start_end(header, self._charge['start'],
                                          self._charge['end'])
            precursor_charge = header[start:end]
        data['precursorCharge'] = precursor_charge
        return data

    @staticmethod
    def process_spectra(spectra):
        '''Processes the spectra and extracts the m/z and intensities'''

        # init return
        data = defaultdict(list)
        # iterate over rows in spectra
        spectra = spectra.splitlines()
        for row in spectra:
            row = row.split()
            # mz/intensity paired values
            if len(row) == 2:
                mz_value, intensity = row
                data[mz_value] = [intensity]
            # mz/charge/intensity values
            elif len(row) == 3:
                mz_value, charge, intensity = row
                data[mz_value] = [intensity, charge]
        try:
            del data['END']
        except KeyError:
            pass
        return data


# ------------------
#    SCAN FIXER
# ------------------

class FixScans(ParseScans):
    '''Fixes the PAVA scans from the MGF scan data'''

    _scan_start = 'BEGIN IONS'
    _scan_end = 'END IONS'
    _start = 'TITLE=Scan '
    _end = ' (rt='

    def __init__(self, pava_scans, charges, output):
        super(FixScans, self).__init__(pava_scans, self._scan_start,
                                       self._scan_end)

        # bind instance attributes
        self.scans = self.run()
        pava_string = self.process_scans(charges)
        self.fixed_scans = str()
        # write to file
        with open(output, 'w') as fileobj:
            fileobj.write(pava_string)

    def process_scans(self, charges):
        '''Processes the PAVA scan list and corrects their charges'''


        for scan in self.scans:
            # grab start/end pair
            start, end = paired_start_end(scan, self._start, self._end)
            num = scan[start:end]
            try:
                # replace old charge with new charge in string
                new_charge, old_charge = charges[num]
                old_str = "CHARGE=%s+" %(str(old_charge))
                new_str = "CHARGE=%s+" %(str(new_charge))
                scan = scan.replace(old_str, new_str)
            except KeyError:
                # not in scan
                pass
            self.fixed_scans += "BEGIN IONS\n%s\n\n" %scan
        return self.fixed_scans

# ------------------
#      OUTPUT
# ------------------

class CompareCharges(object):
    '''Compares and corrects the charge settings in the PAVA-like MGF
    file from a TPP-like MGF reference file.
    '''

    _output_name = "chargeStates.txt"

    def __init__(self, tpp_scans, pava_scans, out_path):
        super(CompareCharges, self).__init__()

        # grab scan data and bind to instance
        tpp_cls = ParseMGF(tpp_scans)
        self.tpp_data = tpp_cls.scan_data
        pava_cls = ParseMGF(pava_scans)
        self.pava_data = pava_cls.scan_data
        # make
        self.charges = {}
        self.compile_charges()
        # fix the scans in place
        cls = FixScans(pava_scans, self.charges, out_path)
        cls.run()
        # write comparative output
        self.output_path = os.path.join(PATH, self._output_name)
        self.write_comparative_output()

    def compile_charges(self):
        '''Creates a {scan: [MGF, PAVA]} dict of charges'''

        # grab scans
        tpp_scans = self.tpp_data.keys()
        pava_scans = self.pava_data.keys()
        # grab shared keys
        keys = [i for i in pava_scans if i in tpp_scans]
        # iteratively grab keys
        for key in keys:
            # grab scans
            tpp_scan = self.tpp_data.get(key, {})
            pava_scan = self.pava_data.get(key, {})
            # grab charges
            tpp_charge = str(tpp_scan.get("precursorCharge"))
            pava_charge = str(pava_scan.get("precursorCharge"))
            # assign to dict
            self.charges[key] = [tpp_charge, pava_charge]

    def write_comparative_output(self):
        '''Writes the comparative summary between the two files'''

        # init counters
        pava_counter = 0
        mgf_counter = 0
        # iteratively write daata
        with open(self.output_path, 'w') as fileobj:
            # comparative
            fileobj.write('Scan\tMGF\tPAVA\n')
            keys = sorted(self.charges.keys(), key=int)
            for key in keys:
                tpp_charge, pava_charge = self.charges.get(key)
                # add counters
                if tpp_charge != '1':
                    mgf_counter += 1
                if pava_charge != '1':
                    pava_counter += 1
                # if charges differ...
                if tpp_charge != pava_charge:
                    out = '%s\t%s\t%s\n' %(key, tpp_charge, pava_charge)
                    fileobj.write(out)
            # write counters
            fileobj.write('MGF Scans Above 1: %d\n' %mgf_counter)
            fileobj.write('PAVA Scans Above 1: %d\n' %pava_counter)

if __name__ == '__main__':
    CompareCharges(MGF_SCANS, PAVA_SCANS, OUT_PATH)
