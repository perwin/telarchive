# FILE: archive_analyze.py

# Some preliminary suport for Spitzer archive included, but it's not working
# properly yet, so for now spitzer_archive.py will overrived the AnalyzeHTML
# method in basic_archive.py.

#    Utility stuff for archive_search.py, moved into a separate file to keep
# things cleanly separated.  This file has code dealing with searching the
# HTML text an archive sends back.

import re
from utils import SearchError


NO_NAME = "NO NAME"

# These are searches to find the text wherein an archive tells us how many
# data sets it found.  They are set up so that the numeral is stored in
# group #1 of the result.
findWereRetrieved = re.compile(r"""of (\d+)(| record| records) were retrieved""")
findNOAORecords = re.compile(r"(\d+)(| record| records) found.")
findSmokaRecords = re.compile(r"(\d+)(| frame| frames) were found.")
findSpitzerRecords = re.compile(r"#\s+(\d+)\s+ \(Records Found\)")
findSTScIRecords = re.compile(r"(\d+) records \(\d+ proprietary\) returned")
findMASTRecords = re.compile(r"(\d+) observations\s+found")
findESORecords = re.compile(r"""of \s+ (\d+)(| record| records)""", re.VERBOSE)
# findESORecords = re.compile(r"""A \s+ total \s+ of \s+ (\d+)(| record| records)|
# A \s+ maximum \s+ of (\d+)(| record| records)""", re.VERBOSE)
#A maximum of 5000 records were found matching the provided criteria - any remaining rows were ignored.

#   Check for errors in connecting to SIMBAD, which occasionally happens:
findSIMBADError = re.compile(r"ERROR connecting to SIMBAD")

#   Look for the standard "No data returned !" text:
text = r"No data returned|"
text = text + r"No records found matching query.|"   # STScI-HST message
text = text + r"0 records found.|"   # NOAO message
text = text + r"No matching frame were found."   # SMOKA message
findNoDataReturned = re.compile(text)

#   Error message from the database, so far only seen at CFHT:
findMiscError = re.compile(r"An error has occurred")

#   Check for variations on the "A total of X were retrieved" or
# "a total of X records were retrieved" phrase and save it if found.
text = r"A total of \d+ were retrieved|"
text += r"A total of \d+ records were retrieved|"
text += r"A total of \d+ records were found|"
text += r"A <b>maximum</b> of \d+ were retrieved|"
text += r"A <b>maximum</b> of \d+ records were retrieved|"
text += r"A total of \d+ were found matching the provided criteria|"
text += r"A <b>maximum</b> of \d+ were found matching the provided criteria|"
text += r"A maximum of \d+ records were found matching the provided criteria|"  # ESO for > 5000 records
text += r"\d+ records \(\d+ proprietary\) returned|"
text += r"[1-9](\d)* records found.|"   # NOAO (matches if > 0 found)
text += r"\d+ frames were found.|"   # Smoka
text += r"\d+ observations\s+found|"   # MAST
text += r"#\s+\d+\s+ \(Records Found\)"   # Spitzer
text += r"A total of \d+ were found"
findNReturned = re.compile(text)

# WARNING -- do *not* use "re.VERBOSE" for the following -- it screws up the recognition
# of spaces!
text = r"A <b>maximum</b> of \d+ were retrieved|"
text += r"A <b>maximum</b> of \d+ records were retrieved|"
text += r"A <b>maximum</b> of \d+ were found matching the provided criteria|"
text += r"A maximum of \d+ records were found matching the provided criteria"
findLimit = re.compile(text)

#   The annoying tendency of some archives to return a completely
# different kind of page if only *one* exposure or "association" was
# found necessitates the findOneReturned search:
#   The final case ("Data Product Information") is for the ESO archive
text = r"Association:|Target Ra, Dec|Exposure ID|Date_obs|aat_id|Data Product Information"
findOneReturned = re.compile(text)

#   Checks to see if the proxy server sent us a "no connection" message:
failedConnection = re.compile(r"The requested URL could not be retrieved")



def CountDataSets( dataSetsText ):
	# check for standard message:
	nRetrieved = findWereRetrieved.search(dataSetsText)
	if nRetrieved:
		# extract actual number and convert to integer
		numberFound = int(nRetrieved.group(1))
	else:
		# check for various archive-specific formulations:
		esorec = findESORecords.search(dataSetsText)
		noaorec = findNOAORecords.search(dataSetsText)
		smokarec = findSmokaRecords.search(dataSetsText)
		spitzerrec = findSpitzerRecords.search(dataSetsText)
		strec = findSTScIRecords.search(dataSetsText)
		# special mode for MAST (multiple lines with "# observations found",
		# one per mission
		mastrec = findMASTRecords.findall(dataSetsText)
		if esorec:
			# extract number and convert to integer
			numberFound = int(esorec.groups(1)[0])
		elif noaorec:
			# extract number and convert to integer
			numberFound = int(noaorec.groups(1)[0])
		elif smokarec:
			# extract number and convert to integer
			numberFound = int(smokarec.groups(1)[0])
		elif spitzerrec:
			# extract number and convert to integer
			numberFound = int(spitzerrec.groups(1)[0])
		elif strec:
			# extract number and convert to integer
			numberFound = int(strec.groups(1)[0])
		elif mastrec:
			numberFound = sum([int(n) for n in mastrec])
		else:
			print("Unable to find number of records retrieved")
			numberFound = 0
	return numberFound


def AnalyzeHTML( htmlText ):
	"""Function which searches a big blob of HTML text.  We look for various text
	fragments: signs of valid or invalid reply, did the archive find data or not,
	did the archive get valid coordinates from Simbad or NED, etc.  Uses the
	regular-expression objects defined in TextSearch object (see above); passed
	as a parameter since the object name has to be provided from elsewhere.
	"""
	# Default boolean flags:
	connectionMade = 1       # successfully connected to archive web server
	validReply = 0           # we got a genuine reply from the web server
	noDataExists = 0         # archive did proper search, found no data
	nDataFound = 0           # OUR flag indicating whether archive found data, and if so,
	                         #    how *many* data sets
	badName = 0              # archive complained that Simbad couldn't find target
	simbadError = 0          # archive complained about some mysterious error from Simbad
	miscError = 0            # archive said, "An error has occurred" (big help, eh?)
	nSetsString = "No information about # datasets found"
	limitReached = False

	# Search the text, try to figure out if we got a valid result,
	# and if any data exists:
	# First, look for evidence that the archive found data (even if it was a mistake):
	dataSets = findNReturned.search(htmlText)
	if ( dataSets ):
		dataSetsText = dataSets.group()
		nDataFound = CountDataSets(htmlText)
		if findLimit.search(htmlText):
			limitReached = True
		validReply = 1
		if limitReached:
			nSetsString = "at least %d observations found" % nDataFound
		else:
			nSetsString = "%d observations found" % nDataFound
	else:
		oneDataSet = findOneReturned.search(htmlText)
		if ( oneDataSet ):
			nDataFound = 1
			validReply = 1
			nSetsString = "One observation/association"

	
	# Next, check to see if there was a screw-up of some kind.  This includes
	# cases where an archive gets an "object doesn't exist" message from Simbad,
	# and then goes ahead and searches anyway (using default Vernal Equinox
	# position).  In those cases, the archive will say it found data, but it's
	# WRONG (so we look for clues that this might have happened).
	try:
		if ( findNoDataReturned.search(htmlText) ):
			# The archive said, "Found no data"
			validReply = 1
			nDataFound = 0
		if ( findSIMBADError.search(htmlText) ):
			# The archive got a mysterious error message from Simbad
			validReply = 1
			simbadError = 1
			nDataFound = 0
			raise SearchError( "Archive got error message from Simbad" )
		if ( findMiscError.search(htmlText) ):
			# The archive said, helpfully, "An error has occured"
			validReply = 1
			miscError = 1
			nDataFound = 0
			raise SearchError( "Archive said \"An error has occured\"" )
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0
			nDataFound = 0
			raise SearchError( "Failed to connect with archive web server" )


		if ( nDataFound > 0 ):
			messageString = "Data exists! " + "(" + nSetsString + ")"
		else:
			messageString = "No data found."
		
	except SearchError as e:
		messageString = e.value
		nDataFound = 0

	return (messageString, nDataFound)


# Helper function to handle looking for connection errors, etc.
def CheckForError( htmlText ):
	# Default boolean flags:
	connectionMade = 1       # successfully connected to archive web server
	validReply = 0           # we got a genuine reply from the web server
	noDataExists = 0         # archive did proper search, found no data
	badName = 0              # archive complained that Simbad couldn't find target
	simbadError = 0          # archive complained about some mysterious error from Simbad
	miscError = 0            # archive said, "An error has occurred" (big help, eh?)
	nSetsString = "No information about # datasets found"

	messageString = ""       # default for no problems

	# Check to see if there was a screw-up of some kind.  This includes
	# cases where an archive gets an "object doesn't exist" message from Simbad,
	# and then goes ahead and searches anyway (using default Vernal Equinox
	# position).  In those cases, the archive will say it found data, but it's
	# WRONG (so we look for clues that this might have happened).
	try:
		if ( findSIMBADError.search(htmlText) ):
			# The archive got a mysterious error message from Simbad
			validReply = 1
			simbadError = 1
			raise SearchError( "Archive got error message from Simbad" )
		if ( findMiscError.search(htmlText) ):
			# The archive said, helpfully, "An error has occured"
			validReply = 1
			miscError = 1
			raise SearchError( "Archive said \"An error has occured\"" )
		if ( failedConnection.search(htmlText) ):
			# Oops, couldn't connect to archive web server
			connectionMade = 0
			validReply = 0
			raise SearchError( "Failed to connect with archive web server" )
		
	except SearchError as e:
		messageString = e.value

	return (messageString)


