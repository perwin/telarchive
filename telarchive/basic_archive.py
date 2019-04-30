# Base class for individual telescope archives.  Actual archive classes
# are derived from this class -- or at least created as specialized 
# instances of this class via factory functions -- in the individual archive
# models (ing_archive.py, etc.).

import sys
import math
from contextlib import closing

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



DEFAULT_TIMEOUT = 30.0
BROWSER_MASQUERADE = "Mozilla/5.0 [en]"


class BasicArchive(object):
	def __init__(self, long_name, short_name, url, params_dict,
				specialSearches, targetLabel, raLabel, decLabel,
				special_params=None, boxLabel='box', publicURL=None):
		self.longName = long_name
		self.shortName = short_name
		self.URL = url
		# we know that params_dict is a dictionary, so make a *copy* of it;
		# otherwise, we'll be modifying the original instance in the
		# individual-archive module, which makes things hard to debug...
		self.params = params_dict.copy()
		self.specialParams = special_params
		self.nSearches = len(specialSearches)
		self.theSearches = specialSearches
		self.targetLabel = targetLabel
		self.raLabel = raLabel
		self.decLabel = decLabel
		self.boxLabel = boxLabel
		self.timeout = DEFAULT_TIMEOUT
		if publicURL is None:
			self.publicURL = url
		else:
			self.publicURL = publicURL
		self.mode = "default"   # "default" = standard behavior for use 
		                        # with archive_search.py
	
	
	def InsertBoxSize(self, box_size):
		# By default, we assume input box size is a float specifying
		# box size in arcminutes; we convert this to a string of "dd mm ss" form,
		# which is what most of the archives require.
		# We also assume that box_size < 60 !
		arcminString = "%02d" % math.ceil(box_size)
		if ( math.floor(box_size) == box_size ):
			arcsecString = "00"
		else:
			arcsecs = math.floor( (box_size - math.floor(box_size)) * 60 )
			arcsecString = "%02d" % arcsecs
		boxSizeString = "00 " + arcminString + " " + arcsecString
		self.params[self.boxLabel] = boxSizeString


	def InsertTarget(self, target_name):
		# This is a tricky part, since each archive can have a different name
		# for the HTML form parameter that specifies the astronomical object to
		# search for:
		self.params[self.targetLabel] = target_name
		# When we search by target name, zero the RA+Dec entries:
		self.params[self.raLabel] = ""
		self.params[self.decLabel] = ""


	def InsertCoordinates(self, coords_list):
		# Coordinate list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" sexigesimal format, though decimal values 
		# for the seconds are optional.
		#    Override this for SDSS searches, which require decimal degrees!
		self.params[self.raLabel] = coords_list[0]
		self.params[self.decLabel] = coords_list[1]
		# When we search by coords, zero the Name entry:
		self.params[self.targetLabel] = ""
	
	
	def SetURL(self, newURL):
		# Changes URL for the archive; mostly intended for testing
		self.URL = newURL


	def SetTimeout(self, timeout_secs):
		# Changes connection timeout for the archive (in seconds)
		self.timeout = timeout_secs


	def EncodeParams(self):
		encodedParams = urlencode(self.params, doseq=True)
		if ( self.specialParams != None ):
			encodedParams += self.specialParams
		return encodedParams.encode('utf-8')
	
	
	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us
		#req = urllib.request.Request(self.URL, self.EncodeParams())
		req = Request(self.URL, self.EncodeParams())
		req.add_header('User-agent', BROWSER_MASQUERADE)
		#response = urlopen(req, timeout=self.timeout)
		with closing(urlopen(req, timeout=self.timeout)) as response:
			htmlReceived = response.read().decode('utf-8')
		#response.close()
		return htmlReceived


	def DoSpecialSearches(self, htmlText, nFound):
		messageString = ""
		for i in range(self.nSearches):
			messageString += self.theSearches[i](htmlText, nFound)
		return messageString
	
	
	def AnalyzeHTML(self, htmlReceived):
		# For "basic" archives, we use the standard AnalyzeHTML function
		return archive_analyze.AnalyzeHTML(htmlReceived)
	
# End Class

