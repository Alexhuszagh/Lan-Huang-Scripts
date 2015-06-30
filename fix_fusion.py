#!/usr/bin/env python
'''
Copyright (C) 2015 Alex Huszagh <<github.com/Alexhuszagh>>

xlDiscoverer is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This xlDiscoverer is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this xlDiscoverer.  If not, see <http://www.gnu.org/licenses/>.
'''

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# This program aims to fix the missing data from the PAVA Raw Distiller
# with newer versions of the Thermo RAW file format, such as with the
# Orbitrap FUSION format. This can lead to an empty PEPMASS line, as
# well as other missing data. By using a TPP-compatible MGF file, we
# can correct the PAVA-file.

# Ex.:
# INPUT:
#       BEGIN IONS
#       SCAN_FILTER=ITMS + c NSI r d Full ms3 380.70@cid23.00 560.27@hcd30.00 [120.00-571.00]
#       MS2_SCAN_NUMBER= 1045
#       TITLE=Scan 1046 (rt=9.324) [20140313_02_Lan_1_MS2CIDOT23_MS3HCDIT_Top3.raw]
#       PEPMASS=0   0.0000
#       CHARGE=1+
#       ....

# OUTPUT:
#       BEGIN IONS
#       SCAN_FILTER=ITMS + c NSI r d Full ms3 380.70@cid23.00 560.27@hcd30.00 [120.00-571.00]
#       MS2_SCAN_NUMBER= 1045
#       TITLE=Scan 1046 (rt=9.324) [20140313_02_Lan_1_MS2CIDOT23_MS3HCDIT_Top3.raw]
#       PEPMASS=560.26831 30933.20313
#       CHARGE=1+
#       ....

# Tested on Python 2.7.9 Ubuntu and Python 3.4.3, Ubuntu

# load modules
import argparse
import os
import re
import six

# pylint: disable=protected-access, too-many-instance-attributes

# constants
PATH = os.path.dirname(os.path.realpath(__file__))
TPP_PARSER = re.compile(
    r'BEGIN IONS\r?\n'
    r'TITLE=(.*)\.[0-9]+\.[0-9]+\.[0-9]* '
    # one massively long line
    r'File:\"(.*)\", NativeID:\"'
    r'controllerType=[0-9]+ '
    r'controllerNumber=[0-9]+ scan=([0-9]+)\"\r?\n'
    # newline
    r'RTINSECONDS=([0-9]*\.?[0-9]*)\r?\n'
    r'PEPMASS=([0-9]+\.[0-9]+)'
    r'(?: ([0-9]*\.[0-9]+))?\r?\n'
    r'(CHARGE=([0-9]+)\+\r?\n)?')
PAVA_PARSER = re.compile(
    r'^BEGIN IONS\r?\n'
    # In case of file header line, in _ms3cid files
    r'(.*\r?\n)?'
    # precursor in ms2
    r'(?:MS2_SCAN_NUMBER= ([0-9]+)\r?\n)?'
    r'TITLE=Scan ([0-9]+) '
    r'\(rt=([0-9]*\.[0-9]+)\) \[(.*)\]\r?\n'
    r'PEPMASS=([0-9]+\.?[0-9]*)\s+'
    r'([0-9]*(\.?[0-9]*)?)\r?\n'
    # Line could be missing if CHARGE=1+
    r'(CHARGE=([0-9]+)\+\r?\n)?'
)

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
BASE_NAME = os.path.splitext(os.path.basename(ARGS.PAVA))[0] + "_corrected.txt"
OUT_PATH = os.path.join(PATH, BASE_NAME)
if ARGS.output:
    OUT_PATH = os.path.join(PATH, ARGS.output)

# ------------------
#        I/O
# ------------------

# output
try:
    TPP_SCANS = open(TPP_PATH, 'r')
except IOError:
    raise argparse.ArgumentTypeError("MGF File not found. Make sure it is "
                                     "in the current working directory.")

# process input
try:
    PAVA_SCANS = open(PAVA_PATH, 'r')
except IOError:
    raise argparse.ArgumentTypeError("PAVA File not found. Make sure it is "
                                     "in the current working directory.")

# ------------------
#    SCAN FINDER
# ------------------

class ScanFinder(object):
    '''Iteratively parses chunks and breaks them into scans, with
    a bound remainder.
    '''

    def __init__(self, start_sub, end_sub):
        '''Binds instance atrributes and calls object'''
        super(ScanFinder, self).__init__()

        # bind instance attributes
        self.remainder = ''
        self.start_sub = start_sub
        self.end_sub = end_sub

    def parse_chunk(self, chunk):
        '''Parses a read chunk and adds to the remainder, and then
        processes scan subs.

        Arguments:
            chunk -- read chunk, ie, 4096 chars, etc.
        '''

        # add to stored
        self.remainder += chunk
        # init return
        scans = []
        start = None
        end = None
        # iteratively add until not found
        while end != -1:
            # find start and end subs
            start = self.find_start()
            end, match = self.find_end()
            # if both found
            if end != -1:
                # yield scan
                scan = self.get_scan(start, end, match)
                scans.append(scan)
                # adjust remainder
                self.adjust_remainder(end, match)
        return scans

    def find_start(self):
        '''Finds the start position of a given scan'''

        if isinstance(self.start_sub, six.string_types):
            start = self.remainder.find(self.start_sub)
        # if re sub
        elif isinstance(self.start_sub, re._pattern_type):
            match = self.start_sub.search(self.remainder)
            if match is None:
                start = -1
            else:
                start = match.start()
        return start

    def find_end(self):
        '''Finds the end position of a given scan'''

        if isinstance(self.end_sub, six.string_types):
            end = self.remainder.find(self.end_sub)
            match = None
        # if re sub
        elif isinstance(self.end_sub, re._pattern_type):
            match = self.end_sub.search(self.remainder)
            if match is None:
                end = -1
            else:
                end = match.start()
        return end, match

    def get_scan(self, start, end, match):
        '''Gets the full scan string of the MS scan file.

        Arguments:
            start, end -- ints for start and end of the scan
            match -- re match pattern or NoneType
        '''

        # grab sub lengths
        if isinstance(self.end_sub, six.string_types):
            sub_end = end + len(self.end_sub)
        # if re sub
        elif isinstance(self.end_sub, re._pattern_type):
            sub_end = match.end()
        # grab full scan and return
        scan = self.remainder[start:sub_end]
        return scan

    def adjust_remainder(self, end, match):
        '''Adjusts the remaining string length for new scan processing.

        Arguments:
            end -- ints for start and end of the scan
            match -- re match pattern or NoneType
        '''

        # grab sub lengths
        if isinstance(self.end_sub, six.string_types):
            sub_end = end + len(self.end_sub)
        # if re sub
        elif isinstance(self.end_sub, re._pattern_type):
            sub_end = match.end()
        self.remainder = self.remainder[sub_end:]

# ------------------
#    SCAN PARSER
# ------------------

class ParseMgf(object):
    '''Parses MGF file format using series of known subs (specific
    to each version of MGF file) and stores data in dictionary.
    MGF Format:
        BEGIN IONS
        scan=470
        PEPMASS=473.456
        ...
        475.34\t1800
        ...
        END IONS
    '''

    _start_sub = 'BEGIN IONS'
    _end_sub = 'END IONS'
    _pep_mass = r'PEPMASS=[0-9]*\.?[0-9]*'
    _pep_intensity = r'\t[0-9]*\.?[0-9]*'

    def __init__(self, fileobj, mode, **kwargs):
        super(ParseMgf, self).__init__()

        # bind instance attributes
        self.fileobj = fileobj
        self.scan_finder = ScanFinder(self._start_sub,
                                      self._end_sub)
        # set parser mode
        if mode == 'PAVA':
            # if read/write new string
            self.parser = self.process_pava_scan
            self.re_scan = PAVA_PARSER
            self.data = OUT_FILE
            self.tpp_data = kwargs.get('TPP')
        elif mode == 'TPP':
            # grab charges, don't replace
            self.data = {}
            self.parser = self.process_tpp_scan
            self.re_scan = TPP_PARSER

    def run(self):
        '''On start. Reads line by line until StopIterationError.
        Use of next() over readline() is to control exit loop.
        '''

        chunk = True
        while chunk:
            # grab chunks
            chunk = self.fileobj.read(4096)
            scans = self.scan_finder.parse_chunk(chunk)
            for scan in scans:
                self.parser(scan)

    # ------------------
    #        MAIN
    # ------------------

    def process_pava_scan(self, scan_string):
        '''Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self.process_data(). Processes PAVA-like formats.

        Arguments:
            scan_string -- string encompassing the full scan
        '''

        # grab our match
        match = self.re_scan.split(scan_string)
        scan_string = self.replace_pep_mass(scan_string, match)
        self.write_new_scan(scan_string)

    def replace_pep_mass(self, scan_string, match):
        '''Replaces the pep_mass within the scan string'''

        # init return
        num = int(match[3])
        # grab tpp data
        tpp_data = self.tpp_data.get(num, {})
        # format replacements
        sub = ''
        repl = ''
        try:
            # add in m/z value
            repl += 'PEPMASS={0}'.format(tpp_data['precursorMz'])
            sub += self._pep_mass
            # add in m/z value
            repl += '\t{0}'.format(tpp_data['precursorIntensity'])
            sub += self._pep_intensity
        except KeyError:
            pass
        return re.sub(sub, repl, scan_string)

    def process_tpp_scan(self, scan_string):
        '''Processes a single scan and stores the data in self.data.
        Stores the meta-data directly and then processes the scan
        spectra via self.process_data(). Processes TPP-like formats.

        Arguments:
            scan_string -- string encompassing the full scan
        '''

        # grab our match
        match = self.re_scan.split(scan_string)
        # init return
        scan = {}
        num = int(match[3])
        self.data[num] = scan
        # mz
        if match[5] is not None:
            scan['precursorMz'] = float(match[5])
        # intensity, if < 1, is 8, otherwise is 7
        if match[6] is not None:
            scan['precursorIntensity'] = float(match[6])

    # ------------------
    #        UTILS
    # ------------------

    def write_new_scan(self, scan_string):
        '''Writes the new scan string to file'''

        scan_string = ''.join([scan_string, '\n\n'])
        # pylint: disable=maybe-no-member
        self.data.write(scan_string)

# ------------------
#       MAIN
# ------------------

def main():
    '''Runs the core tasks'''

    # parse the tpp
    tpp_cls = ParseMgf(TPP_SCANS, 'TPP')
    tpp_cls.run()
    # parse the pava file
    pava_cls = ParseMgf(PAVA_SCANS, 'PAVA', TPP=tpp_cls.data)
    pava_cls.run()
    # grab shared keys

if __name__ == '__main__':

    # make write file
    OUT_FILE = open(OUT_PATH, 'w')
    # call main tasks
    main()
    OUT_FILE.close()
