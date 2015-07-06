#! /usr/bin/env python
#   A Python script to find and download SDSS image tarballs for a
# specific target (astronomical object or coordinates).
# 
# Requires Python 2.3 or higher (due to use of optparse and booleans)
# 
#    POSSIBLE IMPROVEMENTS:
#       [] What about cases where the SQL server tells us there's
#       more than one image available (because the requested coordinate
#       sits in an overlap region between two different runs -- e.g.,
#       NGC 1068 (open image in DS9, use WCS to get coordinate of overlap
#       region, try querying SQL server for those coordinates, ...)
#       
# HISTORY:
#   12 July 2007: Updated to use DR6 instead of DR5.
#    1 Feb 2006: Replaced footprint_archive with sdss_sql_archive, which
# talks to the SDSS SQL server, which does not have trouble finding DR4
# sources the way the footprint server has (recently).


# Import various standard modules:
import sys, urllib, re, optparse

# Import our libraries:
import utils
import getcoords
import sdss_sql_archive, sdss_das_archive, footprint_archive

VERSION_STRING = "0.8"

NO_COORDS = "NO COORDS"
DEFAULT_ROOTNAME = "sdss"
DEFAULT_COORDLIST = ['12 00 00', '-70 00 00']  # should be outside SDSS!
DEBUG_SAVE_FILE = "fetchsdss.html"

kServerError = -1   # covers -1 values returned by sdss_sql_archive.AnalyzeHTML()
kConnectionError = -2
kCoordinateLookupError = -3
kInputError = -4

findNonSDSSFilters = re.compile("[^ugriz]")


def FetchCoordinates( objectName, verboseFlag=True ):
	"""Wrapper function which calls getcoords.GetCoordinates() to fetch
	coordinates of objectName from SIMBAD.  Returns a two-element list
	of strings (first string = RA, second string = Declination)."""
	
	success, coordinates = getcoords.GetCoordinates(objectName, verbose=verboseFlag)
	if ( success >= 1 ):
		if verboseFlag:
			print "Found object coordinates: RA = %s, Dec = %s" % (coordinates[1],
															   coordinates[2])
		return coordinates[1:]
	else:
		return None



def QueryArchive( archive, debug=False ):
	"""Handles submission of request and evaluation of results for a single archive.
	Requires a BasicArchive object [see basic_archive.py] or derived object.
	Returns a tuple of (messageString, nDataFound); for SDSS queries, nDataFound
	is 1 if data exist, 0 if not, and -1 if there was an I/O error.
	If debug = 1, then *all* returned HTML is saved to a file."""

	# Query archive and save resulting HTML in a list of lines:
	try:
		htmlReceived = archive.QueryServer()
		# Search HTML text:
		(messageString, nDataFound) = archive.AnalyzeHTML(htmlReceived)
		if ( debug ):
			saveFileName = archive.shortName + "_" + DEBUG_SAVE_FILE
			saveFile = open(saveFileName, 'w')
			saveFile.write(htmlReceived)
			saveFile.close()
	except IOError, e:
		messageString = "I/O Error -- " + str(e.args[0]) + ": " + \
						str(e.args[1]) + "\n"
		if ( str(e.args[1]) == "(7, 'No address associated with nodename')" ):
			messageString += 20*" " + "(DNS server is down,"
			messageString += " or we're not connected to the Internet?)"
		else:
			messageString += " (try again later?)"
		htmlReceived = ""
		nDataFound = kConnectionError

	return (messageString, nDataFound)



def VetFilterString( theString ):
	"""Simple function to make sure that only proper SDSS filters are listed
	in the user-supplied filter string."""
	
	# In the future, we might have some more sophisticated processing; for now,
	# we just check to see that the string contains only characters from the set
	# [ugriz], by looking for any characters *not* in that set.
	if findNonSDSSFilters.search(theString):
		return 0
	else:
		return 1



def CheckSDSSString( theString ):
	"""Simple function to vet strings containing SDSS field specifications:
	"run rerun camcol field" or "run,rerun,camcol,field". Also, camcol must
	be between 1 and 6."""
	# First, check to make sure there are 4 components, separated by spaces
	# *or* by commas
	pps = theString.split()
	ppc = theString.split(",")
	if len(pps) == 4:
		pp = pps
	elif len(ppc) == 4:
		pp = ppc
	else:
		return False
	# Now check to make sure all values are integers >= 0
	try:
		for p in pp:
			testv = int(p)
			if testv < 0:
				return False
	except ValueError:
		return False
	camcol = int(pp[2])
	if (camcol > 6) or (camcol < 1):
		return False
	return True
	


def GetAndSaveJPEG( coordinateList, jpegFilename, pixelSize="350" ):
	"""Simplistic function to retrieve a color JPEG from SDSS.  Currently,
	we default to 350x350 images, and no attempt is made to handle the
	outcome of sending the SDSS server bad coordinates!
	Thanks to Michael Pohlen for working out the URL string for this."""
	
	ra_str = coordinateList[0]
	dec_str = coordinateList[1]
	(ra_decdeg, dec_decdeg) = utils.RADecToDecimalDeg(ra_str, dec_str)
	width = int(pixelSize)
	height = int(pixelSize)
	
	imageURL = "http://casjobs.sdss.org/ImgCutout/getjpeg.aspx?"
	imageURL += "ra=%010.6f&dec=%09.6f" % (ra_decdeg, dec_decdeg)
	imageURL += "&scale=0.792254&width=%d&height=%d&opt=G" % (width, height)

	urllib.urlretrieve(imageURL, jpegFilename)
		
		
#    Simple function to print basic info (invoke with archive_search -h):
# def	PrintHelp():
# 	"PrintHelp(): basic function to print usage and possible command-line arguments"
# 	print "\nUsage: fetchsdss <filters> \"target_name\""
# 	print "            --coords=\"hh mm ss dd mm ss\" : search on coordinates"
# 	print "            -f <output_filename>"
# 	print "            --filename=<output_filename> : base name for saved tarball"
# 	print "                        (default = \"sdss\")"
# 	print
# 	print "<filters> = requested SDSS-filter images, in order of increasing"
# 	print "wavelength (e.g., ugr)"
# 	print



def main(argv):
	"""Wrapper function which handles command-line parameters and dispatch for
	searching SDSS archive and retrieving data.
	
	Returns -2 for problems with input, -1 for problems with getting coordinates
	from SIMBAD, 0 for successful search with no data found, and 1 for successful
	search with data found.
	"""

	# Set up target, etc, by parsing command-line:
	coordsList = DEFAULT_COORDLIST
	dataFound = 0
	doSQLQuery = True
	dataStringSupplied = False
	# this is currently predefined as True because we don't yet have
	# anything in place to check to see if data is retrieved or not
	dataRetrieved = True
	
	usageString =  "%prog \"target_name\" [filter-list] [options]\n"
	usageString += "       %prog --coords=\"hh mm ss dd mm ss\" [filter-list] [options]\n"
	usageString += "       %prog --ref=\"run rerun camcol field\" [filter-list] [options]"
	usageString += "\n\nfilter-list contains the desired SDSS filters;\nit must be \"ugriz\" (no quotation marks) or a subset thereof."
	usageString += "\n(default is \"ugriz\")"
	usageString += "\n\nExamples: %prog \"NGC 936\""
	usageString += "\n          %prog \"NGC 936\" ugz --output=n936ugz"
	usageString += "\n          %prog ugriz --ref=\"3177 40 1 62\""
	usageString += "\n\nRequested data is stored in an file named \"sdss.tar.gz\" or \"sdss.jpeg\";\n"
	usageString += "use -o/--output to specify a different root name instead of \"sdss\"."
	parser = optparse.OptionParser(usage=usageString, version="%prog " + VERSION_STRING)

	hstring = "RA and Dec as string (\"hh mm ss dd mm ss\" or \"hh:mm:ss dd:mm:ss\""
	hstring += " or decimal degrees [\"ra.dddd dec.dddd\"])"
	parser.add_option("-o", "--output", dest="filename", default=DEFAULT_ROOTNAME,
						help="root name for saved archive file (\".tar.gz\" or \".jpeg\" will be appended)")
	parser.add_option("--coords", dest="coordinates", default=NO_COORDS,
						help=hstring)
	helpmsg = "specify a specific SDSS field directly as \"run rerun camcol field\""
	helpmsg += " (e.g., --ref=\"3177 40 1 62\" or --ref=\"3177,40,1,62\")"
	parser.add_option("--ref", dest="sdssString", default=None, help=helpmsg)
	parser.add_option("--nodata", action="store_false", dest="getData", default=True,
						help="check availability only (don't retrieve data)")
	parser.add_option("--silent", action="store_false", dest="verbose", default=True,
						help="only print error messages")
	parser.add_option("--sql", action="store_false", dest="footprint", default=True,
						help="use SQL server instead of footprint server for coordinate search")
	parser.add_option("--jpeg", action="store_true", dest="getJPEG", default=False,
						help="retrieve color JPEG image (not FITS files)")
	parser.add_option("--jpegsize", dest="jpegsize", default="350",
						help="size of JPEG image in pixels")
	parser.add_option("--debug", action="store_true", dest="debugState", default=False,
						help="save all HTML files received")
	
	(options, args) = parser.parse_args(argv)
	

	# Check: If we're just fetching JPEG imgaes, we don't need FITS files
	if (options.getJPEG):
		options.getData = False
		if options.verbose:
			print "\nFetching color JPEG image; no FITS files will be retrieved..."

	
	# Check: Do we have an SDSS string, a target name, or a set of coordinates?
	if (options.sdssString is not None):
		# User specified a specific field in run-rerun-camcol-field format,
		# so we assume look for the filter string, if any:
		doSQLQuery = False
		if CheckSDSSString(options.sdssString):
			sdssDataString = options.sdssString
			dataStringSupplied = True
			dataFound = 1
		else:
			msg = "\nThe SDSS field-specification string \"%s\"" % options.sdssString
			msg += " didn't have the right format\n"
			msg += "(\"run rerun camcol field\" or \"run,rerun,camcol,field\", "
			msg += "with all values being positive integers and camcol < 7).\n"
			print msg
			return kInputError
		if len(args) < 2:
			filterString = "ugriz"
		elif len(args) == 2:
			filterString = args[1].lower()
		else:
			print "\nToo many arguments supplied (" + args + ").\n"
			print "Only an optional filter-list is required when using --ref option.\n"
			return kInputError
	elif (options.coordinates == NO_COORDS):
		# User is evidently giving us a target name
		if (len(args) < 2):
			print "\nYou must supply a target name (or else use the --coords options).\n"
			return kInputError
		targetName = args[1]
		if (len(args) == 2):
			filterString = "ugriz"
		else:
			filterString = args[2].lower()
		if options.verbose:
			print "\nDoing coordinate lookup for \"%s\"..." % targetName
		coordsList = FetchCoordinates(targetName, options.verbose)
		if (coordsList == getcoords.NO_COORDS_FOUND) or (coordsList is None):
			msg = "*** Unable to get coordinates for \"%s\". *** \n" % targetName
			msg += "Cannot search SDSS archive -- terminating search.\n"
			print msg
			return kCoordinateLookupError
		p1 = coordsList[0].split()
		p2 = coordsList[1].split()
		if ( len(p1) < 3 ) or ( len(p2) < 3 ):
			print "*** Warning: coordinates appear to be truncated or low-resolution! ***"
			print "Try entering full coordinates (including seconds) by hand with --coords option.\n"
			return kCoordinateLookupError
	else:
		try:
			coordsList = utils.ProcessCoords(options.coordinates, decimalDegreeOK=True)
		except utils.CoordinateError, e:
			newmsg = "*** Problem with coordinate string \"%s\"\n" % str(e) + "\n"
			print newmsg
			return kInputError
		if (len(args) < 2):
			filterString = "ugriz"
		else:
			filterString = args[2].lower()
	
		# Check filter string to make sure it's OK
		if options.getData:
			if (not VetFilterString(filterString)):
				print "\nList of filters (\"%s\") must be \"ugriz\" or subset thereof.\n" % filterString
				return kInputError


	# If necessary, do SQL query to see if coordinates are within SDSS
	if doSQLQuery:
		if (not options.getData) and options.verbose:
			print "\nChecking availability only (no FITS files will be retrieved)..."
		# Create an instance of sdss_sql_archive and prep it for queries
		if options.footprint is True:
			searchServer = footprint_archive.MakeArchive()
			if options.verbose:
				print "\nQuerying SDSS DR6 footprint server..."
		else:
			searchServer = sdss_sql_archive.MakeArchive()
			if options.verbose:
				print "\nQuerying SDSS DR6 SQL server..."
		searchServer.SetMode("fetchsdss")
		searchServer.InsertCoordinates(coordsList)
		(responseString, dataFound) = QueryArchive(searchServer)
		# responseString should come back with this format:
		#    "Data: <run> <rerun> <camcol> <field> (run, rerun, camcol, field)"
		# where <run> is the integer specifying the run, etc.
		if options.verbose:
			print "   server response = %s" % responseString
	
	
	
	# Data exists, and we are going to get it, so request tarball from archive
	if ( (dataFound > 0) and options.getData ):
		if (not dataStringSupplied):
			# Extract useful info from response string and package it for sdss_das_archive
			#    first, separate out the run/rerun/etc. info, which is on 
			#    the second line, after the equals sign
			xx = responseString.split("\n")[1].split("=")[1].strip(")")
			pp = xx.split()
			sdssDataString = "%s %s %s %s" % (pp[0], pp[1], pp[2], pp[3])
			dataStringSupplied = True
		# construct DAS-server object and prep it for use
		dasServer = sdss_das_archive.MakeArchive()
		dasServer.InsertCoordinates([sdssDataString, filterString])
		#print dasServer.params
	
		# query DAS-server
		if options.verbose:
			print "\nContacting SDSS DR6 Data Archive Server..."
		(outputString, dataFound_DAS) = QueryArchive(dasServer, options.debugState)
	
		if dataFound_DAS > 0:
			outputURL = outputString
			savedTarball = options.filename + ".tar.gz"
			if options.verbose:
				print "\nRetrieving data from %s ..." % outputURL
			# get the data!
			urllib.urlretrieve(outputURL, savedTarball)
			#  xxx fix the following (currently, we make no check of retrieved data)
			if dataRetrieved and options.verbose:
				# rename tarball
				print "Data saved in file %s." % savedTarball
		else:
			print "\n*** Problems contacting Data Archive Server:\n%s" % outputString
				
	# Data exists, but we're just getting JPEG images
	elif ( (dataFound > 0) and options.getJPEG ):
		savedJPEG = options.filename + ".jpeg"
		GetAndSaveJPEG(coordsList, savedJPEG, options.jpegsize)
		
	elif (dataFound == 0) and options.verbose:
		print "Object or coordinates apparently not within SDSS DR6!"
	elif (dataFound < 0):
		print "Problems contacting SDSS SQL server."

	if options.verbose:
		print "Done!\n"
	return dataFound



if __name__ == '__main__':
	main(sys.argv)
