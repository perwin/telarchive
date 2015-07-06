# Archive class specialization for UKIRT archive
# 
# This module is primarily for generating and returning an instance of
# the BasicArchive class with data and methods appropriate for the
# United Kingtom Infrared Telescope archive.

import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_ROWS_RETURNED = "1000"

# UKIRT Archive:
TARGET_LABEL = "OBJECT"
#RA_LABEL = "ra_int"
#DEC_LABEL = "dec_int"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "UKIRT Archive"
ARCHIVE_SHORTNAME = "ukirt"
#ARCHIVE_URL = "http://archive.ast.cam.ac.uk/cgi-bin/wdbuk/ukirt_arch/common/query"
ARCHIVE_URL = "http://archive.ast.cam.ac.uk/cgi-bin/ukirt_query/ukirt_wrap.cgi"
#ARCHIVE_USER_URL = "http://archive.ast.cam.ac.uk/cgi-bin/wdbuk/ukirt_arch/common/form"
ARCHIVE_USER_URL = "http://archive.ast.cam.ac.uk/cgi-bin/ukirt_query/ukirt_wrap.cgi"
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'box': DEFAULT_BOXSIZE_STRING, 'method': "standard",
		'OBSTYPE': "OBJECT", 'max_rows_returned': MAX_ROWS_RETURNED,
		'mode': "html_summary"}


# Put all special search functions in a list:
SEARCHES = []


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return basic_archive.BasicArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

