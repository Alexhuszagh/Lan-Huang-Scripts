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

# This program aims to extract a pdb file to a FASTA format meant for
# importation into the Integrative Modeling Platform:
#   integrativemodeling.org
#   Copyright 2007-2015 IMP Inventors.
#   For additional information about IMP, see <http://integrativemodeling.org>.

# This program is NOT a part of IMP, simply meant as a utility for IMP.

# Ex.:
# OLD:
#   HEADER    LECTIN                                  12
#   TITLE     PHYTOHEMAGGLUTININ-L
#   COMPND    MOL_ID: 1;
#   COMPND   2 MOLECULE: PHYTOHEMAGGLUTININ-L;
#   COMPND   3 CHAIN: A, B, C, D;
#   COMPND   4 SYNONYM: LEUCOAGGLUTINATING PHYTOHEMAGGLU
#   SOURCE    MOL_ID: 1;
#   SOURCE   2 ORGANISM_SCIENTIFIC: PHASEOLUS VULGARIS;
#   SOURCE   3 ORGANISM_TAXID: 3885;
#   SOURCE   4 ORGAN: SEED;
#   SOURCE   5 OTHER_DETAILS: PURIFIED PHA-L WAS PURCHAS
#   KEYWDS    GLYCOPROTEIN, PLANT DEFENSE PROTEIN, LECTI
#   EXPDTA    X-RAY DIFFRACTION
#   AUTHOR    T.HAMELRYCK,R.LORIS
#   REVDAT   3   13-JUL-11 1FAT    1       VERSN

# NEW:
#   >1WCM:A|PDBID|CHAIN|SEQUENCE
#   MVGQQYSSAPLRTVKEVQFGLFSPEEVRAISVAKIRFPETMDETQTRAKIGGLNDPRLGSIDRNLKCQT
#   CQEGMNECPGH
#   FGHIDLAKPVFHVGFIAKIKKVCECVCMHCGKLLLDEHNELMRQALAIKDSKKRFAAIWTLCKTKMVCETDV
#   PSEDDPTQ

# load modules
import argparse
import os
import shutil

from Bio import PDB

# import functions/objects
from six import StringIO

from Bio.SeqUtils import seq1

# ------------------
#     ARGUMENTS
# ------------------

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', "--file", type=str,
                    help="Full (preferably) or local path to file")
PARSER.add_argument('-c', "--code", type=str,
                    help="PDB code to enter")
PARSER.add_argument('-l', "--line-length", type=int, default=80,
                    help="Characters per line")
PARSER.add_argument('-o', "--output", type=str, default="out.fasta",
                    help="Characters per line")
ARGS = PARSER.parse_args()

# check arguments
if ARGS.code and len(ARGS.code) != 4:
    raise argparse.ArgumentTypeError("Please enter a valid PDB code if "
                                     "downloading a sequence.")
elif ARGS.code:
    FILE = None
elif ARGS.file and os.path.exists(ARGS.file):
    FILE = ARGS.file
elif ARGS.file and os.path.exists(os.path.join(os.getcwd(), ARGS.file)):
    FILE = os.path.join(os.getcwd(), ARGS.file)
elif ARGS.file:
    raise argparse.ArgumentTypeError("Please enter a valid path to a "
                                     "PDB file.")
elif ARGS.code is None and ARGS.file is None:
    raise argparse.ArgumentTypeError("Please enter either a file path or "
                                     "a PDB code.")

# CONSTANTS
LINE_LENGTH = ARGS.line_length

# ------------------
#      CLASSES
# ------------------

class ParsePDB(object):
    '''Core parser for the PDB, which handles IO to form sequences'''

    def __init__(self):
        super(ParsePDB, self).__init__()

        # bind insstanee attributes
        self.parser = PDB.PDBParser(QUIET=True)
        self.file_io = PDB.PDBIO()
        self.pdbl = PDB.PDBList()

    def get_structure(self, code=None, path=None):
        '''Acquires the structure from a PDB code or a file path'''

        # break if no path provided
        assert code or path
        if code:
            return self.open_code(code)
        else:
            return self.open_file(path)

    def open_code(self, code):
        '''Opens a PDB file from the internet or from file'''

        path = self.pdbl.retrieve_pdb_file(code)
        return self.parser.get_structure(code, path)

    def open_file(self, path):
        '''Opens the file and returns the structure'''

        name = os.path.splitext(os.path.basename(path))[0]
        return self.parser.get_structure(name, path)

class MakeSequence(ParsePDB):
    '''Makes the sequence from a given PDB path or code'''

    def __init__(self, code=None, path=None):
        super(MakeSequence, self).__init__()

        # bind instance attributes
        self.structure = self.get_structure(code, path)
        # only need first model -- same sequence
        self.model = self.structure.child_list[0]
        self.chains = self.model.child_dict
        self.code = code or os.path.splitext(os.path.basename(path))[0]
        self.buf = StringIO()

    def run(self):
        '''On start'''

        chain_list = sorted(self.chains)
        for chain in chain_list:
            self.write_chain(chain)

    def write_chain(self, key):
        '''Writes the chain information to sequence'''

        # make our output
        header = '>{0}:{1}|PDBID|CHAIN|SEQUENCE'.format(self.code, key)
        print(header, file=self.buf)
        # init our sequence
        seq = []
        # grab attributes
        chain = self.chains[key]
        residues = chain.get_residues()
        # grab sequences
        for res in residues:
            seq.append(seq1(res.resname))
        # write sequence
        length = len(seq)
        for index in range(0, length, LINE_LENGTH):
            out = ''.join(seq[index:index+LINE_LENGTH])
            print(out, file=self.buf)

# ------------------
#       MAIN
# ------------------

def main():
    '''On init'''

    # grab code path
    cls = MakeSequence(code=ARGS.code, path=FILE)
    cls.run()
    cls.buf.seek(0)         # if not, empty output
    with open(ARGS.output, 'w') as dst:
        shutil.copyfileobj(cls.buf, dst)

if __name__ == '__main__':
    main()
