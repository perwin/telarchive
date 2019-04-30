# Utility functions for archive_search

import math
import urllib


# Subclass of Exception, for our own unique errrors[sic]:
class CoordinateError( Exception ):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)

class SearchError( Exception ):
	def __init__(self, value):
		self.value = value
	def __str__(self):
		return repr(self.value)



def ProcessCoords( coordinateString, decimalDegreesOK=False, convertDecimalDegrees=False ):
	"""Converts command-line coordinate-list (a string)
	to a list of strings of the form [ra, dec].
	coordinateString must have standard	astronomical formatting:
	"hh mm ss dd mm ss" (where "ss" can also be "ss.s" or "ss.ss")
	or "hh:mm:ss dd:mm:ss" or "XXhYYmZZs XXdYYmZZs"; optional "+" or "-"
	in front of the Declination part.
	
	Alternately, if decimaDegreesOK=True, then coordinateString can also 
	have the format "d+.d+ d+.d+" or "d+.d+, d+.d+"(decimal degrees for both RA and Dec).
	
	If *both* decimaDegreesOK and convertDecimalDegrees are True, then decimal-degree
	input is converted to sexagesimal output
	"""
	
	decimalDegreeFormat = False
	badInput = False
	
	if (coordinateString.find("h") >= 0):
		# sexagesimal XXhYYmSSs format
		pp = coordinateString.split()
		pp1 = pp[0].split("h")
		rah = pp1[0]
		pp2 = pp1[1].split("m")
		ram = pp2[0]
		pp3 = pp2[1].split("s")
		ras = pp3[0]
		raPieces = [rah, ram, ras]
		pp1 = pp[1].split("d")
		decd = pp1[0]
		pp2 = pp1[1].split("m")
		decm = pp2[0]
		pp3 = pp2[1].split("s")
		decs = pp3[0]
		decPieces = [decd, decm, decs]
		coordPieces = raPieces + decPieces
	elif (coordinateString.find(":") >= 0):
		# sexagesimal hh:m:ss format
		pieces = coordinateString.split()
		raPieces = pieces[0].split(":")
		decPieces = pieces[1].split(":")
		coordPieces = raPieces + decPieces
	else:
		if coordinateString.find(",") > 0:
			# decimal-degrees "dd.d,dd.d" format (comma-separated)
			coordPieces = coordinateString.split(",")
			# remove possible spaces
			coordPieces = [coordPieces[0].strip(), coordPieces[1].strip()]
		else:
			# sexagesimal "hh mm ss" format OR decimal-degrees "dd.d dd.d" format
			coordPieces = coordinateString.split()
	if len(coordPieces) != 6:
		# must be decimal degrees (or bad input)
		if decimalDegreesOK:
			if ((len(coordPieces) == 2) and (coordPieces[0].find(".") in [1, 2, 3])
				and (coordPieces[1].find(".") in [1, 2, 3])):
				decimalDegreeFormat = True
			else:
				badInput = True
		else:
			badInput = True
	if badInput:
		msg = "Coordinate string (\"%s\") is not in proper format! " % coordinateString
		msg += "(i.e., \"hh mm ss[.s] dd mm ss[.s]\", \"hh:mm:ss[.s] dd:mm:ss[.s]\","
		msg += " \"XXhYYmZZ.Zs +/-XXdYYmZZ.Zs\" or \"dd.d dd.d\")"
		if len(coordPieces) < 5:
			msg += "   Coordinates may be truncated or low-resolution"
		raise CoordinateError(msg)

	# check for valid numerical ranges:
	badCoords = False
	if decimalDegreeFormat:
		ra_d = float(coordPieces[0].rstrip("d"))
		dec_d = float(coordPieces[1].rstrip("d"))
		if ( (ra_d >= 0.0) and (ra_d < 360.0) and
			 (dec_d > -90.0) and (dec_d < 90.0) ):
			pass
		else:
			badCoords = True
	else:
		ra_h = int(coordPieces[0])
		ra_m = int(coordPieces[1])
		ra_s = float(coordPieces[2])
		dec_d = int(coordPieces[3])
		dec_m = int(coordPieces[4])
		dec_s = float(coordPieces[5])
		if ( ((ra_h >= 0) and (ra_h < 24)) and
			 ((ra_m >= 0) and (ra_m < 60)) and
			 ((ra_s >= 0.0) and (ra_s < 60.0)) and
			 ((dec_d > -90) and (dec_d < 90)) and
			 ((dec_m >= 0) and (dec_m < 60)) and
			 ((dec_s >= 0.0) and (dec_s < 60.0)) ):
			pass
		else:
			badCoords = True
	if badCoords:
		msg = "Coordinates (\"%s\") have non-astronomical values!" % coordinateString
		raise CoordinateError(msg)
	
	if decimalDegreeFormat:
		ra_deg_str = coordPieces[0].rstrip("d")
		dec_deg_str = coordPieces[1].rstrip("d")
		if convertDecimalDegrees:
			ra, dec = RADecFromDecimalDeg(ra_deg_str, dec_deg_str)
		else:
			ra = ra_deg_str
			dec = dec_deg_str
	else:
		ra = ' '.join(coordPieces[0:3])
		dec = ' '.join(coordPieces[3:])
	return [ra, dec]


def RADecToDecimalDeg(ra_str, dec_str):
	"""
	Takes two string representing RA and Dec in 'hh mm ss', 'dd mm ss' format
	and returns a 2-element tuple containg the equivalent values in decimal
	degrees (as numbers, not strings).
	Alternately, if input string is already in "dd.ddddd dd.ddddd" format,
	returns the 2-element tuple containing the numerical values.
	Currently assumes input RA and Dec are strings in hh mm ss and dd mm ss
	format [if in hh:mm:ss format, change split() to split(':')]
	"""

	dec_pieces = dec_str.split()
	
	if ra_str.find(".") in [1, 2, 3]:
		# RA string is of form x.xxxx or xx.xxxx or xxx.xxxx, so we'll
		# assume it's already decimal degrees
		ra_deg = float(ra_str)
	else:
		ra_pieces = ra_str.split()
		ra_s = float(ra_pieces[2])
		ra_m = float(ra_pieces[1]) + ra_s/60.0
		ra_h = float(ra_pieces[0]) + ra_m/60.0
		ra_deg = 15 * ra_h
		
	if dec_str.find(".") in [1, 2, 3]:
		# Dec string is of form x.xxxx or xx.xxxx or xxx.xxxx, so we'll
		# assume it's already decimal degrees
		dec_deg = float(dec_str)
	else:
		dec_s = float(dec_pieces[2])
		dec_m = float(dec_pieces[1]) + dec_s/60.0
		dec_d = float(dec_pieces[0])
		dec_deg = abs(dec_d) + dec_m/60.0
		# make sure that negative declination stays negative (coordinates like
		# "-00 00 14" are tricky, because float("-00") = 0.0]
		if (dec_str[0] == "-"):
			dec_sign = -1.0
		else:
			dec_sign = 1.0
		dec_deg = dec_sign * dec_deg

	if not ( (0.0 <= ra_deg < 360.0) and (-90.0 <= dec_deg <= 90.0) ):
		msg = "RA (%s --> %.5f) and/or Dec (%s --> %.5f) are outside bounds!" % \
				(ra_str, ra_deg, dec_str, dec_deg)
		raise CoordinateError(msg)
	return (ra_deg, dec_deg)


def RADecFromDecimalDeg(ra_str_deg, dec_str_deg):
	"""
	Takes two string representing RA and Dec in "dd.ddd", "dd.ddd" format
	and returns a 2-element tuple containg the equivalent values our standard
	sexagesimal format: "hh mm ss.ss", "dd mm ss.s" (as strings)
	"""

	ra_deg = float(ra_str_deg)
	dec_deg = float(dec_str_deg)
	if not ( (0.0 <= ra_deg < 360.0) and (-90.0 <= dec_deg <= 90.0) ):
		msg = "RA (\"%sd\") and/or Dec (\"%sd\") are outside bounds!" % \
				(ra_str_deg, dec_str_deg)
		raise CoordinateError(msg)

	ra_h_decimal = ra_deg / 15.0
	ra_m_decimal = 60*(ra_h_decimal - math.floor(ra_h_decimal))
	ra_s_decimal = 60*(ra_m_decimal - math.floor(ra_m_decimal))
	# check to make sure that output doesn't look funny (e.g., 59.996 rounding to "60.00")
	if ("%05.2f" % ra_s_decimal) == "60.00":
		ra_m_decimal += 1
		ra_s_decimal = 0.0
	if math.floor(ra_m_decimal) == 60.0:
		ra_h_decimal += 1
		ra_m_decimal = 0.0
	if math.floor(ra_h_decimal) == 24.0:
		ra_h_decimal = 0.0
	ra_hms_str = "%02d %02d %05.2f" % (math.floor(ra_h_decimal), math.floor(ra_m_decimal),
									ra_s_decimal)

	dec_d_decimal = dec_deg
	if (dec_d_decimal < 0):
		negVals = True
	else:
		negVals = False
	# if input value was "-0.0", then dec_d_decimal = -0.0, which is *not* < 0,
	# but will still mess up the final output. So we always take the absolute value,
	# to force -0.0 ==> 0.0
	dec_d_abs = abs(dec_d_decimal)
	dec_m_decimal = 60*(dec_d_abs - math.floor(dec_d_abs))
	dec_s_decimal = 60*(dec_m_decimal - math.floor(dec_m_decimal))
	if ("%05.2f" % dec_s_decimal) == "60.00":
		dec_m_decimal += 1
		dec_s_decimal = 0.0
	if math.floor(dec_m_decimal) == 60.0:
		dec_d_abs += 1
		dec_m_decimal = 0.0
	if math.floor(dec_d_abs) >= 90.0:
		dec_d_abs = 90.0
	dec_dms_str = "%02d %02d %04.1f" % (math.floor(dec_d_abs), math.floor(dec_m_decimal),
									dec_s_decimal)
	if negVals:
		dec_dms_str = "-" + dec_dms_str
	
	return (ra_hms_str, dec_dms_str)


def ConstructCountString( inputList ):
	"""Given a list of observation-type names and the numbers for each, this
	function returns a string containing the minimal, properly punctuated list
	
	inputList = list of lists
	
	Example:
		[ ["image", "images", 1], ["spectrum", "spectra", 4] ]
		==> "1 image, 4 spectra"
	"""
	nEntries = len(inputList)
	nSoFar = 0
	outputString = ""
	for i in range(nEntries):
		currentSubList = inputList[i]
		singleName = currentSubList[0]
		pluralName = currentSubList[1]
		number = currentSubList[2]
		txt = ""
		if number > 0:
			if (nSoFar > 0):
				txt = ", "
			if number == 1:
				txt += "1 %s" % singleName
			else:
				txt += "%d %s" % (number, pluralName)
			nSoFar += 1
		outputString += txt
	
	return outputString
	


#sort_column=Start+Date&sort_order=descending&formName=adsform&SelectList=Observation.observationURI+AS+%22Preview%22%2C+Observation.collection+AS+%22Collection%22%2C+Observation.sequenceNumber+AS+%22Sequence+Number%22%2C+Plane.productID+AS+%22Product+ID%22%2C+COORD1(CENTROID(Plane.position_bounds))+AS+%22RA+(J2000.0)%22%2C+COORD2(CENTROID(Plane.position_bounds))+AS+%22Dec.+(J2000.0)%22%2C+Observation.target_name+AS+%22Target+Name%22%2C+Plane.time_bounds_cval1+AS+%22Start+Date%22%2C+Plane.time_exposure+AS+%22Int.+Time%22%2C+Observation.instrument_name+AS+%22Instrument%22%2C+Plane.energy_bandpassName+AS+%22Filter%22%2C+Plane.calibrationLevel+AS+%22Cal.+Lev.%22%2C+Observation.type+AS+%22Obs.+Type%22%2C+Observation.proposal_id+AS+%22Proposal+ID%22%2C+Observation.proposal_pi+AS+%22P.I.+Name%22%2C+Plane.dataRelease+AS+%22Data+Release%22%2C+Observation.observationID+AS+%22Obs.+ID%22%2C+Plane.energy_bounds_cval1+AS+%22Min.+Wavelength%22%2C+Plane.energy_bounds_cval2+AS+%22Max.+Wavelength%22%2C+AREA(Plane.position_bounds)+AS+%22Field+of+View%22%2C+Plane.position_sampleSize+AS+%22Pixel+Scale%22%2C+Plane.energy_resolvingPower+AS+%22Resolving+Power%22%2C+Plane.dataProductType+AS+%22Data+Type%22%2C+Observation.target_moving+AS+%22Moving+Target%22%2C+Plane.provenance_name+AS+%22Provenance+Name%22%2C+Observation.intent+AS+%22Intent%22%2C+Observation.target_type+AS+%22Target+Type%22%2C+Observation.target_standard+AS+%22Target+Standard%22%2C+Observation.algorithm_name+AS+%22Algorithm+Name%22%2C+Observation.proposal_title+AS+%22Proposal+Title%22%2C+Observation.proposal_keywords+AS+%22Proposal+Keywords%22%2C+Plane.position_resolution+AS+%22IQ%22%2C+Observation.instrument_keywords+AS+%22Instrument+Keywords%22%2C+Plane.energy_transition_species+AS+%22Molecule%22%2C+Plane.energy_transition_transition+AS+%22Transition%22%2C+Plane.energy_emBand+AS+%22Band%22%2C+Plane.provenance_version+AS+%22Prov.+Version%22%2C+Plane.provenance_project+AS+%22Prov.+Project%22%2C+Plane.provenance_runID+AS+%22Prov.+Run+ID%22%2C+Plane.provenance_lastExecuted+AS+%22Prov.+Last+Executed%22%2C+Plane.energy_restwav+AS+%22Rest-frame+Energy%22%2C+Observation.requirements_flag+AS+%22Quality%22%2C+isDownloadable(Plane.planeURI)+AS+%22DOWNLOADABLE%22%2C+Plane.planeURI+AS+%22CAOM+Plane+URI%22&MaxRecords=30000&format=csv&Observation.observationID=&Form.name=Observation.observationID%40Text&Observation.proposal.pi=&Form.name=Observation.proposal.pi%40Text&Observation.proposal.id=&Form.name=Observation.proposal.id%40Text&Observation.proposal.title=&Form.name=Observation.proposal.title%40Text&Observation.proposal.keywords=&Form.name=Observation.proposal.keywords%40Text&Plane.dataRelease=&Form.name=Plane.dataRelease%40TimestampFormConstraint&Form.name=Plane.dataRelease%40PublicTimestampFormConstraint&Observation.intent=&Form.name=Observation.intent%40Text&Plane.position.bounds%40Shape1Resolver.value=ALL&Plane.position.bounds%40Shape1.value=210.05+54.3+0.5&targetList=&Form.name=targetList.targetList&Form.name=Plane.position.bounds%40Shape1&Plane.position.sampleSize=&Form.name=Plane.position.sampleSize%40Number&Form.name=Plane.position.DOWNLOADCUTOUT%40Boolean&Plane.time.bounds%40Date.value=&Plane.time.bounds_PRESET%40Date.value=&Form.name=Plane.time.bounds%40Date&Plane.time.exposure=&Form.name=Plane.time.exposure%40Number&Plane.time.bounds.width=&Form.name=Plane.time.bounds.width%40Number&Plane.energy.bounds%40Energy.value=&Form.name=Plane.energy.bounds%40Energy&Plane.energy.sampleSize=&Form.name=Plane.energy.sampleSize%40Number&Plane.energy.resolvingPower=&Form.name=Plane.energy.resolvingPower%40Number&Plane.energy.bounds.width=&Form.name=Plane.energy.bounds.width%40Number&Plane.energy.restwav=&Form.name=Plane.energy.restwav%40Number&Form.name=Plane.energy.DOWNLOADCUTOUT%40Boolean&Form.name=Plane.energy.emBand%40Enumerated&Form.name=Observation.collection%40Enumerated&Form.name=Observation.instrument.name%40Enumerated&Form.name=Plane.energy.bandpassName%40Enumerated&Form.name=Plane.calibrationLevel%40Enumerated&Form.name=Plane.dataProductType%40Enumerated&Form.name=Observation.type%40Enumerated&Plane.energy.emBand=&Observation.collection=CFHT&Observation.instrument.name=&Plane.energy.bandpassName=&Plane.calibrationLevel=&Plane.dataProductType=&Observation.type=

def DecodeURLToDict( url ):
	"""Given a URL with full encoding, return a dictionary mapping individual
	items to their values, with URL encoding undone.
	"""
	
	pp = url.split("?")
	if len(pp) == 2:
		site = pp[0]
		params = pp[1]
	else:
		site = None
		params = url
	
	paramsList = params.split("&")
	newDict = {}
	for item in paramsList:
		pp = item.split("=")
		newDict[pp[0]] = urllib.unquote(pp[1])
	return site, newDict

	
	

