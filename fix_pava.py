#!/usr/bin/env python

import argparse, os, sys, math
from collections import defaultdict

strPath = os.path.dirname(os.path.realpath(__file__))

# Process arguments
parser = argparse.ArgumentParser()
parser.add_argument("-m", "--MGF", help="MGF File",
                    type=str)
parser.add_argument("-p", "--PAVA", help="PAVA File",
                    type=str)
parser.add_argument("-o", "--output", help="Output File Name (Optional)",
                    type=str)
args = parser.parse_args()

if not args.MGF or not args.PAVA:
	raise IOError("Please include both a PAVA file and MGF file in the working directory")

strMGF = os.path.join(strPath, args.MGF)
strPAVA = os.path.join(strPath, args.PAVA)
outputBaseName = args.PAVA[:-4] + "_corrected.txt"
strOutputPath = os.path.join(strPath, outputBaseName)
if args.output:
	strOutputPath = os.path.join(strPath, args.output)

# Process output
try:
	with open(strMGF, 'r') as e:
		strMGFFile = e.read()
except IOError:
	raise IOError("MGF File not found. Make sure it is in the current working directory.")

try:
	with open(strPAVA, 'r') as e:
		strPAVAFile = e.read()
except IOError:
	raise IOError("PAVA File not found. Make sure it is in the current working directory.")

def paired_start_end(strValue, strStartSub, strEndSub):
	nStart = strValue.find(strStartSub) + len(strStartSub)
	nEnd = strValue.find(strEndSub, strValue.find(strStartSub))
	return nStart, nEnd
	
def find_all_shift_sub(strValue, strSub):
	"""Find all occurrences within a string"""
	nStart = 0
	while True:
		nStart = strValue.find(strSub, nStart)
		if nStart == -1: return
		nStart += len(strSub)
		yield nStart

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

			lStartVal = list(find_all_shift_sub(strSearchSpace, self.strStartSub))
			lEndVal = list(find_all_shift_sub(strSearchSpace, self.strEndSub))

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

class Parse_MGF(object):
	#---------------
	def __init__(self, strMGFFile):
		self.lScans = Parse_Scans(strMGFFile, 'BEGIN IONS\n', '\nEND IONS').parse_scans()
		self.dScanToData = defaultdict(dict)
		self.process_scan_nums_to_data()
	#---------------
	def process_scan_nums_to_data(self):
		for strScan in self.lScans: 															# Extract all spectra values per scan
			dData = self.extract_scan_mgf(strScan)
			strScanNum = dData.get('num')
			self.dScanToData['%s' %strScanNum] = dData
	#---------------
	def extract_scan_mgf(self, strScan):
		strHeader, strSpectra = self.find_header_spectra(strScan)
		dScan = self.extract_header_mgf(strHeader)
		dMZToIntensity = self.process_spectra(strSpectra)
		dScan['type'] = 'MGF'
		dScan['peaks'] = dMZToIntensity
		return dScan
	#---------------
	def find_header_spectra(self, strScan):
		lScan = strScan.splitlines()
		nScanIndex = 0
		for nIndex, strRow in enumerate(lScan): 												# In each spectra scan, first line that starts with a float
			try: 																				# number is the start of the spectral data
				float(strRow.split()[0])
				nScanIndex = nIndex
				break
			except ValueError:	pass

		if not nScanIndex: 																		# If no scans, set the scan list to be blank,
			lHeader = lScan 																	# and the header to be the rest
			lSpectra = []
			return '\n'.join(lHeader), '\n'.join(lSpectra)
		else:
			lHeader = lScan[:nScanIndex]
			lSpectra = lScan[nScanIndex:]
			return '\n'.join(lHeader), '\n'.join(lSpectra)
	#---------------
	def extract_header_mgf(self, strHeader):
		if '(rt=' in strHeader: 																# Unique substring for a PAVA-style MGF file
			return self.extract_PAVA_header(strHeader)

		elif 'RTINSECONDS=' in strHeader: 														# Substring for TPP-compatible MGF file
			return self.extract_TPP_header(strHeader)

		else:	return
	#---------------
	def extract_PAVA_header(self, strHeader):
		dReturn = {}
		dParse = {
			'num':['TITLE=Scan ', ' (rt='],
			'retentionTime':[' (rt=', ') [']
		}

		if 'MS2_SCAN_NUMBER' in strHeader:	dParse.update({'precursorScanNum':['MS2_SCAN_NUMBER= ', '\n']})
		dReturn.update(self.parse_header(strHeader, dParse))
		dReturn.update(self.parse_pep_mass(strHeader, 'PEPMASS=', '\n'))
		dReturn.update(self.parse_charge(strHeader, 'CHARGE=', '+'))

		return dReturn
	#---------------
	def extract_TPP_header(self, strHeader):
		dReturn = {}

		dParse = {'num':['scan=', '"\n'],
				  'retentionTime':['RTINSECONDS=', '\n']
				 }

		dReturn.update(self.parse_header(strHeader, dParse))
		dReturn.update(self.parse_pep_mass(strHeader, 'PEPMASS=', '\n'))
		dReturn.update(self.parse_charge(strHeader, 'CHARGE=', '+'))

		if 'retentionTime' in dReturn:
			strRetentionTime = dReturn.get('retentionTime')
			nSecToMin = 60
			dReturn['retentionTime'] = round(float(strRetentionTime)/nSecToMin, 3)

		return dReturn
	#---------------
	def parse_header(self, strHeader, dParse):
		dReturn = {}

		for strKey in dParse:
			strStartSub, strEndSub = dParse.get(strKey)
			nStart, nEnd = paired_start_end(strHeader, strStartSub, strEndSub)
			strValue = strHeader[nStart:nEnd]
			dReturn[strKey] = strValue
		return dReturn
	#---------------
	def parse_pep_mass(self, strHeader, strStartSub, strEndSub):
		dReturn = {}
		nStart, nEnd = paired_start_end(strHeader, strStartSub, strEndSub)
		strPepMassRow = strHeader[nStart:nEnd]
		lPepMass = strPepMassRow.split()

		if len(lPepMass) == 1:
			precursorMz = lPepMass[0]
			dReturn['precursorMz'] = precursorMz

		elif len(lPepMass) == 2:
			precursorMz, precursorIntensity = lPepMass
			dReturn['precursorMz'] = precursorMz
			dReturn['precursorIntensity'] = precursorIntensity
		return dReturn
	#---------------
	def parse_charge(self, strHeader, strStartSub, strEndSub):
		dReturn = {}
		precursorCharge = 1
		if 'CHARGE=' in strHeader:
			nStart, nEnd = paired_start_end(strHeader, strStartSub, strEndSub)
			precursorCharge = strHeader[nStart:nEnd]
		dReturn['precursorCharge'] = precursorCharge
		return dReturn
	#---------------
	def process_spectra(self, strSpectra):
		lSpectra = strSpectra.splitlines()
		dSpectra = defaultdict(list)
		for strRow in lSpectra:
			lRow = strRow.split()
			if len(lRow) == 2:
				strMZ, strIntensity = lRow
				dSpectra[strMZ] = [strIntensity]
			elif len(lRow) == 3:
				strMZ, strZ, strIntensity = lRow
				dSpectra[strMZ] = [strIntensity, strZ]
		try:	dSpectra.pop('END')
		except KeyError:	pass
		return dSpectra
	#---------------
	#---------------
	#---------------
	
class fixScans(object):
	def __init__(self, strPAVAFile, dCharges, outputPath):
		self.lScans = Parse_Scans(strPAVAFile, 'BEGIN IONS\n', '\nEND IONS').parse_scans()
		strPAVA = self.processScans(dCharges)
		
		with open(outputPath, 'w') as e:	pass								# Blank it
		with open(outputPath, 'w') as e:
			e.write(strPAVA)
			
	def processScans(self, dCharges):
		self.ScanFile = str()
		for strScan in self.lScans:
			strStartSub, strEndSub = 'TITLE=Scan ', ' (rt='
			nStart, nEnd = paired_start_end(strScan, strStartSub, strEndSub)
			strScanNum = strScan[nStart:nEnd]
			if strScanNum in dCharges:
				newCharge, oldCharge = dCharges.get(strScanNum)
			
				strScan = strScan.replace("CHARGE=%s+" %(str(oldCharge)), "CHARGE=%s+" %(str(newCharge)))
			self.ScanFile += "BEGIN IONS\n%s\n\n" %strScan
		return self.ScanFile
		
class Compare_Charges(object):
	def __init__(self, MGFFile, PAVAFile, outputPath):
		cMGF = Parse_MGF(MGFFile)
		self.dMGF = cMGF.dScanToData
		
		cPAVA = Parse_MGF(PAVAFile)
		self.dPAVA = cPAVA.dScanToData
		
		self.dCharges = self.compileCharges(self.dMGF, self.dPAVA)
		
		fixScans(PAVAFile, self.dCharges, outputPath)
		self.printOutput(self.dCharges, "chargeStates.txt")
	#---------------
	def compileCharges(self, dMGF, dPAVA):
		dCharges = dict()
		lMGFScans = dMGF.keys()
		lPAVAScans = dPAVA.keys()
		
		lKeys = [i for i in lPAVAScans if i in lMGFScans]
		
		for key in lKeys:
			dMGFScan = dMGF.get(key)
			dPAVAScan = dPAVA.get(key)
			
			chargeMGF = dMGFScan.get("precursorCharge")
			chargePAVA = dPAVAScan.get("precursorCharge")
			
			dCharges[key] = [str(chargeMGF), str(chargePAVA)]
			
		return dCharges
	#---------------
	def printOutput(self, dCharges, outputPath):
		PAVACounter = 0
		MGFCounter = 0
		with open(outputPath, 'w') as e:	pass								# Blank it
		with open(outputPath, 'w') as e:
			e.write('Scan\tMGF\tPAVA\n')
			lKeys = dCharges.keys()
			lKeys = sorted([int(i) for i in lKeys])
			lKeys = [str(i) for i in lKeys]
			for key in lKeys:
				chargeMGF, chargePAVA = dCharges.get(key)
				if chargeMGF != '1':
					MGFCounter += 1
				if chargePAVA != '1':
					PAVACounter += 1
				if chargeMGF != chargePAVA:
					e.write('%s\t%s\t%s\n' %(key, chargeMGF, chargePAVA))
			
			e.write('MGF Scans Above 1: %d\n' %MGFCounter)
			e.write('PAVA Scans Above 1: %d\n' %PAVACounter)
	#---------------
	#---------------
	#---------------

Compare_Charges(strMGFFile, strPAVAFile, strOutputPath)
