# Archive class specialization for ING archive (newer interface served from
# ING at La Palma, rather than CASU at Cambridge)
# 
# This module is primarily for generating and returning an instance of
# the INGLaPalmaArchive class.

# Sample submission URL:
#http://catserver.ing.iac.es/insobslog/index.php?telescope=All&wht_ins=Any&fov=4&expmin=&run_nr=&expmax=&search=box&end=&name=&int_ins=Any&submit=RETRIEVE+RUN+DATA&filter=&jkt_ins=JAG&mode=any&output=ascii_simp&dec=69.20333&type=science&start=&ra=139.82750

# IMPORTANT: the "submit" value has to be "RETRIEVE+RUN+DATA", which means we need
# to store it using spaces in the params dict (if we store it with "+" signs instead,
# then urllib.urlencode will generate "RETRIEVE%2BRUN%2BDATA", which will not work.


# No data found message: "\nNo entries found in ING's observing-log database.<br>"

#http://catserver.ing.iac.es/insobslog/index.php?telescope=All&wht_ins=Any&fov=4&expmin=&run_nr=&expmax=&search=box&end=&name=&int_ins=Any&submit=RETRIEVE+RUN+DATA&filter=&jkt_ins=JAG&mode=any&output=ascii_simp&dec=69.20333&type=science&start=&ra=139.82750

DEFAULT_TIMEOUT = 30.0
BROWSER_MASQUERADE = "Mozilla/5.0 [en]"


import sys, re
import basic_archive
import archive_analyze
import utils

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

DEFAULT_TARGET = ""
DEFAULT_BOXSIZE_STRING = "4"
MAX_ROWS_RETURNED = "5000"

# Isaac Newton Group Archive:
TARGET_LABEL = "name"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "ING Archive (La Palma)"
ARCHIVE_SHORTNAME = "ing"
ARCHIVE_URL = "http://catserver.ing.iac.es/insobslog/index.php"
ARCHIVE_USER_URL = "http://www.ing.iac.es/astronomy/observing/inglogs.php"
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "0.0", DEC_LABEL: "0.0",
		'telescope': "All", 'wht_ins': "Any", 'int_ins': "Any", 'jkt_ins': "JAG",
		'mode': "any", 'search': "box", 'fov': DEFAULT_BOXSIZE_STRING,
		'start': "", 'end': "", 'expmin': "", 'expmax': "", 'filter': "",
		'run_nr': "", 'type': "science", 'output': "ascii_simp", 'submit': "RETRIEVE RUN DATA"}




def GetObsTextLines( htmlText ):
	"""
	Given a blob of text returned by the ING La Palma archive, we split it into
	individual lines, replace "&nbsp" with actual spaces, and return a list containing
	only those lines which (we hope) have individual observation info.
	"""
	cleanText = htmlText.replace("&nbsp;", " ")
	lines = cleanText.split("<br>")
	startIndex = -99
	for i in range(len(lines)):
		if lines[i].find("---+---") > 0:
			startIndex = i
	# remove short lines (e.g, final line which is usually something like "</pre>")
	dlines = [ line for line in lines[startIndex:] if len(line.split("|")) >= 10 ]
	return dlines	
	

def GetNFound( htmlText ):
	"""Returns an integer specifying the number of observations found by
	the La Palma ING archive.
	"""
	if htmlText.find("No entries found in ING's observing-log database.") > 0:
		return 0
	else:
		return len(GetObsTextLines(htmlText))


def SearchHTMLForObs( htmlText, nFound=None ):
	"""
	Returns string containing counts for different observation types (images,
	spectra, etc.)
	
	Meant to be called from archive_search.py, only when there actually *are*
	observations.
	"""
	dlines = GetObsTextLines(htmlText)
	nObs = len(dlines)
	if nObs > 0:
		nPhot = nSpec = nUnknown = 0
		for line in dlines:
			if line.find("img") > 0:
				nPhot += 1
			elif line.find("spe"):
				nSpec += 1
			else:
				nUnknown += 1

		# Add up all the images and/or spectra:
		inputList = [ ["image","images",nPhot], ["spectrum","spectra",nSpec],
						["unknown","unknown",nUnknown] ]

	return "\n\t\t" + utils.ConstructCountString(inputList)


def AddEntry( theDict, telKey, instKey ):
	"""
	Given a pre-existing dictionary, this increments the integer value stored in
		theDict[telKey][instKey]
	
	If no such entry exists in the dictionary, then one is created, with value = 0
	"""
	if telKey not in theDict.keys():
		theDict[telKey] = {instKey: 1}
	else:
		if instKey not in theDict[telKey].keys():
			theDict[telKey][instKey] = 1
		else:
			theDict[telKey][instKey] += 1

def FindTelescopesAndInstruments( inputText, nFound=None ):
	"""
	Given HTML input text returned by La Palma ING archive, this returns a
	string summarizing the individual observations by telescope and instrument.
	
	Sample output:
		"WHT -- INGRID (12); INT -- WFC (1)"
		
	Meant to be called from archive_search.py, only when there actually *are*
	observations.
	"""
	msgText = "\n\t\t"
	
	# First, search through HTML text and accumulate finds
	dlines = GetObsTextLines(inputText)
	telDict = {}
	for line in dlines:
		pp = line.split("|")
		telescopeName = pp[5].strip()
		instrumentName = pp[6].strip()
		AddEntry(telDict, telescopeName, instrumentName) 
	
	nTelescope = 0
	for telName in ["WHT", "INT", "JKT"]:
		if telName in telDict.keys():
			if nTelescope > 0:
				msgText += "; "
			msgText += "%s -- " % telName
			instList = list(telDict[telName].keys())
			instList.sort()
			nInstruments = len(instList)
			if nInstruments == 1:
				instName = instList[0]
				msgText += "%s (%d)" % (instName, telDict[telName][instName])
			else:
				for j in range(nInstruments):
					instName = instList[j]
					msgText += "%s (%d)" % (instName, telDict[telName][instName])
					if (j < (nInstruments - 1)):
						msgText += ", "
			nTelescope += 1
	
	return msgText


# Put all the functions	in a list:
SEARCHES = [SearchHTMLForObs, FindTelescopesAndInstruments]




# Subclass the BasicArchive class to handle deviant input requirements
# of the La Palma ING archive
class INGLaPalmaArchive(basic_archive.BasicArchive):

	# Override the InsertBoxSize() method, because La Palma ING archive wants the 
	# search box size in decimal arc minutes, *not* the standard "hh mm ss" format
	# we use otherwise
	def InsertBoxSize(self, box_size):
		self.params[self.boxLabel] = str(box_size)
		
	# Override InsertTarget() method so we *don't* store the target name, because 
	# ING La Palma archive interprets "name" as meaning "search for exact match with object
	# name in FITS file" (which we don't want it to do!)
	def InsertTarget(self, target_name):
		# This is a tricky part, since each archive can have a different name
		# for the HTML form parameter that specifies the astronomical object to
		# search for:
		pass

	# Override InsertCoordinates() method, because ING La Palma archive
	# requires decimal degrees.
	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for SDSS searches, which require decimal degrees!
		ra_str = coords_list[0]
		dec_str = coords_list[1]
		# currently, we store RA & Dec in decimal degrees to an accuracy of 0.1 arcsec
		ra_decimal, dec_decimal = utils.RADecToDecimalDeg(ra_str, dec_str)
		self.params[self.raLabel] = "%.5f" % (ra_decimal)
		self.params[self.decLabel] = "%.5f" % (dec_decimal)

	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us
		
		# NOTE: for some reason, the La Palma archive server requires that we
		# send the request as a GET command -- however, urllib2.Request
		# automatically generates a POST command instead if you give it
		# data (e.g., the encoded params dict). So we need to construct the
		# URL by hand before passing it to urllib2.Request...
		
		# NOTE: in Python 3, the EncodeParams() method will return a *byte* string
		# which will cause an exception to be thrown when added to the strings
		# self.URL and "?"; so we call decode() to convert it to a (Unicode) string
		urlFull = self.URL + "?" + self.EncodeParams().decode()
		specialHeader = {'User-agent': BROWSER_MASQUERADE}
		req = Request(urlFull, self.EncodeParams(), specialHeader)
		response = urlopen(req, timeout=self.timeout)
		htmlReceived = response.read()
		response.close()

		# convert result from bytes to Unicode string so Python 3 doesn't choke;
		# specify 'utf-8' instead of 'ascii' in case we get Unicode characters
		return htmlReceived.decode('utf-8')


	def AnalyzeHTML( self, htmlText):
	
		# check for possible errors
		errMessage = archive_analyze.CheckForError(htmlText)
		if errMessage != "":
			return (errMessage, 0)
		
		# Search for possible observations (or straightforward "none found" message)
		nDataFound = GetNFound(htmlText)
		if ( nDataFound > 0 ):
			if nDataFound == 1:
				nSetsString = "One observation"
			else:
				nSetsString = "%d observations found" % nDataFound
			messageString = "Data exists! " + "(" + nSetsString + ")"
		else:
			messageString = "No data found."
		
		return (messageString, nDataFound)
		



# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return INGLaPalmaArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="fov")

