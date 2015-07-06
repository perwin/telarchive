#! /usr/bin/env python

"""Unit test for get_sdssfiles.py"""

import get_sdssfiles
import unittest


# Unit tests use one of the NGC 2859 (RA, Dec = 141.077212   34.513490)
# fields: run=3704, rerun=40, camcol=6, field=69
# http://das.sdss.org/www/cgi-bin/segments?LIST=RW3c5c&RUN=3704&RERUN=40&CAMCOL=6

singleField = (3704, 40, 6, 69)
singleFieldString = "3704 40 6 69"
singleFieldDict = {"run": 3704, "rerun": 40, "camcol": 6, "field": 69, "filter": None,
					"jpeg_size": None, "dr12": False}
singleFieldDict_nochange = {"run": 3704, "rerun": 40, "camcol": 6, "field": 69, 
							"filter": None, "jpeg_size": None, "dr12": False}
singleField_dr12 = (1302, 3, 248)
singleFieldString_dr12 = "1302 3 248"
singleFieldDict_dr12 = {"run": 1302, "rerun": None, "camcol": 3, "field": 248,
							"filter": None, "jpeg_size": None, "dr12": True}
singleFieldDict_nochange_dr12 = {"run": 1302, "rerun": None, "camcol": 3, "field": 248,
							"filter": None, "jpeg_size": None, "dr12": True}
singleSpectrumString = "908 52373 302"
singleSpectrumDict = {"plate": 908, "mjd": 52373, "fiber": 302}
singleFieldURL = "http://das.sdss.org/imaging/3704/40/corr/6/fpC-003704-i6-0069.fit.gz"
singleFieldfname = "n2859i_3704-69.fits.gz"
singleFieldConversion = (singleFieldURL, singleFieldfname)
singleFieldfname_bare = "n2859i.fits.gz"
singleFieldConversion_bare = (singleFieldURL, singleFieldfname_bare)
defaultFname = "fpC-003704-i6-0069.fit.gz"
defaultFilenameConversion = (singleFieldURL, defaultFname)
#singleFieldURL_dr9 = "http://dr9.sdss3.org/sas/dr9/boss/photoObj/frames/301/1302/3/frame-i-001302-3-0248.fits.bz2"
singleFieldURL_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/1302/3/frame-i-001302-3-0248.fits.bz2"
singleFieldfname_dr12 = "n2859i_dr12_1302-248.fits.bz2"
singleFieldConversion_dr12 = (singleFieldURL_dr12, singleFieldfname_dr12)
singleFieldfname_bare_dr12 = "n2859i.fits.bz2"
singleFieldConversion_bare_dr12 = (singleFieldURL_dr12, singleFieldfname_bare_dr12)
defaultFname_dr12 = "frame-i-001302-3-0248.fits.bz2"
defaultFilenameConversion_dr12 = (singleFieldURL_dr12, defaultFname_dr12)

tsFieldURL = "http://das.sdss.org/imaging/3704/40/calibChunks/6/tsField-003704-6-40-0069.fit"
tsField_default_fname = "tsField-003704-6-40-0069.fit"
tsFieldfname = "tsField_n2859_3704-69.fit"
tsFieldfname_bare = "tsField_n2859.fit"
default_tsFieldConversion = (tsFieldURL, tsField_default_fname)
tsFieldConversion = (tsFieldURL, tsFieldfname)
tsFieldConversion_bare = (tsFieldURL, tsFieldfname_bare)

# special test for correct handling of tsField name in case of shorter run number
singleFieldDict_shortrun = {"run": 752, "rerun": 40, "camcol": 4, "field": 201, "filter": None,
					"jpeg_size": None, "dr12": False}
tsFieldURL_shortrun = "http://das.sdss.org/imaging/752/40/calibChunks/4/tsField-000752-4-40-0201.fit"
tsField_default_fname_shortrun = "tsField-000752-4-40-0201.fit"
shortrun_tsFieldConversion = (tsFieldURL_shortrun, tsField_default_fname_shortrun)

jpegURL = "http://das.sdss.org/imaging/3704/40/Zoom/6/fpC-003704-6-40-0069-z00.jpeg"
alt_jpegURL = "http://das.sdss.org/imaging/3704/40/Zoom/6/fpC-003704-6-40-0069-z30.jpeg"
default_jpegFname = "fpC-003704-6-40-0069-z00.jpeg"
jpegFname = "n2859_3704-69.jpeg"
jpegFname_bare = "n2859.jpeg"
default_jpegConversion = (jpegURL, default_jpegFname)
jpegConversion = (jpegURL, jpegFname)
jpegConversion_bare = (jpegURL, jpegFname_bare)
jpegConversion_AltSize = (alt_jpegURL, jpegFname)

secondFieldDict = {"run": 3560, "rerun": 40, "camcol": 1, "field": 220, "filter": None, "dr12": False}
secondFieldString = "3560 40 1 220"
secondFieldDict_dr12 = {"run": 1345, "rerun": None, "camcol": 3, "field": 234, "filter": None, "dr12": True}
secondFieldString_dr12 = "1345 3 234"
secondSpectrumDict = {"plate": 1593, "mjd": 52991, "fiber": 349}
secondSpectrumString = "1593 52991 349"

# DR7
urlA1 = "http://das.sdss.org/imaging/3704/40/corr/6/fpC-003704-r6-0069.fit.gz"
urlA2 = "http://das.sdss.org/imaging/3704/40/corr/6/fpC-003704-i6-0069.fit.gz"
urlB1 = "http://das.sdss.org/imaging/3560/40/corr/1/fpC-003560-r1-0220.fit.gz"
urlB2 = "http://das.sdss.org/imaging/3560/40/corr/1/fpC-003560-i1-0220.fit.gz"
fnameA1 = "n2859r_3704-69.fits.gz"
fnameA2 = "n2859i_3704-69.fits.gz"
fnameB1 = "n2859r_3560-220.fits.gz"
fnameB2 = "n2859i_3560-220.fits.gz"
multiFilterListA = [(urlA1, fnameA1), (urlA2, fnameA2)]
multiFilterListB = [(urlB1, fnameB1), (urlB2, fnameB2)]
multiFieldList = multiFilterListA + multiFilterListB
# dr12
urlA1_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/1302/3/frame-r-001302-3-0248.fits.bz2"
urlA2_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/1302/3/frame-i-001302-3-0248.fits.bz2"
urlB1_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/1345/3/frame-r-001345-3-0234.fits.bz2"
urlB2_dr12 = "http://dr12.sdss3.org/sas/dr12/boss/photoObj/frames/301/1345/3/frame-i-001345-3-0234.fits.bz2"
fnameA1_dr12 = "n2859r_dr12_1302-248.fits.bz2"
fnameA2_dr12 = "n2859i_dr12_1302-248.fits.bz2"
fnameB1_dr12 = "n2859r_dr12_1345-234.fits.bz2"
fnameB2_dr12 = "n2859i_dr12_1345-234.fits.bz2"
multiFilterListA_dr12 = [(urlA1_dr12, fnameA1_dr12), (urlA2_dr12, fnameA2_dr12)]
multiFilterListB_dr12 = [(urlB1_dr12, fnameB1_dr12), (urlB2_dr12, fnameB2_dr12)]
multiFieldList_dr12 = multiFilterListA_dr12 + multiFilterListB_dr12

#urlC1 = "http://data.sdss3.org/sas/dr9/sdss/spectro/redux/26/spectra/lite/0908/spec-0908-52373-0302.fits"
urlC1 = "http://data.sdss3.org/sas/dr12/sdss/spectro/redux/26/spectra/lite/0908/spec-0908-52373-0302.fits"
fnameC1 = "n2859_spec-0908-52373-0302.fits"
urlC2 = "http://data.sdss3.org/sas/dr12/sdss/spectro/redux/26/spectra/lite/1593/spec-1593-52991-0349.fits"
fnameC2 = "n2859_spec-1593-52991-0349.fits"
multiSpectrumList = [(urlC1, fnameC1), (urlC2, fnameC2)]

second_tsFieldURL = "http://das.sdss.org/imaging/3560/40/calibChunks/1/tsField-003560-1-40-0220.fit"
second_tsFieldfname = "tsField_n2859_3560-220.fit"
second_tsFieldConversion = (second_tsFieldURL, second_tsFieldfname)

singleFieldListA = [(urlA1, fnameA1), (urlA2, fnameA2)]
singleFieldListA_plus_tsFieldPair = [(urlA1, fnameA1), (urlA2, fnameA2), tsFieldConversion]
singleFieldListA_plus_jpeg = [(urlA1, fnameA1), (urlA2, fnameA2), tsFieldConversion, jpegConversion]
tsList = [tsFieldConversion, second_tsFieldConversion]
multiFieldList_and_tsField = multiFieldList + tsList



class RetrieveSDSSfilesTestCase(unittest.TestCase):
	def setUp(self):
		pass


class CheckConversion(RetrieveSDSSfilesTestCase):
	def testMakeFieldDict(self):
		"""Do we convert a string describing (run, rerun, camcol, field) to
		the corresponding dictionary?"""
		input="3704 40 6 69"
		output = get_sdssfiles.MakeFieldDict(input)
		self.assertEqual(output, singleFieldDict_nochange)

	def testMakeFieldDict_dr12(self):
		"""Do we convert a DR12 string describing (run, camcol, field) to
		the corresponding dictionary?"""
		input="1302 3 248"
		output = get_sdssfiles.MakeFieldDict(input)
		self.assertEqual(output, singleFieldDict_nochange_dr12)

	def testMakeSpectrumDict(self):
		"""Do we convert a string describing (plate, mjd, fiber) to
		the corresponding dictionary?"""
		input="908 52373 302"
		output = get_sdssfiles.MakeSpectrumDict(input)
		self.assertEqual(output, singleSpectrumDict)
	
 	def testSingleFieldConversion(self):
		"""Does MakeURLFilePair() convert a single-field dict to url,filename pair?"""
 		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict, "i", "n2859")
		self.assertEqual(outputTuple, singleFieldConversion)
 		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict_dr12, "i", "n2859")
		self.assertEqual(outputTuple, singleFieldConversion_dr12)

 	def testSingleFieldConversion_bare(self):
		"""Does MakeURLFilePair(noSuffixFlag=True) convert a single-field dict to url,filename pair?"""
 		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict, "i", "n2859", noSuffixFlag=True)
		self.assertEqual(outputTuple, singleFieldConversion_bare)
 		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict_dr12, "i", "n2859", noSuffixFlag=True)
		self.assertEqual(outputTuple, singleFieldConversion_bare_dr12)

  	def testDefaultFilename(self):
 		"""Does MakeURLFilePair() convert a single-field dict to url,filename pair,
 		with filename = original SDSS name?"""
  		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict, "i", None)
 		self.assertEqual(outputTuple, defaultFilenameConversion)
		outputTuple = get_sdssfiles.MakeURLFilePair(singleFieldDict_dr12, "i", None)
 		self.assertEqual(outputTuple, defaultFilenameConversion_dr12)

  	def testtsFieldDefaultFilename(self):
		"""Does Make_tsField_Pair() generate the correct tsField url,filename pair,
 		with filename = original SDSS name?"""
  		outputTuple = get_sdssfiles.Make_tsField_Pair(singleFieldDict, None)
 		self.assertEqual(outputTuple, default_tsFieldConversion)

  	def testtsFieldDefaultFilename_shortrun(self):
		"""Does Make_tsField_Pair() generate the correct tsField url,filename pair,
 		with filename = original SDSS name, *when* the run number is shorter than
 		usual?"""
  		outputTuple = get_sdssfiles.Make_tsField_Pair(singleFieldDict_shortrun, None)
 		self.assertEqual(outputTuple, shortrun_tsFieldConversion)

 	def testtsFieldConversion(self):
		"""Does Make_tsField_Pair() generate the correct tsField url,filename pair?"""
 		outputTuple = get_sdssfiles.Make_tsField_Pair(singleFieldDict, "n2859")
		self.assertEqual(outputTuple, tsFieldConversion)

 	def testtsFieldConversion_bare(self):
		"""Does Make_tsField_Pair(noSuffixFlag=True) generate the correct tsField url,filename pair?"""
 		outputTuple = get_sdssfiles.Make_tsField_Pair(singleFieldDict, "n2859", noSuffixFlag=True)
		self.assertEqual(outputTuple, tsFieldConversion_bare)

  	def testJPEGDefaultFilename(self):
		"""Does MakeJPEGPair() generate the correct JPEG url,filename pair,
 		with filename = original SDSS name?"""
  		outputTuple = get_sdssfiles.MakeJPEGPair(singleFieldDict, None)
 		self.assertEqual(outputTuple, default_jpegConversion)

 	def testJPEGConversion(self):
		"""Does MakeJPEGPair() generate the correct JPEG url,filename pair?"""
 		outputTuple = get_sdssfiles.MakeJPEGPair(singleFieldDict, "n2859")
		self.assertEqual(outputTuple, jpegConversion)

 	def testJPEGConversion_bare(self):
		"""Does MakeJPEGPair(noSuffixFlag=True) generate the correct JPEG url,filename pair?"""
 		outputTuple = get_sdssfiles.MakeJPEGPair(singleFieldDict, "n2859", noSuffixFlag=True)
		self.assertEqual(outputTuple, jpegConversion_bare)

 	def testJPEGConversion_AltSize(self):
		"""Does MakeJPEGPair() generate the correct JPEG url,filename pair
		with an alternate size specification?"""
 		outputTuple = get_sdssfiles.MakeJPEGPair(singleFieldDict, "n2859", "z30")
		self.assertEqual(outputTuple, jpegConversion_AltSize)

 	def testSingleFieldMultiFilterConversion(self):
		"""Does MakeFieldList() cycle through multiple filters correctly (for a single field)?"""
		filterList = ["r", "i"]
 		outputList = get_sdssfiles.MakeFieldList(singleFieldDict, filterList, "n2859")
		self.assertEqual(outputList, multiFilterListA)
	
	def testMultiFieldConversion(self):
		"""Does MakeFieldList() create proper list for multiple fields?"""
		filterList = ["r", "i"]
		fieldList = [singleFieldDict, secondFieldDict]
		outputList = get_sdssfiles.MakeFieldList(fieldList, filterList, "n2859")
		self.assertEqual(outputList, multiFieldList)

	def testMultiFieldConversion_dr12(self):
		"""Does MakeFieldList() create proper list for multiple fields?"""
		filterList = ["r", "i"]
		fieldList = [singleFieldDict_dr12, secondFieldDict_dr12]
		outputList = get_sdssfiles.MakeFieldList(fieldList, filterList, "n2859")
		self.assertEqual(outputList, multiFieldList_dr12)

	def testMultiSpectrumConversion(self):
		"""Does MakeSpectrumList() create proper list for multiple spectra?"""
		spectrumList = [singleSpectrumDict, secondSpectrumDict]
		outputList = get_sdssfiles.MakeSpectrumList(spectrumList, "n2859")
		self.assertEqual(outputList, multiSpectrumList)


class CheckMakeURLFilePairs(RetrieveSDSSfilesTestCase):
	def testMakeURLFieldPairs_SingleField_imageonly(self):
		"""Does MakeURLFilePairs() create proper list of (url,filename) pairs
		for a single field (FITS images only, no tsField or JPEG)?"""
		fieldStringList = [singleFieldString]
		filterString = "ri"
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeURLFilePairs(fieldStringList, filterString,
						fnameRoot, get_tsField=False)
		correctList = singleFieldListA
		self.assertEqual(resultList, correctList)

	def testMakeURLFieldPairs_SingleField(self):
		"""Does MakeURLFilePairs() create proper list of (url,filename) pairs
		for a single field (including tsField file)?"""
		fieldStringList = [singleFieldString]
		filterString = "ri"
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeURLFilePairs(fieldStringList, filterString,
						fnameRoot)
		correctList = singleFieldListA_plus_tsFieldPair
		self.assertEqual(resultList, correctList)

	def testMakeURLFieldPairs_SingleField_and_JPEG(self):
		"""Does MakeURLFilePairs() create proper list of (url,filename) pairs
		for a single field, including JPEG?"""
		fieldStringList = [singleFieldString]
		filterString = "ri"
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeURLFilePairs(fieldStringList, filterString,
						fnameRoot, get_JPEG=True)
		correctList = singleFieldListA_plus_jpeg
		self.assertEqual(resultList, correctList)

	def testMakeURLFieldPairs_SingleField_JPEG_only(self):
		"""Does MakeURLFilePairs() create the proper list containing the correct
		(url,filename) pair for JPEG only?"""
		fieldStringList = [singleFieldString]
		filterString = "ri"
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeURLFilePairs(fieldStringList, filterString,
						fnameRoot, getFITS=False, get_tsField=False, get_JPEG=True)
		correctList = [jpegConversion]
		self.assertEqual(resultList, correctList)

	def testMakeURLFieldPairs_Multi(self):
		"""Does MakeURLFilePairs() create proper list of (url,filename) pairs for
		multiple fields?"""
		fieldStringList = [singleFieldString, secondFieldString]
		filterString = "ri"
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeURLFilePairs(fieldStringList, filterString,
						fnameRoot)
		correctList = multiFieldList_and_tsField
		self.assertEqual(resultList, correctList)

	def testMakeURLSpectrumPairs_Multi(self):
		"""Does MakeSpectrumURLFilePairs() create proper list of (url,filename) pairs for
		multiple spectra?"""
		spectrumList = [singleSpectrumString, secondSpectrumString]
		fnameRoot = "n2859"
		resultList = get_sdssfiles.MakeSpectrumURLFilePairs(spectrumList, fnameRoot)
		correctList = multiSpectrumList
		self.assertEqual(resultList, correctList)




if __name__	== "__main__":
	
	print "\n** Unit tests for sdss_coords_archive.py **\n"
	unittest.main()	  

