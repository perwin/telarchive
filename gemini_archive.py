# Archive class and module for the Gemini Observatory Archive
# (previously the "Gemini Science Archive" at CADC)
# 
# This module defines a new class (GeminiArchive) derived from the 
# BasicArchive class, specialized for dealing with JSON output from the
# new Gemini archive API; for details on the latter, see:
#    https://archive.gemini.edu/help/api.html

import re, math, sys
import json
from contextlib import closing
from collections import Counter

if sys.version_info[0] > 2:
	usingPython2 = False
	import urllib.request, urllib.parse, urllib.error
	from urllib.parse import urlencode
	from urllib.request import Request
	from urllib.request import urlopen
else:
	usingPython2 = True
	import urllib
	from urllib import urlencode
	from urllib2 import Request
	from urllib2 import urlopen
import archive_analyze

import basic_archive, utils


DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# Gemini Science Archive:
TARGET_LABEL = "tobject"
RA_LABEL = "ra2000"
DEC_LABEL = "dec2000"
ARCHIVE_NAME = "Gemini Observatory Archive"
ARCHIVE_SHORTNAME = "gemini"
ARCHIVE_URL = "https://archive.gemini.edu/jsonsummary/"
#ARCHIVE_USER_URL = "http://www1.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/gsa/wdbi.cgi/gsa/gsa_science/form"
ARCHIVE_USER_URL = "https://archive.gemini.edu/searchform"

DICT = {}


# Possible modes for Gemini data: imaging, spectroscopy, long-slit spectroscopy,
# multi-object spectroscopy, integral field spectroscopy

def GetModes( fileDictList ):
	"""Returns list of tuples, where each tuple is (mode_name, count)"""
	modeNameList = [f['mode'] for f in fileDictList]
	modeCounter = Counter(modeNameList)
	return list(modeCounter.items())

def GetInstruments( fileDictList ):
	"""Returns list of tuples, where each tuple is (instrument_name, count)"""
	instNameList = [f['instrument'] for f in fileDictList]
	instCounter = Counter(instNameList)
	return list(instCounter.items())

modeNameDict = {"imaging": "image", "ls": "long-slit spectrum", "ifs": "ifu",
				"mos": "mos"}
modeNamePlurals = {"image": "images", "long-slit spectrum": "long-slit spectra"}
modeNamePluralsList = list(modeNamePlurals.keys())

def MakeModeString( number, name ):
	nameFinal = name.lower()
	niceName = modeNameDict[nameFinal]
	if number > 1 and niceName in modeNamePluralsList:
		niceName = modeNamePlurals[niceName]
	return "%d %s" % (number, niceName)

def FindGeminiModesAndInstruments( inputText, nFound=None ):
	jsonList = json.loads(inputText)
	modeCountList = GetModes(jsonList)
	instCountList = GetInstruments(jsonList)

	nSets = len(modeCountList)
	msgText = "\n\t\t"
	if nSets > 1:
		for i in range(nSets - 1):
			msgText += MakeModeString(modeCountList[i][1], modeCountList[i][0]) + ", "
	msgText += MakeModeString(modeCountList[-1][1], modeCountList[-1][0])

	nSets = len(instCountList)
	msgText += "\n\t\t"
	if nSets > 1:
		for i in range(nSets - 1):
			msgText += "%s: %d, " % (instCountList[i][0], instCountList[i][1])
	msgText += "%s: %d" % (instCountList[-1][0], instCountList[-1][1])
	return msgText
	



# Put all the functions in a list:
SEARCHES = [FindGeminiModesAndInstruments]


# Subclass the BasicArchive class to handle deviant input and posting 
# requirements of the Gemini archive
class GeminiArchive(basic_archive.BasicArchive):

	def __init__( self, long_name, short_name, url, params_dict,
					specialSearches, targetLabel, raLabel, decLabel,
					special_params=None, boxLabel='box', publicURL=None ):
		super(GeminiArchive, self).__init__(long_name, short_name, url, params_dict,
										specialSearches, targetLabel, raLabel, decLabel, 
										special_params, boxLabel, publicURL)
		self.searchRadius = 2.0
		self.raDeg = 0.0
		self.decDeg = 0.0

	def InsertBoxSize(self, box_size):
		"""Stores the user-specified search-box size (in arcmin),
		coverting it internally to radius in arcmin.
		"""
		self.searchRadius = box_size / 2.0

	def InsertCoordinates(self, coords_list):
		"""Stores the target RA,Dec coordinates.
		Coordinate list is a two-element list of strings; each string must
		be in the usual "hh mm ss.s" sexigesimal format, though decimal values 
		for the seconds are optional.
		
		(We override this for Gemini searches, because we store and process the
		coordinates in decimal degrees.)
		"""
		self.raDeg, self.decDeg = utils.RADecToDecimalDeg(coords_list[0],coords_list[1])

	def MakeRADecBounds(self):
		"""Takes internally stored RA, Dec, and search radius and returns a string
		describing RA_min,RA_max,Dec_min,Dec_max suitable for the Gemini Observatory
		Archive API.
		"""
		radiusDeg = self.searchRadius / 60.0
		dec_min = self.decDeg - radiusDeg
		if (dec_min) <= -90.0:
			dec_min = -89.999999
		dec_max = self.decDeg + radiusDeg
		if (dec_max) >= 90.0:
			dec_max = 89.999999
		scalingFactor = math.cos(math.radians(self.decDeg))
		ra_min = self.raDeg - radiusDeg / scalingFactor
		ra_max = self.raDeg + radiusDeg / scalingFactor
		txt = "ra=%.7f-%.7f/dec=%.7f-%.7f" % (ra_min,ra_max,dec_min,dec_max)
		return txt
	
	# We override QueryServer because the Gemini Science Archive wants 
	# a special URL-based API
	def QueryServer(self):
		# Compute RA,Dec range and add it to the URL
		raDecRange = self.MakeRADecBounds()
		self.queryURL = self.URL + raDecRange
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us.
		req = Request(self.queryURL)
		req.add_header('User-agent', basic_archive.BROWSER_MASQUERADE)
		with closing(urlopen(req, timeout=self.timeout)) as response:
			htmlReceived = response.read().decode('utf-8')
		return htmlReceived

	def AnalyzeHTML( self, jsonText):
		jsonList = json.loads(jsonText)
		nDataFound = len(jsonList)
		if ( nDataFound > 0 ):
			if nDataFound == 1:
				nSetsString = "One observation"
			else:
				nSetsString = "%d observations found" % nDataFound
			messageString = "Data exists! " + "(" + nSetsString + ")"
		else:
			messageString = "No data found."
		
		return (messageString, nDataFound)


# Factory function to create an instance of GeminiArchive
def MakeArchive():
	return GeminiArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="box")
