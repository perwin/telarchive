# Archive class and module for the NOAO Science Archive
# 
# This module defines a new class (NOAOArchive) derived from the 
# BasicArchive class.

import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "4.0"
MAX_ROWS_RETURNED = "1000"

# NOAO Science Archive:
TARGET_LABEL = "objectName"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "NOAO Science Archive"
ARCHIVE_SHORTNAME = "noao"
ARCHIVE_URL = "http://archive.noao.edu/nsa/search_output.php"
ARCHIVE_USER_URL = "http://archive.noao.edu/nsa/nsa_form.html"
DICT = {TARGET_LABEL: DEFAULT_TARGET, RA_LABEL: "", DEC_LABEL: "",
		'resolver': "simbad", 'width': DEFAULT_BOXSIZE_STRING,
		'obsDate': "", 'photoDepth': ""}

# Put all the functions in a list:
#    No special searches for NOAO (yet)
SEARCHES = []


# Subclass the BasicArchive class to handle deviant input requirements
# of the NOAO archive
class NOAOArchive(basic_archive.BasicArchive):

	# The only modification we need to do is to the InsertBoxSize()
	# method, which needs to be overridden because the NOAO archive
	# wants the search box size in decimal arc minutes, *not* the
	# standard "hh mm ss" format we use otherwise
	def InsertBoxSize(self, box_size):
		self.params[self.boxLabel] = str(box_size)


# Factory function to create an instance of NOAOArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return NOAOArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="width")



# example of a properly encoded submission URL:
sample="""
http://archive.noao.edu/nsa/search_output.php?Submit=Search&objectName=ngc+6822&resolver=simbad&ra=19%3A44%3A57.80&dec=-14%3A48%3A11.00&width=4.0&obsDate=&photoDepth=
"""
