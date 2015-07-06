#! /usr/bin/env python

"""Unit test for cfht_archive.py"""

import cfht_archive
import unittest


ngc4321_coordsList = ["12 22 54.95", "+15 49 19.5"]
#  Successful search (target was observed = NGC 4321 w/ 4.0 arcmin box = 77 obs):
htmlFile = "html/ngc_4321_cfht.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
htmlFile = "html/cfht_nodata.html"
foundNoDataHTML = open(htmlFile).read()

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class CFHTArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = cfht_archive.MakeArchive()


class CheckAnalyzeHTML(CFHTArchiveTestCase):
 	def testDataExistsHTML(self):
 		"""Analyzing HTML text indicating data exists"""
 		correctResult = ('Data exists! (72 observations found)', 72)
 		result = self.theArchive.AnalyzeHTML( foundDataHTML )
 		self.assertEqual(correctResult, result)
		
# 	def testBadQueryHTML(self):
# 		"""Analyzing HTML text indicating improper query (e.g., object name instead of RA,dec)"""
# 		correctResult = ("Invalid reply from archive (possibly malformed coordinates?).", 0)
# 		result = self.theArchive.AnalyzeHTML( badQueryHTML )
# 		self.assertEqual(correctResult, result)

	def testNoDataHTML(self):
		"""Analyzing HTML text indicating no data exists"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML( foundNoDataHTML )
		self.assertEqual(correctResult, result)


class MakeQuery(CFHTArchiveTestCase):
	def setUp(self):
		self.theArchive = cfht_archive.MakeArchive()	
		self.theArchive.InsertCoordinates(ngc4321_coordsList)
		self.theArchive.InsertBoxSize(4.0)
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 4321?"""
		correctResult = ('Data exists! (72 observations found)', 72)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
 	def testCountingData(self):
 		"""Live search: Do we find and count instruments for NGC 4321?"""
 		correctInstCount = "\n\t\tMOS (25), HRC (36), PALILA (11)"
 		instCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
 		self.assertEqual(correctInstCount, instCount)


if __name__	== "__main__":
	
	print "\n** Unit tests for cfht_archive.py **\n"
	unittest.main()	  
