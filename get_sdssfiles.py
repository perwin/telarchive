# Code to help in retrieving images from SDSS; mainly for use in fetchsdss.py
#
# NEW INTERFACE:
#    Convert archive reply (+ user request) into list of (url, filename) pairs:
#       list_of_url-filename_pairs = MakeURLFilePairs(dataStringList, list_of_filters, tsField?, jpeg?)
#
#    Fetch files:
#       outcome = F2(list_of_url-filename_pairs, destinationDir)


import sys, io

if sys.version_info[0] > 2:
	usingPython2 = False
	import urllib.request, urllib.parse, urllib.error
	from urllib.parse import urlencode
	from urllib.request import Request
	from urllib.request import urlopen
else:
	usingPython2 = True
	import urllib
	from urllib import urlencode
	from urllib2 import Request
	from urllib2 import urlopen
import archive_analyze


# Templates
baseURLTemplate = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/corr/%(camcol)d/fpC-%(run)06d-%(filter)s%(camcol)d-%(field)04d.fit.gz"
baseTemplate = "fpC-%(run)06d-%(filter)s%(camcol)d-%(field)04d.fit.gz"
altTemplate = "%(rootname)s%(filter)s_%(run)d-%(field)d.fits.gz"
altTemplate_bare = "%(rootname)s%(filter)s.fits.gz"
# for (run, camcol, field = 1302 3 248)
# http://dr9.sdss3.org/sas/dr9/boss/photoObj/frames/301/1302/3/frame-g-001302-3-0248.fits.bz2
baseURLTemplate_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/%(run)d/%(camcol)d/frame-%(filter)s-%(run)06d-%(camcol)d-%(field)04d.fits.bz2"
baseTemplate_dr12 = "frame-%(filter)s-%(run)06d-%(camcol)d-%(field)04d.fits.bz2"
altTemplate_dr12 = "%(rootname)s%(filter)s_dr12_%(run)d-%(field)d.fits.bz2"
altTemplate_bare_dr12 = "%(rootname)s%(filter)s.fits.bz2"

baseURLTemplates = {"dr7": baseURLTemplate, "dr12": baseURLTemplate_dr12}
baseTemplates = {"dr7": baseTemplate, "dr12": baseTemplate_dr12}
altTemplates = {"dr7": altTemplate, "dr12": altTemplate_dr12}
altTemplates_bare = {"dr7": altTemplate_bare, "dr12": altTemplate_bare_dr12}

tsFieldURLTemplate = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/calibChunks/%(camcol)d/tsField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit"
tsFileTemplate = "tsField-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d.fit"
alt_tsFileTemplate = "tsField_%(rootname)s_%(run)d-%(field)d.fit"
alt_tsFileTemplate_bare = "tsField_%(rootname)s.fit"
jpegURLTemplate = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/Zoom/%(camcol)d/fpC-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d-%(jpeg_size)s.jpeg"
jpegTemplate = "fpC-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d-%(jpeg_size)s.jpeg"
alt_jpegTemplate = "%(rootname)s_%(run)d-%(field)d.jpeg"
alt_jpegTemplate_bare = "%(rootname)s.jpeg"

spectrumURLTemplate = "http://data.sdss3.org/sas/dr12/sdss/spectro/redux/26/spectra/lite/%(plate)04d/spec-%(plate)04d-%(mjd)d-%(fiber)04d.fits"
spectrumTemplate = "spec-%(plate)04d-%(mjd)d-%(fiber)04d.fits"



def MakeFieldDict( fieldText ):
	"""Given an input string of the form "run rerun camcol field" (e.g.,
	"1345 41 3 233"), this function returns a dictionary of the form {'run': #,
	'rerun': #, 'camcol': #, 'field' #, 'filter': None, 'jpeg_size': None}, where
	# = corresponding value as integer.  (The 'filter' and 'jpeg_size' fields are
	meant to be filled in later.)
	
	If the input fieldText is of the form "run camcol field" (for DR12), then
	the dictionary is the same, except that 'camcol' = None and 'dr12' = True.
	"""
	
	pp = fieldText.split()
	if len(pp) == 4:
		# DR7 "run rerun camcol field"
		newDict = {"run": int(pp[0]), "rerun": int(pp[1]), "camcol": int(pp[2]),
					"field": int(pp[3]), "filter": None, "jpeg_size": None,
					"dr12": False}
	else:
		# DR12 "run camcol field"
		newDict = {"run": int(pp[0]), "rerun": None, "camcol": int(pp[1]),
					"field": int(pp[2]), "filter": None, "jpeg_size": None,
					"dr12": True}
	return newDict


def MakeSpectrumDict( fieldText ):
	"""Given an input string of the form "plate mjd fiber" (e.g., "908 52373 302"),
	this function returns a dictionary of the form {'plate': #, 'mjd': #, 'fiber': #},
	where # = corresponding value as integer. 
	"""
	
	pp = fieldText.split()
	newDict = {"plate": int(pp[0]), "mjd": int(pp[1]), "fiber": int(pp[2])}
	return newDict


def MakeURLFilePair( singleFieldDict, filterName, filenameRoot, noSuffixFlag=False ):
	"""Returns a tuple of (url_for_image, local_filename) for an SDSS FITS
	image.  The filename will have the form
		filenameRoot<f>_<run>-<field>.fits.gz
	or (if noSuffixFlag=True) just:
		filenameRoot<f>.fits.gz
	UNLESS filenameRoot = None, in which case the original SDSS
	name will be used."""
	
	singleFieldDict['filter'] = filterName
	if singleFieldDict['dr12'] is True:
		dr = "dr12"
	else:
		dr = "dr7"
	
	newURL = baseURLTemplates[dr] % singleFieldDict
	if filenameRoot is None:
		newFilename = baseTemplates[dr] % singleFieldDict
	else:
		singleFieldDict["rootname"] = filenameRoot
		if noSuffixFlag is True:
			newFilename = altTemplates_bare[dr] % singleFieldDict
		else:
			newFilename = altTemplates[dr] % singleFieldDict
	return (newURL, newFilename)


def Make_tsField_Pair( singleFieldDict, filenameRoot=None, noSuffixFlag=False ):
	"""Returns a tuple of (url, local_filename) for the tsField FITS table for
	the field specified by singleFieldDict.
	By default, we save the table under its original SDSS name
	(tsField-<run>-<camcol>-<rerun>-<field>.fit), *unless* filenameRoot
	is specified, in which case the file will be saved as
		tsField_filenameRoot_<run>-<field>.fit"""
	
	newURL = tsFieldURLTemplate % singleFieldDict
	if filenameRoot is None:
		newFilename = tsFileTemplate % singleFieldDict
	else:
		singleFieldDict["rootname"] = filenameRoot
		if noSuffixFlag is True:
			newFilename = alt_tsFileTemplate_bare % singleFieldDict
		else:
			newFilename = alt_tsFileTemplate % singleFieldDict
		#newFilename = "tsField_%s_%d-%d.fit" % (filenameRoot, singleFieldDict["run"], singleFieldDict["field"])
	return (newURL, newFilename)


def MakeJPEGPair( singleFieldDict, filenameRoot=None, jpegSize="z00", noSuffixFlag=False ):
	"""Returns a tuple of (url, local_filename) for a color JPEG image of
	the field specified by singleFieldDict.
	By default, we save the table under its original SDSS name
	(fpC-<run>-<camcol>-<rerun>-<field>-<zoom>.jpeg), *unless* filenameRoot
	is specified, in which case the file will be saved as
		filenameRoot_<run>-<field>.jpeg
	
	jpegSize can one of the following values:
		["z00", "z05", "z10", "z15", "z20", "z25", "z30"],
	which specify *decreasing* image sizes (from 1984x1361 pixels for "z00"
	down to 248x170 pixels for "z30").  This is the same as <zoom> in the
	default SDSS name described above.
	"""
	
	singleFieldDict['jpeg_size'] = jpegSize
	newURL = jpegURLTemplate % singleFieldDict
	if filenameRoot is None:
		newFilename = jpegTemplate % singleFieldDict
	else:
		singleFieldDict["rootname"] = filenameRoot
		if noSuffixFlag is True:
			newFilename = alt_jpegTemplate_bare % singleFieldDict
		else:
			#newFilename = "%s_%d-%d.jpeg" % (filenameRoot, singleFieldDict["run"], singleFieldDict["field"])
			newFilename = alt_jpegTemplate % singleFieldDict
	return (newURL, newFilename)


def MakeFieldList( fieldSpecification, filterList, filenameRoot, noSuffixFlag=False ):
	"""Returns a list of (url, filename) tuples for FITS images of one or
	more SDSS fields, stepping through the filters in filterList.
	   For DR7, filenames will have the form filenameRoot<f>_<run>-<field>.fits.gz
	(where <f> = filter), e.g., n2950r_3705-69.fits.gz -- EXCEPT that if
	filenameRoot = None, the filenames will be the same as their SDSS
	originals.
	   For DR12, filenames will have the form filenameRoot<f>_<run>-<field>.fits.bz2
	(where <f> = filter), e.g., n2859r_1302-248.fits.bz2 -- EXCEPT that if
	filenameRoot = None, the filenames will be the same as their SDSS
	originals.
	   fieldSpecification should be either a single-field dictionary (e.g.,
	as produced by MakeFieldDict) or a list of single-field dictionaries.
	
	noSuffixFlag = True --> saved filenames will *not* have <run>-<field> as part
	of their names.
	"""
	
	if isinstance(fieldSpecification, list):
		fieldList = fieldSpecification
	else:
		fieldList = [fieldSpecification]
	newList = [ MakeURLFilePair(fieldDict, thisFilter, filenameRoot, noSuffixFlag) for
				fieldDict in fieldList for thisFilter in filterList  ]
	return newList


def MakeSpectrumList( spectrumSpecification, filenameRoot ):
	"""Returns a list of (url, filename) tuples for FITS spectra.
	   filenames will have the form filenameRoot_spec-<plate>-<mjd>-<fiber>.fits
	EXCEPT that if filenameRoot = None, the filenames will be the same as their SDSS
	originals.
	   spectrumSpecification should be either a single-spectrum dictionary (e.g.,
	as produced by MakeSpectrumDict) or a list of single-spectrum dictionaries.
	"""
	
	if isinstance(spectrumSpecification, list):
		specList = spectrumSpecification
	else:
		specList = [spectrumSpecification]
	newList = []
	for specDict in specList:
		url = spectrumURLTemplate % specDict
		newFilename = spectrumTemplate % specDict
		if filenameRoot is not None:
			newFilename = filenameRoot + "_" + newFilename
		newList.append( (url, newFilename) )
	return newList


def MakeURLFilePairs( fieldStringList, filterString, filenameRoot, getFITS=True,
						get_tsField=True, get_JPEG=False, jpegSize="z00", noSuffixFlag=False ):
	"""Given a list of SDSS files (in the form ["run rerun camcol field", ...]), a
	set of filters (e.g., "ugriz" or a subset thereof), a root filename (= None for to
	signal using original SDSS filenames), and True/False flags signalling whether to
	retrive associated tsField and JPEG files, we return a list of (URL, filename) tuples
	for use in retrieving and saving SDSS files.
	
	noSuffixFlag = True --> indicates that filename should *not* have <run>-<field> as part
	of the name (passed on to MakeFieldList).
	"""
	
	fieldDictList = [ MakeFieldDict(fieldString) for fieldString in fieldStringList ]
	
	if getFITS:
		urlFilePairList = MakeFieldList(fieldDictList, filterString, filenameRoot, noSuffixFlag)
	else:
		urlFilePairList = []
	if get_tsField:
		for fieldDict in fieldDictList:
			urlFilePairList.append(Make_tsField_Pair(fieldDict, filenameRoot, noSuffixFlag))
	if get_JPEG:
		for fieldDict in fieldDictList:
			urlFilePairList.append(MakeJPEGPair(fieldDict, filenameRoot, jpegSize, noSuffixFlag))
	
	return urlFilePairList


def MakeSpectrumURLFilePairs( specStringList, filenameRoot ):
	"""Given a list of SDSS spectra (in the form ["plate mjd fiber", ...]) and a root 
	filename (= None for to signal using original SDSS filenames) we return a list of 
	(URL, filename) tuples for use in retrieving and saving SDSS spectra.
	"""
	
	spectrumDictList = [ MakeSpectrumDict(specString) for specString in specStringList ]	
	urlFilePairList = MakeSpectrumList(spectrumDictList, filenameRoot)
	
	return urlFilePairList



def SaveSIOtoFile( stringFileObj, filename, baseDir ):
	"""Transfer (binary) data in a BytesIO object to a real (filesystem) file."""
	if baseDir[-1] != "/":
		baseDir += "/"
	outputPath = baseDir + filename
	outf = open(outputPath, 'wb')
	outf.write(stringFileObj.getvalue())
	outf.close()


def GetHeader( urlFilePair ):
	"""Code for testing URL access: we contact the url in urlFilePair[0]
	and return the header (mimetools.Message object representing the 
	server-supplied metadata).
	"""
	
	# open connection to server and get info about reply
	theURL = urlFilePair[0]
	urlf = urlopen(theURL)
	infoHeader = urlf.info()
	urlf.close()
	return infoHeader


def GetAndSaveFile( urlFilePair, baseDir, checkOutput=True ):
	"""Retrieve data from the url in urlFilePair[0] and save it in the
	file specified by baseDir+urlFilePair[1].
	   This function checks the return header and saves the data *only*
	if the server told us that it was either a .gz or .fits file.
	   To turn off checking of returned-data type, set checkOutput=False.
	   Returns tuple of (status, header, sioFile), where status = True for
	successful retrieval of FITS file and status = False for failure; header
	is the mimetools.Message object representing the server-supplied metadata
	about the reply, which can be checked for more information; and sioFile is
	the BytesIO file object containing the transmitted data (e.g., for reading
	possible HTML error messages)."""
	
	# open connection to server and get info about reply
	theURL = urlFilePair[0]
	urlf = urlopen(theURL)
	infoHeader = urlf.info()

	# create BytesIO file to store data temporarily
	sioFile = io.BytesIO()
	# read the data, looping till we get nothing further (code swiped
	# and modified from urllib.URLopener.retrieve, Python 2.5 version)
	blockSize = 1024*8
	while True:
		block = urlf.read(blockSize)
		if len(block) == 0:
			break
		sioFile.write(block)
	urlf.close()

	# Save results to file *only* if server actually sent us .fit or .fit.gz
	# [10 April 2010: OK, we're making checking optional because the SDSS DAS
	# server seems to be classifying tsField files as "text/plain", but with
	# variable encoding.]
	status = True
	if (checkOutput and infoHeader["content-type"] not in ["application/x-gzip", "image/x-fits", "image/jpeg"]):
			print(infoHeader["content-type"])
			status = False
	if (status is True):
		# save data to a real file on the filesystem:
		SaveSIOtoFile( sioFile, urlFilePair[1], baseDir )
	return (status, infoHeader, sioFile)



# New JPEG access:
# SDSS Run 125, Rerun 40, Camcol 1, Field 321
# http://das.sdss.org/imaging/125/40/Zoom/1/fpC-000125-1-40-0321-z00.jpeg
# jpegFieldURLTemplate = "http://das.sdss.org/imaging/%(run)d/%(rerun)d/Zoom/%(camcol)d/fpC-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d-%3s.jpeg
# 
# z00 = full scale = 1984x1361 pix
# z05 = 1388x952 pix
# z10 = 992x680 pix
# z15 = 694x476 pix
# z20 = 496x340 pix
# z25 = 347x238 pix
# z30 = 248x170 pix
# 
# fpC-003355-1-40-0121-z30.jpeg
# jpegTemplate = "fpC-%(run)06d-%(camcol)d-%(rerun)d-%(field)04d-%3s.jpeg"

# DR9 spectrum FITS file access:
# http://dr9.sdss3.org/sas/dr9/DETECTOR/spectro/redux/RUN2D/spectra/lite/PLATE4/spec-PLATE4-MJD-FIBERID4.fits
# where DETECTOR = "sdss" or "boss", RUN2D = reduction number, 
#    for BOSS: v5_4_45; for SDSS Legacy: 26 (standard DR7 reduction); for SDSS stellar cluster plates: 103;
#    for SDSS SEGUE-2: 104
# 'PLATE4' should be replaced by the zero-padded, 4-digit plate number, 
# 'MJD' should be replaced by the MJD number 
# and 'FIBERID4' should be replaced by the zero-padded, 4-digit fiber number.
#
# BOSS spectra:
# http://data.sdss3.org/sas/dr9/boss/spectro/redux/v5_4_45/spectra/
# SDSS Legacy spectra:
# http://data.sdss3.org/sas/dr9/sdss/spectro/redux/26/spectra/lite/0908/spec-0908-52373-0302.fits

# DR9 imaging data access:
# http://dr9.sdss3.org/sas/dr9/boss/photoObj/frames/RERUN/RUN/CAMCOL/frame-FILTER-RUN6-CAMCOL-FIELD.fits.bz2
# where 'RERUN' should be replaced by the appropriate imaging reduction
# number (currently '301'), 'RUN' should be replaced by the run number,
# 'CAMCOL' should be replaced by the single-digit camcol number (1-6),
# 'FILTER' should be replaced by the filter name ('u', 'g', 'r', 'i',
# 'z'), 'RUN6' should be replaced by the zero-padded, 6-digit run number
# and 'FIELD' should be replaced by the zero-padded, 4-digit field
# number.

# for (run, camcol, field = 1302 3 248)
# http://dr9.sdss3.org/sas/dr9/boss/photoObj/frames/301/1302/3/frame-g-001302-3-0248.fits.bz2

