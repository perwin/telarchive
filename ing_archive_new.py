# Archive class specialization for ING archive
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# Isaac Newton Group (La Palma) archive.

# Sample submission URL:
#http://catserver.ing.iac.es/insobslog/index.php?ra=209.4750&dec=29.9611&fov=5&submit=SUBMIT
# 
# Feb 2007: Updated with new URL for the "old" archive form

import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "1000"

# Isaac Newton Group Archive:
TARGET_LABEL = "object"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "ING Archive (old interface)"
ARCHIVE_SHORTNAME = "ing"
#ARCHIVE_URL = "http://cass38.ast.cam.ac.uk/cgi-bin/wdb/ingarch/ingarch/query"
#ARCHIVE_USER_URL = "http://cass38.ast.cam.ac.uk/ingarch/ingarchold.html"
ARCHIVE_URL = "http://archive.ast.cam.ac.uk/cgi-bin/wdb/ingarch/ingarch/query"
ARCHIVE_USER_URL = "http://archive.ast.cam.ac.uk/ingarch/ingarchold.html"
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'tab_ra': "checked", 'tab_dec': "checked", 'box': DEFAULT_BOXSIZE_STRING,
		'tab_telescope': "checked", 'tab_instrument': "checked",
		'tab_photspec': "checked", 'scionly': "checked",
		'max_rows_returned': MAX_ROWS_RETURNED}
#    NOTA BENE: we need to include 'tab_ra' and 'tab_dec' = "checked" in
# order to check the RA and Dec of returned HTML, in case the archive failed
# its Simbad lookup (in which it searches using Vernal Equinox coordinates).


N_TELESCOPES = 3
# lists of ING telescopes, in simple human-readable form and in regex form 
# (not any different, really, but we need different versions for ESO)
INGTelescopes =   [ "JKT",  "INT",  "WHT"]
INGTelescopesRE = [r"JKT", r"INT", r"WHT"]

#   This is an example of  how to find a telescope named "BFT" and
#   whatever instrument was used with it:
# findBFT = re.compile(r"""
# 	</td><td>BFT\s*</td><td>   # telescope name
# 	([^<>]+?)</td>             # instrument name, stored in a group
# 	                           #    [^<>]+? = match anything (except <>) non-greedily
# 	""", re.VERBOSE)

#   However, for simplicity, we'll assemble a list of compiled regex
#   objects, including all the telescopes:
findTelInstList = []
for telnameRE in INGTelescopesRE:
	new_regex = r"</td><td>" + telnameRE + r"\s*</td><td>([^<>]+?)</td>"
	findTelInstList.append( re.compile(new_regex) )


def	FindINGImagesAndSpectra(inputText, nFound):
	# Bits of text to search for, telling us whether data is image or spectrum:
	photometryString = r"<td>P</td>"
	spectroscopyString = r"<td>S</td>"

	messageText = "\n\t\t"
	nPhot = len(re.findall(photometryString, inputText))
	nSpec = len(re.findall(spectroscopyString, inputText))
	nUnknown = nFound - (nPhot + nSpec)
	# Add up all the images and/or spectra:
	if (nPhot == 1):
		imName = " image, "
	else:
		imName = " images, "
	messageText += str(nPhot) + imName
	if (nSpec == 1):
		spName = " spectrum"
	else:
		spName = " spectra"
	messageText += str(nSpec) + spName
	if (nUnknown > 0):
		messageText += ", " + str(nUnknown) + " unclassified"

	return messageText


def FindTelescopesAndInstruments(inputText, nFound=None):
	msgText = "\n\t\t"
	instFoundList = []
	telFoundList = []
	
	# First, search through HTML text and accumulate finds
	for i in range(N_TELESCOPES):
		telName = INGTelescopes[i]
		# extract regex object for this telescope and do search
		telFinder = findTelInstList[i]
		instrumentsFound = telFinder.findall(inputText)
		if (len(instrumentsFound) > 0):
			# found observations by this telescopes
			telFoundList.append(telName)
			instFoundList.append(instrumentsFound)
		
	# now, go through finds and construct output message
	nTelescopesFound = len(telFoundList)
	for i in range( nTelescopesFound ):
		telName = telFoundList[i]
		instrumentsFound = instFoundList[i]
		msgText += telName + " -- "
		newDict = {}
		for inst_string in instrumentsFound:
			instName = inst_string.strip()
			if instName not in newDict.keys():
				# create new dictionary entry and set count = 1
				newDict[instName] = 1
			else:
				newDict[instName] += 1
		theKeys = newDict.keys()
		for j in range(len(newDict)):
			# assemble output string for this telescope
			instName = theKeys[j]
			if (instName == "&nbsp;"):
				# oops -- this observation has no entry for instrument
				printedInstName = "unknown"
			else:
				printedInstName = instName
			msgText += printedInstName + " (%d)" % newDict[instName]
			if (j < (len(newDict) - 1)):
				msgText += ", "
		if (i < (nTelescopesFound - 1)):
			msgText += ";  "
		
		
	return msgText
		

# Put all the functions	in a list:
SEARCHES = [FindINGImagesAndSpectra, FindTelescopesAndInstruments]


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

