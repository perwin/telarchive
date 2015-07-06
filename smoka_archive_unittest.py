#! /usr/bin/env python

"""Unit test for smoka_archive.py"""

import smoka_archive
import unittest


#  Successful search (target was observed = NGC 936 = 59 obs):
htmlFile = "html/Smoka_n936_result.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
noData_htmlFile = "html/Smoka_NoData.html"
foundNoDataHTML = open(noData_htmlFile).read()

ngc936_coords = ["02 27 37.46", "-01 09 22.6"]




class SmokaArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = smoka_archive.MakeArchive()	


class CheckAnalyzeHTML(SmokaArchiveTestCase):
	def testNoDataFound(self):
		"""Check to see that case of "no data found" is correctly identified"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML(foundNoDataHTML)
		self.assertEqual(correctResult, result)
		
	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ('Data exists! (59 observations found)', 59)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testSpecialSearches(self):
# 		"""Checking HTML text to find missions and observations"""
# 		correctResult = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		result = self.theArchive.DoSpecialSearches(foundDataHTML, 1)
# 		self.assertEqual(correctResult, result)
		

class MakeQuery(SmokaArchiveTestCase):
	def setUp(self):
		self.theArchive = smoka_archive.MakeArchive()	
		self.theArchive.InsertTarget("NGC 936")
		self.theArchive.InsertBoxSize(1.0)
#		print self.theArchive.EncodeParams()
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 936?"""
		outf=open("bob.txt",'w')
		outf.write(self.textReceived)
		outf.close()
		correctResult = ('Data exists! (74 observations found)', 74)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testFindingDataByCoords(self):
		"""Live search: Do we find data for NGC 936 using coords?"""
		self.theArchive.InsertTarget("")
		self.theArchive.InsertCoordinates(ngc936_coords)
		correctResult = ('Data exists! (74 observations found)', 74)
		newText = self.theArchive.QueryServer()
		result = self.theArchive.AnalyzeHTML(newText)
		self.assertEqual(correctResult, result)
		
		
# 	def testCountingData(self):
# 		"""Live search: Do we find and count the (non-HST) missions and obs. for M83?"""
# 		correctMissionCount = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		missionCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
# 		self.assertEqual(correctMissionCount, missionCount)




if __name__	== "__main__":
	
	print "\n** Unit tests for smoka_archive.py **\n"
	unittest.main()	  
