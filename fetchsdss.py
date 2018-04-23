#! /usr/bin/env python
#   A Python script to find and download SDSS image tarballs for a
# specific target (astronomical object or coordinates).
# 
# Requires Python 2.5 or higher (due to use of optparse and booleans + preliminary
# # print function syntax)
# 
#       
# HISTORY:
#   May 2015: Fixes accomodating DR12 (mainly just spectral search, plus renaming)
#   Aug 2013: Minor changes to include DR10 search and retrieval
#   March 2013: Updated to include DR9 search and retrieval; package also includes
# fetchsdss_spectra.py script to find and retrieve spectra.
#   25 March--6 April 2009: Updated to use DR7 via sdss_coords_archive.py; major
# changes to image-retrieval code (now using functions from get_sdssfiles.py);
# sdss_sql_archive, sdss_das_archive, and footprint_archive modules no longer used.
#   12 July 2007: Updated to use DR6 instead of DR5.
#    1 Feb 2006: Replaced footprint_archive with sdss_sql_archive, which
# talks to the SDSS SQL server, which does not have trouble finding DR4
# sources the way the footprint server has (recently).

from __future__ import print_function
# Import various standard modules:
import os, sys, re, optparse
import logging

# Import our modules:
import utils, getcoords, get_sdssfiles
import sdss_coords_archive, sdss_dr12_archive

VERSION_STRING = "1.3"

NO_COORDS = "NO COORDS"
DEFAULT_ROOTNAME = "sdss"
DEFAULT_COORDLIST = ['12 00 00', '-70 00 00']  # should be outside SDSS!
DEBUG_SAVE_FILE = "fetchsdss.html"

kServerError = -1   # covers -1 values returned by sdss_sql_archive.AnalyzeHTML()
kConnectionError = -2
kCoordinateLookupError = -3
kInputError = -4

findNonSDSSFilters = re.compile("[^ugriz]")


logging.basicConfig(filename='log_for_fetchsdss.log',level=logging.DEBUG)


def FetchCoordinates( objectName, verboseFlag=True ):
	"""Wrapper function which calls getcoords.GetCoordinates() to fetch
	coordinates of objectName from SIMBAD.  Returns a two-element list
	of strings (first string = RA, second string = Declination)."""
	
	success, coordinates = getcoords.GetCoordinates(objectName, verbose=verboseFlag)
	if ( success >= 1 ):
		if verboseFlag:
			print("Found object coordinates: RA = %s, Dec = %s" % (coordinates[1],
															   coordinates[2]))
		return coordinates[1:]
	else:
		return None



def QueryArchive( archive, debug=False ):
	"""Handles submission of request and evaluation of results for a single archive.
	Requires a BasicArchive object [see basic_archive.py] or derived object.
	Returns a tuple of (messageString, nDataFound).
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
	except IOError as e:
#		messageString = "I/O Error -- " + str(e.args[0])
# 		messageString = "I/O Error -- " + str(e.args)
		messageString = "I/O Error"
		if len(e.args) > 1:
			messageString += ": " + str(e.args[1])
			if ( str(e.args[1]) == "(7, 'No address associated with nodename')" ):
				messageString += 20*" " + "(DNS server is down,"
				messageString += " or we're not connected to the Internet?)"
			else:
				messageString += " (try again later?)"
		htmlReceived = ""
		nDataFound = kConnectionError

	return (messageString, nDataFound)



def FilterStringOK( theString ):
	"""Simple function to make sure that only proper SDSS filters are listed
	in the user-supplied filter string."""
	
	# In the future, we might have some more sophisticated processing; for now,
	# we just check to see that the string contains only characters from the set
	# [ugriz], by looking for any characters *not* in that set.
	if findNonSDSSFilters.search(theString):
		return False
	else:
		return True


def JPEGSizeOK( sizeString ):
	"""Simple function to make sure that only allowed JPEG size specifications
	are used."""
	
	if sizeString not in ["z00", "z05", "z10", "z15", "z20", "z25", "z30"]:
		return False
	else:
		return True



def IsDR12FieldString( sdssDataString ):
	if len(sdssDataString.split()) == 3:
		return True
	else:
		return False
	

def CheckSDSSString( theString ):
	"""Simple function to vet strings containing SDSS field specifications:
	"run rerun camcol field" or "run,rerun,camcol,field" for DR7;
	"run camcol field" or "run,camcol,field" for DR12. Also, camcol must
	be between 1 and 6.
	
	Returns 1 for valid DR7 field specification, 2 for valid DR12 specification,
	or 0 for bad field specification.
	"""
	# First, check to make sure there are 4 components, separated by spaces
	# *or* by commas
	pps = theString.split()
	ppc = theString.split(",")
	if len(pps) in [3,4]:
		pp = pps
	elif len(ppc) in [3,4]:
		pp = ppc
	else:
		return 0
	# Now check to make sure all values are integers >= 0
	try:
		for p in pp:
			testv = int(p)
			if testv < 0:
				return 0
	except ValueError:
		return 0
	if len(pp) == 3:
		camcol = int(pp[1])
		fieldType = 2
	else:
		camcol = int(pp[2])
		fieldType = 1
	if (camcol > 6) or (camcol < 1):
		return 0
	return fieldType
	



def main(argv):
	"""Wrapper function which handles command-line parameters and dispatch for
	searching SDSS archive and retrieving data.
	
	Returns -2 for problems with input, -1 for problems with getting coordinates
	from SIMBAD, 0 for successful search with no data found, and 1 for successful
	search with data found.
	"""

	# Set up target, etc, by parsing command-line:
	coordsList = DEFAULT_COORDLIST
	nDR7DataFound = nDR12DataFound = 0
	doFetchCoords = False   # do we need to query SIMBAD for object coordinates?
	doCoordsQuery = True    # do we need find out if coordinates are inside SDSS?
	dataStringSupplied = False
	retrieveData = False    # final go-ahead to fetch data from servers
	# this is currently predefined as True because we don't yet have
	# anything in place to check to see if data is retrieved or not
	dataRetrieved = True
	# option to check MIME type of returned files from archive; currently turned off
	# because archive seems to be consistently calling tsField FITS tables "ASCII"
	# these days.
	checkOutput = False
	
	usageString =  "%prog \"target_name\" [filter-list] [options]\n"
	usageString += "       %prog --coords=\"hh mm ss dd mm ss\" [filter-list] [options]\n"
	usageString += "       %prog --ref=\"run rerun camcol field\" [filter-list] [options]"
	usageString += "\n\nfilter-list contains the desired SDSS filters; it must be \"ugriz\" (no quotation marks) or a subset thereof."
	usageString += "\n(default is \"ugriz\")"
	usageString += "\n\nExamples: %prog \"NGC 4321\""
	usageString += "\n          %prog \"NGC 4321\" ugz --output=n4321"
	usageString += "\n          %prog ugriz --ref=\"3177 40 1 62\""
	parser = optparse.OptionParser(usage=usageString, version="%prog " + VERSION_STRING)


	parser.add_option("-v", "--version", action="store_true", dest="printVersion", 
						default=False, help="print version number and quit")
	parser.add_option("-o", "--output", dest="filename", default=DEFAULT_ROOTNAME,
						help="root name for saved image files (\"_<run>-<field>\" will be appended)")
	hstring = "RA and Dec as string (\"hh mm ss dd mm ss\" or \"hh:mm:ss dd:mm:ss\""
	hstring += " or decimal degrees [\"ra.dddd dec.dddd\"])"
	parser.add_option("--coords", dest="coordinates", default=NO_COORDS,
						help=hstring)
	helpmsg = "specify a specific SDSS field directly as \"run rerun camcol field\" (DR7)"
	helpmsg += " or \"run camcol field\" (DR12)"
	helpmsg += " (e.g., --ref=\"3177 40 1 62\" or --ref=\"3177,40,1,62\")"
	parser.add_option("--ref", dest="sdssString", default=None, help=helpmsg)
	parser.add_option("--nodr7", action="store_false", dest="getDR7", default=True,
						help="do not retrieve DR7 images")
	parser.add_option("--nodr12", action="store_false", dest="checkDR12", default=True,
						help="do NOT check for (or retrieve) DR12 images")
	parser.add_option("--getdr12", action="store_true", dest="getDR12", default=False,
						help="retrieve DR12 images")
	parser.add_option("--nodata", action="store_false", dest="getData", default=True,
						help="check availability only (don't retrieve any images or tables)")
	parser.add_option("--notables", action="store_false", dest="get_tsField", default=True,
						help="do *not* retrieve tsField FITS tables when retrieving DR7 images")
	parser.add_option("--nofits", action="store_false", dest="getFITS", default=True,
						help="do *not* retrieve FITS images")
	parser.add_option("--jpeg", action="store_true", dest="getJPEG", default=False,
						help="retrieve color JPEG image of each DR7 field")
	parser.add_option("--jpeg-only", action="store_true", dest="getJPEG_only", default=False,
						help="*only* retrieve color JPEG image of each DR7 field (no FITS files)")
	parser.add_option("--jpegsize", dest="jpegsize", default="z00",
						help="size of DR7 JPEG image (one of 'z00' [largest], 'z05', ..., 'z30' [smallest])")
	parser.add_option("--nosuffix", action="store_true", dest="noSuffix", default=False,
						help="do *not* add run and field numbers to saved FITS filenames (if -o option is used)")
	parser.add_option("--max", dest="maxFields", type="int", default=1,
						help="maximum number of separate fields to retrieve (default=1)")
	# getFieldN = 0 [default] means get *all* fields (as long as # fields < maxFields)
	parser.add_option("--getfield", dest="getFieldN", type="int", default=0,
						help="retrieve N-th field in list (first = 1, second = 2, etc.), if more than one field is found")
	
	parser.add_option("--silent", "--quiet", action="store_false", dest="verbose", default=True,
						help="only print error messages")
#	parser.add_option("--nochecks", action="store_false", dest="checkOutput", default=True,
#						help="don't check type of returned data")
	parser.add_option("--debug", action="store_true", dest="debugState", default=False,
						help="save all HTML files received")
	
	(options, args) = parser.parse_args(argv)
	
	if ((options.getFITS is False) and (options.get_tsField is False) and (options.getJPEG is False)):
		options.getData = False
	if options.getJPEG_only:
		options.getFITS = False
		options.get_tsField = False
		options.getJPEG = True
	
	
	# Check: Do we have an SDSS string, a target name, or a set of coordinates?
	if (options.sdssString is not None):
		# check for possibility of multiple options (user error):
		if (options.coordinates != NO_COORDS):
			print("\nPlease specify --ref *or* --coords, not both.\n")
			return kInputError
		# User specified a specific field in run-rerun-camcol-field format (via --ref),
		# so look for the filter string, if any:
		doCoordsQuery = False
		fieldType = CheckSDSSString(options.sdssString)
		if (fieldType > 0):
			sdssDataString = options.sdssString
			dataStringSupplied = True
			if fieldType == 1:
				nDR7DataFound = 1
			else:
				nDR12DataFound = 1
		else:
			msg = "\nThe SDSS field-specification string \"%s\"" % options.sdssString
			msg += " didn't have the right format\n"
			msg += "(for DR7, \"run rerun camcol field\" or \"run,rerun,camcol,field\"; "
			msg += " for DR12, \"run camcol field\" or \"run,camcol,field\"; "
			msg += "with all values being positive integers and camcol < 7).\n"
			print(msg)
			return kInputError
		if len(args) < 2:
			filterString = "ugriz"
		elif len(args) == 2:
			filterString = args[1].lower()
		else:
			msg = "\nToo many arguments supplied with --ref option ("
			for arg in args[1:]:
				msg += " " + "\"%s\"" % arg
			msg += " )."
			print(msg)
			print("Only an optional filter-list is allowed when using --ref.\n")
			return kInputError
	elif (options.coordinates == NO_COORDS):
		# User is evidently giving us a target name
		doFetchCoords = True
		if (len(args) < 2):
			print("\nYou must supply a target name (or else use the --coords options).\n")
			return kInputError
		targetName = args[1]
		if (len(args) == 2):
			filterString = "ugriz"
		else:
			filterString = args[2].lower()
	else:
		# User gave us coordinate string (via --coords)
		try:
			coordsList = utils.ProcessCoords(options.coordinates, decimalDegreesOK=True)
		except utils.CoordinateError as e:
			newmsg = "*** Problem with coordinate string \"%s\"\n" % str(e) + "\n"
			print(newmsg)
			return kInputError
		if (len(args) < 2):
			filterString = "ugriz"
		elif len(args) == 2:
			filterString = args[1].lower()
		else:
			msg = "\nToo many arguments supplied with --coords option ("
			for arg in args[1:]:
				msg += " " + "\"%s\"" % arg
			msg += " )."
			print(msg)
			print("Only an optional filter-list is allowed when using --coords.\n")
			return kInputError
	
	# Check filter string to make sure it's OK (only an issue when retrieving FITS images)
	if options.getFITS:
		if (not FilterStringOK(filterString)):
			print("\nList of filters (\"%s\") must be \"ugriz\" or subset thereof.\n" % filterString)
			return kInputError
	
	# Check JPEG size specification, if necessary
	if options.getJPEG:
		if (not JPEGSizeOK(options.jpegsize)):
			print("\nBad specification for JPEG image size (\"%s\")" % options.jpegsize)
			print("(Should be one of [\"z00\", \"z05\", ..., \"z25\", \"z30\"])\n")
			return kInputError


	# Do we need to look up coordinates for a target?
	if doFetchCoords:
		if options.verbose:
			print("\nDoing coordinate lookup for \"%s\"..." % targetName)
		coordsList = FetchCoordinates(targetName, options.verbose)
		if (coordsList == getcoords.NO_COORDS_FOUND) or (coordsList is None):
			msg = "*** Unable to get coordinates for \"%s\". *** \n" % targetName
			msg += "Cannot search SDSS archive -- terminating search.\n"
			print(msg)
			return kCoordinateLookupError
		p1 = coordsList[0].split()
		p2 = coordsList[1].split()
		if ( len(p1) < 3 ) or ( len(p2) < 3 ):
			print("*** Warning: coordinates appear to be truncated or low-resolution! ***")
			print("Try entering full coordinates (including seconds) by hand with --coords option.\n")
			return kCoordinateLookupError


	# If necessary, see if coordinates are within SDSS
	if doCoordsQuery:
		if options.verbose:
			print("\nQuerying SDSS DR7 Data Archive Server for availability...")
			if (not options.getData):
				print("(no files will be retrieved)...")
		# Create an instance of sdss_coords_archive and prep it for queries
		searchServer = sdss_coords_archive.MakeArchive()
		searchServer.SetMode("fetchsdss")
		searchServer.InsertCoordinates(coordsList)
		(responseString_dr7, nDR7DataFound) = QueryArchive(searchServer)
		if options.verbose:
			print("   server response = %s" % responseString_dr7)
		if (nDR7DataFound > 1):
			print("   %d separate DR7 fields found" % nDR7DataFound)
			if (options.getData) and (options.getFieldN < 1) and (nDR7DataFound > options.maxFields):
				print("\nNumber of DR7 fields (%d) is greater than maximum (%d)" % (nDR7DataFound, options.maxFields))
				print("No data will be retrieved.")
				print("\t(use \"--max\" to specify larger maximum if desired, or \"--nodr7\" to skip DR7 images)")
				options.getData = False
		elif (nDR7DataFound == 0) and options.verbose:
			print("Object or coordinates apparently not within SDSS DR7!")
		if options.checkDR12:
			if options.verbose:
				print("\nQuerying SDSS DR12 Science Archive Server for availability...")
				if (not options.getData):
					print("(no files will be retrieved)...")
			# Create an instance of sdss_dr12_archive and prep it for queries
			dr12Server = sdss_dr12_archive.MakeArchive()
			dr12Server.SetMode("fetchsdss")
			dr12Server.InsertCoordinates(coordsList)
			(responseString_dr12, nDR12DataFound) = QueryArchive(dr12Server)
			if options.verbose:
				print("   server response = %s" % responseString_dr12)
			if (nDR12DataFound > 1):
				print("   %d separate DR12 fields found" % nDR12DataFound)
				if (options.getData) and (options.getFieldN < 1) and (nDR12DataFound > options.maxFields):
					print("\nNumber of DR12 fields (%d) is greater than maximum (%d)" % (nDR12DataFound, options.maxFields))
					print("No data will be retrieved.")
					print("\t(use \"--max\" to specify larger maximum if desired, or \"--nodr12\" to skip DR12 images)")
					options.getData = False
			elif (nDR12DataFound == 0) and options.verbose:
				print("Object or coordinates apparently not within SDSS DR12!")
		
	
	# Data exists, and we are going to get it, so request files from archive
	if ( options.getData and ((nDR7DataFound > 0) or (nDR12DataFound > 0)) ):
		if dataStringSupplied:
			# user gave us a single "run rerun camcol field" or "run camcol field" string
			# this means we *definitely* get the data
			dataStringList = [sdssDataString]
			if IsDR12FieldString(sdssDataString):
				# OK, we know that we're retrieving *only* DR12 data
				options.get_tsField = False
				options.getJPEG = False
			urlFilePairList = get_sdssfiles.MakeURLFilePairs(dataStringList, filterString, 
									options.filename, options.getFITS, options.get_tsField,
									options.getJPEG, options.jpegsize, options.noSuffix)
			retrieveData = True

		else:
			# Extract useful info from response string: separate out the run/rerun/etc.
			# info, which is on the second line, after the equals sign
			# (second and subsequent lines, in the case of multiple fields)
			urlFilePairList = []
			if (nDR7DataFound > 0) and options.getDR7:
				fieldInfoLines = responseString_dr7.split("\n")[1:]
				dataStringList_dr7 = [ line.split(" = ")[1].split(")")[0] for line in fieldInfoLines ]
				if options.getFieldN > 0:
					# user specifies field N, we get index N-1 (as a single-element list)
					try:
						dataStringList_dr7 = dataStringList_dr7[options.getFieldN - 1:options.getFieldN]
					except IndexError:
						msg = "User specified field number (%d) greater than " % options.getFieldN
						msg += "number of available fields!\n"
						print(msg)
						return -12
				urlFilePairList += get_sdssfiles.MakeURLFilePairs(dataStringList_dr7, filterString, 
										options.filename, options.getFITS, options.get_tsField,
										options.getJPEG, options.jpegsize, options.noSuffix)
				retrieveData = True
			if (nDR12DataFound > 0) and options.getDR12:
				options.get_tsField = False
				options.getJPEG = False
				fieldInfoLines = responseString_dr12.split("\n")[1:]
				dataStringList_dr12 = [ line.split(" = ")[1].split(")")[0] for line in fieldInfoLines ]
				if options.getFieldN > 0:
					# user specifies field N, we get index N-1 (as a single-element list)
					try:
						dataStringList_dr12 = dataStringList_dr12[options.getFieldN - 1:options.getFieldN]
					except IndexError:
						msg = "User specified field number (%d) greater than " % options.getFieldN
						msg += "number of available fields!\n"
						print(msg)
						return -12
				urlFilePairList += get_sdssfiles.MakeURLFilePairs(dataStringList_dr12, filterString, 
										options.filename, options.getFITS, options.get_tsField,
										options.getJPEG, options.jpegsize, options.noSuffix)
				retrieveData = True
		
		
		# attempt to fetch the data
	if retrieveData is True:
		if options.verbose:
			print("\nAttempting to retrieve requested files from SDSS... ")
		saveDir = os.getcwd()
		for urlFilePair in urlFilePairList:
			print(urlFilePair)
			(savedFlag, header, stringFile) = get_sdssfiles.GetAndSaveFile(urlFilePair, 
												saveDir, checkOutput)
			if savedFlag is False:
				print("Failed to retrieve %s\n" % urlFilePair[1])

		
				

	if (nDR7DataFound < 0) or (nDR12DataFound < 0):
		print("Problems contacting SDSS servers.")

	if options.verbose:
		print("Done!\n")



if __name__ == '__main__':
	main(sys.argv)
