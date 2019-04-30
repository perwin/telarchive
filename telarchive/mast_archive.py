# Archive module for the Mikulski Archive for Space Telescopes
# (formerly "Multimission Archive at STScI")
# 
# This module defines a new class (MASTArchive) derived from the 
# BasicArchive class.
# 
# Currently, we *exclude* HST from the list of "missions", since we have a
# separate module for HST queries.

import re
import basic_archive

DEFAULT_TARGET = "No Target"
DEFAULT_BOXSIZE_STRING = "3.0"
MAX_ROWS_RETURNED = "1"   # The "Summary" field at the end of the returned 
                          # web page tells us all we need to know, so we 
                          # don't need to request extra rows

# MAST Archive:
TARGET_LABEL = "target"
RA_LABEL = "ra"
DEC_LABEL = "dec"
ARCHIVE_NAME = "Mikulski Archive for Space Telescopes (MAST)"
ARCHIVE_SHORTNAME = "mast"
ARCHIVE_URL = "http://archive.stsci.edu/xcorr.php"
ARCHIVE_USER_URL = ARCHIVE_URL

# missions_list = ["ACS", "WFPC2", "WFPC2_ASN", "WFPC1", "FOS", "GHRS",
# 		 		"STIS", "NICMOS", "FOC", "FGS", "HSP",
# 				"FUSE", "IUE", "EUVE", "COPERNICUS", "UIT", "HUT",
# 				"WUPPE", "BEFS", "IMAPS", "TUES", "VLAFIRST", "GALEX"]
non_hst_missions_list = ["SWIFTUVOT", "FUSE", "IUE", "COPERNICUS", "UIT", "HUT", "WUPPE",
						 "BEFS", "IMAPS", "TUES", "VLAFIRST", "XMM-OM", "GALEX", "EUVE",
						 "KEPLER"]
# We need to construct a special string for the "missions" parameters, 
# since urllib.urlencode doesn't do in a form that the archive understands
# properly.  This will get added to the query URL via the special_params
# keyword when instantiating the archive
MISSIONS_LIST_PARAMS = "&missions%5B%5D=" + "&missions%5B%5D=".join(non_hst_missions_list)

# radius_list = ["radius_ACS", "radius_WFPC2", "radius_WFPC2_ASN", "radius_WFPC1",
# 				"radius_FOS", "radius_GHRS", "radius_STIS", "radius_NICMOS",
# 				"radius_FOC", "radius_FGS", "radius_HSP",
# 				"radius_FUSE", "radius_IUE", "radius_EUVE", "radius_COPERNICUS",
# 				"radius_UIT", "radius_HUT", "radius_WUPPE", "radius_BEFS", "radius_IMAPS",
# 				"radius_TUES",	"radius_VLAFIRST",	"radius_GALEX"]
non_hst_radius_list = ["radius_swiftuvot", "radius_FUSE", "radius_IUE", "radius_COPERNICUS",
						"radius_UIT", "radius_HUT", "radius_WUPPE", "radius_BEFS", "radius_IMAPS",
						"radius_TUES",	"radius_VLAFIRST",	"radius_xmm-om", "radius_GALEX",
						"radius_EUVE", "radius_kepler"]

DICT = { 'target': DEFAULT_TARGET, 'resolver': "SIMBAD",
		 'ra': "", 'dec': "", 'equinox': "J2000", 'radius': DEFAULT_BOXSIZE_STRING,
		 'outputformat': "HTML_Table", 'max_records': MAX_ROWS_RETURNED, 'action': "Search" }
radius_dict = {}
for name in non_hst_radius_list:
	radius_dict[name] = DEFAULT_BOXSIZE_STRING
DICT.update(radius_dict)



#   Some regular expressions we will need:
#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")
#   Check for data-returned reply (MAST-specific)
findPossibleData = re.compile(r"observations\s+found", re.VERBOSE)
#   Find "no data returned" equivalent for MAST
findNoDataReturned = re.compile(r"no \s rows \s found", re.VERBOSE)
#   Special search to extract names of missions and corresponding number 
#   of observations
findMissions = re.compile(r"""
	&nbsp;&nbsp;&nbsp;&nbsp;   # leading blank spaces
	([^:]+?):\s+                  # mission name -- [^<>]+? = match anything (except :) non-greedily
	([0-9]+?)\s+observations\s+found<br>                  # how many obs found
	                    #    
	""", re.VERBOSE)



# Subclass the BasicArchive class to handle deviant input requirements
# of the MAST archive
class MASTArchive(basic_archive.BasicArchive):

	# We need to override InsertBoxSize() because the MAST archive
	# allows specification of separate search radii for each sub-archive.
	# Also, the archive requires that the box size be in decimal
	# arc minutes, *not* the "hh mm ss" format which 
	# BasicArchive.InsertBoxSize converts the intput to.
	def InsertBoxSize(self, box_size):
		for name in non_hst_radius_list:
			self.params[name] = str(box_size)
	
	

def FindMissions(inputText, nFound=None):
	msgText = "\n\t\t"
	missionFoundList = []
	
	# Find start of Summary block, then cut out Summary text
	startIndex = inputText.find("<br><hr noshade><b>Summary</b><br><br>")
	summaryText = inputText[startIndex:]
	
	missionsFound = findMissions.findall(summaryText)
	nFound = len(missionsFound)
	
	for i in range(nFound):
		currentMission = missionsFound[i]
		# first element is name of mission, second is number of obs. found
		msgText += currentMission[0] + " (%s)" % currentMission[1]
		if (i < (nFound - 1)):
			msgText += "; "
	
	return msgText


# Put all the functions in a list:
SEARCHES = [FindMissions]


# Factory function to create an instance of MASTArchive
def MakeArchive():
	return MASTArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			special_params=MISSIONS_LIST_PARAMS)





# Here's the actual posted request, excluding HST, as captured by the LiveHTTPHeaders 
# plug-in for Firefox:
xx1 ="""
POST /xcorr.php target=&resolver=SIMBAD&ra=13h37m00.9s&dec=-29d51m57s&equinox=J2000&radius_acs=3.0&missions%5B%5D=FUSE&radius_fuse=1.0&radius_wfpc2=3.0&missions%5B%5D=IUE&radius_iue=1.0&radius_wfpc2_asn=3.0&missions%5B%5D=EUVE&radius_euve=1.0&radius_wfpc1=3.0&missions%5B%5D=COPERNICUS&radius_copernicus=1.0&radius_fos=1.0&missions%5B%5D=UIT&radius_uit=5.0&radius_ghrs=1.0&missions%5B%5D=HUT&radius_hut=1.0&radius_stis=3.0&missions%5B%5D=WUPPE&radius_wuppe=1.0&radius_nicmos=5.0&missions%5B%5D=BEFS&radius_befs=1.0&radius_foc=3.0&missions%5B%5D=IMAPS&radius_imaps=1.0&radius_fgs=3.0&missions%5B%5D=TUES&radius_tues=1.0&radius_hsp=3.0&missions%5B%5D=VLAFIRST&radius_vlafirst=1.0&missions%5B%5D=GALEX&radius_galex=1.0&outputformat=HTML_Table&max_records=1&action=Search
"""

# Here's the encoded params portion:
xx2="""
target=&resolver=SIMBAD&ra=13h37m00.9s&dec=-29d51m57s&equinox=J2000&radius_acs=3.0&missions%5B%5D=FUSE&radius_fuse=1.0&radius_wfpc2=3.0&missions%5B%5D=IUE&radius_iue=1.0&radius_wfpc2_asn=3.0&missions%5B%5D=EUVE&radius_euve=1.0&radius_wfpc1=3.0&missions%5B%5D=COPERNICUS&radius_copernicus=1.0&radius_fos=1.0&missions%5B%5D=UIT&radius_uit=5.0&radius_ghrs=1.0&missions%5B%5D=HUT&radius_hut=1.0&radius_stis=3.0&missions%5B%5D=WUPPE&radius_wuppe=1.0&radius_nicmos=5.0&missions%5B%5D=BEFS&radius_befs=1.0&radius_foc=3.0&missions%5B%5D=IMAPS&radius_imaps=1.0&radius_fgs=3.0&missions%5B%5D=TUES&radius_tues=1.0&radius_hsp=3.0&missions%5B%5D=VLAFIRST&radius_vlafirst=1.0&missions%5B%5D=GALEX&radius_galex=1.0&outputformat=HTML_Table&max_records=1&action=Search
"""
# example of a properly encoded submission URL:
sample="""
http://archive.stsci.edu/xcorr.php&target=&resolver=SIMBAD&ra=13h37m00.9s&dec=-29d51m57s&equinox=J2000&radius_acs=3.0&missions%5B%5D=FUSE&radius_fuse=1.0&radius_wfpc2=3.0&missions%5B%5D=IUE&radius_iue=1.0&radius_wfpc2_asn=3.0&missions%5B%5D=EUVE&radius_euve=1.0&radius_wfpc1=3.0&missions%5B%5D=COPERNICUS&radius_copernicus=1.0&radius_fos=1.0&missions%5B%5D=UIT&radius_uit=5.0&radius_ghrs=1.0&missions%5B%5D=HUT&radius_hut=1.0&radius_stis=3.0&missions%5B%5D=WUPPE&radius_wuppe=1.0&radius_nicmos=5.0&missions%5B%5D=BEFS&radius_befs=1.0&radius_foc=3.0&missions%5B%5D=IMAPS&radius_imaps=1.0&radius_fgs=3.0&missions%5B%5D=TUES&radius_tues=1.0&radius_hsp=3.0&missions%5B%5D=VLAFIRST&radius_vlafirst=1.0&missions%5B%5D=GALEX&radius_galex=1.0&outputformat=HTML_Table&max_records=1&action=Search
"""

# Here's the useful part of the HTML returned by a search:
xx3 ="""
<br><hr noshade><b>Summary</b><br><br>
&nbsp;&nbsp;Target = <b>m83</b><br>
&nbsp;&nbsp;&nbsp;&nbsp;ACS: 10 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;FUSE: 1 observations found<br>

&nbsp;&nbsp;&nbsp;&nbsp;WFPC2: 26 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;IUE: 19 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;WFPC2_ASN: 8 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;WFPC1: 11 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;FOS: 7 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;UIT: 7 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;GHRS: 7 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;HUT: 4 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;STIS: 11 observations found<br>

&nbsp;&nbsp;&nbsp;&nbsp;WUPPE: 2 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;NICMOS: 47 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;FOC: 12 observations found<br>
&nbsp;&nbsp;&nbsp;&nbsp;GALEX: 70 observations found<br>
<br><hr noshade>
"""
