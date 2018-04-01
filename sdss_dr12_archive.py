# Archive class specialization for SDSS DR12 imaging queries
# 
# This module defines a new class (SloanDR12Archive) derived from the 
# BasicArchive class, to allow queries to the coordinate-list submission
# form interface of the SDSS archive.

import re
import basic_archive
import utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_RETURNED = "200"

DEFAULT_RADEC = "164.68184,55.59788"

TARGET_LABEL = None
RA_LABEL = None
DEC_LABEL = None
RADEC_LABEL = "radecs"
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR12) Science Archive Server -- Coverage Check"
ARCHIVE_SHORTNAME = "sdss-dr12"
#ARCHIVE_URL ="http://data.sdss3.org/coverageCheck/search"
ARCHIVE_URL ="https://dr12.sdss.org/coverageCheck/search"
ARCHIVE_USER_URL = "http://data.sdss3.org/coverageCheck/"
DICT = {RADEC_LABEL: DEFAULT_RADEC}


#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""Coverage Check""")
#   Check for number of hits:
findPossibleData = re.compile(r"""<a href="/fields/runCamcolField\?run""")
#   Check for data-returned reply and extract useful numbers
findImageData = re.compile(r"""<a href="/fields/runCamcolField\?run=(?P<run>\d+)\&amp\;camcol=(?P<camcol>\d+)\&amp\;field=(?P<field>\d+)">""")
#	zoom=00&run=(?P<run>\d+)&rerun=(?P<rerun>\d+)&camcol=(?P<camcol>\d+)&field=(?P<field>\d+)&
#	""", re.VERBOSE)
# note that the desired fields can access thus:
#    m = findPossibleData.seach(someHTMLtext)
#    print m.group('plate'), m.group('mjd'), m.group('fiber') et cetera


# Put all the functions in a list:
SEARCHES = []



# Subclass the BasicArchive class to handle deviant input and posting 
# requirements 
class SloanDR12Archive(basic_archive.BasicArchive):

	def SetMode(self, mode_name):
		self.mode = mode_name
		
		
	def InsertBoxSize(self, box_size):
		# Useless for SDSS searches, so we do nothing
		pass


	def InsertTarget(self, target_name):
		# SDSS interface won't let us use target names, so we do nothing
		#    (in principle, we *could* do a coordinate lookup instead,
		#    but that's excessive)
		pass


	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for SDSS searches, which require decimal degrees!
		ra_str = coords_list[0]
		dec_str = coords_list[1]
		# currently, we store RA & Dec in decimal degrees to an accuracy
		# of 0.1 arcsec
		# NOTE that there must be *no* space after the comma (search will silently
		# fail if there is a space)
		#raDeg, decDeg = utils.RADecToDecimalDeg(ra_str, dec_str)
		self.params[RADEC_LABEL] = "%.5f,%.5f" % utils.RADecToDecimalDeg(ra_str, dec_str)



	# slight kludge: we don't need to search the HTML again; we just need to return
	# a message stating how many separate fields were found
	def DoSpecialSearches(self, htmlText, nFound):
		if (nFound == 1):
			messageString = "\n\t\tone field found"
		else:
			messageString = "\n\t\t%d separate fields found" % nFound
		return messageString


	def AnalyzeHTML(self, htmlText):
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
			foundData = findImageData.findall(htmlText)
			nDataFound = len(foundData)
			#nDataFound = len(findPossibleData.findall(htmlText))
	
		# Next, check to see if there was a screw-up of some kind.
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0


		# Evaluate results of search and construct returned string:
		if ( connectionMade ):
			if ( validReply ):
				if ( nDataFound > 0 ):
					messageString = "DR12 imaging data exists!"
					if (self.mode == "fetchsdss"):
						for ds in foundData:
							messageString += "\n\t\t(run, camcol, field = "
							messageString += "%s %s %s)" % (ds[0].strip(), ds[1].strip(), ds[2].strip())
				else:
					messageString = "No data found."
			else:
				messageString = "Invalid reply from archive (possibly malformed coordinates?)."
				nDataFound = -1
		else:
			messageString = "Failed connection to archive web site..."
			nDataFound = -1

		return (messageString, nDataFound)

# End Class


# Factory function to create an instance of SDSSFootprintArchive
def MakeArchive():
	return SloanDR12Archive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

