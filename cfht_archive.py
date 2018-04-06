# Archive class specialization for CFHT archive
# 
# This module defines a new class (CFHTArchive) derived from the BasicArchive class, 
# to allow queries to the archive of the Canada-France-Hawaii Telescope.

# The new class uses the (not really officially public?) SQL interface to the
# CADC archive, which can be figured out by looking at the
# "Download complete query results: VOTable CSV TSV" links on the web page
# when a query is executed.
# It requests CSV data rather than HTML, to make parsing the results easier.

import sys, re
from contextlib import closing

import basic_archive, utils, archive_analyze
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

BROWSER_MASQUERADE = "Mozilla/5.0 [en]"

UNSPECIFIED_DEC_STRING = "-99.0"


# Canada-France-Hawaii Telescope archive (Canada):
TARGET_LABEL = "tobject"   # not used, but needed for basic_archive interface
RA_LABEL = "ra"            # not used, but needed for basic_archive interface
DEC_LABEL = "dec"          # not used, but needed for basic_archive interface
ARCHIVE_NAME = "CFHT Archive"
ARCHIVE_SHORTNAME = "cfht"
ARCHIVE_URL = "http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/tap/sync"
ARCHIVE_USER_URL = "http://www.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/search/?collection=CFHT&noexec=true"

# The following is a default request
DEFAULT_QUERY_STRING = """SELECT Observation.collection AS "Collection", Plane.dataProductType AS "Data Type", Observation.instrument_name AS "Instrument" FROM caom2.Plane AS Plane JOIN caom2.Observation AS Observation ON Plane.obsID = Observation.obsID WHERE  ( Observation.collection = \'CFHT\' AND INTERSECTS( CIRCLE(\'ICRS\',221.546343, -0.222948, 0.1), Plane.position_bounds ) = 1 AND  ( Plane.quality_flag IS NULL OR Plane.quality_flag != \'junk\' ) )"""
QUERY_TEMPLATE = """SELECT Observation.collection AS "Collection", Plane.dataProductType AS "Data Type", Observation.instrument_name AS "Instrument" FROM caom2.Plane AS Plane JOIN caom2.Observation AS Observation ON Plane.obsID = Observation.obsID WHERE  ( Observation.collection = \'CFHT\' AND INTERSECTS( CIRCLE(\'ICRS\',{0}, {1}, {2:.3f}), Plane.position_bounds ) = 1 AND  ( Plane.quality_flag IS NULL OR Plane.quality_flag != \'junk\' ) )"""

DICT = { 'LANG': 'ADQL', 'FORMAT': 'csv', 'QUERY': DEFAULT_QUERY_STRING,
		'REQUEST': 'doQuery' }


# Code to parse CSV text and count up instrument uses

def GetDataLines( inputText ):
	"""
	Given a blob of text returned by the CFHT archive (CSV format),
	this returns a list of just those lines corresponding to actual observations
	"""
	# split using newline character, not whitespace (some column titles may have whitespace)
	lines = inputText.split("\n")
	# skip the first line, since it has column titles
	dataLines = [line for line in lines[1:] if len(line) > 1]
	return dataLines


def GetNFound( inputText ):
	"""Returns an integer specifying the number of observations found by
	the CADC for the CFHT archive
	"""
	dataLines = GetDataLines(inputText)
	return len(dataLines)


def AddInstrumentToDict( theDict, instrumentName ):
	if instrumentName not in list(theDict.keys()):
		theDict[instrumentName] = 1
	else:
		theDict[instrumentName] += 1

def FindInstruments( inputText, nFound=None ):
	# first line is header, so skip it
	dataLines = GetDataLines(inputText)
	instCountDict = {}
	instList = []
	for line in dataLines:
		instName = line.split(",")[2]
		AddInstrumentToDict(instCountDict, instName)
		if instName not in instList:
			instList.append(instName)
	
	msgText = "\n\t\t"
	for i in range(len(instList)):
		instName = instList[i]
		msgText += instName + " (%d)" % instCountDict[instName]
		if (i < (len(instList) - 1)):
			msgText += ", "

	return msgText


# Put all the functions in a list:
SEARCHES = [FindInstruments]


# Subclass the BasicArchive class to handle deviant input and posting 
# requirements of the CFHT archive
class CFHTArchive(basic_archive.BasicArchive):

	def __init__( self, long_name, short_name, url, params_dict,
					specialSearches, targetLabel, raLabel, decLabel,
					special_params=None, boxLabel='box', publicURL=None ):
		super(CFHTArchive, self).__init__(long_name, short_name, url, params_dict,
										specialSearches, targetLabel, raLabel, decLabel, 
										special_params, boxLabel, publicURL)
		self.box_size_deg = 0.0667
		self.ra_string = "0.0"
		self.dec_string = UNSPECIFIED_DEC_STRING
	

	# Override the InsertBoxSize() method, because CFHT wants box size in degrees
	def InsertBoxSize( self, box_size ):
		self.box_size_deg = box_size / 60.0

	def InsertCoordinates( self, coords_list ):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for SDSS searches, which require decimal degrees!
		ra_str = coords_list[0]
		dec_str = coords_list[1]
		# currently, we store RA & Dec in decimal degrees to an accuracy of 0.1 arcsec
		ra_decimal, dec_decimal = utils.RADecToDecimalDeg(ra_str, dec_str)
		self.ra_string = ra_decimal
		self.dec_string = dec_decimal

	def SetupSQLQuery( self ):
		newQueryString = QUERY_TEMPLATE.format(self.ra_string, self.dec_string, self.box_size_deg)
		self.params['QUERY'] = newQueryString
		pass
	
	# We override QueryServer because the CFHT Archive requires special
	# SQL format 
	def QueryServer( self ):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML or CSV the server sends us.
		
		# Special setup for position + box-size
		if self.dec_string != UNSPECIFIED_DEC_STRING:
			self.SetupSQLQuery()
		specialHeader = {'User-agent': BROWSER_MASQUERADE}
		req = Request(self.URL, self.EncodeParams(), specialHeader)
		#response = urlopen(req, timeout=self.timeout)
		with closing(urlopen(req, timeout=self.timeout)) as response:
			csvReceived = response.read()
		#response.close()

		# convert result from bytes to Unicode string so Python 3 doesn't choke;
		# specify 'utf-8' instead of 'ascii' in case we get Unicode characters
		return csvReceived.decode('utf-8')


	def AnalyzeHTML( self, csvText):
	
		# Search for possible observations (or straightforward "none found" message)
		nDataFound = GetNFound(csvText)
		if ( nDataFound > 0 ):
			if nDataFound == 1:
				nSetsString = "One observation"
			else:
				nSetsString = "%d observations found" % nDataFound
			messageString = "Data exists! " + "(" + nSetsString + ")"
		else:
			messageString = "No data found."
		
		return (messageString, nDataFound)


# Factory function to create an instance of CFHTArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return CFHTArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="box")
