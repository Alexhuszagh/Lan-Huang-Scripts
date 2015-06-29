#!/usr/bin/env python
#-*- coding:utf-8 -*-
# Lan Huang Theoretical XLed, Program Manager
# Created by Alex Huszagh, 2014

__doc__ = """This program creates a visual framework for scripts in the XL Toolset.
Dependencies include PySide, Matplotlib, Pandas, Numpy, and Biopython"""
__author__ = "Alex Huszagh"
__version__ = "0.8.0.0 RC"
__maintainer__ = "Alex Huszagh"
__email__ = "ahuszagh@uci.edu"
__status__ = "Development"
__license__ = """Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in
all copies or substantial portions of the Software."""

import sys, argparse, os, math

strPath = os.path.dirname(os.path.realpath(__file__))

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--MGF", help="MGF File",
                    type=str)
parser.add_argument("-p", "--PAVA", help="PAVA File",
                    type=str)
args = parser.parse_args()

if not args.MGF or not args.PAVA:
	raise IOError("Please include both a PAVA file and MGF file in the working directory")

strMGF = os.path.join(strPath, args.MGF)
strPAVA = os.path.join(strPath, args.PAVA)

# Process output
try:
	with open(strMGF, 'r') as e:
		strMGFFile=e.read()
except IOError:
	raise IOError("MGF File not found. Make sure it is in the current working directory.")

try:
	with open(strPAVA, 'r') as e:
		strPAVAFile=e.read()
except IOError:
	raise IOError("PAVA File not found. Make sure it is in the current working directory.")

class Find_Tools(object):
	#------------
	def find_all(self, strValue, strSub):
		"""Find all occurrences within a string"""
		nStart = 0
		while True:
			nStart = strValue.find(strSub, nStart)
			if nStart == -1: return
			yield nStart
			nStart += len(strSub)
	#------------
	def find_all_indices(self, lValue, strSub):
		"""Find all occurrences within a list"""
		lReturn = []
		nOffset = -1
		while True:
			try:
				nOffset = lValue.index(strSub, nOffset+1)
			except ValueError:
				return lReturn
			lReturn.append(nOffset)
	#------------
	def find_all_shift_sub(self, strValue, strSub):
		"""Find all occurrences within a string"""
		nStart = 0
		while True:
			nStart = strValue.find(strSub, nStart)
			if nStart == -1: return
			nStart += len(strSub)
			yield nStart
	#------------
	def splitif(self, strValue, strSub, strCondition):
		lReturn = []
		while strCondition in strValue:
			nStart = strValue.find(strSub, strValue.find(strCondition))
			lReturn.append(strValue[:nStart])
			strValue = strValue[nStart+len(strSub):]
		lReturn.append(strValue)
		return lReturn
	#------------
	def find_substring(self, strValue, strStart, strEnd):
		nStart = strValue.find(strStart)
		nEnd = strValue.find(strEnd, nStart) + len(strEnd)
		return strValue[nStart:nEnd]
	#------------
	def paired_start_end(self, strValue, strStartSub, strEndSub):
		nStart = strValue.find(strStartSub) + len(strStartSub)
		nEnd = strValue.find(strEndSub, strValue.find(strStartSub))
		return nStart, nEnd
	#------------
	#------------
	#------------

# Define key modules
cFtools = Find_Tools()

class Parse_Scans(object):
	#---------------
	def __init__(self, strMSFile, strStartSub, strEndSub):
		self.strMSFile = strMSFile
		self.strStartSub = strStartSub
		self.strEndSub = strEndSub
	#---------------
	def parse_scans(self):
		nSplitLen=100000

		cSplitFile = self.split_file(nSplitLen)
		lStart, lEnd = self.find_all_positions(cSplitFile, nSplitLen)
		return self.find_scans(lStart, lEnd)
	#---------------
	def split_file(self, nSplitLen):
		nIter = int(math.ceil(len(self.strMSFile)/nSplitLen))+1
		for x in range(nIter):
			if (x+1)*nSplitLen <= len(self.strMSFile):
				yield self.strMSFile[nSplitLen*x:nSplitLen*(x+1)]
			else:
				yield self.strMSFile[nSplitLen*x:] 												# Remaining string after last substring identified
	#---------------
	def find_all_positions(self, cGenerator, nSplitLen):
		lStart = []
		lEnd = []
		strRemainder = ''
		for index, scan in enumerate(cGenerator):
			nCounter = index*nSplitLen - len(strRemainder)
			strSearchSpace = strRemainder+scan

			lStartVal = list(cFtools.find_all_shift_sub(strSearchSpace, self.strStartSub))
			lEndVal = list(cFtools.find_all_shift_sub(strSearchSpace, self.strEndSub))

			try:
				nLastIndex = max(lStartVal + lEndVal)
			except ValueError: 																	# In case none are found, then the scan is expanded
				nLastIndex = 0
			strRemainder = (strSearchSpace)[nLastIndex:]
			lStart += [i+nCounter for i in lStartVal]
			lEnd += [i+nCounter for i in lEndVal]
		return lStart, lEnd
	#---------------
	def find_scans(self, lStart, lEnd):
		for i, start in enumerate(lStart):
			end = lEnd[i]
			yield self.strMSFile[start:end]
	#---------------
	#---------------
	#---------------

class ReplaceScan(object):
	#---------------
	def __init__(self, strMGFFile, strPAVAFile):
		self.dMGFScanToPepMass = self.parseMGF(strMGFFile)
		del strMGFFile
		self.strPAVAFile = self.fixHeader(strPAVAFile)
	#---------------
	def parseMGF(self, strMGFFile):
		lScans = Parse_Scans(strMGFFile, 'BEGIN IONS\n', '\nEND IONS').parse_scans()
		dMGFScanToPepMass = dict()

		for strScan in lScans:
			lScan = strScan.splitlines()
			nStart, nEnd = cFtools.paired_start_end(strScan, 'scan=', '"\n')
			strScanNum = strScan[nStart:nEnd]
			for strRow in lScan:
				if 'PEPMASS' in strRow:
					strPepMass = strRow
			dMGFScanToPepMass[strScanNum] = strPepMass

		return dMGFScanToPepMass
	#---------------
	def fixHeader(self, strPAVAFile):
		lScans = Parse_Scans(strPAVAFile, 'BEGIN IONS', 'END IONS').parse_scans()
		lReturn = list()
		for strScan in lScans:
			nStart, nEnd = cFtools.paired_start_end(strScan, 'TITLE=Scan ', ' (rt=')
			strScanNum = strScan[nStart:nEnd]
			strPepMass = self.dMGFScanToPepMass.get(strScanNum)
			try:
				strScanNew = strScan.replace('PEPMASS=0\t0.0000', strPepMass)
			except TypeError:
				print repr(strPepMass), repr(strScanNum); quit()
			strScanNew='BEGIN IONS' + strScanNew
			lReturn.append(strScanNew)
		return '\n\n'.join(lReturn)
	#---------------
	#---------------
	#---------------

# Process output
cReplaceScan = ReplaceScan(strMGFFile, strPAVAFile)

with open(strPAVA[:-4] + '_fixed.txt', 'w') as e:	pass
with open(strPAVA[:-4] + '_fixed.txt', 'w') as e:
	e.write(cReplaceScan.strPAVAFile)
