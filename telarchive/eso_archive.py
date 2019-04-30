# Archive class specialization for ESO archive
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# European Southern Observatory archive.


import collections
import basic_archive, utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# European Southern Observatory Archive:
TARGET_LABEL = "target"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "ESO Archive"
ARCHIVE_SHORTNAME = "eso"
ARCHIVE_URL ="http://archive.eso.org//wdb/wdb/eso/eso_archive_main/query"
ARCHIVE_USER_URL = ARCHIVE_URL
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'deg_or_hour': "hours",
		'box': DEFAULT_BOXSIZE_STRING, 'resolver': "simbad",
		'dp_cat': "SCIENCE", 'tab_dp_tech': "checked",
		'tab_telescope': "checked", 'tab_instrument': "checked",
		'max_rows_returned': MAX_ROWS_RETURNED }



def GetTableRows( htmlTxt ):
	"""Given input text from a query of the ESO archive, extract just the rows
	belonging to the table of observations (defined as the rows bounded by
	"<tbody>" and "</tbody>")
	"""
	htmlLines = htmlTxt.splitlines()
	i_tableStart = [i for i in range(len(htmlLines)) if htmlLines[i].find("<tbody>") > -1]
	i_tableStart = i_tableStart[0]
	i_tableEnd = [i for i in range(i_tableStart,len(htmlLines)) if htmlLines[i].find("</tbody>") > -1]
	i_tableEnd = i_tableEnd[0]
	
	# the line that begins with "<tbody>" is the first line of the table
	# the line that beings with "</tbody>" is *after* the last line of the table
#	tableRows = htmlLines[i_tableStart:i_tableEnd - 1]
	tableRows = htmlLines[i_tableStart:i_tableEnd]
	
	return tableRows
	

def ExtractEntries( tableRowString ):
	"""Returns a list of table-data entries (each bounded by "<tdXXX>" and "</td>",
	where XXX can be almost anything -- including nothing at all -- except ">")
	extracted from the input string.
	"""
	leftBoundary, rightBoundary = "<td", "/td>"
	len1 = len(leftBoundary)
	len2 = len(rightBoundary)
	
	index = 0
	indices_start = []
	while index < len(tableRowString):
		index = tableRowString.find(leftBoundary, index)
		if index == -1:
			break
		# shift over so we start just after the closing ">"
		index2 = tableRowString.find(">", index)
		indices_start.append(index2 + 1)
		index += len1
	# search for end of td
	index = 0
	indices_end = []
	while index < len(tableRowString):
		index = tableRowString.find(rightBoundary, index)
		if index == -1:
			break
		# avoid starting at "<"
		indices_end.append(index - 1)
		index += len2

	# extract table-data entries
	tdEntries = []
	for n in range(len(indices_start)):
		i1,i2 = indices_start[n], indices_end[n]
		tdEntries.append(tableRowString[i1:i2])

	return tdEntries

modeNamePlurals = {"image": "images", "spectrum": "spectra"}
modeNamePluralsList = list(modeNamePlurals.keys())

def MakeModeString( number, name ):
	nameFinal = name.lower()
	if number > 1 and nameFinal in modeNamePluralsList:
		nameFinal = modeNamePlurals[nameFinal]
	return "%d %s" % (number, nameFinal)

def FindESOModesAndInstruments( inputText, nFound=None ):

	tableRows = GetTableRows(inputText)

	instNames = []
	modeNames = []
	for i in range(len(tableRows)):
		tdEntries = ExtractEntries(tableRows[i])
		# currently, instrument name and mode are penultimate and last entries in each line
# 		if len(tdEntries) == 5:
# 			instrumentName, modeName = tdEntries[-2], tdEntries[-1]
# 			instNames.append(instrumentName)
# 			modeNames.append(modeName)
		# revised formatting as of early 2018
		if len(tdEntries) == 6:
			instrumentName, modeName = tdEntries[3], tdEntries[4]
			instNames.append(instrumentName)
			modeNames.append(modeName)
	modeCountList = list(collections.Counter(modeNames).items())
	instCountList = list(collections.Counter(instNames).items())

	nSets = len(modeCountList)
	msgText = "\n\t\t"
	if nSets > 1:
		for i in range(nSets - 1):
			msgText += MakeModeString(modeCountList[i][1], modeCountList[i][0]) + ", "
	msgText += MakeModeString(modeCountList[-1][1], modeCountList[-1][0])

	nSets = len(modeCountList)
	msgText += "\n\t\t"
	if nSets > 1:
		for i in range(nSets - 1):
			msgText += "%s (%d), " % (instCountList[i][0], instCountList[i][1])
	msgText += "%s (%d)" % (instCountList[-1][0], instCountList[-1][1])
	
	return msgText


# Put all the functions in a list:
SEARCHES = [FindESOModesAndInstruments]


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

