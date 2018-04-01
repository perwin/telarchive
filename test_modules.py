# Some code to simply testing of new or modified archive modules,
# as well as to help in developing such modules (i.e., urlStringToDict
# can help in preparing a proper DICT variable in an archive module).

# Examples of use within a Python session -- module for fetchsdss
#
# coordsList = ["ra_deg.dddd", "dec_deg.dddd"]
#
# >>> reload(newmodule)
# >>> text = DoFetchSDSS(MakeArchive(newmodule), coordsList)
# >>> SaveText(text)
# [re-open defaultFile in web browser or text editor]
#
# SaveText(text)
#
#
# Example of testing an archive module's HTML parsing:
# >>> reload(newmodule)
# >>> theArchive = MakeArchive(newmodule)
# >>> theArchive.AnalyzeHTML(someHTML)
#
# or, drilling down to archive_analyze.AnalyzeHTML:
# >>> archive_analyze.AnalyzeHTML(someHTML)

defaultDir = "/Beleriand/dev/telarchive_working/testing/"
defaultFile = defaultDir + "junk.html"


def urlStringToDict( urlString ):
	"""Given a partial URL string encoding submitted/posted options of
	the form '"object=&resolver=SIMBAD&coordsys=Equatrial&equinox=J2000',
	return a parsed dictionary, where the LH part of each '=' pair is
	a key and the RH side is a value associated with that key.
	
	Suggested use: Make a query to an archive using Firefox + Live HTTP Headers;
	copy the resulting partial URL string from the Live HTTP Headers window,
	use it as input to this function.  Then take the resulting dictionary as
	the template for the DICT variable in an archive module.
	"""
	pp = urlString.split("&")
	newDict = {}
	for p in pp:
		ppp = p.split("=")
		newDict[ppp[0]] = ppp[1]
	return newDict

	
def SaveText( htmlText, filename=defaultFile ):
	outf = open(filename, 'w')
	# save as bytes (assume UTF-8) to handle cases where archives send us
	# non-ASCII text (e.g., SDSS SAS uses en-dashes in column titles)
	outf.write(htmlText.encode('utf-8'))
	outf.close()

	
def MakeArchive(archive_module, targetName=None, coordinates=None, boxSize=None):
	searchServer = archive_module.MakeArchive()
	if targetName is not None:
		currentArchive.InsertTarget(name)
	if coordinates is not None:
		currentArchive.InsertCoordinates(coords)
	if boxSize is not None:
		currentArchive.InsertBoxSize(boxString)
	return searchServer


def GetHTML( currentArchive, targetName=None, coordinates=None ):
	if targetName is not None:
		currentArchive.InsertTarget(name)
	elif coordinates is not None:
		currentArchive.InsertCoordinates(coords)
	htmlText = currentArchive.QueryServer()
	return htmlText


def DoFetchSDSS(searchServer, coordsList, analyze=False):
	searchServer.SetMode("fetchsdss")
	searchServer.InsertCoordinates(coordsList)
	htmlReceived = searchServer.QueryServer()
	if analyze is True:
		(messageString, nDataFound) = searchServer.AnalyzeHTML(htmlReceived)
		print messageString
	return htmlReceived


