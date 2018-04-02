# Archive class and module for querying SDSS archive via SQL for DS8
# 
# This module defines a new class (SloanSQLArchive) derived from the 
# BasicArchive class.
# 
#    This is meant to be used by both archive_search.py *and* fetchsdss.py
#    
#    For Data Release 8 (DR6)
#       -- based on code kindly provided by Stefano Zibetti
#    
#
# OR: http://data.sdss3.org/coverageCheck
# ==> http://data.sdss3.org/coverageCheck.html?search=radec&radec=228.75516%2C65.50821&submit=Submit
# where ra,dec = 228.75516,65.50821
#
# How to get run/rerun/camcol/field info (but only for one field; e.g. 'NGC 936' gives you
# one field -- perhaps DR8 hasn't ingested Stripe 82?):
# http://data.sdss3.org/fields?search=radec&ra=228.75516&dec=65.50821&submit=Submit

import re, urllib
import basic_archive
import utils

# Structure of the SQL query:
#    SELECT F.run, F.rerun, F.camcol, F.field
#    FROM Field F, PhotoObjAll P
#    Join dbo.fGetNearestObjEq(ra_decdeg, dec_decdeg, 1.0) as SN
#    on P.objID = SN.objID
#    WHERE P.fieldID = F.fieldID

# SELECT 
#    p.run, p.rerun, p.camcol, p.field
# FROM #upload u
#       JOIN #x x ON x.up_id = u.up_id
#       JOIN PhotoTag p ON p.objID = x.objID 
# ORDER BY x.up_id

SQLSTRING_START = "SELECT F.run,F.rerun,F.camcol,F.field FROM Field F,PhotoObjAll P\n"
SQLSTRING_END = "on P.objID = SN.objID WHERE P.fieldID=F.fieldID"

# Sloan Digital Sky Survey, Data Release 6:
TARGET_LABEL = None
RA_LABEL = None
DEC_LABEL = None
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR6) SQL Search"
ARCHIVE_SHORTNAME = "sdss"
# URL for DR5:
#ARCHIVE_URL = "http://cas.sdss.org/DR5/en/tools/search/x_sql.asp"
# DR6:
ARCHIVE_URL = "http://cas.sdss.org/astrodr6/en/tools/search/x_sql.asp"
# URL for DR5:
#ARCHIVE_USER_URL = "http://cas.sdss.org/DR5/en/tools/search/sql.asp"
# DR6:
ARCHIVE_USER_URL = "http://cas.sdss.org/astrodr6/en/tools/search/sql.asp"
DICT = {'cmd': "", 'format': "csv"}


#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   Find "no data returned" equivalent for SDSS
findNoDataReturned = re.compile(r"No \s objects \s have \s been \s found", re.VERBOSE)
#   Check for data-returned reply and extract useful numbers
findPossibleData = re.compile(r"""
	run,rerun,camcol,field \s
	(?P<run>\d+),(?P<rerun>\d+),(?P<camcol>\d+),(?P<field>\d+)
	""", re.VERBOSE)
# note that the desired fields can access thus:
#    m = findPossibleData.seach(someHTMLtext)
#    print m.group('run'), m.group('rerun'), m.group('camcol') et cetera


# Put all the functions in a list:
SEARCHES = []


# New class for SDSS searches:
class SloanSQLArchive( basic_archive.BasicArchive ):
	# No point in overriding the base class initialization for now
	
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
		queryText = SQLSTRING_START
		queryText += "Join dbo.fGetNearestObjEq(%.5f,%.5f,1.0) as SN " % utils.RADecToDecimalDeg(ra_str, dec_str)
		queryText += SQLSTRING_END
		self.params['cmd'] = queryText


	def AnalyzeHTML(self, htmlText, textSearches=None):
		#    Function which searches a big blob of HTML text.  We look for various
		# text fragments: signs of valid or invalid reply, did the archive find data
		# or not, etc.  Uses the regular-expression objects defined above.
		#    htmlText = big blob of HTML text (entire reply from archive, in a string)
		#    textSearches = not used here; listed for interface compatibility, since
		#                   archive_search.py will call this function with two
		#                   arguments
		
		# Default boolean flags:
		connectionMade = 1       # successfully connected to archive web server
		validReply = 0           # we got a genuine reply from the web server
		noDataExists = 0         # archive did proper search, found no data
		nDataFound = 0           # OUR flag indicating whether archive found data, and if so,
		                         #    how *many* data sets
	
		# Search the text, try to figure out if we got a valid result,
		# and if any data exists:
	
		# First, check to see if we got a well-formed reply (data or not):
		findData = findPossibleData.search(htmlText)
		noDataExists = findNoDataReturned.search(htmlText)
		# Now, check to see if there's any data present or not:
		if (findData):
			validReply = 1
			nDataFound = 1
		elif (noDataExists):
			validReply = 1
			noDataExists = 1
			nDataFound = 0
	
		# Next, check to see if there was a screw-up of some kind.
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0


		# Evaluate results of search and construct returned string:
		if ( connectionMade ):
			if ( validReply ):
				if ( nDataFound > 0 ):
					r = findData.group('run')
					rr = findData.group('rerun')
					cc = findData.group('camcol')
					f = findData.group('field')
					messageString = "Imaging data exists!"
					if (self.mode == "fetchsdss"):
						messageString += "\n\t\t(run, rerun, camcol, field ="
						messageString += " %s %s %s %s)" % (r,rr,cc,f)
				else:
					if ( noDataExists ):
						messageString = "No data found."
					else:
						messageString = "Strange reply from archive:"
						messageString += htmlText
						nDataFound = -1
			else:
				messageString = "Invalid reply from archive (possibly malformed coordinates?)."
				nDataFound = -1
		else:
			messageString = "Failed connection to archive web site..."
			nDataFound = -1

		return (messageString, nDataFound)

# End Class



# Factory function to create an instance of SloanSQLArchive
def MakeArchive():
	return SloanSQLArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

