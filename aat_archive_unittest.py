#! /usr/bin/env python

"""Unit test for aat_archive.py"""

import aat_archive
import unittest


n5846_coordsList = ["15 06 29.2"," +01 36 20.2"]
#  Successful search [31 obs found]
htmlFile = "html/ngc_5846_aat_dec2016.html"
foundDataCSV = open(htmlFile).read()
nDataFoundCorrect = 30

#  Unsuccessful search (target not observed):
htmlFile = "html/NGC_1023_aat.html"
foundNoDataHTML = open(htmlFile).read()

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class AATArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = aat_archive.MakeArchive()


class CheckAnalyzeHTML(AATArchiveTestCase):
	def testDataExistsHTML( self ):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ("Data exists! (%d observations found)" % nDataFoundCorrect, nDataFoundCorrect)
		result = self.theArchive.AnalyzeHTML( foundDataCSV )
		self.assertEqual(correctResult, result)
		
	def testNoDataHTML(self):
		"""Analyzing HTML text indicating no data exists"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML( foundNoDataHTML )
		self.assertEqual(correctResult, result)


class MakeQuery(AATArchiveTestCase):
	def setUp(self):
		self.theArchive = aat_archive.MakeArchive()	
		self.theArchive.InsertCoordinates(n5846_coordsList)
		self.theArchive.InsertBoxSize(4.0)
		print("MakeQuery.setUp: running live search using coords for NGC 5846...")
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 5846?"""
		correctResult = ("Data exists! (%d observations found)" % nDataFoundCorrect, nDataFoundCorrect)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testCountingData(self):
		"""Live search: Do we find and count instruments for NGC 5846?"""
		correctInstCount = "\n\t\t-- 1 image, 29 spectra, 0 polarimetry"
		instCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
		self.assertEqual(correctInstCount, instCount)


if __name__	== "__main__":
	
	print("\n** Unit tests for aat_archive.py **\n")
	unittest.main()	  
