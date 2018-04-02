#! /usr/bin/env python3
#
#    Simple Python module/script for getting coordinates of astronomical objects
# from Simbad.  Probably only works if your site has some kind of site account
# with Simbad, since you have to have an account to use Simbad and this
# module has no way of dealing with username-password queries.
# 
#    Usage:
# > getcoords.py "object name"  [<<- quotation marks needed!]
#    Or just:
# > getcoords.py
# and you will be asked for an object name (quotation marks not needed)
#
#
# Notes on possibly using NED:
#   [] If Simbad searches don't work, ask user if he/she wants to try NED?
# (So user can give up if they know object is not extragalactic)  Switch to
# toggle this on and off, so automated multi-object searches won't halt waiting
# for user response...
#   [] Switch to let user specify NED-first or NED-only search?  (For
# situations where no site account with Simbad exists.)
#
# First line of real data in table should be where coordinates are.  Extract
# Object Name (in case something else came up first, like a SN) and coords.
# Print object name, so that user can check that the correct object was
# found...
# Extra items coming up shouldn't be a problem if we specify "Extended Name
# Search" = "No".
# 
# 10 Dec 2006: Updated to work with output from SIMBAD4
#

from __future__ import print_function
import sys
#import urllib
import re
#from . import simbad_archive
import simbad_archive

#import archive_class

DEFAULT_TARGET = "ngc 900"

PRECISE_COORDS_FOUND = 1
VAGUE_COORDS_FOUND = 2
NO_COORDS_FOUND = 0
SERVER_ERROR = -1
CONNECTION_REFUSED = -2
MYSTERY_ERROR = -666


simbadURL_france = "http://simbad.u-strasbg.fr/sim-id.pl"

#http://simbad.u-strasbg.fr/sim-id.pl?protocol=html&Ident=ngc+936&NbIdent=1&Radius=10&Radius.unit=arcmin&CooFrame=FK5&CooEpoch=2000&CooEqui=2000&output.max=all&output.mesdisp=N&Bibyear1=1983&Bibyear2=2004&Frame1=FK5&Frame2=FK4&Frame3=G&Equi1=2000.0&Equi2=1950.0&Equi3=2000.0&Epoch1=2000.0&Epoch2=1950.0&Epoch3=2000.0
#http://simbad.u-strasbg.fr/sim-id.pl?protocol=html&Ident=ngc+936&NbIdent=1&Radius=10&Radius.unit=arcmin&CooFrame=ICRS&CooEpoch=2000&CooEqui=2000&output.max=all&output.mesdisp=N&Bibyear1=1983&Bibyear2=2004&Frame1=none&Frame2=none&Frame3=none&Equi1=2000.0&Equi2=1950.0&Equi3=2000.0&Epoch1=2000.0&Epoch2=1950.0&Epoch3=2000.0

# this works as a shortened query form:
#http://simbad.u-strasbg.fr/sim-id.pl?protocol=html&Ident=ngc+936&NbIdent=1&Radius=10&Radius.unit=arcmin&CooFrame=ICRS
#&CooEpoch=2000&CooEqui=2000&output.max=all&output.mesdisp=N&Bibyear1=1983&Bibyear2=2004&Frame1=none&Frame2=none&Frame3=none


# the following may be down or out-of-date:
# simbadURL_us = "http://simbad.harvard.edu/sim-id.pl"
# nedURL = "http://ned.ipac.caltech.edu/cgi-bin/nph-objsearch"
# 
# 
# SIMBAD_PARAMS_DICT = {'Ident': DEFAULT_TARGET, 'protocol': 'html',
#                       'NbIdent': '1', 'Radius': '10', 'Radius.unit': 'arcmin',
# 					  'CooFrame': 'ICRS', 'CooEpoch': '2000', 'CooEqui': '2000',
# 					  'output.max': 'all', 'output.mesdisp': 'N',
# 					  'Bibyear': '1983', 'Bibyear2': '2004',
# 					  'Frame1': 'none', 'Frame2': 'none', 'Frame3': 'none' }
# SIMBAD_SEARCHES = {}
# NED_PARAMS_DICT = {'objname': DEFAULT_TARGET, 'extend': 'no'}
# NED_PARAMS_FULL_DICT = {'objname': DEFAULT_TARGET, 'extend': 'no',
#                         'out_csys': 'Equatorial', 'out_equinox': 'J2000.0',
#                         'zv_breaker': '30000.0', 'img_stamp': 'NO'}
# NED_SEARCHES = {}

# simbadFrance = archive_class.SingleArchive( 10, 'SIMBAD Archive (France)',
#                                             'simbad', simbadURL_france,
#                                             SIMBAD_PARAMS_DICT, SIMBAD_SEARCHES )
# simbadUS = archive_class.SingleArchive( 10, 'SIMBAD Archive (US mirror)',
#                                         'simbad', simbadURL_us,
#                                         SIMBAD_PARAMS_DICT, SIMBAD_SEARCHES )
# ned = archive_class.SingleArchive( 11, 'NED', 'ned', nedURL, NED_PARAMS_DICT,
# 								   NED_SEARCHES)
# nedFull = archive_class.SingleArchive( 11, 'Ned', 'ned', nedURL,
#                                        NED_PARAMS_FULL_DICT, NED_SEARCHES )

#simbadArchiveList = [simbadFrance, simbadUS]
#simbadArchiveList = [simbadFrance]


# Set up searches of the big HTML string:
findBadName = re.compile(r"Identifier not found in the database")
findServerError = re.compile(r"Internal Server Error")
findFullCoords = re.compile(r"""
	ICRS\s+</B>\s+coord.\s+\([^)]*2000\)\s+:\s+</DIV>\s+</TD>\s+<TD>\s+<B>\s+<TT>\s+
	(?P<ra>\d\d\s\d\d\s\d\d[.]*\d*\b)\s+
	(?P<dec>(\+|-)\d\d\s\d\d\s\d\d[.]*\d*\b)
	""", re.VERBOSE)
# newer version of search for minor change in SIMBAD output (Aug 2011);
# should handle older format if that gets reinstated
findFullCoordsNew = re.compile(r"""
	ICRS\s+</B>\s+coord.\s+<I>\s+\(ep=J2000\)\s+:\s+</I>\s+</SPAN>\s+</TD>\s+
    <TD\sNOWRAP>\s+<B>\s+<TT>\s+
    (?P<ra>\d\d\s\d\d\s\d\d[.]*\d*\b)\s+
    (?P<dec>(\+|-)\d\d\s\d\d\s\d\d[.]*\d*\b)
	""", re.VERBOSE)
# findFullCoordsNew_old = re.compile(r"""
# 	ICRS\s+</B>\s+coord.\s+\([^)]*2000\)\s+:\s+(</SPAN>|</DIV>)\s+</TD>\s+<TD>\s+<B>\s+<TT>\s+
# 	(?P<ra>\d\d\s\d\d\s\d\d[.]*\d*\b)\s+
# 	(?P<dec>(\+|-)\d\d\s\d\d\s\d\d[.]*\d*\b)
# 	""", re.VERBOSE)
findLimitedCoords = re.compile(r"""
	ICRS\s+</B>\s+coord.\s+\([^)]*2000\)\s+:\s+</DIV>\s+</TD>\s+<TD>\s+<B>\s+<TT>\s+
	(?P<ra>\d\d\s\d\d[.]*\d*\b)       # RA group (w/ 0+ decimals in minutes)
	\s+                               # skip whitspace btwn RA & Dec
	(?P<dec>(\+|-)\d\d\s\d\d[.]*\d*\b)   # Dec group (w/ 0+ decimals in minutes)
	""", re.VERBOSE)



def QuerySimbad( archive, objectName ):

	try:
		#connection = urllib.urlopen( archive.URL, archive.EncodeParams() )
		archive.InsertTarget(objectName)
		htmlReceived = archive.QueryServer()
	except IOError as e:
		messageString = "I/O Error -- " + str(e) + "\n"
# 		messageString = "I/O Error -- " + str(e.args[0]) + ": " + \
# 						str(e.args[1]) + "\n"
# 		if ( str(e.args[1]) == "(7, 'No address associated with nodename')" ):
# 			messageString += 20*" " + "(DNS server is down,"
# 			messageString += " or we're not connected to the Internet?)"
# 		else:
# 			messageString += " (try again later?)"
		print(messageString)
		htmlReceived = ""

	return htmlReceived



def CheckResults( htmlString ):

	# Do searches and evaluate results:
	badNameResult = findBadName.search(htmlString)
	if badNameResult:
		messageString = "Simbad reports bad name: \"%s\"" % badNameResult.group()
		return (NO_COORDS_FOUND, messageString)
	serverErrorResult = findServerError.search(htmlString)
	if serverErrorResult:
		messageString = "Server error (try again later)"
		return (SERVER_ERROR, messageString)
	findFullCoordsResult = findFullCoordsNew.search(htmlString)
	if findFullCoordsResult:
		coordsRA = findFullCoordsResult.group('ra')
		coordsDec = findFullCoordsResult.group('dec')
		return (PRECISE_COORDS_FOUND, coordsRA, coordsDec)
	findLimitedCoordsResult = findLimitedCoords.search(htmlString)
	if findLimitedCoordsResult:
		coordsRA = findLimitedCoordsResult.group('ra')
		coordsDec = findLimitedCoordsResult.group('dec')
		return (VAGUE_COORDS_FOUND, coordsRA, coordsDec)
	else:
		messageString = "Unable to find actual coordinates"
		return (MYSTERY_ERROR, messageString)



def GetCoordinates( objectName, archiveList=None, saveFile=None, verbose=True ):
	# This function is called by archive_search2.py.  The default is to only
	# query the main Simbad server in France.
	if ( archiveList == None ):
		archiveList = [ simbad_archive.MakeArchive() ]
	nSimbadArchives = len(archiveList)
	objectFound = -1
	for i in range(nSimbadArchives):
		currentArchive = archiveList[i]
		if verbose:
			print("\t" + currentArchive.longName + ": ", end=' ')
		try:
			outputHTML = QuerySimbad( currentArchive, objectName )
			#outputHTML = outputHTML.decode("utf-8")
			objectCoords = CheckResults(outputHTML)
		except IOError as e:
			print("Error connecting to server!")
			objectCoords = [CONNECTION_REFUSED, e]
		if ( objectCoords[0] == PRECISE_COORDS_FOUND):
			# We got some coordinates back!
			objectFound = PRECISE_COORDS_FOUND
			break
		elif ( objectCoords[0] == VAGUE_COORDS_FOUND):
			# We got coordinates, but only down to minutes
			objectFound = VAGUE_COORDS_FOUND
			break
		elif ( objectCoords[0] == NO_COORDS_FOUND):
			# We were told it can't be found in the database
			print(objectCoords[1])
			objectFound = NO_COORDS_FOUND
			break
		else:
			# Problem with the search (e.g., archive server error)
			print(objectCoords[1])
			if (i < (nSimbadArchives - 1) ):
				print("Checking next mirror...")

	if (saveFile is not None):
		outf = open(saveFile, 'w')
		outf.write(outputHTML)
		outf.close()
		print("Wrote HTML to file %s.\n" % saveFile)
			
	return (objectFound, objectCoords)




def main(argv):
	# Set up target, etc:
	saveHTML = None
	if ( len(argv) > 1 ):
		objectName = argv[1]
		if ( len(argv) > 2 ):
			saveHTML = argv[2]
	else:
		print("Please enter an object name to search for: ", end=' ')
		objectName = sys.stdin.readline().strip()


	print("\nStarting search...")
	success, coordinates = GetCoordinates(objectName, saveFile=saveHTML)

	if ( success == PRECISE_COORDS_FOUND ):
		print("")
		print("RA, Dec  =  %s   %s" % (coordinates[1], coordinates[2]))
	elif ( success == VAGUE_COORDS_FOUND ):
		print("")
		print("RA  =   %s" % coordinates[1])
		print("Dec =  %s\n" % coordinates[2])
	elif ( success == NO_COORDS_FOUND ):
		print("No coordinates found for object: bad name?")
	else:
		print("No luck querying servers; try again later...")
	print("Done!\n")



if __name__ == '__main__':
	main(sys.argv)
