# Archive class specialization for HST archive at ESO
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# HST archive hosted at the European Southern Observatory.

import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "1000"

# ESO-HST Archive:
TARGET_LABEL = "targname"
RA_LABEL = "ra_targ_int"
DEC_LABEL = "dec_targ_int"
ARCHIVE_NAME = "HST Archive (at ESO)"
ARCHIVE_SHORTNAME = "hst"
ARCHIVE_URL = "http://archive.eso.org/wdb/wdb/hst/science/query"
ARCHIVE_USER_URL = ARCHIVE_URL
DICT = { 'extra_constr': "1:Exclusion_of_non_scientific_exposures_and_proposals",
		 'targname': DEFAULT_TARGET, 'deg_or_hour': "hours",
		 'ra_targ_int':	"",
		 'dec_targ_int': "", 'box': DEFAULT_BOXSIZE_STRING,
		 'resolver': "simbad", 'tab_targname': "checked",
		 'tab_computed_instrument': "checked", 'tab_dataset_name': "checked",
		 'tab_release_date_dmf': "checked",
		 'tab_actual_duration': "checked", 'tab_filter': "checked",
		 'tab_pi_lname': "checked", 'tab_pep_id': "checked",
		 'tab_grating': "checked", 'tab_assoc_type': "checked",
		 'tab_num_members': "checked", 'tab_camera': "checked",
		 'max_rows_returned': MAX_ROWS_RETURNED }


def SearchLines(searchString, inputTextLines):
	"""Search a block of text, line-by-line, and report how many hits on
	searchString were found.  Note that we do this line-by-line so that
	no more than one hit per line is achieved (e.g., a given line of text
	may have "WFPC2" more than once, but we should count that as only one
	hit).
	"""
	
	nHits = 0
	for line in inputTextLines:
		if re.search(searchString, line):
			nHits += 1
	return nHits


def FindHSTTypes(inputText, nFound):
	#    Bits of text to search for (these assume the HST archive sends us stuff
	# in *tabular* form, and that we requested "Instrument" and "Camera" info if
	# we are using ESO-HST archive; if we are using STScI, then we need to request
	# the "Instrument Config" column.
	#    The "Instrument" field tells us the general instrument (WFPC2, STIS,
	# etc.) -- except that for some reason FOC only shows up as a question mark.
	# Then, in the "Camera" field, we find more precise info (WF or PC for WF/PC1,
	# NIC1/2/3 for NICMOS, FUV-MAMA or CCD for STIS, BL or RD for FOS.  FOC
	# observations only show up here, and are described as FOC/48 or FOC/96.
	# (Preceeding info applies to HST-ESO archive; intrument information from
	# HST-STScI is in "Instrument Configuration" column; corresponding 
	# text-to-search-for is second in each entry below.)
	#    The final option is for the single-exposure case, when the returned
	# HTML is different.
	wfpc2String = r"<td>WFPC2 |<TD>WFPC2</TD>\n<TD>WFPC2</TD>|WFPC2</a></td>"
	wfString = r"<td>WFC |<TD>WFC"
	pcString = r"<td>PC |<TD>PC"
	nicmosString = r"NICMOS"
	acswfcString = r"ACS/WFC"
	acshrcString = r"ACS/HRC"
	stisString = r"<td>STIS/|<TD>STIS/"
	focString = r"<td>FOC/|<TD>FOC"
	fosString = r"<td>FOS/|<TD>FOS"
	ghrsString = r"GHRS"

	foundList = []
	nTypesFound = 0

	inputTextLines = inputText.split("\n")
	nWFPC2 = SearchLines(wfpc2String, inputTextLines)
	if (nWFPC2 > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nWFPC2) + " WFPC2"
		foundList.append(foundText)
	nWF = SearchLines(wfString, inputTextLines)
	if (nWF > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nWF) + " WF"
		foundList.append(foundText)
	nPC = SearchLines(pcString, inputTextLines)
	if (nPC > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nPC) + " PC"
		foundList.append(foundText)
	nNIC = SearchLines(nicmosString, inputTextLines)
	if (nNIC > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nNIC) + " NICMOS"
		foundList.append(foundText)
	nACS_WFC = SearchLines(acswfcString, inputTextLines)
	if (nACS_WFC > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nACS_WFC) + " ACS/WFC"
		foundList.append(foundText)
	nACS_HRC = SearchLines(acshrcString, inputTextLines)
	if (nACS_HRC > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nACS_HRC) + " ACS/HRC"
		foundList.append(foundText)
	nFOC = SearchLines(focString, inputTextLines)
	if (nFOC > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nFOC) + " FOC"
		foundList.append(foundText)
	nSTIS = SearchLines(stisString, inputTextLines)
	if (nSTIS > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nSTIS) + " STIS"
		foundList.append(foundText)
	nFOS = SearchLines(fosString, inputTextLines)
	if (nFOS > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nFOS) + " FOS"
		foundList.append(foundText)
	nGHRS = SearchLines(ghrsString, inputTextLines)
	if (nGHRS > 0):
		nTypesFound = nTypesFound + 1
		foundText = str(nGHRS) + " GHRS"
		foundList.append(foundText)

	if (nTypesFound > 0):
		messageText = "\n\t\t-- " + foundList[0]
		if (nTypesFound > 1):
			for i in range(1, nTypesFound):
				messageText = messageText + ", " + foundList[i]
	else:
		messageText = ""

	return messageText


# Put all the functions in a list:
SEARCHES = [FindHSTTypes]


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

