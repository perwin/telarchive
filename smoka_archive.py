# SMOKA Archive module
# 
# NOTE that their preferred format for *coordinates* is "hh:mm:ss" or
# "NNhNNmNNs" but *not* space-separated "hh mm ss".  With no delimeters,
# values are interpreted as decimal degrees.  (Despite what the help
# pages say, space-separated versions [e.g., "12h 34m 56s"] are not
# accepted!)

import re
import basic_archive

DEFAULT_TARGET = ""
DEFAULT_BOXSIZE_STRING = "4.0"
MAX_ROWS_RETURNED = "500"   # max value allowed on web page

# SMOKA Archive:
TARGET_LABEL = "object"
RA_LABEL = "longitudeC"
DEC_LABEL = "latitudeC"
ARCHIVE_NAME = "SMOKA (Subaru Mitaka Okayama Kiso Archive)"
ARCHIVE_SHORTNAME = "smoka"
ARCHIVE_URL = "http://smoka.nao.ac.jp/search"
ARCHIVE_USER_URL = "http://smoka.nao.ac.jp/search.jsp"

instruments_list = ["SUP", "FCS", "HDS", "OHS", "IRC", "CIA", "COM", "CAC", "MIR",
			"MCS", "K3D", "HIC", "FMS", "KCC", "KCD", "ISL", "KLS", "HID", "OAS", 
			"CSD", "MTA", "MTO", "HWP"]
mode_list = ["IMAG", "SPEC", "IPOL"]
# We need to construct special strings for "instruments", "multiselect_0",
# "obs_mode", and "multiselect_1"
# "spectrographs" parameters, since urllib.urlencode doesn't do in a form 
# that the archive understands properly.
# This will get added to the query URL via the special_params
# keyword when instantiating the archive
INSTRUMENT_LIST_PARAMS = "&instruments=" + "&instruments=".join(instruments_list)
MULTISELECT0_LIST_PARAMS = "&multiselect_0=" + "&multiselect_0=".join(instruments_list)
MODE_LIST_PARAMS = "&obs_mod=" + "&obs_mod=".join(mode_list)
MULTISELECT1_LIST_PARAMS = "&multiselect_1=" + "&multiselect_1=".join(mode_list)
FINAL_LIST_PARAMS = INSTRUMENT_LIST_PARAMS + MULTISELECT0_LIST_PARAMS + MODE_LIST_PARAMS + MULTISELECT1_LIST_PARAMS

# this version (based on Live HTTP Headers output) will retrieve data for all
# imagers and spectrographs
DICT = {TARGET_LABEL: '', RA_LABEL: '12h34m56.7s', DEC_LABEL: '-01d09m22.6s', 'action': 'Search',
		'radius': DEFAULT_BOXSIZE_STRING,
		'resolver': 'SIMBAD', 'coordsys': 'Equatorial', 'equinox': 'J2000', 'fieldofview': 'auto',
		'RadOrRec': 'radius', 'longitudeF': '', 'latitudeF': '', 
		'longitudeT': '', 'latitudeT': '', 'date_obs': '', 'exptime': '', 'observer': '', 
		'prop_id': '', 'frameid': '', 'exp_id': '', 'dataset': '', 'asciitable': 'Table', 
		'data_typ': 'OBJECT', 'multiselect_2': 'OBJECT', 'bandwidth_type': 'FILTER', 'band': '',
		'dispcol': 'FRAMEID', 'orderby': 'FRAMEID', 'diff': MAX_ROWS_RETURNED, 
		'output_equinox': 'J2000', 'from': '0'}

INSTRUMENT_DICT = {"SUP": "Subaru -- Suprime-Cam", "FCS": "Subaru -- FOCAS",
					"HDS": "Subaru -- HDS", "OHS": "Subaru -- OHS/CISCO", 
					"IRC": "Subaru -- IRCS", "CIA": "Subaru -- CIAO", 
					"COM": "Subaru -- COMICS", "CAC": "Subaru -- CAC", 
					"MIR": "Subaru -- MIRTOS", "MCS": "Subaru -- MOIRCS", 
					"K3D": "Subaru -- Kyoto-3DII", "HIC": "Subaru -- HiCIAO",
					"FMS": "Subaru -- FMOS",
					"KCC": "Kiso -- 1k CCD", "KCD": "Kiso -- 2k CCD",
					"ISL": "Okayama -- ISLE", "KLS": "Okayama -- KOOLS",
					"HID": "Okayama -- HIDES", "OAS": "Okayama -- OASIS", 
					"CSD": "Okayama -- SNG", 
					"MTA": "MITSuME -- Akeno", "MTO": "MITSuME -- OAO",
					"HWP": "Hiroshima -- HOWPol" }
# INSTRUMENT_DICT = {"SUP_im": "Subaru -- Suprime-Cam", "FCS_im": "Subaru -- FOCAS",
# 					"OHS_im": "Subaru -- OHS/CISCO", "IRC_im": "Subaru -- IRCS",
# 					"CIA_im": "Subaru -- CIAO", "COM_im": "Subaru -- COMICS",
# 					"CAC_im": "Subaru -- CAC", "MIR_im": "Subaru -- MIRTOS",
# 					"MCS_im": "Subaru -- MOIRCS", "K3D_im": "Subaru -- Kyoto-3DII",
# 					"KCC_im": "Kiso -- 1k CCD", "KCD_im": "Kiso -- 2k CCD",
# 					"OAS_im": "Okayama -- OASIS", "MTO_im": "MITSuME -- OAO",
# 					"MTA_im": "MITSuME -- Akeno",
# 					"FCS_sp": "Subaru -- FOCAS", "HDS_sp": "Subaru -- HDS",
# 					"OHS_sp": "Subaru -- OHS/CISCO", "IRC_sp": "Subaru -- IRCS",
# 					"CIA_sp": "Subaru -- CIAO", "COM_sp": "Subaru -- COMICS",
# 					"MCS_sp": "Subaru -- MOIRICS", "K3D_sp": "Subaru -- Kyoto-3DII",
# 					"CSD_sp": "Okayama -- SNG", "HID_sp": "Okayama -- HIDES" }


findInst = re.compile(r"<tr><td>(?P<inst>\w+)</td><td>(?P<count>\d+)")
# findImagingResult = re.compile(r"<tr><td>([^<>]+?)</td><td>Imaging</td><td>(\d+)</td></tr>")
# findSpecResult = re.compile(r"<tr><td>([^<>]+?)</td><td>Spectroscopy</td><td>(\d+)</td></tr>")

def FindSmokaInfo(inputText, nFound):
	
#	imagingString = r"<td>Imaging</td>"
#	spectroscopyString = r"<td>Spectroscopy</td>"
	summaryString = "results are summarized below"
	
	foundData = {}
	foundInst = []
	nImages = nSpec = 0

	lines = inputText.splitlines()
	nLines = len(lines)
	
	# Find the table with instrument info
	startIndex = endIndex = -1
	for i in range(nLines):
		if lines[i].find(summaryString) >= 0:
			# skip this line and the next two
			startIndex = i + 3
			break
	if (startIndex > 0):
		for i in range(startIndex, nLines):
			if lines[i].find(r"</table>") >= 0:
				endIndex = i
				break
	
	for i in range(startIndex,endIndex):
		m = findInst.search(lines[i])
		nFrames = int(m.group('count'))
		if nFrames > 0:
			instrument = m.group('inst')
			foundData[instrument] = nFrames
			foundInst.append(instrument)	

# 	lines = inputText.split()
# 	for line in lines:
# 		if line.find(imagingString) >= 0:
# 			res = findImagingResult.search(line)
# 			nFrames = int(res.groups()[1])
# 			if nFrames > 0:
# 				instrument = res.groups()[0]
# 				foundData[instrument + "_im"] = nFrames
# 				foundInst.append(instrument + "_im")
# 				nImages += nFrames
# 		elif line.find(spectroscopyString) >= 0:
# 			res = findSpecResult.search(line)
# 			nFrames = int(res.groups()[1])
# 			if nFrames > 0:
# 				instrument = res.groups()[0]
# 				foundData[instrument + "_sp"] = nFrames
# 				foundInst.append(instrument + "_sp")
# 				nSpec += nFrames
	
	
# 	if (nImages == 1):
# 		imName = " image"
# 	else:
# 		imName = " images"
# 	if (nSpec == 1):
# 		spName = " spectrum"
# 	else:
# 		spName = " spectra"
# 	messageText = "\n\t\t" + str(nImages) + imName + " and " + str(nSpec) + spName
# 	messageText += "\n\t\t"
	messageText = "\n\t\t"
	for j in range(len(foundInst)):
		key = foundInst[j]
		telInstName = INSTRUMENT_DICT[key]
		messageText += telInstName + " (%d)" % foundData[key]
		if (j < len(foundInst) - 1):
			messageText += ", "

	return messageText


# Put all the functions in a list:
#    No special searches for SMOKA (yet)
SEARCHES = [FindSmokaInfo]


# Subclass the BasicArchive class to handle deviant input requirements
# of the SMOKA archive
class SmokaArchive(basic_archive.BasicArchive):

	# Override the InsertBoxSize() method, which needs to be overridden 
	# because the SMOKA archive wants the search box size in decimal 
	# arc minutes, *not* the standard "hh mm ss" format we use otherwise
	def InsertBoxSize(self, box_size):
		self.params[self.boxLabel] = str(box_size)
		
		
	# Override InsertCoordinates() method, because SMOKA archive won't
	# handle "hh mm ss.s" format; it wants to see "XXhXXmXX.Xs"
	# [12 April 2009: modified so that there are no spaces between
	# elements of RA and Dec -- something changed in archive processing!]
	def InsertCoordinates(self, coords_list):
		rapp = coords_list[0].split()
		decpp = coords_list[1].split()
		self.params[self.raLabel] = "%sh%sm%ss" % (rapp[0], rapp[1], rapp[2])
		self.params[self.decLabel] = "%sd%sm%ss" % (decpp[0], decpp[1], decpp[2])



# Factory function to create an instance of SmokaArchive
# Note that for this archive, we have a different label for the search box
# size.
def MakeArchive():
	return SmokaArchive(ARCHIVE_NAME, ARCHIVE_SHORTNAME, 
			ARCHIVE_URL, DICT, SEARCHES, TARGET_LABEL, RA_LABEL, DEC_LABEL,
			boxLabel="radius", special_params=FINAL_LIST_PARAMS)



# example of a properly encoded submission URL (11 aug 2011):
#    in this case, radius = 4.0 arcmin, object name="ngc 4321", and we request *all* instruments
#    "Generator" output from LiveHTTPHeaders
# POST /search object=ngc+4321&resolver=SIMBAD&coordsys=Equatorial&equinox=J2000&fieldofview=auto&RadOrRec=radius&longitudeC=&latitudeC=&radius=4.0&longitudeF=&latitudeF=&longitudeT=&latitudeT=&date_obs=&exptime=&observer=&prop_id=&frameid=&exp_id=&dataset=&asciitable=Table&action=Search&instruments=SUP&instruments=FCS&instruments=HDS&instruments=OHS&instruments=IRC&instruments=CIA&instruments=COM&instruments=CAC&instruments=MIR&instruments=MCS&instruments=K3D&instruments=KCC&instruments=KCD&instruments=ISL&instruments=KLS&instruments=HID&instruments=OAS&instruments=CSD&instruments=MTA&instruments=MTO&instruments=HWP&multiselect_0=SUP&multiselect_0=FCS&multiselect_0=HDS&multiselect_0=OHS&multiselect_0=IRC&multiselect_0=CIA&multiselect_0=COM&multiselect_0=CAC&multiselect_0=MIR&multiselect_0=MCS&multiselect_0=K3D&multiselect_0=KCC&multiselect_0=KCD&multiselect_0=ISL&multiselect_0=KLS&multiselect_0=HID&multiselect_0=OAS&multiselect_0=CSD&multiselect_0=MTA&multiselect_0=MTO&multiselect_0=HWP&obs_mod=IMAG&obs_mod=SPEC&obs_mod=IPOL&multiselect_1=IMAG&multiselect_1=SPEC&multiselect_1=IPOL&data_typ=OBJECT&multiselect_2=OBJECT&bandwidth_type=FILTER&band=&dispcol=FRAMEID&orderby=FRAMEID&diff=500&output_equinox=J2000&from=0

# split by "&" ==>
# ['object=ngc+4321', 'resolver=SIMBAD', 'coordsys=Equatorial',
# 'equinox=J2000', 'fieldofview=auto', 'RadOrRec=radius', 'longitudeC=',
# 'latitudeC=', 'radius=4.0', 'longitudeF=', 'latitudeF=', 'longitudeT=',
# 'latitudeT=', 'date_obs=', 'exptime=', 'observer=', 'prop_id=',
# 'frameid=', 'exp_id=', 'dataset=', 'asciitable=Table', 'action=Search',
# 'instruments=SUP', 'instruments=FCS', 'instruments=HDS',
# 'instruments=OHS', 'instruments=IRC', 'instruments=CIA',
# 'instruments=COM', 'instruments=CAC', 'instruments=MIR',
# 'instruments=MCS', 'instruments=K3D', 'instruments=KCC',
# 'instruments=KCD', 'instruments=ISL', 'instruments=KLS',
# 'instruments=HID', 'instruments=OAS', 'instruments=CSD',
# 'instruments=MTA', 'instruments=MTO', 'instruments=HWP',
# 'multiselect_0=SUP', 'multiselect_0=FCS', 'multiselect_0=HDS',
# 'multiselect_0=OHS', 'multiselect_0=IRC', 'multiselect_0=CIA',
# 'multiselect_0=COM', 'multiselect_0=CAC', 'multiselect_0=MIR',
# 'multiselect_0=MCS', 'multiselect_0=K3D', 'multiselect_0=KCC',
# 'multiselect_0=KCD', 'multiselect_0=ISL', 'multiselect_0=KLS',
# 'multiselect_0=HID', 'multiselect_0=OAS', 'multiselect_0=CSD',
# 'multiselect_0=MTA', 'multiselect_0=MTO', 'multiselect_0=HWP',
# 'obs_mod=IMAG', 'obs_mod=SPEC', 'obs_mod=IPOL', 'multiselect_1=IMAG',
# 'multiselect_1=SPEC', 'multiselect_1=IPOL', 'data_typ=OBJECT',
# 'multiselect_2=OBJECT', 'bandwidth_type=FILTER', 'band=',
# 'dispcol=FRAMEID', 'orderby=FRAMEID', 'diff=500',
# 'output_equinox=J2000', 'from=0\n']


# No data found reply includes this text:
# "No matching frame were found."
#
# Bad name produces:
# "Error: Cannot resolve object name 'ngc bob' by SIMBAD."

