# Archive class and module for SDSS DAS server (for retrieving actual
# FITS files -- images and tables)
# 
# This module defines a new class (DASArchive) derived from the 
# BasicArchive class.
# 
#    For Data Release 6 (DR6)
#    
#    This has been modified from the original "standard" SDSS archive 
# class (sdss_archive.py) to generate a "data-request" query for the actual
# Data Archive Server.  The returned HTML are parsed to find the URL
# for the data tarball; this is included in the "message text" returned
# by AnalzyeHTML()

import re, urllib
import basic_archive
import utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "1000"

DEFAULT_CSVCOORDS = "256.443154,58.0255"

DAS_DATA_URL = "http://das.sdss.org/"

# Sloan Digital Sky Survey, Data Release 6:
TARGET_LABEL = None
RA_LABEL = None
DEC_LABEL = None
REQUESTED_IMAGES_LABEL = "csvIn"
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR5) Data Archive Server"
ARCHIVE_SHORTNAME = "sdss-das"
# older URL for DR5:
#ARCHIVE_URL = "http://das.sdss.org/DR5-cgi-bin/DAS"
# for DR6:
ARCHIVE_URL = "http://das.sdss.org/DR6-cgi-bin/DAS"
ARCHIVE_USER_URL = ARCHIVE_URL
# note that in order to handle multiple "products" entries, we specify
# a list of values
DICT = {'Submit': "Submit Request", 'products': ["fpC", "bestTsField"],
		'inputFile': "", 'csvIn': "", 'outputType': "tar.gz"}


#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   Check for data-returned reply and extract useful numbers
#   Slightly kludgy: we look for text in this format and save everything
# between "<a href=" and " </a>", which is actually *two* copies of the
# URL, separated by the closing ">" of the href piece
# ("<a href=/blah/blah.tar.gz> /blah/blah.tar.gz </a>").
# Then we can chop this string up using ">" as a separator...
findURL = re.compile(r"""Use your browser to download the results file.<a href=(?P<url>.+) </a>""")


# Put all the functions in a list:
SEARCHES = []


# New class for SDSS searches:
class DASArchive( basic_archive.BasicArchive ):
	# No point in overriding the base class initialization for now
	
	def InsertBoxSize(self, box_size):
		# Useless for this server
		pass


	def InsertTarget(self, target_name):
		# Useless for this server
		pass


	def InsertCoordinates(self, coords_list):
		# coords_list is a list containing two *strings*: the first has the
		# necessary SDSS "coordinates" -- i.e., run, rerun, camcol, and field --
		# obtained by querying the Footprint Server (or supplied by the 
		# user); the second has the user-requested filters.
		sdss_info = coords_list[0]
		filters = coords_list[1]
		# Extract sdss info:
		if (sdss_info.find(",") >= 0):
			# comma-separated values
			sdss_pieces = sdss_info.split(",")
		else:
			sdss_pieces = sdss_info.split()
		run = sdss_pieces[0]
		rerun = sdss_pieces[1]
		camcol = sdss_pieces[2]
		field = sdss_pieces[3]
		
		requestString = "run,rerun,camcol,filter,field\n"
		requestString += "%s,%s,%s,%s,%s\n" % (run, rerun, camcol, filters, field)
		
		self.params[REQUESTED_IMAGES_LABEL] = requestString


	def EncodeParams(self):
		# Need to override the basic_archive version of this because we need
		# to specify "doseq=True" for urlencode, due to multiple "products"
		# entries (see notes for DICT above)
		encodedParams = urllib.urlencode(self.params, doseq=True)
		if ( self.specialParams != None ):
			encodedParams += self.specialParams
		return encodedParams
	
	
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
	
		# Check to see if there's any data present or not:
		urlPresent = findURL.search(htmlText)
		
		if (urlPresent):
			validReply = 1
			nDataFound = 1
	
		# Next, check to see if there was a screw-up of some kind.
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0


		# Evaluate results of search and construct returned string:
		if ( connectionMade ):
			if ( validReply ):
				if ( nDataFound > 0 ):
					theString = urlPresent.group('url')
					relativeURL = theString.split('>')[0]
					absoluteURL = DAS_DATA_URL + relativeURL
					messageString = absoluteURL
				else:
					if ( noDataExists ):
						messageString = "No data found."
					else:
						messageString = "Strange reply from archive."
						nDataFound = -1
			else:
				messageString = "Invalid reply from archive (possibly malformed coordinates?)."
				nDataFound = -1
		else:
			messageString = "Failed connection to archive web site..."
			nDataFound = -1

		return (messageString, nDataFound)

# End Class



# Factory function to create an instance of DASArchive
def MakeArchive():
	return DASArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)



			

# example of a properly encoded submission URL [DR3]:
sample="""
http://das.sdss.org/DR3-cgi-bin/DAS?products=fpC;products=bestTsField;inputFile=;csvIn=run%2Crerun%2Ccamcol%2Cfilter%2Cfield%0D%0A1339%2C40%2C5%2Cgri%2C75%0D%0A;outputType=tar.gz;Submit=Submit%20Request
"""

#  And here's what a link to actual data looks like:
tarballLinkHTML="Use your browser to download the results file.<a href=/webscratch/DAS_26221_1111347757/csv.tar.gz>"
# the full link is:
#    http://das.sdss.org/webscratch/DAS_26221_1111347757/csv.tar.gz

#  And here's the full HTML for successful query:
fullHTML = """
<html>
<p>Begin access on Sun Mar 20 13:42:37 CST 2005
 at /webscratch/DAS_26221_1111347757. </p>
<title>SDSS Data Archive Server: DR3 Results</title><body bgcolor=#FFFFFF>
<h1>SDSS Data Archive Server Results (DR3)</h1>
<p><a href="http://das.sdss.org/DR3-cgi-bin/DAS?products=fpC;products=bestTsField;inputFile=;csvIn=run%2Crerun%2Ccamcol%2Cfilter%2Cfield%0D%0A1339%2C40%2C5%2Cgri%2C75%0D%0A%20%20;outputType=tar.gz;Submit=Submit%20Request">Bookmark this link to recreate this DAS query result</a></p>Use your browser to download the results file.<a href=/webscratch/DAS_26221_1111347757/csv.tar.gz> /webscratch/DAS_26221_1111347757/csv.tar.gz </a><p> (Note that any files generated under /export/data/www/data/webscratch/DAS_26221_1111347757 will have a limited lifetime -- typically 24 hours.)<p>The file size is 6973872 bytes.<p><pre>SDSS wrapper report Sun Mar 20 13:42:43 CST 2005
Version v16_210 
Total number of bytes to be written:  6996356
        2134973 1339/40/corr/5/fpC-001339-g5-0075.fit.gz
        2307969 1339/40/corr/5/fpC-001339-r5-0075.fit.gz
        2524614 1339/40/corr/5/fpC-001339-i5-0075.fit.gz
          28800 stripe42_mu750191_1/5/tsField-001339-5-40-0075.fit
</pre><hr><p><hr>Create a <a href=http://das.sdss.org/DR3-cgi-bin/DAS>new request</a> or use your browser's back button to modify this request.
"""