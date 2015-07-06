# Archive class specialization for GSC2 (Guide Star Catalog 2.3) archive
# 
# This module defines a new class (GSC2Archive) derived from the BasicArchive
# class.


import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "2.0"   # radius in arc minutes
MAX_ROWS_RETURNED = "1000"

# Guide Star Catalog 2.3:
BOX_SIZE_LABEL = "SIZE"
TARGET_LABEL = None
RA_LABEL = None
DEC_LABEL = None
ARCHIVE_NAME = "GSC2 Archive"
ARCHIVE_SHORTNAME = "gsc2"
ARCHIVE_URL = "http://galex.stsci.edu/GSC2/GSC2DataReturn.aspx"
ARCHIVE_USER_URL = "http://galex.stsci.edu/GSC2/GSC2WebForm.aspx"
DICT = {'RAH': RAH_DEFAULT, 'RAM': RAM_DEFAULT, 'RAS': RAS_DEFAULT, 
		'DSN': "+", 'DD': DECD_DEFAULT, 'DM': DECM_DEFAULT, 'DS': DECS_DEFAULTS,
		'EQ': "2000", BOX_SIZE_LABEL: DEFAULT_BOXSIZE_STRING, 'SRCH': "Radius",
		'FORMAT': "Plain Text", 'CAT': "GSC23", 'HSTID': "", 'GSC1ID': ""}

# Put all the functions in a list:
#    No special searches for CFHT
SEARCHES = []

# New class for SDSS searches:
class GSC2Archive( basic_archive.BasicArchive ):
	# No point in overriding the base class initialization for now
	
	def InsertBoxSize(self, box_size):
		# We assume that "box size" is a float specifying the search *radius*
		# in arc minutes.
		self.params[self.boxLabel] = "%f" % box_size


	def InsertTarget(self, target_name):
		# SDSS interface won't let us use target names, so we do nothing
		#    (in principle, we *could* do a coordinate lookup instead,
		#    but that's excessive)
		pass


	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for GSC searches, which require separate entries for H, M, S,
		#    etc.
		ra_pieces = coords_list[0].split()
		ra_h = ra_pieces[0]
		ra_m = ra_pieces[1]
		ra_s = ra_pieces[2]
		dec_pieces = coords_list[1].split()
		# chop off leading + or -, if any; store correct sign
		if dec_pieces[0][0] == "-":
			dec_sign = "-"
			dec_d = dec_pieces[0][1:]
		elif dec_pieces[0][0] == "+":
			dec_sign = "+"
			dec_d = dec_pieces[0][1:]
		else:
			dec_sign = "+"
			dec_d = dec_pieces[0]
		dec_m = dec_pieces[1]
		dec_s = dec_pieces[2]
		
		self.params['RAH'] = ra_h
		self.params['RAM'] = ra_m
		self.params['RAS'] = ra_s
		self.params['DSN'] = dec_sign
		self.params['DD'] = dec_d
		self.params['DM'] = dec_m
		self.params['DS'] = dec_s


# End Class


# Factory function to create specialized instance of BasicArchive
def MakeArchive():
	return GSC2Archive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel=BOX_SIZE_LABEL)

