#! /usr/bin/env python
#   A Python script to retrieve lists of sources from the HST
# Guide Star Catalog (currently at version 2.3)
# specific target (astronomical object or coordinates).
# 
# Requires Python 2.3 or higher (due to use of optparse and booleans)
# 
# HISTORY:
#    29 May 2007: Created.


# Import various standard modules:
import sys, optparse

# Import our libraries:
import utils
import getcoords
import gsc2_archive

VERSION_STRING = "0.1"

NO_COORDS = "NO COORDS"
DEFAULT_ROOTNAME = "gsc2"
DEFAULT_COORDLIST = ['12 00 00', '-70 00 00']
DEFAULT_SAVE_FILE = "gsc2_sources.dat"
DEFAULT_RADIUS = 2.0   # radius in arc minutes


def FetchCoordinates( objectName ):
	"""Wrapper function which calls getcoords.GetCoordinates() to fetch
	coordinates of objectName from SIMBAD.  Returns a two-element list
	of strings (first string = RA, second string = Declination)."""
	
	success, coordinates = getcoords.GetCoordinates(objectName)
	if ( success >= 1 ):
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
		textReceived = archive.QueryServer()
		nDataFound = 1
	except IOError, e:
		messageString = "I/O Error -- " + str(e.args[0]) + ": " + \
						str(e.args[1]) + "\n"
		if ( str(e.args[1]) == "(7, 'No address associated with nodename')" ):
			messageString += 20*" " + "(DNS server is down,"
			messageString += " or we're not connected to the Internet?)"
		else:
			messageString += " (try again later?)"
		textReceived = messageString
		nDataFound = -1

	return (textReceived, nDataFound)



def main(argv):

	# Set up target, etc, by parsing command-line:
	coordsList = DEFAULT_COORDLIST
	dataFound = 0
	searchRadius = DEFAULT_RADIUS
	
	usageString =  "%prog \"target_name\" [options]\n"
	usageString += "       %prog --coords=\"hh mm ss dd mm ss\" [filter-list] [options]\n"
	usageString += "\n\nExamples: %prog \"NGC 936\""
	usageString += "\n          %prog \"NGC 936\""
	usageString += "\n\nRequested data is stored in an file named \"sdss.tar.gz\" or \"sdss.jpeg\";\n"
	usageString += "use -o/--output to specify a different root name instead of \"sdss\"."
	parser = optparse.OptionParser(usage=usageString, version="%prog " + VERSION_STRING)

	parser.add_option("-o", "--output", dest="filename", default=DEFAULT_ROOTNAME,
						help="name for saved data file")
	parser.add_option("--coords", dest="coordinates", default=NO_COORDS,
						help="RA and Dec as string (\"hh mm ss dd mm ss\" or \"hh:mm:ss dd:mm:ss\")")
	
	(options, args) = parser.parse_args(argv)
	

	
	if (options.coordinates == NO_COORDS):
		# User is evidently giving us a target name
		if (len(args) < 2):
			print "\nYou must supply a target name (or else use the --coords options).\n"
			return 1
		targetName = args[1]
		if (len(args) > 2):
			searchRadius = float(args[2])
		print "\nDoing coordinate lookup for \"%s\"..." % targetName
		coordsList = FetchCoordinates(targetName)
		if (coordsList == getcoords.NO_COORDS_FOUND) or (coordsList is None):
			msg = "*** Unable to get coordinates for \"%s\". *** \n" % targetName
			msg += "Cannot check Guide Star Catalog -- terminating search.\n"
			print msg
			return 2
		p1 = coordsList[0].split()
		p2 = coordsList[1].split()
		if ( len(p1) < 3 ) or ( len(p2) < 3 ):
			print "*** Warning: coordinates appear to be truncated or low-resolution! ***"
			print "Try entering full coordinates (including seconds) by hand with --coords option.\n"
			return 2
	else:
		if (len(args) > 1):
			searchRadius = float(args[1])
		# Convert user-supplied coordinates to decimal degrees
		try:
			coordsList = utils.ProcessCoords(options.coordinates)
		except utils.CoordinateError, e:
			newmsg = "*** Problem with coordinate string \"%s\"\n" % str(e) + "\n"
			print newmsg
			return 2


	# Create an instance of gsc2_archive and prep it for queries
	gscServer = gsc2_archive.MakeArchive()
	gscServer.InsertCoordinates(coordsList)
	print "\nQuerying Guide Star Catalog 2.3 server..."
	(responseText, dataFound) = QueryArchive(gscServer)
	if (dataFound > 0):
		saveFileName = DEFAULT_SAVE_FILE
		saveFile = open(responseText, 'w')
		saveFile.write(textReceived)
		saveFile.close()
	else:
		print "Problems contacting Guide Star Catalog server:"
		print responseText
		

	print "Done!\n"
	return 0



if __name__ == '__main__':
	main(sys.argv)
