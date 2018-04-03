#! /usr/bin/env python

# CURRENTLY NOT WORKING (BCS RELEVANT HTML FILES ARE MISSING)

"""Unit test for sdss_coords_archive.py"""

import sdss_coords_archive
import unittest


goodCoordsList1 = ["09 42 35.26", "+58 51 03.9"]  # NGC 2950 (in DR2)
multiFieldCoordsList = ["141.077212", "34.513490"]  # NGC 2859 (3 distinct fields in DR7)
badCoordsList = ["10 46 45.78", "-89 49 10.2"]    # outside SDSS

goodMessage = "Imaging data exists!"
goodMessageFull = "Imaging data exists!\n\t\t(run, rerun, camcol, field = 1345 41 3 234)"

goodmessageMultiFull = "Imaging data exists!\n\t\t(run, rerun, camcol, field = 3560 40 1 220)\n\t\t(run, rerun, camcol, field = 3635 41 6 210)\n\t\t(run, rerun, camcol, field = 3704 40 6 69)"

htmlGoodStatic = open("/Beleriand/dev/telarchive_working/testing/sdss_dr7_n2859.html").read()
htmlOutsideStatic = open("/Beleriand/dev/telarchive_working/testing/sdss_dr7_outsidecoords.html").read()

noDataReply = "No objects have been found"
noDataMessage = "No data found."



class SloanArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = sdss_coords_archive.MakeArchive()


class MakeQuery(SloanArchiveTestCase):
	def testAnalyzeHTML_GoodQuery(self):
		"""Does AnalyzeHTML respond properly to a good reply? [NGC 2859, saved HTML]"""
		self.theArchive.SetMode("fetchsdss")
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(htmlGoodStatic)
		self.assertEqual(messageString, goodmessageMultiFull)

	def testAnalyzeHTML_BadQuery(self):
		"""Does AnalyzeHTML respond properly to a no-data reply? [saved HTML]"""
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(htmlOutsideStatic)
		self.assertEqual(messageString, noDataMessage)

	def testGoodQuery1a(self):
		"""Live search: Do we sucessfully find & analyze NGC 2950? [telarchive mode]"""
		self.theArchive.InsertCoordinates(goodCoordsList1)
		self.theArchive.SetMode(None)
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(messageString, goodMessage)
		
	def testGoodQuery1b(self):
		"""Live search: Do we sucessfully find & analyze NGC 2950? ["fetchsdss" mode]"""
		self.theArchive.InsertCoordinates(goodCoordsList1)
		self.theArchive.SetMode("fetchsdss")
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(messageString, goodMessageFull)
		
	def testMultiFieldQuery(self):
		"""Live search: Do we sucessfully find all 3 fields of NGC 2859? [telarchive mode]"""
		self.theArchive.InsertCoordinates(multiFieldCoordsList)
		self.theArchive.SetMode(None)
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(messageString, goodMessage)
		
	def testBadQuery(self):
		"""Live search: Do we get the proper "no data" reply for coordinates outside SDSS?"""
		self.theArchive.InsertCoordinates(badCoordsList)
		textReceived = self.theArchive.QueryServer()
		(messageString, nDataFound) = self.theArchive.AnalyzeHTML(textReceived)
		self.assertEqual(messageString, noDataMessage)



if __name__	== "__main__":
	
	print("\n** Unit tests for sdss_coords_archive.py **\n")
	unittest.main()	  

