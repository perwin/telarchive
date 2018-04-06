#! /usr/bin/env python

"""Unit test for ing_archive_lapalma.py"""

import ing_archive_lapalma
import unittest


#  Successful search (target was observed = NGC 4321 = 252 obs as of 29 Aug 2015):
htmlFile = "html/ngc_4321_ing_lapalma.html"
foundDataHTML = open(htmlFile).read()
dataFoundText = 'Data exists! (252 observations found)'
nDataFoundCorrect = 252
imageSpectraCountText = "\n\t\t116 images, 136 spectra"
instrumentCountText = """\n\t\tWHT -- AF2 (17), ISIS (62), LIRIS (25), PFIP (10), PNS (9), SAURON (52), TAURUS (5); INT -- WFC (70); JKT -- JAG (2)"""
specialSearchesText = """\n\t\t116 images, 136 spectra\n\t\tWHT -- AF2 (17), ISIS (62), LIRIS (25), PFIP (10), PNS (9), SAURON (52), TAURUS (5); INT -- WFC (70); JKT -- JAG (2)"""

#  Unsuccessful search (target not observed):
htmlFile_nodata = "html/ing_lapalma_nodata.html"
foundNoDataHTML = open(htmlFile_nodata).read()

# Reference for live searching (retrieved 29 Aug 2015):
htmlFile_n5750 = "html/ngc_5750_ing_lapalma.html"
NGC5750_COORDSLIST = ["14 46 11.104", "-00 13 22.99"]
dataFoundText_n5750 = 'Data exists! (13 observations found)'
nDataFoundCorrect_n5750 = 13


#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class INGLaPalmaArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = ing_archive_lapalma.MakeArchive()


class CheckAnalyzeHTML(INGLaPalmaArchiveTestCase):
	def testNoDataHTML(self):
		"""Analyzing HTML text indicating no data exists"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML( foundNoDataHTML )
		self.assertEqual(correctResult, result)

	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = (dataFoundText, nDataFoundCorrect)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testBadQueryHTML(self):
# 		"""Analyzing HTML text indicating improper query (e.g., object name instead of RA,dec)"""
# 		correctResult = ("Invalid reply from archive (possibly malformed coordinates?).", 0)
# 		result = self.theArchive.AnalyzeHTML( badQueryHTML )
# 		self.assertEqual(correctResult, result)

	def testCountImagesAndSpectra(self):
		"""Testing the function SearchHTMLForObs as defined in the module.
		"""
		correctResult = imageSpectraCountText
		result = ing_archive_lapalma.SearchHTMLForObs( foundDataHTML )
		self.assertEqual(correctResult, result)

	def testCountInstruments(self):
		"""Testing the function FindTelescopesAndInstruments as defined in the module.
		"""
		correctResult = instrumentCountText
		result = ing_archive_lapalma.FindTelescopesAndInstruments( foundDataHTML )
		self.assertEqual(correctResult, result)

	def testSpecialSearches(self):
		"""
		This tests how an instance of the archive class handles the DoSpecialSearches() 
		method (usually called from archive_search.py).
		"""
		correctResult = specialSearchesText
		result = self.theArchive.DoSpecialSearches(foundDataHTML, nDataFoundCorrect)
		self.assertEqual(correctResult, result)



class MakeQuery(INGLaPalmaArchiveTestCase):
	def setUp(self):
		self.theArchive = ing_archive_lapalma.MakeArchive()	
		self.theArchive.InsertBoxSize(4.0)
		
	def testFindingDataByCoords(self):
		"""Live search: Do we find data for NGC 5750 using coords?"""
		self.theArchive.InsertCoordinates(NGC5750_COORDSLIST)
		correctResult = (dataFoundText_n5750, nDataFoundCorrect_n5750)
		print("MakeQuery.testFindingDataByCoords: running live search using coords for NGC 5750...")
		newText = self.theArchive.QueryServer()
		result = self.theArchive.AnalyzeHTML(newText)
		self.assertEqual(correctResult, result)
		


if __name__	== "__main__":
	
	print("\n** Unit tests for ing_archive_lapalma.py **\n")
	unittest.main()	  
