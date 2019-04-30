#! /usr/bin/env python

"""Unit test for cfht_archive.py"""

import cfht_archive
import unittest


#  Successful search (target was observed = NGC 4321 w/ 4.0 arcmin box = 77 obs):
ngc4321_coordsList = ["12 22 54.95", "+15 49 19.5"]
csvFile = "testing/ngc_4321_cfht.csv"
foundDataCSV = open(csvFile).read()

#  Unsuccessful search (target not observed):
bad_coordsList = ["10 00 00.0", "-89 00 00.0"]
csvFile = "testing/cfht_nodata.csv"
foundNoDataCSV = open(csvFile).read()

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class CFHTArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = cfht_archive.MakeArchive()


class CheckAnalyzeHTML(CFHTArchiveTestCase):
	def testDataExistsCSV(self):
		"""Analyzing CSV text indicating data exists"""
		correctResult = ('Data exists! (269 observations found)', 269)
		result = self.theArchive.AnalyzeHTML( foundDataCSV )
		self.assertEqual(correctResult, result)
		
# 	def testBadQueryHTML(self):
# 		"""Analyzing HTML text indicating improper query (e.g., object name instead of RA,dec)"""
# 		correctResult = ("Invalid reply from archive (possibly malformed coordinates?).", 0)
# 		result = self.theArchive.AnalyzeHTML( badQueryHTML )
# 		self.assertEqual(correctResult, result)

	def testNoDataCSV(self):
		"""Analyzing CSV text indicating no data exists"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML( foundNoDataCSV )
		self.assertEqual(correctResult, result)


class MakeQuery(CFHTArchiveTestCase):
	def setUp(self):
		self.theArchive = cfht_archive.MakeArchive()	
		self.theArchive.InsertCoordinates(ngc4321_coordsList)
		self.theArchive.InsertBoxSize(4.0)
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 4321?"""
		correctResult = ('Data exists! (269 observations found)', 269)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testCountingData(self):
		"""Live search: Do we find and count instruments for NGC 4321?"""
		correctInstCount = "\n\t\tMegaPrime (223), HRCAM (46)"
		instCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
		self.assertEqual(correctInstCount, instCount)


if __name__	== "__main__":
	
	print("\n** Unit tests for cfht_archive.py **\n")
	unittest.main()	  
