#! /usr/bin/env python

"""Unit test for sdss_dr14spec_archive.py"""

import sdss_dr14spec_archive
import unittest


goodCoordsList1 = ["13 00 08.097", "+27 58 37.29"]  # NGC 4889 (1 spectrum)
badCoordsList = ["10 46 45.78", "-89 49 10.2"]    # outside SDSS

goodMessage = "Spectroscopic data exists!"
goodMessageFull = "Spectroscopic data exists! (one spectrum within r = 0.100 arcmin)"

goodmessageMultiFull = "Spectroscopic data exists! (2 spectra within r = 1.000 arcmin)"

csvGoodStatic = open("./testing/sdss_dr14spec_n4889.csv").read()
csvOutsideStatic = open("./testing/sdss_dr14spec_south.csv").read()

noDataMessage = "No spectroscopic data found."



class SloanArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = sdss_dr14spec_archive.MakeArchive()


class MakeQuery(SloanArchiveTestCase):
	def testAnalyzeHTML_GoodQuery(self):
		"""Does AnalyzeHTML respond properly to a good reply? [NGC 4889, saved CSV]"""
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(csvGoodStatic)
		self.assertEqual(nDataFound, 1)
		self.assertEqual(messageString, goodMessageFull)

	def testAnalyzeHTML_NoData(self):
		"""Does AnalyzeHTML respond properly to a no-data reply? [saved CSV]"""
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(csvOutsideStatic)
		self.assertEqual(nDataFound, 0)
		self.assertEqual(messageString, noDataMessage)

	def testGoodQuery1a(self):
		"""Live search: Do we sucessfully find & analyze NGC 4889? [telarchive mode]"""
		self.theArchive.InsertCoordinates(goodCoordsList1)
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(nDataFound, 1)
		self.assertEqual(messageString, goodMessageFull)
		
# 	def testGoodQuery1b(self):
# 		"""Live search: Do we sucessfully find & analyze NGC 2950? ["fetchsdss" mode]"""
# 		self.theArchive.InsertCoordinates(goodCoordsList1)
# 		self.theArchive.SetMode("fetchsdss")
# 		textReceived = self.theArchive.QueryServer()
# 		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
# 		self.assertEqual(messageString, goodMessageFull)
# 		
# 	def testMultiFieldQuery(self):
# 		"""Live search: Do we sucessfully find all 3 fields of NGC 2859? [telarchive mode]"""
# 		self.theArchive.InsertCoordinates(multiFieldCoordsList)
# 		self.theArchive.SetMode(None)
# 		textReceived = self.theArchive.QueryServer()
# 		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
# 		self.assertEqual(messageString, goodMessage)
# 		
	def testQuery_NoData(self):
		"""Live search: Do we get the proper "no data" reply for coordinates outside SDSS?"""
		self.theArchive.InsertCoordinates(badCoordsList)
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(nDataFound, 0)
		self.assertEqual(messageString, noDataMessage)



if __name__	== "__main__":
	
	print("\n** Unit tests for sdss_dr14spec_archive.py **\n")
	unittest.main()	  

