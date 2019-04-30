# Archive class specialization for Anglo-Australian Telescope archive
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# Anglo-Australian Telescope archive.
# 
# User interface is:
# http://site.aao.gov.au/arc-bin/wdb/aat_database/observation_log/make
# 
# Note that we *could* try collecting and counting instrument names, but
# this will be very hard, since the archive returns mostly long rows of
# plain text, rather than HTML tables, making it harder to isolate the
# instrument column.  (And the archive appears to ignore the checkboxes
# in the actual HTML form: it just returns *everything* for each observation).

import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "5000"

# Anglo-Australian Telescope archive:
TARGET_LABEL = "object"
RA_LABEL = "raj2000_int"
DEC_LABEL = "decj2000_int"
ARCHIVE_NAME = "AAT Archive"
ARCHIVE_SHORTNAME = "aat"
# alternate URLs, one at AAO in Australia, the other at Cambridge, UK
ARCHIVE_URL = "http://site.aao.gov.au/arc-bin/wdb/aat_database/user/query"
#ARCHIVE_URL = "http://apm5.ast.cam.ac.uk/arc-bin/wdb/aat_database/user/query"
ARCHIVE_USER_URL = "http://site.aao.gov.au/AATdatabase/aat/index.html"
#ARCHIVE_USER_URL = "http://apm5.ast.cam.ac.uk/arc-bin/wdb/aat_database/observation_log/make"


DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'box': DEFAULT_BOXSIZE_STRING, 'obsmode': "", 'tab_obsmode': "checked",
		'obstype': "==run", 'tab_instrument': "checked",
		'simbad': "simbad",	'max_rows_returned': MAX_ROWS_RETURNED}


def FindAATTypes(inputText, nFound=None):
	# Bits of text to search for:
	imageString = r"<td nowrap>IMAG |IMAG</td>"
	spectroscopyString = r"<td nowrap>SPEC "
	polarimetryString = r"<td nowrap>POLA "

	messageText = ""
	nPhot = len(re.findall(imageString, inputText))
	if (nPhot == 1):
		imName = " image"
	else:
		imName = " images"
	nSpec = len(re.findall(spectroscopyString, inputText))
	if (nSpec == 1):
		spName = " spectrum"
	else:
		spName = " spectra"
	nPolar = len(re.findall(polarimetryString, inputText))
	polarName = " polarimetry"

	messageText = "\n\t\t-- " + str(nPhot) + imName + ", " + str(nSpec) + \
				  spName + ", " + str(nPolar) + polarName

	return messageText


# Put all the functions	in a list:
SEARCHES = [FindAATTypes]


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

