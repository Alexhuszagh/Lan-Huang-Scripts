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

# This program aims to convert a .gmm file for simplified reading.

# Ex.:
# OLD:
#   HEADER 3D Gaussian Mixture Model
#   REMARK COMMAND gmconvert -imap emd_2173.map -ng 20
#   REMARK START_DATE Jul 17,2015 18:21:38
#   REMARK END_DATE   Jul 17,2015 18:21:54
#   REMARK COMP_TIME_SEC  16.025257 1.602526e+01
#   REMARK FILENAME emd_2173_20.gmm
#   REMARK NGAUSS 20
#   REMARK COMMENT Corr.Coeff. 0.901609
#   HETATM    1  GAU GAU I   1      32.710  42.856 -32.64
#   0 0.035 0.035
#   REMARK GAUSS   1 W 0.0354812267
#   REMARK GAUSS   1 det  846763.5361033136
#   REMARK GAUSS   1 Cons 0.0000690000
#   REMARK GAUSS   1 M 32.710309 42.855750 -32.639773
#   REMARK GAUSS   1 CovM  xx  135.9549688055 xy  -23.906
#   1392263 xz   15.1371992216
#   REMARK GAUSS   1 CovM  yy   91.5158481038 yz    6.163
#   4941934 zz   73.9106411376

# NEW:
# |num|weight|mean|covariance matrix|
#   |0|0.0413058594461|109.030172464 156.16938915 199.811744906|47.6365906013 3.18872165553 25.9605183623 3.18872165553 48.9172548113 7.58697082845 25.9605183623 7.58697082845 82.6404336747|

# load modules
import argparse
import os
import shutil

# load functions.objects
from collections import defaultdict
from six import StringIO

# ------------------
#     ARGUMENTS
# ------------------

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-f', "--file", type=str, required=True,
                    help="Full (preferably) or local path to GMM file")
PARSER.add_argument('-o', "--output", type=str, default="out.gmm.txt",
                    help="Output file")
ARGS = PARSER.parse_args()

# check arguments
if os.path.exists(ARGS.file):
    FILE = ARGS.file
elif os.path.exists(os.path.join(os.getcwd(), ARGS.file)):
    FILE = os.path.join(os.getcwd(), ARGS.file)
else:
    raise argparse.ArgumentTypeError("Please enter a valid path to a "
                                     "GMM file.")

# ------------------
#      FUNCTIONS
# ------------------


def isnumber(value):
    '''Checks to see if the value is a number'''

    try:
        float(value)
        return True
    except ValueError:
        return False

# ------------------
#      CLASSES
# ------------------


class GmmParser(object):
    '''Parsers the core GMM file'''

    def __init__(self, fileobj):
        super(GmmParser, self).__init__()

        # bind instance attributes
        self.fileobj = fileobj
        self.gaussians = defaultdict(dict)
        self.gauss = None
        self.ngauss = None

    def run(self):
        '''On start'''

        line = True
        while line:
            line = self.fileobj.readline()
            if line:
                # pylint: disable=maybe-no-member
                line = line.splitlines()[0]
                self.find_parser(line)

    def find_parser(self, line):
        '''Finds the appropriate parser for the line'''

        if line.startswith("REMARK "):
            line = line[len("REMARK "):]
            self.parse_remark(line)
        # elif line.startswith("HEADER"):
        #     pass
        # elif line.startswith("HETATM"):
        #     pass

    def parse_remark(self, line):
        '''
        Parses a remark, which can either be header information
        or gaussian information.
        '''

        if line.startswith("NGAUSS"):
            # store ngauss info
            self.ngauss = int(line[len("NGAUSS "):])
        # elif line.startswith("COMMAND"):
        #     pass
        # elif line.startswith("START_DATE"):
        #     pass
        # elif line.startswith("END_DATE"):
        #     pass
        # elif line.startswith("COMP_TIME_SEC"):
        #     pass
        # elif line.startswith("FILENAME"):
        #     pass
        # elif line.startswith("COMMENT"):
        #     pass
        elif line.startswith("GAUSS"):
            self.parse_gaussian(line)

    def parse_gaussian(self, line):
        '''Parses the gaussian output'''

        # grab values
        line = line[len("GAUSS "):].split()
        # adjust for 1-index
        num = int(line[0]) - 1
        var = line[1]
        values = line[2:]
        # check consistency
        assert num < self.ngauss if self.ngauss else True
        if var == 'W':
            self.gaussians[num]['weight'] = float(values[0])
        # elif var == 'det':
        #     self.gaussians[num]['det'] = values[0]
        # elif var == 'Cons':
        #     self.gaussians[num]['Cons'] = values[0]
        if var == 'M':
            self.gaussians[num]['mean'] = [float(i) for i in values]
        if var == 'CovM':
            self.gaussians[num].setdefault('CovM', [])
            values = [float(i) for i in values if isnumber(i)]
            self.gaussians[num]['CovM'] += values


class MakeOutput(GmmParser):
    '''Makes the output from a given file path'''

    def __init__(self, fileobj):
        super(MakeOutput, self).__init__(fileobj)

        self.buf = StringIO()

    def write_header(self):
        '''Writes the header to the output file'''

        print('#|num|weight|mean|covariance matrix|', file=self.buf)

    def write_lines(self):
        '''Writes the gaussian models to file'''

        # write gaussians to file
        keys = sorted(self.gaussians)
        for key in keys:
            # grab data
            gaussian = self.gaussians[key]
            weight = gaussian['weight']
            mean = ' '.join([str(i) for i in gaussian['mean']])
            covm = self.process_covariance(gaussian)
            # write to file
            line = '|{0}|{1}|{2}|{3}|'.format(key, weight, mean, covm)
            print(line, file=self.buf)

    @staticmethod
    def process_covariance(gaussian):
        '''
        Processes the covariance matrix, which is stored by gmmconvert
        as 6 variables, when it is a 3x3 symmetric matrix.

        [[xx, xy, xz],         [[xx xy xz],
         [yx, yy, yz].    ->    [yy yz zz]]
         [zx, zy, zz]]

         Need to revert it.
        '''

        # pylint: disable=invalid-name
        # type cast
        covm = [str(i) for i in gaussian['CovM']]
        xx, xy, xz, yy, yz, zz = covm
        return ' '.join([xx, xy, xz, xy, yy, yz, xz, yz, zz])

# ------------------
#       MAIN
# ------------------


def main():
    '''On init'''

    with open(FILE, 'r') as fileobj:
        cls = MakeOutput(fileobj)
        cls.run()
        cls.write_header()
        cls.write_lines()
        cls.buf.seek(0)         # if not, empty output

    with open(ARGS.output, 'w') as dst:
        shutil.copyfileobj(cls.buf, dst)

if __name__ == '__main__':
    main()
