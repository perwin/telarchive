# Spitzer Archive module
# 
# This module is for determining whether Spitzer has observed within
# a given range of a specific coordinate in the sky.  It actually makes
# use of a web interface which demonstrates the NOAO Virtual Observatory nvodata
# command-line tool.

import re
import basic_archive, utils, urllib

DEFAULT_TARGET = ""
DEFAULT_BOXSIZE_STRING = "4.0"
MAX_ROWS_RETURNED = "1000"   # max value allowed on web page

# Spitzer Archive:
TARGET_LABEL = "Entry"
RA_LABEL = None
DEC_LABEL = None
RADEC_LABEL = "Entry"
ARCHIVE_NAME = "Spitzer archive"
ARCHIVE_SHORTNAME = "spitzer"
ARCHIVE_URL = "https://heasarc.gsfc.nasa.gov/db-perl/W3Browse/w3table.pl"
ARCHIVE_USER_URL = "http://heasarc.gsfc.nasa.gov/db-perl/W3Browse/w3table.pl?tablehead=name%3Dspitzmastr&Action=More+Options"


DICT = {'Action': 'Start Search', 'Entry': '', 'Radius': '100', 
'Radius_unit': 'arcsec', 'ResultMax': MAX_ROWS_RETURNED, 
'bparam_pi_lname': '', 'bparam_duration::unit': 'min', 'Coordinates': 'J2000', 
'bparam_program_id::format': 'int4', 'bparam_aor_key::format': 'int4', 
'bparam_dec::unit': 'degree', 'bparam_program_category': '', 'table': 
'heasarc_spitzmastr\n', 'bparam_duration::format': 'float4:.2f', 
'bparam_ra::format': 'float8:.5f', 'bparam_name': '', 'bparam_pi_fname::unit': ' ', 
'displaymode': 'PureTextDisplay', 'bparam_time': '', 'bparam_name::unit': ' ', 
'bparam_pi_fname::format': 'char10', 'bparam_program_title::format': 'char200', 
'bparam_status': '', 'bparam_program_category::unit': ' ', 
'bparam_aot::format': 'char10', 'Time': '', 
'bparam_lii': '', 'NR': 'CheckCaches/GRB/SIMBAD/NED', 'bparam_aor_label::unit': ' ', 
'bparam_lii::format': 'float8:.5f', 'bparam_aor_key': '', 
'bparam_program_name': '', 'bparam_program_title::unit': ' ', 'bparam_status::unit': ' ', 
'bparam_program_id::unit': ' ', 'bparam_program_title': '', 'bparam_pi_fname': '',
'bparam_bii::unit': 'degree', 
'tablehead': 'name=heasarc_spitzmastr&description=Spitzer Space Telescope Observation Log&url=http://heasarc.gsfc.nasa.gov/W3Browse/spitzer/spitzmastr.html&archive=N&radius=3&mission=SPITZER&priority=3&tabletype=Observation',
'bparam_aor_label': '', 'bparam_pi_lname::unit': ' ', 'bparam_program_name::unit': ' ',
'bparam_bii::format': 'float8:.5f', 'bparam_aor_label::format': 'char40', 
'bparam_time::format': 'float8', 'popupFrom': 'Query Results', 
'bparam_name::format': 'char25', 'bparam_lii::unit': 'degree', 
'varon': 'aot', 'bparam_pi_lname::format': 'char10', 
'bparam_program_name::format': 'char30', 'bparam_dec': '', 'bparam_program_id': '', 
'bparam_duration': '', 'bparam_ra::unit': 'degree', 'bparam_aor_key::unit': ' ', 
'bparam_program_category::format': 'char10', 'bparam_aot': '', 'bparam_bii': '', 
'bparam_status::format': 'char9', 
'dummy': 'Examples of query constraints:', 
'bparam_dec::format': 'float8:.5f', 'bparam_time::unit': 'mjd', 
'bparam_ra': '', 'bparam_aot::unit': ' ' }

#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""Spitzer Space Telescope Observation Log""")
#   Check for number of hits:
findPossibleData = re.compile(r"""#\s+(?P<count>\d+)\s+ \(Records Found\)""")


	
def FindInstruments( theText ):
	"""Function to find and count Spitzer instruments (more precisely, instrument
	modes) in a block of text.  Returns a dictionary where keys = instrument
	modes and values = number of occurences.
	"""
	
	lines = theText.splitlines()
	lines = [line for line in lines if len(line.strip()) > 1]
	nlines = len(lines)
	startData = None
	for i in range(nlines):
		if lines[i].startswith("|aot"):
			startData = i + 1
	
	if startData is None:
		return None
	
	obsDict = {}
	for line in lines[startData:]:
		pp = line.split("|")
		instMode = pp[1].strip()
		if instMode not in obsDict.keys():
			obsDict[instMode] = 1
		else:
			obsDict[instMode] += 1
	return obsDict
	

def AnalyzeOutputFile( htmlText, nFound ):
	"""Special search function which parses the HTML (actually just plain text)
	returned from the archive, and returns a text string summarizing the instrument
	counts.
	"""
	
	observationDict = FindInstruments(htmlText)

	messageText = "\n\t\t"
	modes = list(observationDict.keys())
	nModes = len(modes)
	for i in range(nModes - 1):
		thisMode = modes[i]
		counts = observationDict[thisMode]
		messageText += str(counts) + " " + thisMode + ", "
	lastMode = modes[-1]
	messageText += str(observationDict[lastMode]) + " " + lastMode

	return messageText



# Put all the functions in a list:
SEARCHES = [AnalyzeOutputFile]


# Subclass the BasicArchive class to handle deviant input and search requirements
# of the Spitzer archive
class SpitzerArchive(basic_archive.BasicArchive):

	# Override InsertCoordinates() method, because Spitzer archive wants them
	# as a single string
	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for Spitzer searches, which want both coords in a single
		# string, comma-separated
		ra_str = coords_list[0]
		dec_str = coords_list[1]
		# currently, we store RA & Dec in decimal degrees to an accuracy of 0.1 arcsec
		self.params[RADEC_LABEL] = "%s, %s" % (ra_str, dec_str)


	# Override InsertBoxSize() method, because by default we submit a radius in
	# arc seconds to the archive
	def InsertBoxSize(self, box_size):
		radius_arcsec = 0.5*box_size*60.0
		self.params[self.boxLabel] = str(radius_arcsec)


	# Override AnalyzeHTML() method, since we request that pure text be returned.
	# we'll need to retrieve & analyze an additional text file for the special searches
	def AnalyzeHTML( self, htmlText ):
		#    Function which searches a big blob of HTML text.  We look for various
		# text fragments: signs of valid or invalid reply, did the archive find data
		# or not, etc.  Uses the regular-expression objects defined above.
		#    htmlText = big blob of HTML text (entire reply from archive, in a string)
		
		# Default boolean flags:
		connectionMade = 1       # successfully connected to archive web server
		validReply = 0           # we got a genuine reply from the web server
		noDataExists = 0         # archive did proper search, found no data
		nDataFound = 0           # OUR flag indicating whether archive found data, and if so,
		                         #    how *many* data sets
	
		# Search the text, try to figure out if we got a valid result,
		# and if any data exists:
	
		# First, check to see if we got a well-formed reply (data or not):
		foundValidReply = findReply.search(htmlText)
		# Now, check to see if there's any data present or not:
		if (foundValidReply is not None):
			validReply = 1
			foundData = FindInstruments(htmlText)
			nDataFound = 0
			if foundData is not None:
				for k in foundData.keys():
					nDataFound += foundData[k]
	
		# Next, check to see if there was a screw-up of some kind.
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0

		# Evaluate results of search and construct returned string:
		if ( connectionMade ):
			if ( validReply ):
				if ( nDataFound > 0 ):
					messageString = "Data exists! (%d records found)" % nDataFound
				else:
					messageString = "No data found."
			else:
				messageString = "Invalid reply from archive (possibly malformed coordinates?)."
				nDataFound = -1
		else:
			messageString = "Failed connection to archive web site..."
			nDataFound = -1

		return (messageString, nDataFound)




# Factory function to create an instance of SpitzerArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return SpitzerArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="Radius")


# Text indicating no observations found [includes comment character at start]:
#			   0    (Records Found)
