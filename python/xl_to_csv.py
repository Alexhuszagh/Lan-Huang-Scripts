#!/usr/bin/env python
'''
Copyright (C) 2015 Alex Huszagh <<github.com/Alexhuszagh>>

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

from __future__ import print_function

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# This program aims to convert a set of crosslinks in the XL
# Discoverer format directly to the CSV format used by IMP.

# Ex:
# OLD:
#   CSN5:K5-CSN5:K6
#   CSN5:K1;K5&K8-CSN7A:K7
#   CSN7A:K3-CSN7A:K11
#   CSN1:K2-CSN1:K3
#   CSN5:K5;K1&K8-CSN5:K15
#   CSN5:K1;K5&K8-CSN7B:K13
#   CSN5:K4-CSN7B:K5
#   CSN5:K8;K1&K5-CSN5:K6

# NEW:

#   CSN5,5,CSN5,6
#   CSN5,1,CSN7A,7
#   CSN5,5,CSN7A,7
#   CSN5,8,CSN7A,7
#   CSN7A,3,CSN7A,11
#   CSN1,2,CSN1,3
#   CSN5,5,CSN5,15
#   CSN5,1,CSN5,15
#   CSN5,8,CSN5,15
#   CSN5,1,CSN7B,13
#   CSN5,5,CSN7B,13
#   CSN5,8,CSN7B,13
#   CSN5,4,CSN7B,5
#   CSN5,8,CSN5,6
#   CSN5,1,CSN5,6
#   CSN5,5,CSN5,6


# load modules
import argparse
import os
import shutil

# load functions.objects
from six import StringIO

# ------------------
#     ARGUMENTS
# ------------------

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', "--file", type=str, required=True,
                    help="Full (preferably) or local path to XL file")
PARSER.add_argument('-o', "--output", type=str, default="xl_out.txt",
                    help="Output file")
PARSER.add_argument('-m', "--mode", type=str, default="all",
                    choices=['all', 'single'],
                    help="Single XL per Ambiguous or All")
ARGS = PARSER.parse_args()

# check arguments
if os.path.exists(ARGS.file):
    FILE = ARGS.file
elif os.path.exists(os.path.join(os.getcwd(), ARGS.file)):
    FILE = os.path.join(os.getcwd(), ARGS.file)
else:
    raise argparse.ArgumentTypeError("Please enter a valid path to a "
                                     "XL position file.")

# CONSTANTS
NTERM_MODS = ['N-term', 'nterm']
CTERM_MODS = ['C-term', 'cterm']

# ------------------
#      CLASSES
# ------------------

class CrosslinkPositionParser(object):
    '''
    Processes the ':', '-' delimited objects, along with the amibiguous
    residue objects.
    '''

    def __init__(self, fileobj):
        super(CrosslinkPositionParser, self).__init__()

        self.fileobj = fileobj
        self.crosslinks = set()

    def run(self):
        '''On start'''

        line = True
        while line:
            line = self.fileobj.readline()
            if line:
                # pylint: disable=maybe-no-member
                line = line.splitlines()[0]
                self.process_line(line)

    def process_line(self, line):
        '''Processes a given line to the consistuent crosslinks'''

        if any([i in line for i in NTERM_MODS]):
            line = self._remove_term(line, NTERM_MODS, '1')
        # TODO:
        if any([i in line for i in CTERM_MODS]):
            line = self._remove_term(line, CTERM_MODS, 'TBD')
        # split the link and grab res/prot pairs
        part1, part2 = line.split('-')
        prot1, res1 = part1.split(':')
        prot2, res2 = part2.split(':')
        # need to split the residues
        residues_1 = self._split_residue(res1)
        residues_2 = self._split_residue(res2)
        # now need to add all lines
        if ARGS.mode == 'single':
            self._process_single(prot1, residues_1, prot2, residues_2)
        else:
            self._process_all(prot1, residues_1, prot2, residues_2)

    @staticmethod
    def _remove_term(line, term_mods, replace):
        '''Removes terminal modifications from a given line'''

        for term in term_mods:
            if term in line:
                sub = ':{0}'.format(term)
                line = line.replace(sub, replace)
        return line

    @staticmethod
    def _split_residue(res):
        '''Splits a given residue string '''

        # split subs and flatten
        res = res.split(';')
        res = [i for item in res for i in item.split('&')]
        res = [i for item in res for i in item.split('|')]
        # get rid of residue delimiters
        res = [i[1:] for i in res]
        return res

    def _process_single(self, prot1, residues_1, prot2, residues_2):
        '''Processes only a single of the redundant XL positions'''

        res1 = residues_1[0]
        res2 = residues_2[0]
        self.crosslinks.add((prot1, res1, prot2, res2))

    def _process_all(self, prot1, residues_1, prot2, residues_2):
        '''Processes all of the redundant XL positions'''

        for res1 in residues_1:
            for res2 in residues_2:
                self.crosslinks.add((prot1, res1, prot2, res2))

class MakeOutput(CrosslinkPositionParser):
    '''Makes the output from a given file path'''

    def __init__(self, fileobj):
        super(MakeOutput, self).__init__(fileobj)

        self.buf = StringIO()

    def write_header(self):
        '''Writes the header to the output file'''

        print('prot1,res1,prot2,res2', file=self.buf)

    def write_lines(self):
        '''Writes the crosslinks to file'''

        for crosslink in self.crosslinks:
            crosslink = ','.join(crosslink)
            print(crosslink, file=self.buf)

# ------------------
#       MAIN
# ------------------

def main():
    '''On init'''

    with open(FILE, 'r') as fileobj:
        cls = MakeOutput(fileobj)
        cls.run()
        # process output
        cls.write_header()
        cls.write_lines()
        cls.buf.seek(0)         # if not, empty output

    with open(ARGS.output, 'w') as dst:
        shutil.copyfileobj(cls.buf, dst)

if __name__ == '__main__':
    main()
