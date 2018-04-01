# Archive class and module for SIMBAD queries.
# 
# This module defines a new class (SimbadArchive) derived from the 
# BasicArchive class.
# 
# Right now, there's just Simbad-France, but we could also use this for
# the US mirror at CfA (http://simbad.harvard.edu/Simbad) -- however,
# as of 31 Dec 2006, the latter is not yet updated to Simbad 4.
# 
# 10 Dec 2006: Updated to work with output from SIMBAD4; uses
# "Query by identifier" approach 
# (see http://simbad.u-strasbg.fr/simbad/sim-help?Page=sim-url)


#from . import basic_archive
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 00 00"

# SIMBAD archive:
TARGET_LABEL = "Ident"
RA_LABEL = "ra_int"
DEC_LABEL = "dec_int"
ARCHIVE_NAME = "SIMBAD (Simbad 4, France)"
ARCHIVE_SHORTNAME = "simbad"
ARCHIVE_URL = simbadURL_france = "http://simbad.u-strasbg.fr/simbad/sim-id"
ARCHIVE_USER_URL = "http://simbad.u-strasbg.fr/simbad/"
DICT = {TARGET_LABEL: DEFAULT_TARGET, 'output.format': 'html' }


# Put all special search functions in a list:
SEARCHES = []



# New class for Simbad searches:
class SimbadArchive( basic_archive.BasicArchive ):
	# No point in overriding the base class initialization for now
	
	# The following methods are irrelevant for Simbad searches, so
	# we make them do-nothing
	def InsertBoxSize(self, box_size):
		pass
	def InsertCoordinates(self, coords_list):
		pass



# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return SimbadArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

