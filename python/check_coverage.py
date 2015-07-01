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

from __future__ import print_function

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# KNOWN ISSUES:
#   With enough proteins entered, the UniProt KB database will send
#   a 503 gateway error due to refused service.

# This program aims to analyze sequence coverage from a batch list
# of protein identifiers, with optional custom labels given.
# This is useful for refining experiments based on various digestive
# conditions, such as different proteases, different denaturants, etc.
# in order to optimize for a target bait sequence.

# Ex.:
# INPUT:
#   $ python check_coverage.py -c Trypsin Chymo -p P46406 P00761 -f a.txt b.txt

# OUTPUT:
# -------------------------
# >sp|P46406|G3P_RABIT Glyceraldehyde-3-phosphate dehydrogenase OS=Oryctolagus cuniculus GN=GAPDH PE=1 SV=3
#
#             0: MVKVGVNGFGRIGRLVTRAAFNSGKVDVVAINDPFIDLHYMVYMFQYDSTHGKFHGTVKA
# Trypsin :      +++++++++++++++++++++++++                            +++++++
# Chymo :                                                             +++++++
#
#            60: ENGKLVINGKAITIFQERDPANIKWGDAGAEYVVESTGVFTTMEKAGAHLKGGAKRVIIS
# Trypsin :      ++++++++++++++++++++++++                     +++++++++++++++
# Chymo :        ++++
#
#           120: APSADAPMFVMGVNHEKYDNSLKIVSNASCTTNCLAPLAKVIHDHFGIVEGLMTTVHAIT
# Trypsin :      +++++++++++++++++
# Chymo :
#
#           180: ATQKTVDGPSGKLWRDGRGAAQNIIPASTGAAKAVGKVIPELNGKLTGMAFRVPTPNVSV
# Trypsin :          +++++++++++                              +++++++++++++++
# Chymo :
#
#           240: VDLTCRLEKAAKYDDIKKVVKQASEGPLKGILGYTEDQVVSCDFNSATHSSTFDAGAGIA
# Trypsin :      +++++++++++++++++++++++++++++
# Chymo :              +++++++++++ +++++++++++
#
#           300: LNDHFVKLISWYDNEFGYSNRVVDLMVHMASKE
# Trypsin :                           ++++++++++++
# Chymo :
#
# -------------------------
# >sp|P00761|TRYP_PIG Trypsin OS=Sus scrofa PE=1 SV=1
#
#             0: FPTDDDDKIVGGYTCAANSIPYQVSLNSGSHFCGGSLINSQWVVSAAHCYKSRIQVRLGE
# Trypsin :
# Chymo :
#
#            60: HNIDVLEGNEQFINAAKIITHPNFNGNTLDNDIMLIKLSSPATLNSRVATVSLPRSCAAA
# Trypsin :
# Chymo :
#
#           120: GTECLISGWGNTKSSGSSYPSLLQCLKAPVLSDSSCKSSYPGQITGNMICVGFLEGGKDS
# Trypsin :
# Chymo :
#
#           180: CQGDSGGPVVCNGQLQGIVSWGYGCAQKNKPGVYTKVCNYVNWIQQTIAAN
# Trypsin :
# Chymo :
#
# -------------------------

# load modules
import argparse
import os
import six
if six.PY2:
    import httplib
else:
    import http.client
import sys

import numpy as np
import pandas as pd

# constants
SERVER = {
    'host': 'www.uniprot.org',
    'path': '/',
    'domain': 'uniprot',
    'suffix': '.fasta'
}
PATH = os.getcwd()
PROTEIN_COLUMN = 'Acc #'
PEPTIDE_COLUMN = 'DB Peptide'

# args
PARSER = argparse.ArgumentParser()
PARSER.add_argument("-c", "--conditions", nargs='+',
                    help="labels for experiments")
PARSER.add_argument("-f", "--files", nargs='+', required=True,
                    help="Input Tab-Delimited Text Files")
PARSER.add_argument("-p", "--protein", type=str, nargs='+',
                    required=True, help="UniProt ID")
PARSER.add_argument("-o", "--output", type=str,
                    help="Optional output file, default to STDOUT")
ARGS = PARSER.parse_args()

# process args
if not all([len(i) in [6, 10] for i in ARGS.protein]):
    raise argparse.ArgumentTypeError('Please enter a valid UniProt ID')
if len(ARGS.files) != len(ARGS.conditions):
    raise argparse.ArgumentTypeError(
        'Must enter an equal number of conditions and files.')
if not ARGS.conditions:
    ARGS.conditions = ARGS.files
# make local files global
ARGS.files = [os.path.join(PATH, i) for i in ARGS.files]
if not all([os.path.exists(i) for i in ARGS.files]):
    raise argparse.ArgumentTypeError(
        'Please enter valid Protein Prospector result files.')
# pylint: disable=maybe-no-member
try:
    DATAFRAMES = []
    for name in ARGS.files:
        with open(name, 'r') as fileobj:
            DF = pd.read_csv(fileobj, header=2, sep='\t', engine='python')
            # check if needed information available
            assert PROTEIN_COLUMN in DF.columns
            assert PEPTIDE_COLUMN in DF.columns
            # add to dataframe list
            DATAFRAMES.append(DF)
except (IOError, OSError, AssertionError):
    raise argparse.ArgumentTypeError(
        'Please enter valid Protein Prospector result files.')
# pylint: enable=maybe-no-member

# STDOUT
if ARGS.output:
    OUTPUT = os.path.join(PATH, ARGS.output)
    if os.path.exists(OUTPUT):
        raise argparse.ArgumentTypeError('Output file name already exists.')
    STDOUT = open(OUTPUT, 'w')
else:
    STDOUT = sys.stdout

# ------------------
#       UTILS
# ------------------

def find_all(value, sub):
    """Find all occurrences within a string"""

    start = 0
    while True:
        start = value.find(sub, start)
        if start == -1:
            return
        yield start
        start += len(sub)

# ------------------
#    SEQ FUNCTIONS
# ------------------

def connect_uniprot(protein, host=SERVER['host']):
    '''Connects to the UniProt database and makes the query'''

    # establish connection
    if six.PY2:
        conn = httplib.HTTPConnection(host)
    else:
        conn = http.client.HTTPConnection(host)
    # make query
    url = (SERVER['path'] + SERVER['domain'] + SERVER['path'] +
           protein + SERVER['suffix'])
    # post request and read response
    conn.request('GET', url)
    response = conn.getresponse()
    value = response.read()
    if six.PY3:
        value = value.decode('utf-8')
    return value

def get_sequences(proteins=ARGS.protein):
    '''Grabs all the UniProt sequences from a list of UniProt identifiers'''

    # init return
    sequences = []
    # grab sequences
    for protein in proteins:
        sequence = connect_uniprot(protein)
        # remove header
        sequences.append(sequence)
    return sequences

# ------------------
# PEPTIDE FUNCTIONS
# ------------------

def protein_coverage(dataframe, protein, sequence):
    '''Returns the protein coverage for a given UniProt ID bait and
    sequence.
    '''

    # init return
    sequence = ''.join(sequence[1:])
    data = {k: False for k in range(len(sequence))}
    # grab sequences
    indexes, = np.where(dataframe[PROTEIN_COLUMN] == protein)
    sequences = set(dataframe[PEPTIDE_COLUMN][indexes].tolist())
    # iterate over sequences
    for seq in sequences:
        positions = list(find_all(sequence, seq))
        #print(positions, len(seq), seq)
        for position in positions:
            for index in range(len(seq)):
                key = index + position
                data[key] = True
    return data

def get_coverage(dataframes, protein, sequence):
    '''Iterativelt returns the protein coverage for each df within
    dataframes.
    '''

    # init return
    coverage_list = []
    for dataframe in dataframes:
        coverage = protein_coverage(dataframe, protein, sequence)
        coverage_list.append(coverage)
    return coverage_list

def process_condition(header, coverage, sequence, index):
    '''Processes the header to give the conditions coverage of the
    sequence.
    '''

    # grab parameter lengths to determine range
    length = len(sequence[index])
    offset = len(''.join(sequence[1:index]))
    # iteratively add null string or +
    keys = range(offset, offset+length)
    for key in keys:
        value = coverage[key]
        # add '+' if True
        if value is True:
            header += '+'
        else:
            header += ' '
    return header

# ------------------
#    OUT FUNCTIONS
# ------------------

def start_sequence(sequence):
    '''Starts the lines for a new protein'''

    print('-------------------------', file=STDOUT)
    print(sequence[0], file=STDOUT)
    print(file=STDOUT)

def write_sequence_line(sequence, index, indent=15):
    '''Writes a sequence line with indentation to file'''

    # grab offset to add to file
    offset = str(len(''.join(sequence[1:index]))) + ': '
    offset_length = len(offset)
    # init line
    line = ' '*(indent-offset_length)
    line += offset
    line += sequence[index]
    print(line, file=STDOUT)

def write_blank_line():
    print(file=STDOUT)

def write_condition(header, coverage, sequence, index):
    '''Writes the condition with coverage to file'''

    output = process_condition(header, coverage, sequence, index)
    print(output, file=STDOUT)

def close_sequence():
    '''Closes the lines for a protein'''

    print('-------------------------', file=STDOUT)
    print(file=STDOUT)

def get_header(condition, total=12):
    '''Grabs a 35 character header from the given condition'''

    length = min([len(condition), total])
    header = condition[:total]
    header = ''.join([header, ' : '])
    header = ''.join([header, ' '*(total-length)])
    return header

# pylint: disable=dangerous-default-value
def process_output(sequences, conditions=ARGS.conditions,
                   proteins=ARGS.protein, dataframes=DATAFRAMES):
    '''Writes the output to str and returns it.'''

    for idx, sequence in enumerate(sequences):
        protein = proteins[idx]
        # print header
        sequence = sequence.splitlines()
        start_sequence(sequence)
        # grab coverage conditions for each file
        coverage_list = get_coverage(dataframes, protein, sequence)
        for index in range(1, len(sequence)):
            # write sequence
            write_sequence_line(sequence, index)
            # grab conditions and write coverage
            for cond_idx, condition in enumerate(conditions):
                header = get_header(condition)
                # grab dataframe and map sequence coverage
                coverage = coverage_list[cond_idx]
                write_condition(header, coverage, sequence, index)
            write_blank_line()
    close_sequence()
# pylint: enable=dangerous-default-value

# ------------------
#       MAIN
# ------------------

def main():
    '''On start'''

    sequences = get_sequences()
    process_output(sequences)

if __name__ == '__main__':
    main()
    # close any remaining files
    if ARGS.output:
        STDOUT.close()
