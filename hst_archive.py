# HST Archive module
# 
# This module is for determining whether HST has observed within
# a given range of a specific coordinate in the sky.  It uses the
# STScI MAST archive.

import sys, re
import basic_archive


DEFAULT_TARGET = ""
DEFAULT_BOXSIZE_STRING = "4.0"
MAX_ROWS_RETURNED = "1000"   # max value allowed on web page

# HST Archive:
TARGET_LABEL = "target"
RA_LABEL = 'ra'
DEC_LABEL = 'dec'
RADEC_LABEL = None
ARCHIVE_NAME = "HST archive"
ARCHIVE_SHORTNAME = "hst"
ARCHIVE_URL = "http://archive.stsci.edu/hst/search.php"
ARCHIVE_USER_URL = "http://archive.stsci.edu/hst/search.php"

#BASE_URL = "http://iraf-nvo.noao.edu"

DICT = { 'target': DEFAULT_TARGET, 'resolver': "SIMBAD", 
		 'ra': "", 'dec': "", 'equinox': "J2000", 'radius': DEFAULT_BOXSIZE_STRING,
		 'outputformat': "PSV", 'max_records': MAX_ROWS_RETURNED, 'max_rpp': '500', 
		 'action': "Search" }
# {'sci_start_time': '', 'coordformat': 'sex', 'equinox': 'J2000', 'sci_archive_date': '', 
# 'selectedColumnsCsv': 'Mark,sci_data_set_name,sci_targname,sci_ra,sci_dec,sci_refnum,sci_start_time,sci_stop_time,sci_actual_duration,sci_instrume,sci_aper_1234,sci_spec_1234,sci_pep_id,sci_release_date,sci_preview_name,sci_hlsp,ang_sep', 
# 'ordercolumn2': 'sci_targname', 'ordercolumn3': 'sci_data_set_name', 'sci_aper_1234': '',
# 'ordercolumn1': 'ang_sep', 'radius': '4.0', 'sci_pep_id': '', 'sci_pi_last_name': '', 
# 'extra_column_value_1': '', 'max_records': '1001', 'extra_column_value_2': '', 'ra': '', 
# 'sci_obset_id': '', 'outputformat': 'PSV', 'sci_spec_1234': '', 'resolver': 'NED', 
# 'sci_data_set_name': '', 'max_rpp': '500', 'availableColumns': 'Mark', 
# 'sci_release_date': '', 'target': 'ngc 936', 'sci_aec[]': 'S', 
# 'extra_column_name_2': 'sci_data_set_name', 'sci_actual_duration': '', 
# 'extra_column_name_1': 'sci_data_set_name', 'sci_target_descrip': '', 
# 'action': 'Search\n', 'dec': ''}

#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""no rows found|Dataset""")
#   Check for data-returned reply (MAST-specific)
findPossibleData = re.compile(r"observations\s+found", re.VERBOSE)
#   Find "no data returned" equivalent for MAST
findNoDataReturned = re.compile(r"no \s rows \s found", re.VERBOSE)


	
def FindInstruments( theText ):
	"""Function to find and count HST instruments (more precisely, instrument
	modes) in a block of text.  Returns a dictionary where keys = instrument
	modes and values = number of occurences.
	"""
	
	lines = theText.splitlines()
	lines = [line for line in lines if len(line.strip()) > 1]
	if findNoDataReturned.search(lines[0]):
		return None
	
	# First two lines are column titles and units for columns
	colTitles = lines[0].split("|")
	instIndex = -1
	for i in range(len(colTitles)):
		if colTitles[i] == "Instrument":
			instIndex = i
	if (instIndex == -1):
		# something wrong
		return None
	dataLines = lines[2:]
	
	obsDict = {}
	for line in dataLines:
		pp = line.split("|")
		instrument = pp[instIndex].strip()
		if instrument not in list(obsDict.keys()):
			obsDict[instrument] = 1
		else:
			obsDict[instrument] += 1
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
# of the HST archive
class HSTArchive(basic_archive.BasicArchive):

	# Override InsertBoxSize() method, because by default we submit a radius in
	# arc minutes to the archive
	def InsertBoxSize(self, box_size):
		radius_arcmin = 0.5*box_size
		self.params[self.boxLabel] = str(radius_arcmin)


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
				for k in list(foundData.keys()):
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




# Factory function to create an instance of HSTArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return HSTArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="radius")


# Text indicating no observations found [includes comment character at start]:
#			   0    (Records Found)
