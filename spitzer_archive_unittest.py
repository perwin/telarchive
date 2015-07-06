#! /usr/bin/env python

"""Unit test for spitzer_archive.py"""

import spitzer_archive
import unittest


#  Successful search (target was observed = NGC 2787 = 4 obs):
htmlFile = "html/Spitzer_n2787_result.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
noData_htmlFile = "html/Spitzer_NoData.html"
foundNoDataHTML = open(noData_htmlFile).read()

ngc2787_coords = ["09 19 18.596", "+69 12 11.71"]




class SpitzerArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = spitzer_archive.MakeArchive()	


class CheckAnalyzeHTML(SpitzerArchiveTestCase):
	def testNoDataFound(self):
		"""Check to see that case of "no data found" is correctly identified"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML(foundNoDataHTML)
		self.assertEqual(correctResult, result)
		
	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ('Data exists! (4 records found)', 4)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testSpecialSearches(self):
# 		"""Checking HTML text to find missions and observations"""
# 		correctResult = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		result = self.theArchive.DoSpecialSearches(foundDataHTML, 1)
# 		self.assertEqual(correctResult, result)
		

class MakeQuery(SpitzerArchiveTestCase):
	def setUp(self):
		self.theArchive = spitzer_archive.MakeArchive()	
		self.theArchive.InsertTarget("NGC 2787")
		self.theArchive.InsertBoxSize(1.0)
#		print self.theArchive.EncodeParams()
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 2787?"""
#		outf=open("bob.html",'w')
#		outf.write(self.textReceived)
#		outf.close()
		correctResult = ('Data exists! (4 records found)', 4)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testFindingDataByCoords(self):
		"""Live search: Do we find data for NGC 2787 using coords?"""
		self.theArchive.InsertTarget("")
		self.theArchive.InsertCoordinates(ngc2787_coords)
		correctResult = ('Data exists! (4 records found)', 4)
		newText = self.theArchive.QueryServer()
		result = self.theArchive.AnalyzeHTML(newText)
		self.assertEqual(correctResult, result)
		
		
# 	def testCountingData(self):
# 		"""Live search: Do we find and count the (non-HST) missions and obs. for M83?"""
# 		correctMissionCount = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		missionCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
# 		self.assertEqual(correctMissionCount, missionCount)




if __name__	== "__main__":
	
	print "\n** Unit tests for spitzer_archive.py **\n"
	unittest.main()	  
