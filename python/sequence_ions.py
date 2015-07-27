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

# This script aims to provide an interface to simplify the generation of
# high quality figures for sequencing ions, by automatically genrating
# highly customizable images using a TEX format.

# Ex.:
# python sequence_ions.py --peptide SAM_PL^ER_{SAM}PLER^{SA}MPLER
# --ions y1 y2 y3 y4 y10 y13 b1 b2 b3 b5 b10 b13 --color red
# --format png --output output.png

# http://i.imgur.com/04kMGDM.png

# load modules
import argparse
import os
import re
import sys

import matplotlib
matplotlib.rcParams['mathtext.default'] = 'regular'

# load functions.objects
from PySide import QtCore, QtGui

# CONSTANTS

QLABEL_BANNER_STYLE = '''
QLabel {
    font-weight: bold;
    font-size: 20pt;
};
'''

AMINO_ACIDS = ['A', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'K', 'L', 'M', 'N',
               'P', 'Q', 'R', 'S', 'T', 'V', 'W', 'Y']

SUBSCRIPT_RATIO = 0.375

# REGEXES
ION = re.compile('^(b|y|B|Y)([0-9]+)$')
AA_SET = '[{0}]'.format(''.join(AMINO_ACIDS))
# need at least one preceeding AA, then any number of <AA>_{<AA>}
# pairs, where each group can be <AA>, _|^<AA>, {<AA>}, _|^{<AA>}
#RES = r'^(?:%(aa)s|%(aa)s[_^]%(aa)s|' \
#      r'\{%(aa)s+\}|%(aa)s[_^]\{%(aa)s+\})' %{'aa': AA_SET}
#PEPTIDE = re.compile(RES + '+$')

RES = r'^(?:%(aa)s[_^]\{%(aa)s+\}|%(aa)s[_^]%(aa)s|' \
      r'\{%(aa)s+\}|%(aa)s)' %{'aa': AA_SET}
PEPTIDE = re.compile(RES + '+$')

# ------------------
#     ARGUMENTS
# ------------------

def check_ions(peptide, ions):
    '''Validates the input ion choices'''

    try:
        # ensure all are matches
        matches = [ION.match(i) for i in ions]
        assert all(matches)
        if matches:
            # now ensure none are larger than the peptides
            highest = max([int(i.group(2)) for i in matches])
            length = len(peptide)
            # cannot have an ion longer than the peptide
            assert highest < length
    except AttributeError:
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
ARGS = PARSER.parse_args()

if ARGS.peptide is None and ARGS.ions is not None:
    raise argparse.ArgumentTypeError("Please enter a valid peptide before "
                                     "specifying sequencing ions.")
elif ARGS.peptide is not None:
    if not PEPTIDE.match(ARGS.peptide.upper()):
        raise argparse.ArgumentTypeError("Please enter a valid peptide "
                                         "sequence. Supports TEX-like "
                                         "subscript and superscripts.")
elif ARGS.ions is not None:
    check_ions(ARGS.peptide, ARGS.ions)

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
        length = self.get_length()
        offset = self.get_offset()
        width = length + SUBSCRIPT_RATIO*offset
        # make figure for width/height and set axes
        fig = plt.figure(figsize=(width, 2.0), dpi=dpi)
        axes = self._init_axes(fig, length, offset)
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

        length = self.get_length()
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

        self.peptide = self.peptide.upper()
        # need a negative look-behind assertion for formatting quues
        # and then to capture solely the text within the {} notation.
        # use the "\\1" formating notation to replace {(group)} with
        # (group)
        pattern = r'(?<![_^])\{(%s+)\}' %(AA_SET)
        self.peptide = re.sub(pattern, r'\1', self.peptide)

    def get_length(self, peptide=None):
        '''
        Processes the peptide length removing all of the subscripted
        and superscripted characters.
        '''

        peptide = self.peptide if peptide is None else peptide
        pattern = r'(?:[_^]\{(%(aa)s+)\}|[_^]%(aa)s)' %{'aa': AA_SET}
        return len(re.sub(pattern, '', peptide))

    def get_offset(self, peptide=None):
        '''
        Extracts all the subscripted and superscripted characters and
        returns the number of characters.
        '''

        peptide = self.peptide if peptide is None else peptide
        pattern = r'(?:[_^]\{(%(aa)s+)\}|[_^](%(aa)s))' %{'aa': AA_SET}
        matches = re.findall(pattern, peptide)
        matches = ''.join([''.join(i) for i in matches])
        return len(matches)

    # ------------------
    #    PLOT UTILS
    # ------------------

    @staticmethod
    def _init_axes(fig, length, offset):
        '''Initializes the axes for the current plot'''

        axes = fig.add_subplot(111)
        axes.set_ylim(0, 200)
        axes.set_xlim(0, 100*(length+(SUBSCRIPT_RATIO*offset)))
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
        # iteratively find the next sub
        while peptide:
            # match residue
            match = re.match(RES, peptide)
            res = match.group(0)
            # create formatting string + set offsets
            residue = r'$%s$' %res
            offset = 100*SUBSCRIPT_RATIO*self.get_offset(res)
            self.offsets.append(offset)
            # x, y, text
            axes.text(100*index+25+sum(self.offsets[:-1]), 75, residue,
                      fontsize=50, fontproperties=font)
            # reset out peptide and adjust idx
            peptide = peptide[match.end():]
            index += 1

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
            offset = sum(self.offsets[:index])
            # pylint: disable=bad-continuation
            if (ARGS.keep_lines or
                # b-ions have a line
                self.ions[1][index-1] or
                # y-ions have a line
                self.ions[0][length-index-1]):
                axes.plot((index*100+offset, index*100+offset),
                          (37.5, 162.5), self.color, linewidth=5)
        # now have 20+30 room for the horizontal lines
        # bottom ion series
        b_ions = self.ions[1]
        for index, value in enumerate(b_ions):
            # add the horizontal line
            if value:
                offset = sum(self.offsets[:index+1])
                xstart = (index+1)*100 + offset
                axes.plot((xstart-20, xstart), (37.5, 37.5), self.color,
                          linewidth=5)
                # now add the label
                label = r'$b_{%d}$' %(index+1)
                # x, y, text
                axes.text(xstart-80, 27.5, label, fontsize=20,
                          fontproperties=font)
        # top ion series
        y_ions = self.ions[0]
        for index, value in enumerate(y_ions):
            # add the horizontal line
            if value:
                # needs to be inverted ;)
                offset = sum(self.offsets[:length-index-1])
                xstart = (length-index-1)*100 + offset
                axes.plot((xstart, xstart+20), (162.5, 162.5), self.color,
                          linewidth=5)
                # now add the label
                # now add the label
                label = r'$y_{%d}$' %(index+1)
                # x, y, text
                axes.text(xstart+30, 162.5, label, fontsize=20,
                          fontproperties=font)

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
