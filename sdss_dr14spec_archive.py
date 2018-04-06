# Archive class specialization for SDSS archive ("SkyServer DR14 Spectroscopic Query Form")
# 
# This module defines a new class (SloanDR14Archive) derived from the 
# BasicArchive class, to allow queries to the Spectroscopic Query Form
# interface of the SDSS archive.

# The new class includes a modified QueryServer() method which uses 
# multipart/form posting.

import re
import basic_archive, multipart_form
import utils

DEFAULT_TIMEOUT = 30.0
BROWSER_MASQUERADE = "Mozilla/5.0 [en]"
DEFAULT_BOXSIZE_STRING = "00 04 00"

# SDSS DR14 spectroscopic search
TARGET_LABEL = None
RA_LABEL = 'ra'
DEC_LABEL = 'dec'
RADIUS_ARCMIN_LABEL = 'radius'
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR14) Spectrum-Search Server"
ARCHIVE_SHORTNAME = "sdss-spec"
ARCHIVE_URL = "http://skyserver.sdss.org/dr14/en/tools/search/x_results.aspx"
ARCHIVE_USER_URL ="http://skyserver.sdss.org/dr14/en/tools/search/SQS.aspx"
DICT = {'ReturnHtml': 'true', 'TableName': '', 'TaskName': 'Skyserver.Search.SQS',
 'bossFlagsOffList': 'ignore', 'bossFlagsOnList': 'ignore', 'dec': '27.977025',
 'decMax': '0.22', 'decMin': '0.20', 'doGalaxy': 'on', 'doStar': 'on',
 'ebossFlagsOffList': 'ignore', 'ebossFlagsOnList': 'ignore', 'flagsOffList': 'ignore',
 'flagsOnList': 'ignore', 'format': 'csv', 'gMax': '', 'gMin': '', 'grMax': '',
 'grMin': '', 'iMax': '', 'iMin': '', 'imgparams': 'none', 'izMax': '', 'izMin': '',
 'limit': '50', 'magType': 'model', 'minQA': '', 'positionType': 'cone',
 'priFlagsOffList': 'ignore', 'priFlagsOnList': 'ignore', 'rMax': '', 'rMin': '',
 'ra': '195.033737', 'raMax': '10.2', 'raMin': '10', 'radecFilename;': '',
 'radecTextarea': '', 'radius': '0.10', 'radiusDefault': '0.10', 'redshiftMax': '',
 'redshiftMin': '', 'riMax': '', 'riMin': '', 'searchNearBy': 'nearest',
 'searchtool': 'Spectro', 'secFlagsOffList': 'ignore', 'secFlagsOnList': 'ignore',
 'specparams': 'minimal', 'uMax': '', 'uMin': '', 'ugMax': '', 'ugMin': '',
 'zMax': '', 'zMin': '', 'zWarning': 'on'}





#   Some regular expressions we will need:
#   See if we apparently got a proper reply (data or not):
findReply = re.compile(r"""plate,mjd,fiberid""")


# Put all the functions in a list:
SEARCHES = []


def SearchForSpectra( csvText ):
	"""We assume that the CSV text returned by the archive has the following format:
		#Table1
		plate,mjd,fiberid
	followed by zero or more lines of the form
		nnnn,nnnnn,nnn
	
	In the case of *no* data, there will only be the first two lines.
	"""
	spectraInfo = []
	lines = csvText.splitlines()
	nLines = len(lines)
	if nLines > 2:
		for line in lines[2:]:
			spectraInfo.append(line.split(","))
	return nLines - 2, spectraInfo


# Subclass the BasicArchive class
class SloanDR14Archive(basic_archive.BasicArchive):

	def SetMode(self, mode_name):
		self.mode = mode_name
		
		
	def InsertBoxSize(self, box_size):
		# Useless for SDSS searches, so we do nothing
		pass


	def InsertSpectroscopyRadius(self, radius):
		# Assume search radius for spectra is in arcmin
		self.params['radius'] = radius


	def InsertTarget(self, target_name):
		# SDSS interface won't let us use target names, so we do nothing
		pass


	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for SDSS searches, which require decimal degrees!
		ra_str = coords_list[0]
		dec_str = coords_list[1]
		ra_deg_str, dec_deg_str = utils.RADecToDecimalDeg(ra_str, dec_str)
		self.params[RA_LABEL] = ra_deg_str
		self.params[DEC_LABEL] = dec_deg_str


	# We override QueryServer because the SDSS archive prefers 
	# multipart/form-data queries, not urlencoded
	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever text (HTML or CSV) the server sends us.
		# Note that here we are using our special multipart/form-data
		# method for posting to the archive.
		connection = multipart_form.MultipartPost(self.URL, self.params)
		textReceived = connection.read().decode('utf-8')
		connection.close()
		return textReceived


	def AnalyzeHTML(self, csvText):
		#    Function which searches a blob of CSV text.  We look for various
		# text fragments: signs of valid or invalid reply, did the archive find data
		# or not, etc.  Uses the regular-expression objects defined above.
		#    csvText = blob of CSV text (entire reply from archive, in a string)
		
		# Default boolean flags:
		connectionMade = True    # successfully connected to archive web server
		validReply = False       # we got a genuine reply from the web server
		nDataFound = 0           # OUR flag indicating whether archive found data, and if so,
		                         #    how *many* data sets
	
		# Search the text, try to figure out if we got a valid result,
		# and if any data exists:
	
		# First, check to see if we got a well-formed reply (data or not):
		foundValidReply = findReply.search(csvText)
		# Now, check to see if there's any data present or not:
		if (foundValidReply is not None):
			validReply = True
			nDataFound, spectraInfo = SearchForSpectra(csvText)
	
		# Evaluate results of search and construct returned string:
		if ( connectionMade ):
			if ( validReply ):
				if ( nDataFound > 0 ):
					messageString = "Spectroscopic data exists!"
					rad_arcmin = float(self.params[RADIUS_ARCMIN_LABEL])
					if (nDataFound == 1):
						messageString += " (one spectrum within "
					else:
						messageString += " (%d spectra within " % nDataFound
					messageString += "r = %.3f arcmin)" % rad_arcmin
					if (self.mode == "fetchsdss"):
						for specInfo in spectraInfo:
							messageString += "\n\t\t(SDSS plate, mjd, fiber = "
							messageString += "%s %s %s)" % (specInfo[0], specInfo[1], specInfo[2])
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
	return SloanDR14Archive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

