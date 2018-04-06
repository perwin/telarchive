#! /usr/bin/env python3

"""
A Python script to search multiple public telescope archives.
   
Usage:

$ archive_search.py "object name" [search_radius]
   OR:
$ python archive_search.py "object name" [search_radius]
   OR [assuming "telarchive" is a link to archive_search.py or a
      script which calls it -- see dosearch.py]:
$ telarchive "object name" [search_radius]

The name of the object *must* be in quotes, and the optional search radius
is in arc minutes (current default value = 4 arc min).

for a full list of options and examples:
$ archive_search.py -h


How to call this with a simple Python script (see dosearch.py for an
example of a standalone script):
   
      from telarchive import archive_search
      archive_search.main(args)
      
      

Copyright 2003-2018 Peter Erwin

This program is distributed under the terms of the GNU General Public
License (see the file COPYING included with the distribution).
"""

# Copyright 2003-2018 Peter Erwin
# 
# This file is part of telarchive.
# 
# Telarchive is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License as published by
# the Free Software Foundation; either version 2 of the License, or
# (at your option) any later version.
# 
# Telarchive is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
# 
# You should have received a copy of the GNU General Public License
# along with telarchive; if not, write to the Free Software
# Foundation, Inc., 51 Franklin St, Fifth Floor, Boston, MA  02110-1301  USA



#   Some notes on possible archive replies or error messages returned:
#     [] NOTE that when CFHT finds only *one* item, it does *not* give the usual
# "A total of X items were returned" message.  In fact, it gives no such message
# at all; it just returns the item.
#     [] When given a spurious object name (e.g., "NGC z"), the various ESO
# archives (including HST) correctly reports "Object `ngc z' not found in SIMBAD".
# However, some archives fail to catch this, and produce lines like this:
#    SIMBAD coordinates for ngc z : 00 00 00.0, +00 00 00.0
# These archives then go ahead and search using these default Vernal Equinox
# coordinates.  The ING does the same, but doesn't even bother printing the V.E.
# coordinates.  These false searches can turn up a lot of hits -- probably cases 
# where software error, tests, or very old observations mean null values in the
# FITS headers  (or things like, e.g., middle-of-the-day bias frames).
#
#   Other archives which we might include at some future date:
#     [] JCMT -- available via http://cadcwww.dao.nrc.ca/jcmt/
#           Some preliminary notes:
#              <> JCMT has *two* discrete interfaces (SCUBA and spectroscopy)
#              <> JCMT defaults to Vernal Equinox coords for bad object names (like
#                 everybody else except ESO) -- no surprise there...
#     [] "ATNF" = Australia Telescope Compact Array (radio)
#         http://www.atnf.csiro.au/observers/search_pos.html
#        
#   Archives we probably *cannot* search:
#     [] ISO -- main(only?) access is via Java applet, *not* HTML form.
#     [] New ING form -- Javascript only.
#
#   Speculative Improvements:
#     [] Possible finer-grained selection:
#           ING: can select image or spectra ("Photspec"); can enter instrument
#                name by hand, but then you miss all the others...   <td>S</td>
#           HST: can select one (or more?) instruments
#           ESO: can select one instrument (beware of instruments with both
#                imaging and spectroscopy modes)  Possible problem -- it may
#                not be possible to select VLT instruments/modes from the
#                general ESO page; you may have to use the VLT-only page for that.
#           CFHT: separate pages for "Spectra", "Images", and "Infrared" (not clear
#                if IR images would show up on "Images" page...)  Can also select
#                one instrument.
#           
#     [] Command-line switch to specify search *box* or *radius*
#        -- check which archives actually uses boxes and which really use
#           radii; adjust box-size-setting accordingly
#     [] Put a loop around dispatch of searches (contingent on a command-line
#  switch?  how to handle threads, since we can't do another loop until all
#  threads are done?) -- lets us do multiple objects, perhaps even saving
#  stdout results to one file.  Also useful as setup for automated searches
#  using lists of objects...
#     [] Fix saving of web pages -- currently, this code assumes a target name,
#  resulting coordinate-based name for coordinate-searches will be ugly...
#        -- build coordinate-name, a la GOYA names?
#        -- option for user to specify a root name? [more complicated for multiple
#        coordinate searches]
#
#   Timing notes: searching for NGC 4371 with coordinate lookup first:
#      Avg time = 50 sec (46--56 sec)
#   Without coordinate lookup (forces individual archives to do it):
#      Avg time = 48 (42--59 sec)
#   [The latter was done with changes to the object name each time, to get
# around possible caching by archives -- Simbad lookup uses the POST method, so
# it's just a complicated URL...]
#   In any case, doing the name lookup ourselves doesn't seem to save
# any significant time, and may even take more time.  It's probably mostly
# useful as a fallback in case the archives can't intrepret valid Simbad
# replies (as appears to happen if Simbad gives them imprecise coordinates:
# this is the case with "NGC 980" and the ING archive, for example).
#   LATER NOTE: Since SDSS can't handle object names, we now default to 
# doing the name lookup ourselves with Simbad, so we can pass the 
# coordinates on to the SDSS archive.
#


# Import various standard modules:
from __future__ import print_function
import sys, os, optparse

if sys.version_info[0] > 2:
	usingPython2 = False
else:
	usingPython2 = True



# Version number:
kVersionNumber = "2.0.0"

# General constants:
kHST_ESO = 0
kHST_STScI = 1
NO_COORDS = [0, 0]
NO_NAME = "NO NAME"
COORD_SEARCH = 1
BROWSER_MASQUERADE = "Mozilla/5.0 [en]"
MAX_BOXSIZE = 60.0


# Not all systems or installations have threading enabled, even though the
# threading.py module is installed.  Try importing "thread" first to test for
# thread-friendliness...
try:
	if usingPython2:
		import thread
	else:
		import _thread
except ImportError:
	threadingPresent = 0
else:
	import threading
	threadingPresent = 1
	
# Import our own modules:
import archive_list, getcoords, utils, module_list




def FetchCoordinates( objectName ):
	success, coordinates = getcoords.GetCoordinates(objectName)
	if ( success >= 1 ):
		print("Found object coordinates: RA = %s, Dec = %s" % (coordinates[1],
															   coordinates[2]))
		return coordinates[1:]
	else:
		msg = "\n   *** Unable to get coordinates for \"%s\". *** \n" % objectName
		msg += "   Cannot search SDSS archive -- terminating search.\n"
		print(msg)
		sys.exit(2)



def SearchOneArchive( archive, targetName, debugState=0, saveSuccesses=0 ):
	"""SearchOneArchive( archive, targetName, debugState=0, saveSuccesses=0 )
	Handles submission of request and evaluation of results for a single archive.
	It requires a BasicArchive object [see basic_archive.py] or derived object,
	and also the name of the object (the latter is used for naming saved HTML
	files).  If debugState = 1, then *all* HTML is saved to files; if not and
	saveSuccesses = 1, then HTML is saved only if data was found.
	
	This consitutes one thread of execution when we're in multi-threaded mode,
	as specified by DoSearch()."""

	try:
		# Query archive and save resulting HTML in a list of lines:
		try:
			if (debugState > 1):
				print("Starting query: %s" % archive.EncodeParams())
			htmlReceived = archive.QueryServer()
			# Search HTML text:
			(messageString, nDataFound) = archive.AnalyzeHTML(htmlReceived)
		except IOError as e:
			messageString = "I/O Error -- " + str(e) + "\n"
			htmlReceived = ""
			nDataFound = 0
		except KeyboardInterrupt:
			raise

		savedFile = 0
		if ( nDataFound > 0 ):
			# Run special searches, append output to messageString:
			messageString += archive.DoSpecialSearches(htmlReceived, nDataFound)
			# Save the HTML if user requested it:
			if ( saveSuccesses ):
				prefix = targetName.replace(' ', '_')
				saveFileName = prefix + "_" + archive.shortName + ".html"
				saveFile = open(saveFileName, 'w')
				saveFile.write(htmlReceived)
				saveFile.close()
				messageString += " [saved to %s" % saveFileName + "]"
				savedFile = 1

		# Print result:
		messageString = "\t" + archive.longName + ": " + messageString
		print(messageString)

		if ( debugState ):
			if ( not savedFile ):
				prefix = targetName.replace(' ', '_')
				saveFileName = prefix + "_" + archive.shortName + ".html"
				saveFile = open(saveFileName, 'w')
				saveFile.write(htmlReceived)
				saveFile.close()

	except KeyboardInterrupt:
		messageString = "\n   Keyboard interrupt -- %s search terminated!\n" % archive.shortName
		print(messageString)
		raise

	return messageString




def DoSearch( targetName, archiveList, debugSetting = 0, doThreading = True ):
	"""This is the general driver function called by main(); it can also be used
	from within the Python interpreter if the list of archives has been
	properly instantiated and set up.  This runs through the list of archives
	(step-by-step if threading is not used, spawning threads if it is."""

	if doThreading is False:
		print("Multithreading disabled...")
	
	try:
		for currentArchive in archiveList.GetArchives():
			if ( doThreading ):
				inputArgs = (currentArchive, targetName, debugSetting)
				newThread = threading.Thread(target=SearchOneArchive, args=inputArgs)
				newThread.setDaemon(1)
				newThread.start()
			else:
				SearchOneArchive(currentArchive, targetName, debugSetting)

		# Wait until all threads have finished before returning (remember, there is
		# always the main thread, so threading.activeCount() will always be >= 1):
		if ( doThreading ):
			while 1:
				if ( threading.activeCount() < 2 ):
					return

	except KeyboardInterrupt:
		print("KeyboardInterrupt detected --- terminating all searches!\n")
		sys.exit(1)

    


def PrintArchiveList():
	"""Basic function to list which archives we can search."""
	print("\nCurrently supported archives, short-hand names, and their user-interface URLs:\n")
	print(archive_list.ListArchives())
	print




def main(argv):
	# Set DEBUG = 1 to enable saving of *all* web pages returned:
	multipleSearches = False
	whichHSTarchive = kHST_ESO
	doAAT = True
	doSDSS = True
	doGetCoords = True   # do we need to do a Simbad coordinate lookup?
	                     # (default = yes because by default we search SDSS archive)
	archive_module_list = None   # None (default) = load the default set of archives


	# Set up target, etc, by parsing command-line:
	doCoordSearch = False     # are we searching by (user-supplied) coordinates?
	coordsList = NO_COORDS
	targetName = NO_NAME
	noTargetName = True
	noBoxSize = True

	usageString = "\n%prog \"target_name\" [box_size_in_arcmin] [options]\n"
	usageString += "%prog --coords=\"<ra-dec-coodrds>\" [box_size_in_arcmin] [options]\n"
	usageString += "\twhere \"target name\" is an astronomical source name suitable"
	usageString += " for coordinate lookup via SIMBAD (e.g., \"NGC 1000\")\n"
	usageString += "\tand \"<ra-dec-coodrds>\" is a string with RA and Dec in one of the following forms:"
	usageString += "\n\t\"hh mm ss dd mm ss\" or \"hh:mm:ss dd:mm:ss\" or \"XXhXXmXXs XXdXXmXXs\""
	usageString += " or \"dd.d dd.d\""
	parser = optparse.OptionParser(usage=usageString)

	parser.add_option("-v", "--version", action="store_true", dest="printVersion", 
						default=False, help="print version number and quit")
	parser.add_option("--archives","--list-archives", action="store_true", 
						dest="printArchives", default=False,
						help="list all archives which can be searched")
	parser.add_option("-d", "--debug", action="store_const", const=1, dest="DEBUG", default=0,
						help="debugging on (saves *all* returned HTML files)")
	parser.add_option("--debuglevel", type="int", dest="DEBUG", default=0,
						help="set higher levels of debugging")
	parser.add_option("-c", "--coords", type="str", dest="coords", default=None,
						help="\"hh mm ss dd mm ss\" : search on coordinates instead of target name")
	parser.add_option("--usearchive","--use-archive", type="str", dest="singleArchive", 
						default=None,
						help="search using only specified archive")
	parser.add_option("--skiparchives","--skip-archives", type="str", dest="skipArchives", default=None,
						help="comma-separated list of archives to NOT use in search")
# 	parser.add_option("--targetfile", type="str", dest="targetListFile", default=None,
# 					  help="list of target names to search for [DISABLED]")
# 	parser.add_option("--coordsfile", type="str", dest="coordsListFile", default=None,
# 					  help="list of coordinates to search for")
	parser.add_option("--sdss-spec-radius", type="float", dest="sdssSpecSearchRadius", default=None,
					  help="search radius in arcmin for SDSS spectroscopy (default = 0.1)")
	parser.add_option("--nosdss", "--noSDSS", action="store_false", dest="doSDSS", default=True,
					  help="ignore Sloan Digital Sky Survey")
	parser.add_option("--nothreads", action="store_false", dest="doThreading", default=True,
						help="turn multithreading off (slower, easier to halt)")
	parser.add_option("--timeout", type="float", dest="userTimeout", default=30,
						help="set connection timeout (default = 30 sec)")

	(options, args) = parser.parse_args(argv[1:])


	if (options.printVersion is True):
		print("\ntelarchive: version %s\n" % kVersionNumber)
		return 0
	elif (options.printArchives is True):
		PrintArchiveList()
		return 0
# 	elif (options.targetListFile is not None):
# 		if (not os.path.exists(options.targetListFile)):
# 			print "\n   Can't find file \"%s\" containing target name list\n" % options.targetListFile
# 			return -1
# 		multipleSearches = True
# 		noTargetName = False
# 		
# 		print "*** Sorry -- the mode for searching multiple targets is not yet working! ***"
# 		return 0

	if (options.singleArchive is not None):
		archive_module_list = [ module_list.shorthand_dict[options.singleArchive] ]
		if options.singleArchive != "sdss":
			options.doSDSS = False
	
	if (options.skipArchives is not None):
		skipList = options.skipArchives.split(",")
		msg = "Skipping the following archives: "
		for name in skipList[:-1]:
			msg += name + ", "
		msg += skipList[-1]
		print(msg)
		defaultFullList = module_list.archive_shortnames
		archive_module_list = [ module_list.shorthand_dict[archiveName] 
						for archiveName in defaultFullList if archiveName not in skipList ]
		if "sdss_combined_archive" not in archive_module_list:
			options.doSDSS = False
	
	if (options.coords is not None):
		doCoordSearch = True
		doGetCoords = False
		try:
			coordsList = utils.ProcessCoords(options.coords, decimalDegreesOK=True, 
												convertDecimalDegrees=True)
			targetName = "%s %s" % (coordsList[0], coordsList[1])
		except utils.CoordinateError as e:
			newmsg = "*** Problem with coordinate string \"%s\": ***\n" % e
			newmsg += str(e) + "\n"
			print(newmsg)
			return -2
		


	for argument in args:
		if (noTargetName and (not doCoordSearch)):
			targetName = argument
			noTargetName = False
		elif ( noBoxSize ):
			searchBoxSize = float(argument)
			noBoxSize = 0
			if ( searchBoxSize > MAX_BOXSIZE ):
				print("\n%f arc minutes is too large a search radius: it'll take forever!" 
					  % searchBoxSize)
				print("Try something smaller than %d arcmin." % MAX_BOXSIZE)
				print("(Did you forget to put quotation marks around the target name?)\n")
				return -2
			if ( searchBoxSize < 0.0 ):
				print("\nSearch box size should be a positive number!\n")
				return -1



	if ( (not doCoordSearch) and noTargetName ):
		print("Please enter a target name to search for: ", end="")
		targetName = sys.stdin.readline()
		# chop off newline at end of string:
		targetName = targetName[:len(targetName) - 1]
	if ( noBoxSize ):
		searchBoxSize = archive_list.DEFAULT_BOXSIZE


	# Instantiate object holding array of individual-archive objects:
	theArchiveList = archive_list.ArchiveList( targetName, coordsList, searchBoxSize,
											 whichHSTarchive, doAAT, options.doSDSS,
											 options.sdssSpecSearchRadius, archive_module_list )

	if options.userTimeout > 0:
		theArchiveList.InsertTimeout(options.userTimeout)
	
	# THE FOLLOWING CODE IS NOT YET WORKING!
	if (multipleSearches):
		targetLines = open(options.targetListFile).readlines()
		for currentLine in targetLines:
			if ( (currentLine[0] == "#") or (currentLine.strip() == "") ):
				# skip lines beginning with '#" or which are empty
				continue
			currentTarget = currentLine.strip()
			if (not doCoordSearch):   # list of target *names*
				messageString = "Searching archives for %s" % currentTarget
			else:
				messageString = "Searching archives for coordinates %s" % currentTarget
			messageString = messageString + ", with search box = "
			messageString = messageString + "%4.1f arcmin..." % searchBoxSize
			print(messageString)
			
			# Set up for searching on names or on coordinates
			if (not doCoordSearch) and (not doGetCoords):
				theArchiveList.InsertName(targetName)
				finalTargetName = targetName
			else:
				if doGetCoords:
					# user supplied names, but we need to do search using coordinates
					print("\n\nFetching coordinates for %s..." % targetName)
					coordsList = FetchCoordinates(targetName)
				else:
					# user supplied coordinates
					try:
						coordsList = utils.ProcessCoords(currentTarget)
					except utils.CoordinateError as e:
						newmsg = "*** Problem with coordinate string \"%s\"\n" % str(e) + "\n"
						print(newmsg)
						sys.exit(2)
				theArchiveList.InsertCoords(coordsList)
				finalTargetName = coordsList[0] + coordsList[1]
			DoSearch( finalTargetName, theArchiveList, options.DEBUG, options.doThreading )
			
			return 1


	else:
		if ( doGetCoords ):
			coordsList = FetchCoordinates(targetName)
			theArchiveList.InsertCoords(coordsList)
			messageString = "\nSearching archives for %s (RA = %s, dec = %s)" % (targetName,
								coordsList[0], coordsList[1])
		else:
			messageString =	"\nSearching archives for "	+ targetName
		finalTargetName = targetName

		messageString = messageString + ", with search box = "
		messageString = messageString + "%4.1f arcmin..." % searchBoxSize
		print(messageString)

		DoSearch( finalTargetName, theArchiveList, options.DEBUG, options.doThreading )
		
		return 1
#	print("Done!\n")



if __name__ == '__main__':
	main(sys.argv)
