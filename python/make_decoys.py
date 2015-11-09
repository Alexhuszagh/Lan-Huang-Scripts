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

from __future__ import print_function

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# This script aims reads a given FASTA file, and then generates target
# decoys in either MS/MS mode (reversed) or Peptide Mass Fingerprinting
# mode (shuffled, based on the hash of the sequence).

# Ex.:
# python make_decoys.py --fasta P46406.fasta --out P46406_decoys.fasta

# load modules
import argparse
import os
import random

# ARGUMENTS
PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', "--fasta", type=str, help="FASTA file",
                    required=True)
PARSER.add_argument('-o', "--out", type=str, help="Output file",
                    default="out.fasta")
PARSER.add_argument('-m', "--mode", type=str, help="Decoy mode",
                    choices=['msms', 'pmf'], default="msms")
ARGS = PARSER.parse_args()


class ParseFasta(object):
    '''
    Parses the given FASTA file in a generator method, yielding
    each new sequence and header to produce a new decoy
    '''

    def __init__(self, fileobj):
        super(ParseFasta, self).__init__()

        self.fileobj = fileobj

    def __iter__(self):
        '''Yields the header and processed sequences by entry'''

        for spacers, metadata, sequence in self.get_entries():
            metadata = os.linesep.join(metadata)
            sequence = self.convert_sequence(sequence)

            yield spacers, metadata, sequence

    def get_entries(self):
        '''Generates an iterator which returns all the entries in the file'''

        remainder = ''
        while True:
            spacers, metadata, sequence, remainder = self.find_entry(remainder)
            if metadata:
                yield spacers, metadata, sequence
            else:
                break


    def find_entry(self, remainder):
        '''Iterator yielding each seperate entry in a FASTA file'''

        spacers = 0
        metadata = []
        if remainder:
            metadata.append(remainder)
            remainder = ''
        sequence = []
        for line in self.fileobj:
            line = line.splitlines()[0]

            if not line:
                spacers += 1

            elif line.startswith(('>',)) and not sequence:
                metadata.append(line)

            elif line.startswith(('>',)):
                # new scan. sequence info for previous already added
                remainder = line
                break

            else:
                sequence.append(line)

        return spacers, metadata, sequence, remainder

    def convert_sequence(self, sequence):
        '''Converts the sequence to a stable decoy'''

        length = len(sequence[0])
        sequence = ''.join(sequence)

        if ARGS.mode == 'msms':
            sequence = sequence[::-1]
        elif ARGS.mode == 'pmf':
            sequence = self.shuffle_sequence(sequence, seed=True)
        sequence_list = []
        for index in range(0, len(sequence), length):
            sequence_list.append(sequence[index: index+length])
        sequence = os.linesep.join(sequence_list)

        return sequence

    @staticmethod
    def shuffle_sequence(sequence, seed=False):
        '''
        Randomizes a protein sequence and shuffles it for peptide mass
        fingerprint decoys.
        '''

        seq = list(sequence)
        if seed:
            # in Python 2 and 3, random.seed(hashable) is consistent and
            # independent of PYTHONHASHSEED, although order differs 2 to 3
            random.seed(sequence)

        random.shuffle(seq)
        return ''.join(seq)


class Writer(ParseFasta):
    '''Writes the new FASTA sequence information to file'''

    def __init__(self, fasta, outfile):
        super(Writer, self).__init__(fasta)

        self.outfile = outfile

        for spacers, metadata, sequence in self:

            while spacers:
                print(file=self.outfile)
                spacers -= 1

            print(metadata, file=self.outfile)
            print(sequence, file=self.outfile)


def main():
    '''On script execution'''

    with open(ARGS.fasta) as fasta:
        with open(ARGS.out, 'w') as out:
            Writer(fasta, out)


if __name__ == '__main__':
    main()
