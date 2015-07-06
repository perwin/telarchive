# Archive class specialization for CFHT archive
# 
# This module defines a new class (CFHTArchive) derived from the 
# BasicArchive class, to allow queries to the archive of the Canada-France-
# Hawaii Telescope.

# The new class includes a modified QueryServer() method which uses 
# multipart/form posting (tests show that, unlike the case for the Gemini 
# archive), old-fashioned GET apparently still works for the CFHT archive 
# server; but since the default approach implemented by the current web page
# uses multipart/form, we'll use that.

import re
import basic_archive, multipart_form

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# Canada-France-Hawaii Telescope archive (Canada):
TARGET_LABEL = "tobject"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "CFHT Archive"
ARCHIVE_SHORTNAME = "cfht"
ARCHIVE_URL = "http://www1.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/cadcbin/cfht/wdbi.cgi/cfht/wfi/query"
ARCHIVE_USER_URL = "http://www4.cadc-ccda.hia-iha.nrc-cnrc.gc.ca/en/cfht/"
DICT = {TARGET_LABEL: DEFAULT_TARGET, 
		RA_LABEL: "", DEC_LABEL: "",
		'wdbi_order': "",
		'tobject': "",
		'simbad': "simbad",
		'max_rows_returned': MAX_ROWS_RETURNED,
		'box': DEFAULT_BOXSIZE_STRING,
		'expnum': "",
		'tab_instrument': "on",
		'instrument': "%",
		'exposure': "",
		'filter': "",
		'photometric': "%",
		'creation_date': "",
		'release_date': "",
		'runid': "",
		'obstype': "OBJECT",
		'category': "%"
		}


# Code to parse HTML text and count up instrument uses

# the following RE object searches for instances of table entries referring to
# instruments and stores the actual instrument name
# text to search for in order to find/count instruments:
#      <input type="hidden" name="Instrument" value="*instrument-name*">
# e.g.,
#      <input type="hidden" name="Instrument" value="HRC">
findInstruments = re.compile(r"""<input type="hidden" name="Instrument" value="([^"]+?)">""")

def FindInstruments(inputText, nFound=None):
	foundStuff = findInstruments.findall(inputText)
	theDict = {}
	instList = []
	for item in foundStuff:
		if item not in instList:
			theDict[item] = 1
			instList.append(item)
		else:
			theDict[item] += 1

	msgText = "\n\t\t"
	for i in range(len(instList)):
		instName = instList[i]
		msgText += instName + " (%d)" % theDict[instName]
		if (i < (len(instList) - 1)):
			msgText += ", "
	
	return msgText

# Put all the functions in a list:
SEARCHES = [FindInstruments]


# Subclass the BasicArchive class to handle deviant input and posting 
# requirements of the CFHT archive
class CFHTArchive(basic_archive.BasicArchive):

	# We override QueryServer because the CFHT Archive prefers 
	# multipart/form-data queries, not urlencoded
	def QueryServer(self):
		# Opens connection to the archive server, retrieves and returns
		# whatever HTML the server sends us.
		# Note that here we are using our special multipart/form-data
		# method for posting to the archive.
		connection = multipart_form.MultipartPost(self.URL, self.params)
		# Loop to make sure we get *all* of the HTML (bug of sorts in MacPython 2.0--2.2):
		htmlReceived = ''
		newdata = connection.read()
		while newdata:
			htmlReceived += newdata
			newdata = connection.read()
		connection.close()
		return htmlReceived


# Factory function to create an instance of CFHTArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return CFHTArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="box")

