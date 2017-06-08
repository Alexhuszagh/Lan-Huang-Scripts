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

# This program aims to split linkages to a CSV file.

# Ex.:
# OLD:
#   Ecm29:K1438-Ecm29:K1475
#   Ecm29:K879-Ecm29:K949
#   Ecm29:K313;K315&K321-Ecm29:K313;K315;K321

# NEW:
#   Ecm29	K1438	Ecm29	K1475
#   Ecm29	K879	Ecm29	K949
#   Ecm29	K313;K315&K321	Ecm29	K313;K315;K321

# Ex.:
# INPUT:
#   $ python split_linkages.py -f=file.csv

# load modules
import argparse
import itertools as it
import os


# ARGUMENTS
# ---------

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', "--file", type=str, required=True,
                    help="Full (preferably) or local path to CSV file")
PARSER.add_argument('-o', "--output", type=str, default="linkages_out.txt",
                    help="Output file")
ARGS = PARSER.parse_args()


# FUNCTIONS
# ---------


def split_csv(fin):
    '''Split lines in the CSV file'''

    for line in fin:
        line = line.rstrip()
        items = line.split("-")
        yield list(it.chain.from_iterable(i.split(":") for i in items))


def write_data(iterator, fout):
    '''Write linkages to file'''

    for item in iterator:
        print("\t".join(item), file=fout)


def main():
    '''On init'''

    with open(os.path.expanduser(ARGS.file), 'r') as fin:
        with open(ARGS.output, 'w') as fout:
            write_data(split_csv(fin), fout)

if __name__ == '__main__':
    main()
