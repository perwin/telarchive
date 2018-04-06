#! /usr/bin/env python

"""Unit test for gemini_archive.py"""

import gemini_archive
import unittest


#  Successful search (target was observed = NGC 1291 w/ 4-arcmin box = 82 obs):
htmlFile = "testing/ngc_1291_gemini.json"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
foundNoDataHTML = "[]"

# coords for NGC 1291:
n1291CoordsList = ["03 17 18.600", "-41 06 29.05"]

# number of files found as of 1 Dec 2016, using 4x4-arcmin box
kCorrectNDataFound = 82
kCorrectInstrumentCount = "\n\t\t14 images, 59 long-slit spectra, 9 ifu\n\t\tGMOS-S: 21, GNIRS: 61"

#goodSearchURL = """https://archive.gemini.edu/jsonsummary/canonical/science/NotTwilight/NotFail/ra=204.2443488-204.2635678/dec=-29.8737500--29.8570833"""



class GeminiArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = gemini_archive.MakeArchive()	


class CheckAnalyzeHTML(GeminiArchiveTestCase):
	def testNoDataFound(self):
		"""Check to see that case of "no data found" is correctly identified"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML(foundNoDataHTML)
		self.assertEqual(correctResult, result)
		
	def testDataExistsHTML(self):
		"""Analyzing (old, locally stored) JSON text indicating data exists"""
		correctResult = ('Data exists! (%d observations found)' % kCorrectNDataFound, kCorrectNDataFound)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testSpecialSearches1(self):
# 		"""Checking HTML text to find and count types of observations"""
# 		correctResult = "\n\t\tGMOS-S: 21, GNIRS: 61"
# 		result = self.theArchive.theSearches[0](foundDataHTML, 1)
# 		self.assertEqual(correctResult, result)
		
	def testSpecialSearches2(self):
		"""Checking HTML text to find and count instruments"""
		result = self.theArchive.theSearches[0](foundDataHTML, 1)
		self.assertEqual(kCorrectInstrumentCount, result)
		

class MakeQuery(GeminiArchiveTestCase):
	def setUp(self):
		self.theArchive = gemini_archive.MakeArchive()	
		self.theArchive.InsertCoordinates(n1291CoordsList)
		self.theArchive.InsertBoxSize(4.0)
		print("MakeQuery.setUp: running live search for \"NGC 1291\"...")
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for M83?"""
		correctResult = ('Data exists! (%d observations found)' % kCorrectNDataFound, kCorrectNDataFound)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testCountingData(self):
		"""Live search: Do we find and count modes & instruments for M83?"""
		instCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
		self.assertEqual(kCorrectInstrumentCount, instCount)




if __name__	== "__main__":
	
	print("\n** Unit tests for gemini_archive.py **\n")
	unittest.main()	  
