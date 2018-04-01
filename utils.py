# Utility functions for archive_search

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



def ProcessCoords( coordinateString, decimalDegreeOK=False ):
	"""Converts command-line coordinate-list (a string)
	to a list of strings of the form [ra, dec].
	coordinateString must have standard	astronomical formatting:
	"hh mm ss dd mm ss" (where "ss" can also be "ss.s" or "ss.ss")
	or "hh:mm:ss dd:mm:ss" or "XXhYYmZZs XXdYYmZZs"; optional "+" or "-"
	in front of the Declination part.
	Alternately, if decimaDegreeOK=True, then coordinateString can also 
	have the format "d+.d+ d+.d+" or "d+.d+, d+.d+"(decimal degrees for both RA and Dec).
	"""
	
	decimalDegreeFormat = False
	badInput = False
	
	if (coordinateString.find("h") >= 0):
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
		pieces = coordinateString.split()
		raPieces = pieces[0].split(":")
		decPieces = pieces[1].split(":")
		coordPieces = raPieces + decPieces
	else:
		if coordinateString.find(",") > 0:
			coordPieces = coordinateString.split(",")
			# remove possible spaces
			coordPieces = [coordPieces[0].strip(), coordPieces[1].strip()]
		else:
			coordPieces = coordinateString.split()
	if len(coordPieces) != 6:
		if decimalDegreeOK:
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
		msg += " or \"XXhYYmZZ.Zs +/-XXdYYmZZ.Zs\")"
		if len(coordPieces) < 5:
			msg += "   Coordinates may be truncated or low-resolution"
		raise CoordinateError(msg)

	# check for valid numerical ranges:
	badCoords = False
	if decimalDegreeFormat:
		ra_d = float(coordPieces[0])
		dec_d = float(coordPieces[1])
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
		ra = coordPieces[0]
		dec = coordPieces[1]
	else:
		ra = ' '.join(coordPieces[0:3])
		dec = ' '.join(coordPieces[3:])
	return [ra, dec]


def RADecToDecimalDeg(ra_str, dec_str):
	# Takes two string representing RA and Dec in 'hh mm ss', 'dd mm ss' format
	# and returns a 2-element tuple containg the equivalent values in decimal
	# degrees (as numbers, not strings).
	# Alternately, if input string is already in "dd.ddddd dd.ddddd" format,
	# returns the 2-element tuple containing the numerical values.
	# Currently assumes input RA and Dec are strings in hh mm ss and dd mm ss
	# format [if in hh:mm:ss format, change split() to split(':')]

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


