# Archive class and module for the Gemini Science Archive
# 
# This module defines a new class (GeminiArchive) derived from the 
# BasicArchive class.

import re
import basic_archive, multipart_form

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# Gemini Science Archive:
TARGET_LABEL = "tobject"
RA_LABEL = "ra2000"
DEC_LABEL = "dec2000"
ARCHIVE_NAME = "Gemini Science Archive"
ARCHIVE_SHORTNAME = "gemini"
#ARCHIVE_URL = "http://www1.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/gsa/wdbi.cgi/gsa/gsa_science/query"
ARCHIVE_URL = "http://www4.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/en/gsa/wdbi.cgi/gsa/gsa_science/query"

ARCHIVE_USER_URL = "http://www1.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/gsa/wdbi.cgi/gsa/gsa_science/form"

DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'box': DEFAULT_BOXSIZE_STRING, 'simbad': "simbad",
		'wdbi_order': "ut_date_time desc",
		'max_rows_returned': MAX_ROWS_RETURNED,
		'tab_object': "on",
		'tab_instrument': "on", 'instrument': "%",
		'galactic_latitude': "", 'galactic_longitude': "", 'science_category': "%",
		'keywords': "", 'data_superset_name_op': "~", 'data_superset_name': "", 
		'file_id_op': "==", 'file_id': "", 'observing_program_id_op': "~", 
		'observing_program_id': "", 'ra2000_max': "", 'ra2000_min': "", 
		'dec_max': "", 'dec_min': "", 'exposure': "",'ut_date_time': "",
		'release_date': "", 'telescope': "%",
		'tab_mode': "on", 'mode': "%",
		'filters': "", 'pixel_scale': "", 'wavelength_min': "",
		'wavelength_max': "", 'wavelength_central': "", 'ao_system': "%", }


# Code to parse HTML text and count up instrument uses

# the following RE object searches for instances of table entries referring to
# instruments and stores the actual instrument name
# text to search for in order to find/count instruments:
#      <input type="hidden" name="Instrument" value="instrument-name">
# e.g.,
#      <input type="hidden" name="Instrument" value="GMOS-N">
# Similarly for observing modes (imaging, long-slit, multi-object, etc.):
#      <input type="hidden" name="Observing Mode" value="imaging">

findModes = re.compile(r"""<input type="hidden" name="Observing Mode" value="([^"]+?)">""")
findInstruments = re.compile(r"""<input type="hidden" name="Instrument" value="([^"]+?)">""")


def FindStuff(inputText, reObject):
	"""Simple function to record number of observations per type (e.g., 
	number of observations per mode, or per instrument).
	"""
	foundStuff = reObject.findall(inputText)
	theDict = {}
	typeList = []
	for item in foundStuff:
		if item not in typeList:
			theDict[item] = 1
			typeList.append(item)
		else:
			theDict[item] += 1
	return (typeList, theDict)
	

def FindObservingModes(inputText, nFound=None):
	msgText = "\n\t\t"
	(modeList, theDict) = FindStuff(inputText, findModes)
	for i in range(len(modeList)):
		modeName = modeList[i]
		nObs = theDict[modeName]
		msgText += "%d %s" % (nObs, modeName)
		if (i < (len(modeList) - 1)):
			msgText += ", "
	return msgText


def FindInstruments(inputText, nFound=None):
	msgText = "\n\t\t"
	(instList, theDict) = FindStuff(inputText, findInstruments)
	for i in range(len(instList)):
		instName = instList[i]
		msgText += instName + " (%d)" % theDict[instName]
		if (i < (len(instList) - 1)):
			msgText += ", "
	
	return msgText

# Put all the functions in a list:
SEARCHES = [FindObservingModes, FindInstruments]


# Subclass the BasicArchive class to handle deviant input and posting 
# requirements of the Gemini archive
class GeminiArchive(basic_archive.BasicArchive):

	# We override QueryServer because the Gemini Science Archive wants 
	# multipart/form-data queries, not urlencoded
	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us.
		# Note that here we are using our special multipart/form-data
		# method for posting to the archive.
		connection = multipart_form.MultipartPost(self.URL, self.params)
		# Loop to make sure we get *all* of the HTML (bug of sorts in MacPython 2.0--2.2):
# 		htmlReceived = ''
# 		newdata = connection.read()
# 		while newdata:
# 			htmlReceived += newdata
# 			newdata = connection.read()
# 		connection.close()
		htmlReceived = connection.read()
		connection.close()
		return htmlReceived

# Factory function to create an instance of GeminiArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return GeminiArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="box")


# "No data found" reply contains the following text:
# "No data returned !"
#    -- this is already handled by the standard ArchiveAnalyze() function 
#    in archive_analyze.py
