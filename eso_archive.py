# Archive class specialization for ESO archive
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# European Southern Observatory archive.

# </td><td>MPI-2.2   </td><td>WFI       </td>
# </td><td>ESO-VLT-U1</td><td>FORS1     </td>
# </td><td>ESO-VLT-U4</td><td>FORS2     </td>
# </td><td>ESO-VLT-U1</td><td>ISAAC     </td>
# 
# Look for one of 3(4?) different telescope types ("MPI-2.2", "ESO-VLT-U#",
# "ESO-NTT"?, "ESO-3P6"?), and also capture the group following, which has the
# instrument name --> extract instrument name into instrument_text
# 
# Dictionary for each telescope:
#   instrument_name = rematch.group('inst').strip()
# 	if instrument_text in mpi_instruments.keys():
# 		mpi_instruments[instrument_text] +=	1
# 	else:
# 		# create new dictionary entry and set count = 1
# 		mpi_instruments[instrument_text] = 1
# 		
# Last updated: 14--15 June 2005 (minor chanages in parameter names on 
# search page)



import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# European Southern Observatory Archive:
TARGET_LABEL = "target"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "ESO Archive"
ARCHIVE_SHORTNAME = "eso"
#ARCHIVE_URL ="http://archive.eso.org/wdb/wdb/eso/observations/query"
ARCHIVE_URL ="http://archive.eso.org//wdb/wdb/eso/eso_archive_main/query"
ARCHIVE_USER_URL = ARCHIVE_URL
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'deg_or_hour': "hours",
		'box': DEFAULT_BOXSIZE_STRING, 'resolver': "simbad",
		'dp_cat': "SCIENCE", 'tab_dp_tech': "checked",
		'tab_telescope': "checked", 'tab_instrument': "checked",
		'max_rows_returned': MAX_ROWS_RETURNED }

N_TELESCOPES = 4
# lists of ESO telescopes, in simple human-readable form and in regex
# form (so we lump all four VLT telescopes -- ESO-VLT-U1, ESO-VLT-U2,
# ESO-VLT-U3, ESO-VLT-U4 -- together)
ESOTelescopes =   [ "MPI-2.2",  "ESO-NTT",  "ESO-3P6",  "ESO-VLT"]
ESOTelescopesRE = [r"MPI-2.2", r"ESO-NTT", r"ESO-3P6", r"ESO-VLT-U\d"]

# list of instruments, from ESO web search form, 7 Mar 2013:
# some of these may be followed by "/xxx" e.g., "EMMI/1.57" or "EMMI/2.6"
instrumentList = ["FORS1", "FORS2", "HAWKI", "ISAAC", "NACO", "VIMOS", "VISIR", "VIRCAM",
		"OMEGACAM", "EMMI", "SOFI", "SUSI", "EFOSC", "TIMMI2", "WFI", "CRIRES",
		"GIRAFFE", "SINFONI", "UVES", "XSHOOTER", "CES", "HARPS", "FEROS", "VINCI",
		"MIDI", "AMBER", "APEXHET", "APEXBOL"]

#   Some regular expressions we will need:
# Modes:
# We list image and spectrum first, so we can handle "image" vs "images" and
# "spectrum" vs "spectra" later on
#   Look for IMAGE:
findImage = re.compile(r"<td>IMAGE|IMAGE,PRE")
#   Look for SPECTRUM:
findSpectrum = re.compile(r"<td>SPECTRUM|SPECTRUM,NODDING")
#   Look for other modes
otherModeNames = ["echelle", "MOS", "MXU", "IFU", "polarimetry", "coronography", "interferometry"]
findOtherModesRE = {}
findOtherModesRE["echelle"] = re.compile(r"<td>ECHELLE")
findOtherModesRE["MOS"] = re.compile(r"<td>MOS")
findOtherModesRE["MXU"] = re.compile(r"<td>MXU")
findOtherModesRE["IFU"] = re.compile(r"<td>IFU|<td>IFU,NODDING")
findOtherModesRE["polarimetry"] = re.compile(r"<td>POLARIMETRY")
findOtherModesRE["coronography"] = re.compile(r"<td>CORONOGRAPHY")
findOtherModesRE["interferometry"] = re.compile(r"<td>INTERFEROMETRY")

#   This is an explicit example of how to find the MPI-2.2 telescope and 
#   whatever instrument was used with it:
# findMPI = re.compile(r"""
# 	</td><td>MPI-2.2\s*</td><td>   # telescope name
# 	([^<>]+?)</td>      # instrument name, stored in a group
# 	                    #    [^<>]+? = match anything (except <>) non-greedily
# 	""", re.VERBOSE)

#   However, for simplicity, we'll assemble a list of compiled regex
#   objects, including all the telescopes:
findTelInstList = []
for instnameRE in instrumentList:
	new_regex = r"</td><td>" + instnameRE + r"\s*</td><td>([^<>]+?)</td>"
	findTelInstList.append( re.compile(new_regex) )
# for telnameRE in ESOTelescopesRE:
# 	new_regex = r"</td><td>" + telnameRE + r"\s*</td><td>([^<>]+?)</td>"
# 	findTelInstList.append( re.compile(new_regex) )



def FindESOTypes(inputText, nFound=None):
	"""Search for, count, and return the totals for each type of observation/exposure
	(a.k.a. "mode") -- e.g., IMAGE, SPECTRUM, etc.
	"""
	messageText = ""
	nPhot = len(findImage.findall(inputText))
	if (nPhot == 1):
		imName = "image"
	else:
		imName = "images"
	nSpec = len(findSpectrum.findall(inputText))
	if (nSpec == 1):
		spName = "spectrum"
	else:
		spName = "spectra"
	nOther = {}
	for modeName in otherModeNames:
		nOther[modeName] = findOtherModesRE[modeName].findall(inputText)
		
	messageText = "\n\t\t%d %s, %d %s" %(nPhot, imName, nSpec, spName)
	for otherName in otherModeNames:
		messageText += ", %d %s" % (len(nOther[otherName]), otherName)

	return messageText



# the following RE object searches for instances of table entries referring to
# instruments and stores the actual instrument name
# text to search for in order to find/count instruments:
#      <input type="hidden" name="Instrument" value="instrument-name">
# e.g.,
#      <input type="hidden" name="Instrument" value="GMOS-N">

#</td><td>SINFONI    </td><td>

#findInstruments = re.compile(r"""<input type="hidden" name="Instrument" value="([^"]+?)">""")
findInstruments = re.compile(r"""</td><td>[^"]+?</td><td>([^"]+?)    </td><td>""")


# code copied from gemini_archive.py
def FindStuff(inputText, reObject):
	"""Simple function to record number of observations per type (e.g., 
	number of observations per instrument).
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

def FindInstruments(inputText, nFound=None):
	msgText = "\n\t\t"
	(instList, theDict) = FindStuff(inputText, findInstruments)
	for i in range(len(instList)):
		instName = instList[i]
		msgText += instName.strip() + " (%d)" % theDict[instName]
		if (i < (len(instList) - 1)):
			msgText += ", "
	
	return msgText



def FindInstrumentsOLD(inputText, nFound=None):
	msgText = "bob\n\t\t"
	instFoundList = []
	telFoundList = []
	
	# First, search through HTML text and accumulate finds
	for i in range(N_TELESCOPES):
		telName = ESOTelescopes[i]
		# extract regex object for this telescope and do search
		telFinder = findTelInstList[i]
		instrumentsFound = telFinder.findall(inputText)
		if (len(instrumentsFound) > 0):
			# found observations by this telescopes
			telFoundList.append(telName)
			instFoundList.append(instrumentsFound)
		
	# now, go through finds and construct output message
	nTelescopesFound = len(telFoundList)
	print(nTelescopesFound)
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
			msgText += instName + " (%d)" % newDict[instName]
			if (j < (len(newDict) - 1)):
				msgText += ", "
		if (i < (nTelescopesFound - 1)):
			msgText += ";  "
		
		
	return msgText + "zzz"
		

# Put all the functions in a list:
SEARCHES = [FindESOTypes, FindInstruments]
#SEARCHES = [FindESOTypes]


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

