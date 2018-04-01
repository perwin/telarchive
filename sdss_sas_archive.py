# Archive class specialization for SDSS Science Archive Server 
# 
# This module defines a new class (SloanScienceArchive) derived from the 
# BasicArchive class, to allow queries to the coordinate-list submission
# form interface of the SDSS archive.

import re
import basic_archive
import utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_RETURNED = "200"

DEFAULT_RA = "164.68184"
DEFAULT_DEC = "55.59788"
DEFAULT_RADIUS = "0.002"

TARGET_LABEL = None
RA_LABEL = "center_ra"
DEC_LABEL = "center_dec"
RADEC_LABEL = None
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR12) Science Archive Server"
ARCHIVE_SHORTNAME = "sdss-sas"
ARCHIVE_URL ="http://data.sdss3.org/advancedSearch/process"
ARCHIVE_USER_URL = "http://data.sdss3.org/advancedSearch"
DICT = {'center_ra': DEFAULT_RA, 'center_dec': DEFAULT_DEC, 
'boss_target_logic': 'any', 'classes': 'all', 'fibers': '', 'g_max': '',
'g_min': '', 'i_max': '', 'i_min': '', 'limit': MAX_RETURNED, 'mag_type': 'psf',
'max_dec': '', 'max_ra': '', 'min_dec': '', 'min_ra': '', 'mjds': '',
'plateids': '', 'r_max': '', 'r_min': '', 'radec_searchtype': 'radial',
'radius': DEFAULT_RADIUS, 'redshift_max': '', 'redshift_min': '',
'sdss_target_logic': 'any', 'surveys': ['sdss', 'boss'], 'u_max': '', 'u_min': '',
'z_max': '', 'z_min': '', 'zwarning_logic': 'all', 'zwarning_zero': 'yes'}


#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""(DR10|DR12) Science Archive Server \(SAS\)""")
#   Check for number of hits:
#findPossibleData = re.compile(r"""<td class="ra" onclick="goToURL\('/spectrumDetail""")
findPossibleData = re.compile(r"""<td\s+onclick="goToURL\('/spectrumDetail""")

#   Check for data-returned reply and extract useful numbers
# the following are DR9 format
# findIndividualData = re.compile(r"""<td class="ra" onclick="goToURL\('/spectrumDetail\?plateid=(?P<plate>\d+)\&amp\;mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)'\)\;">""")
# findSDSSData = re.compile(r"""<td onclick="goToURL\('/spectrumDetail\?plateid=(?P<plate>\d+)\&amp\;mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)'\)\;">SDSS</td>""")
# findBOSSData = re.compile(r"""<td onclick="goToURL\('/spectrumDetail\?plateid=(?P<plate>\d+)\&amp\;mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)'\)\;">BOSS</td>""")
# and here we have DR10 format
findIndividualData = re.compile(r"""<td\s*onclick="goToURL\('/spectrumDetail\?mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)\&amp\;plateid=(?P<plateid>\d+)'\)\;">""")
findSDSSData = re.compile(r"""<td\s*onclick="goToURL\('/spectrumDetail\?mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)\&amp\;plateid=(?P<plateid>\d+)'\)\;">SDSS</td>""")
findBOSSData = re.compile(r"""<td\s*onclick="goToURL\('/spectrumDetail\?mjd=(?P<mjd>\d+)\&amp\;fiber=(?P<fiber>\d+)\&amp\;plateid=(?P<plateid>\d+)'\)\;">BOSS</td>""")

#	zoom=00&run=(?P<run>\d+)&rerun=(?P<rerun>\d+)&camcol=(?P<camcol>\d+)&field=(?P<field>\d+)&
#	""", re.VERBOSE)
# note that the desired fields can access thus:
#    m = findPossibleData.seach(someHTMLtext)
#    print m.group('plate'), m.group('mjd'), m.group('fiber') et cetera


# Put all the functions in a list:
SEARCHES = []



# Subclass the BasicArchive class to handle deviant input and posting 
# requirements 
class SloanScienceArchive(basic_archive.BasicArchive):

	def SetMode(self, mode_name):
		self.mode = mode_name
		
		
	def InsertRadius(self, radius):
		# assume radius is in arcmin
		radius_deg = float(radius)/60.0
		self.params['radius'] = str(radius_deg)


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
		raDeg, decDeg = utils.RADecToDecimalDeg(ra_str, dec_str)
		self.params[RA_LABEL] = "%.5f" % raDeg
		self.params[DEC_LABEL] = "%.5f" % decDeg



	# slight kludge: we don't need to search the HTML again; we just need to return
	# a message stating how many separate fields were found
	def DoSpecialSearches(self, htmlText, nFound):
		if (nFound == 1):
			messageString = "\n\t\tone spectrum found"
		else:
			messageString = "\n\t\t%d spectra found" % nFound
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
					# we do the following to get lists of RE match objects, which we
					# can query by group names
					foundSDSS = list(findSDSSData.finditer(htmlText))
					foundBOSS = list(findBOSSData.finditer(htmlText))
					messageString = "Spectroscopic data exists!"
					rad_deg = float(self.params['radius'])
					rad_arcmin = 60*rad_deg
					messageString += " (%d SDSS + %d BOSS within " % (len(foundSDSS), len(foundBOSS))
					messageString += "r = %.5f deg = %.3f arcmin)" % (rad_deg, rad_arcmin)
					if (self.mode == "fetchsdss"):
						for ds in foundSDSS:
							messageString += "\n\t\t(SDSS plate, mjd, fiber = "
							messageString += "%s %s %s)" % (ds.group('plateid').strip(), ds.group('mjd').strip(), ds.group('fiber').strip())
						for ds in foundBOSS:
							messageString += "\n\t\t(BOSS plate, mjd, fiber = "
							messageString += "%s %s %s)" % (ds.group('plateid').strip(), ds.group('mjd').strip(), ds.group('fiber').strip())
				else:
					messageString = "No spectroscopic data found."
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
	return SloanScienceArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

