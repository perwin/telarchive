#! /usr/bin/env python
#   A Python script to find and download SDSS spectra for or near specific target 
# (astronomical object or coordinates).
# 
# Requires Python 2.6 or higher
# 

from __future__ import print_function
# Import various standard modules:
import os, sys, re, optparse

# Import our modules:
import utils, getcoords, get_sdssfiles
# import sdss_sas_archive
import sdss_dr12_archive, sdss_dr14spec_archive

VERSION_STRING = "1.3"

NO_COORDS = "NO COORDS"
DEFAULT_ROOTNAME = "sdss"
DEFAULT_COORDLIST = ['12 00 00', '-70 00 00']  # should be outside SDSS!
DEBUG_SAVE_FILE = "fetchsdss_spectra.html"

kServerError = -1   # covers -1 values returned by sdss_sql_archive.AnalyzeHTML()
kConnectionError = -2
kCoordinateLookupError = -3
kInputError = -4


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
	If debug = True, then *all* returned HTML is saved to a file."""

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



def main(argv):
	"""Wrapper function which handles command-line parameters and dispatch for
	searching SDSS archive and retrieving spectroscopic data.
	
	Returns -2 for problems with input, -1 for problems with getting coordinates
	from SIMBAD, 0 for successful search with no data found, and 1 for successful
	search with data found.
	"""

	# Set up target, etc, by parsing command-line:
	coordsList = DEFAULT_COORDLIST
	nDataFound = 0
	doFetchCoords = False   # do we need to query SIMBAD for object coordinates?
	doCoordsQuery = True    # do we need find out if coordinates are inside SDSS?
	dataStringSupplied = False
	# this is currently predefined as True because we don't yet have
	# anything in place to check to see if data is retrieved or not
	dataRetrieved = True
	# option to check MIME type of returned files from archive; currently turned off
	# because archive seems to be consistently calling tsField FITS tables "ASCII"
	# these days.
	checkOutput = False
	spectrumExists = False
	
	usageString =  "%prog \"target_name\" [options]\n"
	usageString += "       %prog --coords=\"hh mm ss dd mm ss\" [options]\n"
	usageString += "\n\nExamples: %prog \"NGC 4321\""
	usageString += "\n          %prog \"NGC 4321\" --output=n4321"
	parser = optparse.OptionParser(usage=usageString, version="%prog " + VERSION_STRING)

	hstring = "RA and Dec as string (\"hh mm ss dd mm ss\" or \"hh:mm:ss dd:mm:ss\""
	hstring += " or decimal degrees [\"ra.dddd dec.dddd\"])"
	parser.add_option("-o", "--output", dest="filename", default=DEFAULT_ROOTNAME,
						help="root name for saved spectroscopic files (\"_<plate>-<mjd>-<fiber>.fits\" will be appended)")
	parser.add_option("--coords", dest="coordinates", default=NO_COORDS,
						help=hstring)
	parser.add_option("--nodata", action="store_false", dest="getData", default=True,
						help="check availability only (don't retrieve any spectra)")
	
	htxt = "find & retrieve all spectra (not just the nearest spectrum) within R_spec of this object/position, if it exists"
	parser.add_option("--getallspec", action="store_true", dest="getAllSpectra", default=False,
						help=htxt)
	htxt = "specify R_spec (radius to search for SDSS spectra, in arcmin; default = 0.1)"
	parser.add_option("--specradius", dest="specSearchRadius", default=None,
						help=htxt)
	
	parser.add_option("--silent", "--quiet", action="store_false", dest="verbose", default=True,
						help="print just genuine error messages")
#	parser.add_option("--nochecks", action="store_false", dest="checkOutput", default=True,
#						help="don't check type of returned data")
	parser.add_option("--debug", action="store_true", dest="debugState", default=False,
						help="save all HTML files received")
	
	(options, args) = parser.parse_args(argv)
		
	
	if (options.coordinates == NO_COORDS):
		# User is evidently giving us a target name
		doFetchCoords = True
		if (len(args) < 2):
			print("\nYou must supply a target name (or else use the --coords options).\n")
			return kInputError
		targetName = args[1]
	else:
		# User gave us coordinate string (via --coords)
		try:
			coordsList = utils.ProcessCoords(options.coordinates, decimalDegreesOK=True)
		except utils.CoordinateError as e:
			newmsg = "*** Problem with coordinate string \"%s\"\n" % str(e) + "\n"
			print(newmsg)
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
# 	nDR12DataFound = 0
# 	if doCoordsQuery:
# 		if options.verbose:
# 			print("\nQuerying SDSS DR12 Science Archive Server to see if these coordinates are within survey area...")
# 		# Create an instance of sdss_dr12_archive and prep it for queries
# 		dr12Server = sdss_dr12_archive.MakeArchive()
# 		dr12Server.SetMode("fetchsdss")
# 		dr12Server.InsertCoordinates(coordsList)
# 		(responseString, nDR12DataFound) = QueryArchive(dr12Server)
# 		if options.verbose:
# 			print("   server response = %s" % responseString)
# 		if (nDR12DataFound > 1):
# 			print("   %d separate DR12 fields found" % nDR12DataFound)
# 		
# 		if (nDR12DataFound > 1):
# 			# SDSS imaged these coords, so search for spectra
# 			specServer = sdss_sas_archive.MakeArchive()
# 			specServer.InsertCoordinates(coordsList)
# 			if options.specSearchRadius is not None:
# 				specServer.InsertRadius(options.specSearchRadius)
# 			specServer.SetMode("fetchsdss")
# 			if options.verbose:
# 				print("\nQuerying server to search for spectra near coordinates...")
# 			(spectrumResponse, nSpectraFound) = QueryArchive(specServer, debug=True)
# 			print("\n" + spectrumResponse + "\n")
# 			if (nSpectraFound > 0):
# 				spectrumExists = True
	
	# See if DR14 archive has spectra
	specServer = sdss_dr14spec_archive.MakeArchive()
	specServer.SetMode("fetchsdss")
	specServer.InsertCoordinates(coordsList)
	if options.specSearchRadius is not None:
		specServer.InsertSpectroscopyRadius(options.specSearchRadius)
	if options.verbose:
		print("\nQuerying server to search for spectra near coordinates...")
	(spectrumResponse, nSpectraFound) = QueryArchive(specServer, debug=True)
	print("\n" + spectrumResponse)
	if (nSpectraFound > 0):
		spectrumExists = True
	
	# Data exists, and we are going to get it, so request files from archive
	if options.getData and spectrumExists:
		# get spectrum
		specFilename = None
		if options.filename != DEFAULT_ROOTNAME:
			specFilename = options.filename
		# split response string from archive object into individual lines (skip the first,
		# which is just "Spectroscopic data exists! ..."), then extract "plate mjd fiber"
		# substrings
		dlines = spectrumResponse.splitlines()[1:]
		specStringList = [ line.split("=")[1].strip(")") for line in dlines ]
		urlFilePairList = get_sdssfiles.MakeSpectrumURLFilePairs(specStringList, specFilename)
		if options.verbose:
			if (nSpectraFound == 1):
				msg = "\nAttempting to retrieve requested spectrum from SDSS... "
			else:
				msg = "\nAttempting to retrieve requested spectra from SDSS... "
			print(msg)
		saveDir = os.getcwd()
		if options.getAllSpectra is False:
			urlFilePairList = urlFilePairList[:1]
		for urlFilePair in urlFilePairList:
			print(urlFilePair)
			(savedFlag, header, stringFile) = get_sdssfiles.GetAndSaveFile(urlFilePair, 
												saveDir, checkOutput)
			if savedFlag is False:
				print("Failed to retrieve %s\n" % urlFilePair[1])
		

	if options.verbose:
		print("Done!\n")
	return nDataFound



if __name__ == '__main__':
	main(sys.argv)
