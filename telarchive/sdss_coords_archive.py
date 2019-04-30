# Archive class specialization for SDSS archive ("DAS Coordinate List Submission Form")
# 
# This module defines a new class (SloanCoordsArchive) derived from the 
# BasicArchive class, to allow queries to the coordinate-list submission
# form interface of the SDSS archive.

# The new class includes a modified QueryServer() method which uses 
# multipart/form posting.

import re
import basic_archive, multipart_form
import utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

DEFAULT_CSVCOORDS = "256.443154,58.0255"

# Canada-France-Hawaii Telescope archive (Canada):
TARGET_LABEL = None
RA_LABEL = None
DEC_LABEL = None
RADEC_LABEL = "csvIn"
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR7) Coordinate-Search Server"
ARCHIVE_SHORTNAME = "sdss-coords"
ARCHIVE_URL ="http://das.sdss.org/www/cgi-bin/post_coords"
ARCHIVE_USER_URL = "http://das.sdss.org/www/html/post_coords.html"
DICT = {'csvIn': DEFAULT_CSVCOORDS, 'inputFile': "" }


#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""Fields containing specified coordinates""")
#   Check for number of hits:
findPossibleData = re.compile(r"""<td class="segment"><a href=""")
#   Check for data-returned reply and extract useful numbers
findIndividualData = re.compile(r""" <td\s class="run">(?P<run>\d+)</td>\s+
	<td\s class="rerun">(?P<rerun>\d+)</td>\s+
	<td\s class="camcol">(?P<camcol>\d+)</td>\s+
	<td\s class="fields">(?P<fields>\d+\s+)</td>\s+""", re.VERBOSE)

#findPossibleData = re.compile(r"""
#	zoom=00&run=(?P<run>\d+)&rerun=(?P<rerun>\d+)&camcol=(?P<camcol>\d+)&field=(?P<field>\d+)&
#	""", re.VERBOSE)
# note that the desired fields can access thus:
#    m = findPossibleData.seach(someHTMLtext)
#    print m.group('run'), m.group('rerun'), m.group('camcol') et cetera


# Put all the functions in a list:
SEARCHES = []



def BestRun( thisField, restofList ):
	"""Compare a given field specified by thisField with a list of other
	fields (specifed by restofList).  If the field is unique, or if it
	matches another field but has a higher rerun number, then return True.
	Otherwise, return False.
	"""
	for nextList in restofList:
		if (thisField[0] == nextList[0]) and (thisField[2] == nextList[2]) and (thisField[3] == nextList[3]):
			if (int(thisField[1]) >= int(nextList[1])):
				return True
			else:
				return False
	else:
		return True


def FilterRuns( theList ):
	"""Given a list of (run,rerun,camcol,field) tuples, return a "filtered" list
	where duplicate fields are discarded (in case of duplicates, the field with the
	highest rerun number is retained).
	"""
	finalList = []
	done = False
	while not done:
		try:
			currentField = theList[0]
			theList.remove(currentField)
			if BestRun(currentField, theList):
				finalList.append(currentField)
		except IndexError:
			done = True
	return finalList

		

# Subclass the BasicArchive class to handle deviant input and posting 
# requirements of the CFHT archive
class SloanCoordsArchive(basic_archive.BasicArchive):

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
		self.params[RADEC_LABEL] = "%.5f,%.5f" % utils.RADecToDecimalDeg(ra_str, dec_str)


	# We override QueryServer because the SDSS coords archive prefers 
	# multipart/form-data queries, not urlencoded
	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us.
		# Note that here we are using our special multipart/form-data
		# method for posting to the archive.
		connection = multipart_form.MultipartPost(self.URL, self.params)
		htmlReceived = connection.read().decode('utf-8')
		connection.close()
		return htmlReceived


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
			foundData = findIndividualData.findall(htmlText)
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
					messageString = "Imaging data exists!"
					trimmedList = FilterRuns(foundData)
					nDataFound = len(trimmedList)
					if (self.mode == "fetchsdss"):
						for ds in trimmedList:
							messageString += "\n\t\t(run, rerun, camcol, field = "
							messageString += "%s %s %s %s)" % (ds[0].strip(), ds[1].strip(), ds[2].strip(), ds[3].strip())
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
	return SloanCoordsArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

