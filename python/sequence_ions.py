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

from __future__ import division, print_function

__author__ = "Alex Huszagh"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@gmail.com"

# This script aims to provide an interface to simplify the generation of
# high quality figures for sequencing ions, by automatically genrating
# highly customizable images using a TEX format.

# Ex.:
# python sequence_ions.py --peptide SAM_PL^ER_{SAM}PLER^{SA}MPLER
# --ions y1 y2 y3 y4 y10 y13 b1 b2 b3 b5 b10 b13 --color red
# --format png --output output.png

# python sequence_ions.py --peptide
# A_{FISH}-SAM_PL^ER_{SAM}PLER^{SA}MPLER-FISHES --ions y1 y2 y3 y4 y10 y13
# b1 b2 b3 b5 b10 b13 --color red --same-line --format png --output output.png

# python sequence_ions.py --peptide
# "A_{FISH}-SAM_PL^ER_{SAM}PLER^{SA}MP(test)LER-FISHES"
# --ions y1 y2 y3 y4 y10 y13 b1 b2 b3 b5 b10 b13
# --color red --same-line --format png --output output.png

# http://i.imgur.com/04kMGDM.png

# Future improvements:
#   * Needs to handle internal ()

# load modules
import argparse
import os
import re
import sys

import matplotlib
from PySide import QtCore, QtGui

matplotlib.rcParams['mathtext.default'] = 'regular'

# CONSTANTS

QLABEL_BANNER_STYLE = '''
QLabel {
    font-weight: bold;
    font-size: 20pt;
};
'''

AMINO_ACIDS = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N',
               'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']
# display constans
AXIS_0 = 0
HEIGHT = 200
WIDTH = 100

# REGEXES
ION = re.compile('^(b|y|B|Y)([0-9]+)$')
AA_SET = '[{0}]'.format(''.join(AMINO_ACIDS +
                                [i.lower() for i in AMINO_ACIDS]))
_ALNUM = '[a-zA-Z0-9]'
ALNUM = re.compile(_ALNUM)
NOT_ALNUM = re.compile('[^a-zA-Z0-9]')
# need at least one preceeding AA, then any number of <AA>_{<AA>}
# pairs, where each group can be <AA>, _|^<AA>, {<AA>}, _|^{<AA>}
RES = r'(?:%(aa)s%(ps)s[_^]\{\w+\}|%(aa)s%(ps)s[_^]\w|' \
      r'\{%(aa)s+\}|%(aa)s%(ps)s)' % {'aa': AA_SET, 'ps': '(?:\(\w+\))?'}
TERM = r'(?:%(alnum)s+[_^]\{\w+\}|%(alnum)s+[_^]%(alnum)s|' \
       r'%(alnum)s+\{%(alnum)s+\}|%(alnum)s+)' % {'alnum': _ALNUM}
NTERM = '^(%s-)' % TERM
CTERM = '(-%s)$' % TERM
PEPTIDE = re.compile(r'^(?:%s-)?%s+(?:-%s)?$' % (TERM, RES, TERM))
# grab out length pattern
LEN = re.compile(r'(?:[_^]\{\w+\}|[_^]\w)')
SUBSCRIPT_OFFSET = re.compile(r'(?:[_^]\{(\w+)\}|[_^](\w))')
SEQUENCE_OFFSET = re.compile(r'(\(\w+\))')

# ------------------
#     ARGUMENTS
# ------------------


def get_length(peptide):
    '''Returns the peptide length which removes subscripts/underscores'''

    # remove all internal (item)
    peptide = SEQUENCE_OFFSET.sub('', peptide)
    return len(LEN.sub('', peptide))


def get_subscript_offset(peptide):
    '''
    Extracts all the subscripted and superscripted characters and
    returns the number of characters.
    '''

    matches = SUBSCRIPT_OFFSET.findall(peptide)
    matches = ''.join([''.join(i) for i in matches])
    return len(matches)


def get_sequence_offset(peptide):
    '''
    Extracts all the subscripted and superscripted characters and
    returns the number of characters.
    '''

    matches = SEQUENCE_OFFSET.findall(peptide)
    matches = ''.join(matches)
    return len(matches)


def get_term_offset(term_sequence):
    '''Returns the length of a terminal sequence without the "-""'''

    subscript_offset = get_subscript_offset(term_sequence)
    # remove offending sequence
    term_sequence = SUBSCRIPT_OFFSET.sub('', term_sequence)
    sequence_offset = len(term_sequence)

    return (SUBSCRIPT_RATIO*FONTSIZE*subscript_offset +
            FONTSIZE*sequence_offset + FONTSIZE)


def check_ions(peptide, ions):
    '''Validates the input ion choices'''

    try:
        # ensure all are matches
        matches = [ION.match(i) for i in ions]
        assert all(matches)
        if matches:
            # now ensure none are larger than the peptides
            highest = max([int(i.group(2)) for i in matches])
            length = get_length(peptide)
            # cannot have an ion longer than the peptide
            assert highest < length
    except AssertionError:
        raise argparse.ArgumentTypeError("Please enter valid sequencing ions, "
                                         "like \"b1\" or \"y4\".")

PARSER = argparse.ArgumentParser()
PARSER.add_argument('-p', "--peptide", type=str, help="Peptide sequenced")
PARSER.add_argument('-i', "--ions", type=str, nargs="+",
                    help="Sequencing ions")
PARSER.add_argument('-c', "--color", type=str, default="blue",
                    help="Color for the sequencing bars")
PARSER.add_argument('-o', "--output", type=str, help="Outfile path")
PARSER.add_argument('-f', "--format", type=str, default="png",
                    choices=['png', 'svg', 'pdf', 'ps', 'eps'],
                    help="Output format for the image")
PARSER.add_argument('-k', "--keep-lines", action="store_true",
                    help="Keep lines for no sequencing ions")
PARSER.add_argument('-s', '--same-line', action='store_true',
                    help='Put sequencing ion text at same height as line')
PARSER.add_argument('-df', '--different-line-font', type=float, default=0.6,
                    help='Different line font size relative to font')
PARSER.add_argument('-sf', '--same-line-font', type=float, default=0.4,
                    help='Same line font size relative to font')
PARSER.add_argument('-l', '--line-width', type=int, choices=range(2, 21),
                    default=5, help="Line width")
ARGS = PARSER.parse_args()

if ARGS.peptide is None and ARGS.ions is not None:
    raise argparse.ArgumentTypeError("Please enter a valid peptide before "
                                     "specifying sequencing ions.")
elif not (0.2 <= ARGS.same_line_font <= 0.5):
    raise argparse.ArgumentTypeError("Please enter a valid same line font "
                                     "size from 0.2 to 0.5.")
elif not (0.2 <= ARGS.different_line_font <= 1):
    raise argparse.ArgumentTypeError("Please enter a valid different line "
                                     "font size from 0.2 to 1.0.")
if ARGS.peptide is not None:
    if not PEPTIDE.match(ARGS.peptide):
        raise argparse.ArgumentTypeError("Please enter a valid peptide "
                                         "sequence. Supports TEX-like "
                                         "subscript and superscripts.")
if ARGS.ions is not None:
    check_ions(ARGS.peptide, ARGS.ions)
if not ARGS.same_line:
    HEIGHT += 200

# DEPENDENT FONT SETTINGS
# font constants
FONTSIZE = 50
if ARGS.same_line:
    SUB_FONTSIZE = FONTSIZE*ARGS.same_line_font
else:
    SUB_FONTSIZE = FONTSIZE*ARGS.different_line_font
# define height for font to be set at
FONT_HEIGHT = (HEIGHT//2) - (FONTSIZE//2)
# define the font position
FONT_POSITION = (WIDTH//2)-(FONTSIZE//2)
SUBSCRIPT_RATIO = 0.75
# line width settings
SAMELINE_LENGTH = 20
DIFFERENT_LINE_RATIO = 0.75
# need to set the minimum and max to flank the rest
VERT_LINE_MIN = HEIGHT/2 - 5*FONTSIZE/4
VERT_LINE_MAX = HEIGHT/2 + 5*FONTSIZE/4
VERTICAL_LINE_LENGTH = VERT_LINE_MAX - VERT_LINE_MIN

# pylint: disable=too-few-public-methods, invalid-name

# ------------------
#      WIDGETS
# ------------------


class IonSelection(QtGui.QWidget):
    '''Ion selection upon peptide selection'''

    def __init__(self, peptide, parent=None):
        super(IonSelection, self).__init__(parent)

        # init window
        self.setWindowTitle("Select Ions")
        self.setObjectName("IonSelection")
        # bind instance attributes
        self.peptide = peptide
        # init the layout
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter |
                                 QtCore.Qt.AlignCenter)
        # init y-ions
        y_label = QtGui.QLabel("Y-Ions")
        y_label.setStyleSheet(QLABEL_BANNER_STYLE)
        self.layout.addWidget(y_label)
        self.y_ions = []
        self.add_ions('y', self.y_ions)
        # init b-ions
        b_label = QtGui.QLabel("B-Ions")
        b_label.setStyleSheet(QLABEL_BANNER_STYLE)
        self.layout.addWidget(b_label)
        self.b_ions = []
        self.add_ions('b', self.b_ions)
        # add to layouts
        submit = QtGui.QPushButton("Submit")
        submit.clicked.connect(self.parent().make_plot)
        self.layout.addWidget(QtGui.QLabel(""))
        self.layout.addWidget(submit)

    def add_ions(self, label, lst):
        '''
        Makes the y and b-ion series and stores them to a list.
        :
            label -- "y" or "b"
            lst -- storage list for ion series
        '''

        length = self.parent().get_length(self.peptide)
        for idx in range(0, length - 1, 5):
            hlayout = QtGui.QHBoxLayout()
            limit = min([idx+5, length - 1])
            for i in range(idx, limit):
                btn = QtGui.QPushButton('{0}{1}'.format(label, i+1), self)
                btn.setCheckable(True)
                btn.setChecked(False)
                lst.append(btn)
                hlayout.addWidget(btn)
            self.layout.addLayout(hlayout)


class PeptideSelection(QtGui.QWidget):
    '''Peptide selection widget interface'''

    def __init__(self, parent=None):
        super(PeptideSelection, self).__init__(parent)

        # init window
        self.setWindowTitle("Select a Peptide")
        self.setObjectName("PeptideSelection")
        # bind instance attributes
        self.layout = QtGui.QVBoxLayout(self)
        self.layout.setAlignment(QtCore.Qt.AlignHCenter |
                                 QtCore.Qt.AlignCenter)
        header = QtGui.QLabel("Input a Peptide")
        header.setStyleSheet(QLABEL_BANNER_STYLE)
        label = QtGui.QLabel("Peptide: ", self)
        self.peptide = QtGui.QLineEdit("Peptide")
        submit = QtGui.QPushButton("Submit")
        submit.clicked.connect(self.parent().init_ions)
        # add to layouts
        self.layout.addWidget(header)
        hlayout = QtGui.QHBoxLayout()
        hlayout.addWidget(label)
        hlayout.addWidget(self.peptide)
        self.layout.addLayout(hlayout)
        self.layout.addWidget(submit)
        self.show()

# ------------------
#  MAIN APPLICATION
# ------------------


class MainWindow(QtGui.QMainWindow):
    '''Launch Main Window'''

    # n/cterm additions
    _nterm = ''
    _cterm = ''
    # offsets due to additions
    _nterm_offset = 0
    _cterm_offset = 0

    def __init__(self, color, output, peptide=None, ions=None):
        super(MainWindow, self).__init__()

        # bind instance attributes
        self.color = color
        self.peptide = peptide
        self.ions = ions
        self.output = output
        self.offsets = []
        # init main widget
        if peptide is None:
            self.child_widget = PeptideSelection(self)
            self.setCentralWidget(self.child_widget)
        elif ions is None:
            self.init_ions()
        # ions specified on start
        else:
            self._process_peptide()
            self.make_plot()
        self.setStyleSheet("background-color: white")
        self.setFixedSize(300, 300)

    def init_ions(self):
        '''
        Connects the ends of the PeptideSelection signal (upon submit)
        to the ion selection menu.
        '''

        # grab the peptide
        if self.peptide is None:
            self.peptide = self.child_widget.peptide.text()
            self.child_widget.hide()
            self.child_widget.deleteLater()
        self._process_peptide()
        # verify integrity
        if not PEPTIDE.match(self.peptide):
            dialog = QtGui.QMessageBox(text="Please enter a valid peptide",
                                       windowTitle="Input Error", parent=self)
            sys.exit(dialog.exec_())
        else:
            # launch the new window
            self.child_widget = IonSelection(self.peptide, self)
            self.setCentralWidget(self.child_widget)

    def make_plot(self):
        '''
        Connects the ends of the IonSelection signal (upon submit) to
        make the plot and save to file
        '''

        if self.ions is None:
            # need to grab from ion widget
            self._process_ions()
        else:
            # need to split into two categories
            self._split_ions()
        # dynamic imports
        import matplotlib.pyplot as plt
        # grab desktop settings
        app = QtGui.QApplication.instance()
        dpi = app.desktop().logicalDpiX()
        length = self._get_length()
        width = self._get_width()/dpi
        height = HEIGHT/dpi
        # make figure for width/height and set axes
        fig = plt.figure(figsize=(width, height), dpi=dpi)
        axes = self._init_axes(fig)
        # add the data
        self._plot_peptide(axes)
        self._add_lines(axes, length)
        # now save the plot
        self.save_plot(fig, plt)

    def save_plot(self, fig, plt):
        '''Saves the initialized plot to file'''

        if self.output is None:
            func = QtGui.QFileDialog.getSaveFileName
            dialog = func(self, 'Save file as', os.path.expanduser('~'),
                          defaultSuffix='png')
            self.output = dialog[0]
        # if exited, don't save a null string
        if self.output:
            fig.savefig(self.output, bbox_inches='tight', format=ARGS.format,
                        pad_inches=0)
        plt.close()
        # close main app
        sys.exit(0)

    # ------------------
    #       UTILS
    # ------------------

    def _split_ions(self):
        '''
        Splits the argument list ions to two boolean lists.
        :
            ['y1', 'y2', 'y3', 'y4', 'y5', 'b2', 'b3']
                ->[[True, True, True, True, True], [False, True, True, ...]]
            y ions, then b ions
        '''

        length = self._get_length()
        # default off
        ions = [[False]*(length-1), [False]*(length-1)]
        for ion in self.ions:
            # pylint: disable=maybe-no-member
            ion = ion.lower()
            match = ION.match(ion)
            _type = [0, 1][match.group(1) == 'b']
            num = int(match.group(2))-1
            ions[_type][num] = True
        # reassign the ions
        self.ions = ions

    def _process_ions(self):
        '''
        Processes the child ion lists to convert to a boolean list.
        :
            cls.y_ions = [QtGui.QPushButton, ...]
            cls.b_ions = [QtGui.QPushButton, ...]
                ->[[True, True, True, True, True], [False, True, True, ...]]
        '''

        # init values
        cls = self.child_widget
        ions = [[], []]
        for idx, lst in enumerate([cls.y_ions, cls.b_ions]):
            for btn in lst:
                checked = btn.isChecked()
                ions[idx].append(checked)
        # assign the ions
        self.ions = ions

    def _process_peptide(self):
        '''
        Processes the peptide so the TEX codes are simplified, ie,
        removing unnecessary codes for a base expression.
        :
            SAMPL_{L}ER -> SAMPL_{L}ER
            SAMPL{L}ER -> SAMPLER
        '''

        # need a negative look-behind assertion for formatting quues
        # and then to capture solely the text within the {} notation.
        # use the "\\1" formating notation to replace {(group)} with
        # (group)
        pattern = r'(?<![_^()])\{(%s+)\}' % (_ALNUM)
        self.peptide = re.sub(pattern, r'\1', self.peptide)
        # now need to remove N-term, C-term
        nterm_values = re.split(NTERM, self.peptide)
        # match, ['', self._nterm, self.peptide]
        if len(nterm_values) == 3:
            self._nterm = nterm_values[1]
            self._nterm_offset = get_term_offset(self._nterm[:-1])
            self.peptide = nterm_values[2]
        cterm_values = re.split(CTERM, self.peptide)
        # match, [self.peptide, self._cterm, '']
        if len(cterm_values) == 3:
            self.peptide = cterm_values[0]
            self._cterm = cterm_values[1]
            self._cterm_offset = get_term_offset(self._cterm[1:])

    def _get_length(self, peptide=None):
        '''
        Processes the peptide length removing all of the subscripted
        and superscripted characters.
        '''

        peptide = self.peptide if peptide is None else peptide
        return get_length(peptide)

    def _get_subscript_offset(self, peptide=None):
        '''
        Extracts all the subscripted and superscripted characters and
        returns the number of characters.
        '''

        peptide = self.peptide if peptide is None else peptide
        return get_subscript_offset(peptide)

    def _get_sequence_offset(self, peptide=None):
        '''
        Extracts all the parentheses characters.
        '''

        peptide = self.peptide if peptide is None else peptide
        return get_sequence_offset(peptide)

    def _get_width(self):

        length = self._get_length()
        subscript_offset = self._get_subscript_offset()
        sequence_offset = self._get_sequence_offset()
        return (WIDTH*length + SUBSCRIPT_RATIO*FONTSIZE*subscript_offset +
                FONTSIZE*sequence_offset + self._nterm_offset +
                self._cterm_offset)

    # ------------------
    #    PLOT UTILS
    # ------------------

    def _init_axes(self, fig):
        '''Initializes the axes for the current plot'''

        axes = fig.add_subplot(111)
        axes.set_ylim(AXIS_0, HEIGHT)
        # ylim is the width of regular characters + subscript adjustments
        axes.set_xlim(AXIS_0, self._get_width())
        axes.get_xaxis().set_visible(False)
        axes.get_yaxis().set_visible(False)

        return axes

    def _plot_peptide(self, axes):
        '''
        Plots the peptide onto the axes, at fixed width with 25-50-25,
        where 25 is the leading space, 50 is the length of peptide
        (and height), and 25 is the trailing space (per peptide).
        '''

        from matplotlib.font_manager import FontProperties
        font = FontProperties()
        font.set_family('monospace')
        # now need to plot ytext widgets
        index = 0
        peptide = self.peptide
        # first try nterm
        if self._nterm != '':
            text = r'$%s$' % self._nterm
            axes.text(FONT_POSITION, FONT_HEIGHT, text, fontsize=FONTSIZE,
                      fontproperties=font)
        # iteratively find the next sub
        while peptide:
            # match residue
            match = re.match(RES, peptide)
            res = match.group(0)
            # create formatting string + set offsets
            residue = r'$%s$' % res
            sub_offset = (FONTSIZE*SUBSCRIPT_RATIO *
                          self._get_subscript_offset(res))
            seq_offset = (FONTSIZE*self._get_sequence_offset(res))
            self.offsets.append(sub_offset+seq_offset)
            # x, y, text
            x_pos = (WIDTH*index+FONT_POSITION +
                     sum(self.offsets[:-1]) +
                     self._nterm_offset)
            axes.text(x_pos, FONT_HEIGHT, residue, fontsize=FONTSIZE,
                      fontproperties=font)
            # reset out peptide and adjust idx
            peptide = peptide[match.end():]
            index += 1
        # first try nterm
        if self._cterm != '':
            text = r'$%s$' % self._cterm
            x_pos = (WIDTH*index-FONT_POSITION + sum(self.offsets) +
                     self._nterm_offset)
            axes.text(x_pos, FONT_HEIGHT, text, fontsize=FONTSIZE,
                      fontproperties=font)

    def _add_lines(self, axes, length):
        '''
        Adds the vertical sequencing bars between each peptide to the
        axes.
        '''

        # bae params
        from matplotlib.font_manager import FontProperties
        font = FontProperties()
        font.set_family('monospace')
        # add the vertical lines
        for index in range(1, length):
            offset = sum(self.offsets[:index]) + self._nterm_offset
            # pylint: disable=bad-continuation
            if (ARGS.keep_lines or
                # b-ions have a line
                self.ions[1][index-1] or
                # y-ions have a line
                self.ions[0][length - index - 1]):
                axes.plot((WIDTH*index+offset, WIDTH*index+offset),
                          (VERT_LINE_MIN, VERT_LINE_MAX), self.color,
                          linewidth=ARGS.line_width)
        # now have 20+30 room for the horizontal lines
        # bottom ion series
        b_ions = self.ions[1]
        for index, value in enumerate(b_ions):
            # add the horizontal line
            if value:
                self._process_b_line(axes, font, index)
        # top ion series
        y_ions = self.ions[0]
        for index, value in enumerate(y_ions):
            # add the horizontal line
            if value:
                self._process_y_line(axes, font, length, index)

    # ------------------
    #    ION SERIES
    # ------------------

    def _process_b_line(self, axes, font, index):
        '''
        Adds in a line for the b-ion series, which is below and juts
        in towards AXIS_0
        '''

        offset = sum(self.offsets[:index+1]) + self._nterm_offset
        xstart = (index+1)*WIDTH + offset
        self._plot_subline(axes, xstart, 'b', index, minus=True)
        # now add the label
        label = self._ion_label('b', index)
        # need to calculate the adjustment
        adjust = self._ion_label_position('b', index, label)
        # x, y, text
        axes.text(xstart+adjust, self._ion_label_height('b'), label,
                  fontsize=SUB_FONTSIZE,
                  fontproperties=font)

    def _process_y_line(self, axes, font, length, index):
        '''
        Adds in a line for the b-ion series, which is below and extends
        away from AXIS_0
        '''

        # needs to be inverted ;)
        offset_index = length-(index+1)
        offset = sum(self.offsets[:offset_index]) + self._nterm_offset
        xstart = (length-index-1)*WIDTH + offset
        self._plot_subline(axes, xstart, 'y', offset_index)
        # now add the label
        label = self._ion_label('y', index)
        # x, y, text
        adjust = self._ion_label_position('y', offset_index, label)
        # no need to adjust height
        axes.text(xstart+adjust, self._ion_label_height('y'), label,
                  fontsize=SUB_FONTSIZE,
                  fontproperties=font)

    # ------------------
    #    ION LABELS
    # ------------------

    @staticmethod
    def _ion_label(series, index):
        '''Returns a label for the ion series'''

        return r'$%s_{%d}$' % (series, index+1)

    def _plot_subline(self, axes, xstart, series, index, minus=False):
        '''
        Plots a subline
        :
            axes -- plot axes
            xstart -- starting x position
            serues -- y or b ions
            index -- index to self.offsets to adjust length
        '''

        height = self._ion_line_height(series)
        length = self._length(index)
        if minus:
            xstart -= length
        axes.plot((xstart, xstart+length),
                  (height, height),
                  self.color, linewidth=ARGS.line_width)

    def _length(self, index):
        '''Calculates the ion label line length'''

        if ARGS.same_line:
            return SAMELINE_LENGTH
        else:
            return DIFFERENT_LINE_RATIO*(WIDTH + self.offsets[index])

    def _ion_line_height(self, series):
        '''Calculates the ion line y position'''

        if series == 'b':
            height = VERT_LINE_MIN
        else:
            height = VERT_LINE_MAX
        return height

    def _ion_label_height(self, series):
        '''Calculates the ion label y position'''

        if ARGS.same_line:
            return self._same_ion_label_height(series)
        else:
            return self._different_ion_label_height(series)

    def _ion_label_position(self, series, index, label):
        '''Calculates the ion label relative x position'''

        if ARGS.same_line:
            return self._same_ion_label_position(series, index, label)
        else:
            return self._different_ion_label_position(series, index, label)

    # ------------------
    #     SAME LINE
    # ------------------

    def _same_ion_label_height(self, series):
        '''Returns the height for same line series'''

        if series == 'b':
            height = VERT_LINE_MIN - (SUB_FONTSIZE/2)
        else:
            height = VERT_LINE_MAX
        return height

    def _same_ion_label_position(self, series, index, label):
        '''Returns the relative x position for the same line series'''

        label_shift = SAMELINE_LENGTH + SUB_FONTSIZE/2
        num_length = len(NOT_ALNUM.sub('', label)) - 1
        if series == 'b':
            adjust = -(label_shift + SUB_FONTSIZE +
                       SUB_FONTSIZE*SUBSCRIPT_RATIO*(num_length))
        else:
            adjust = label_shift
        return adjust

    # ------------------
    #   DIFFERENT LINE
    # ------------------

    def _different_ion_label_height(self, series):
        '''Returns the label height when not on same line'''

        if series == 'b':
            height = VERT_LINE_MIN - 3*(SUB_FONTSIZE/2) - ARGS.line_width
        else:
            height = VERT_LINE_MAX + SUB_FONTSIZE
        return height

    def _different_ion_label_position(self, series, index, label):
        '''Returns the relative x position for the different line series'''

        length = self._length(index)/DIFFERENT_LINE_RATIO
        label_shift = length/2
        num_length = len(NOT_ALNUM.sub('', label)) - 1
        label_adjust = (SUB_FONTSIZE +
                        SUB_FONTSIZE*SUBSCRIPT_RATIO*(num_length))
        if series == 'b':
            adjust = -(label_shift+(label_adjust-SUB_FONTSIZE)/2)
        else:
            adjust = label_shift - label_adjust/2
        return adjust

# ------------------
#       MAIN
# ------------------


def main():
    '''On init'''

    # init app
    app = QtGui.QApplication([])
    mainwindow = MainWindow(ARGS.color, ARGS.output, peptide=ARGS.peptide,
                            ions=ARGS.ions)
    mainwindow.show()
    status = app.exec_()
    sys.exit(status)

if __name__ == '__main__':
    main()
