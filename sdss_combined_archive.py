# Archive class specialization for SDSS Science Archive Server 
# 
# This module defines a new class (SloanCombinedArchive) derived from the 
# BasicArchive class, to allow queries for imaging data from both DR7 and
# DR12 of SDSS, along with spectroscopic data from DR12.

# It functions largely as a wrapper around three more specialized archive
# classes.

import re
import basic_archive
import sdss_coords_archive, sdss_dr12_archive
import sdss_dr14spec_archive
import utils

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "00 04 00"
MAX_RETURNED = "200"

DEFAULT_RA = "164.68184"
DEFAULT_DEC = "55.59788"
DEFAULT_RADIUS = "0.002"

TARGET_LABEL = None
RA_LABEL = "center_ra"
DEC_LABEL = "center_dec"
RADEC_LABEL = None
ARCHIVE_NAME = "Sloan Digital Sky Survey (DR7+DR12)"
ARCHIVE_SHORTNAME = "sdss-combined"

ARCHIVE_URL ="http://data.sdss3.org/advancedSearch/process"
ARCHIVE_USER_URL = "http://data.sdss3.org/advancedSearch"
DICT = {'center_ra': DEFAULT_RA, 'center_dec': DEFAULT_DEC, 
'boss_target_logic': 'any', 'classes': 'all', 'fibers': '', 'g_max': '',
'g_min': '', 'i_max': '', 'i_min': '', 'limit': MAX_RETURNED, 'mag_type': 'psf',
'max_dec': '', 'max_ra': '', 'min_dec': '', 'min_ra': '', 'mjds': '',
'plateids': '', 'r_max': '', 'r_min': '', 'radec_searchtype': 'radial',
'radius': DEFAULT_RADIUS, 'redshift_max': '', 'redshift_min': '',
'sdss_target_logic': 'any', 'surveys': ['sdss', 'boss'], 'u_max': '', 'u_min': '',
'z_max': '', 'z_min': '', 'zwarning_logic': 'all', 'zwarning_zero': 'yes'}




# Put all the functions in a list:
SEARCHES = []



# Subclass the BasicArchive class to handle deviant input and posting 
# requirements 
class SloanCombinedArchive( basic_archive.BasicArchive ):

	def __init__(self, long_name, short_name, url, params_dict,
				specialSearches, targetLabel, raLabel, decLabel,
				special_params=None, boxLabel='box', publicURL=None):
		
		self.nDataFound_dr7 = 0
		self.nDataFound_dr12 = 0
		self.nSpecFound = 0
		self.dr7_archive = sdss_coords_archive.MakeArchive()
		self.dr12_archive = sdss_dr12_archive.MakeArchive()
		self.spec_archive = sdss_dr14spec_archive.MakeArchive()

		self.longName = long_name
		self.shortName = short_name
		self.URL = url
		# we know that params_dict is a dictionary, so make a *copy* of it;
		# otherwise, we'll be modifying the original instance in the
		# individual-archive module, which makes things hard to debug...
		self.params = params_dict.copy()
		self.specialParams = special_params
		self.nSearches = len(specialSearches)
		self.theSearches = specialSearches
		self.targetLabel = targetLabel
		self.raLabel = raLabel
		self.decLabel = decLabel
		self.boxLabel = boxLabel
		self.spectroscopy_radius = self.spec_archive.params['radius']
		#self.textSearches = None
		if publicURL is None:
			self.publicURL = url
		else:
			self.publicURL = publicURL
		self.mode = "default"   # "default" = standard behavior for use 
		                        # with archive_search.py


	def SetMode(self, mode_name):
		self.mode = mode_name
		
		
	def InsertRadius(self, radius):
		# assume input radius is in arcmin
		radius_deg = float(radius)/60.0
		self.params['radius'] = str(radius_deg)


	def InsertSpectroscopyRadius(self, radius):
		# assume input spectroscopy search radius is in arcmin
		self.spectroscopy_radius = radius
		self.spec_archive.InsertSpectroscopyRadius(radius)


	def InsertTarget(self, target_name):
		# SDSS interface won't let us use target names, so we do nothing
		#    (in principle, we *could* do a coordinate lookup instead,
		#    but that's excessive)
		pass


	def InsertCoordinates(self, coords_list):
		# coords_list is a two-element list of strings; each string must
		# be in the usual "hh mm ss.s" format, though decimal values are optional.
		#    Overriden for SDSS searches, which require decimal degrees!
		self.dr7_archive.InsertCoordinates(coords_list)
		self.dr12_archive.InsertCoordinates(coords_list)
		self.spec_archive.InsertCoordinates(coords_list)


	def SetTimeout(self, timeout_secs):
		# Changes connection timeout for the archive (in seconds)
		self.timeout = timeout_secs
		self.dr7_archive.SetTimeout(timeout_secs)
		self.dr12_archive.SetTimeout(timeout_secs)
		self.spec_archive.SetTimeout(timeout_secs)


	def QueryServer(self):
		# This is a unique variation on the usual approach, since we're telling
		# our embedded ArchiveServer objects to do their own queries, and then
		# analyze their own HTML
		# Store nDataFound for each archive in corresponding object data members
		html_dr7 = self.dr7_archive.QueryServer()
		(msg_dr7, self.nDataFound_dr7) = self.dr7_archive.AnalyzeHTML(html_dr7)
		html_dr12 = self.dr12_archive.QueryServer()
		(msg_dr12, self.nDataFound_dr12) = self.dr12_archive.AnalyzeHTML(html_dr12)
		txt_spec = self.spec_archive.QueryServer()
		msg_spec, self.nSpecFound = self.spec_archive.AnalyzeHTML(txt_spec)
		
		return html_dr12
			

	# slight kludge: we don't need to search the HTML again; we just need to return
	# a message stating how many separate fields (DR7, DR12) and spectra were found
	def DoSpecialSearches(self, htmlText, nFound):
		if self.nDataFound_dr7 == 1:
			fieldString = "field"
		else:
			fieldString = "fields"
		msg = "\n\t\t%d DR7 %s; " % (self.nDataFound_dr7, fieldString)
		if self.nDataFound_dr12 == 1:
			fieldString = "field"
		else:
			fieldString = "fields"
		msg += "%d DR12 %s; " % (self.nDataFound_dr12, fieldString)
		if self.nSpecFound == 1:
			specString = "spectrum"
		else:
			specString = "spectra"
		msg += "%d %s (within %s arcmin of search center)" % (self.nSpecFound, 
							specString, self.spectroscopy_radius)
		return msg


	def AnalyzeHTML(self, htmlText):
		#    Function which searches a big blob of HTML text.  We look for various
		# text fragments: signs of valid or invalid reply, did the archive find data
		# or not, etc.  Uses the regular-expression objects defined above.
		#    htmlText = big blob of HTML text (entire reply from archive, in a string)
		
		# We assume that QueryServer() has already been called (plus, since all DR7
		# images are also in DR12, we don't bother checking the DR7 result for this
		# purpose)
		if (self.nDataFound_dr12 + self.nSpecFound) > 0:
			msg = "Data exists! "
		else:
			msg = "No data found."
		return (msg, self.nDataFound_dr12 + self.nSpecFound)

# End Class


# Factory function to create an instance of SDSSFootprintArchive
def MakeArchive():
	return SloanCombinedArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, ARCHIVE_URL,
			DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL)

