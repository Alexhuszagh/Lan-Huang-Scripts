#!/usr/bin/env python
'''
Copyright (C) 2015 The Regents of the University of California.

This program is free software: you can redistribute it and/or modify
it under the terms of the GNU General Public License as published by
the Free Software Foundation, either version 3 of the License, or
(at your option) any later version.

This program is distributed in the hope that it will be useful,
but WITHOUT ANY WARRANTY; without even the implied warranty of
MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
GNU General Public License for more details.

You should have received a copy of the GNU General Public License
along with this program.  If not, see <http://www.gnu.org/licenses/>.
'''

from __future__ import division

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# This program is a simple converter to fix the RB MGF file extraction,
# which is not recognized in the params/mgf.xml for Protein Prospector
# due to their mixing and matching of the MS_CONVERT and
# PROTEOME_DISCOVERER file formats.

# TITLE=File: "I:\UCIrvine\G6E_lanmod195mintop4forms3.raw"; SpectrumID: "1";
# scans: "228"
# PEPMASS=489.27979 68179.95313
# CHARGE=4+
# RTINSECONDS=98
# SCANS=228
# 129.035 4.3

# Ex.:
# INPUT:
#   $ python rv_mgf_converter.py -m G6E.MGF

# The "File:" and "scans: " subs are mutually incompatible insofar."

# load modules
import argparse
import os
import re
import six

# constants
PATH = os.path.dirname(os.path.realpath(__file__))

# process arguments
PARSER = argparse.ArgumentParser()
PARSER.add_argument("-m", "--MGF", help="RB MGF File", required=True,
                    type=str)
PARSER.add_argument("-o", "--output", help="Output File Name (Optional)",
                    type=str)
ARGS = PARSER.parse_args()

# parse arguments
MGF_PATH = os.path.join(PATH, ARGS.MGF)
BASE_NAME = os.path.splitext(os.path.basename(ARGS.MGF))[0] + "_corrected.txt"
OUT_PATH = os.path.join(PATH, BASE_NAME)
if ARGS.output:
    OUT_PATH = os.path.join(PATH, ARGS.output)

# ------------------
#        I/O
# ------------------

# process input
try:
    MGF_SCANS = open(MGF_PATH, 'r')
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
         TITLE=File: "I:\UCIrvine\G6E_lanmod195mintop4forms3.raw"; SpectrumID: "1"; # scans: "228"
         PEPMASS=489.27979 68179.95313
         CHARGE=4+
         RTINSECONDS=98
         SCANS=228
         129.035 4.3
    '''

    _start_sub = 'BEGIN IONS'
    _end_sub = 'END IONS'

    _sub_repl = ('scans: ', 'scan=')

    _parser = re.compile(
        r'BEGIN IONS\r?\n'
        # ; scans: "228"
        r'TITLE=File: \"(.*)\"; SpectrumID: \"\d*\"; scans: \"(\d*)\"\r?\n'
        # newline
        r'PEPMASS=([0-9]+\.[0-9]+)'
        r'(?: ([0-9]*\.[0-9]+))?\r?\n'
        r'(CHARGE=([0-9]+)\+\r?\n)?'
        r'RTINSECONDS=([0-9]*\.?[0-9]*)\r?\n'
        r'SCANS=\d*\r?\n')

    _out_format = (
        'BEGIN IONS\n'
        # ss[2], round(ss[7] / 60, 3), ss[1]
        'TITLE=Scan {} (rt={}) [{}]\n'
        # ss[3], ss[4]
        'PEPMASS={} {}\n'
        # ss[6]
        'CHARGE={}+\n'
        # ss[8]
        '{}'
    )

    def __init__(self, fileobj, **kwargs):
        super(ParseMgf, self).__init__()

        self.fileobj = fileobj
        self.scan_finder = ScanFinder(self._start_sub,
                                      self._end_sub)

        self.data = OUT_FILE

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

    def parser(self, scan):
        '''Processes the scan and then writes it to file'''

        # sub, repl = self._sub_repl
        match = self._parser.split(scan)
        args = map(match.__getitem__, [2, 7, 1, 3, 4, 6, 8])
        args[1] = str(round(int(args[1]) / 60, 3))
        scan =  self._out_format.format(*args)
        self.write_new_scan(scan)

    # ------------------
    #        UTILS
    # ------------------

    def write_new_scan(self, scan_string):
        '''Writes the new scan string to file'''

        scan_string = ''.join([scan_string, '\n\n'])
        self.data.write(scan_string)


def main():
    '''Runs the core tasks'''

    # parse the tpp
    mgf_cls = ParseMgf(MGF_SCANS)
    mgf_cls.run()

if __name__ == '__main__':

    # make write file
    OUT_FILE = open(OUT_PATH, 'w')
    # call main tasks
    main()
    OUT_FILE.close()
