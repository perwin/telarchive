#! /usr/bin/env python

"""Unit test for hst_archive.py"""

import hst_archive
import unittest


#  Successful search (target was observed = NGC 936 = 9 obs):
htmlFile = "html/ngc_936_hst.txt"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
noData_htmlFile = "html/hst_NoData.txt"
foundNoDataHTML = open(noData_htmlFile).read()

ngc936_coords = ["02 27 37.46s", "-01 09 22.6"]



class HSTArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = hst_archive.MakeArchive()	


class CheckAnalyzeHTML(HSTArchiveTestCase):
	def testNoDataFound(self):
		"""Check to see that case of "no data found" is correctly identified"""
		correctResult = ("No data found.", 0)
		result = self.theArchive.AnalyzeHTML(foundNoDataHTML)
		self.assertEqual(correctResult, result)
		
	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ('Data exists! (9 records found)', 9)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testSpecialSearches(self):
# 		"""Checking HTML text to find missions and observations"""
# 		correctResult = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		result = self.theArchive.DoSpecialSearches(foundDataHTML, 1)
# 		self.assertEqual(correctResult, result)
		

class MakeQuery(HSTArchiveTestCase):
	def setUp(self):
		self.theArchive = hst_archive.MakeArchive()	
		self.theArchive.InsertTarget("NGC 936")
		self.theArchive.InsertBoxSize(1.0)
#		print self.theArchive.EncodeParams()
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for NGC 936?"""
#		outf=open("bob.html",'w')
#		outf.write(self.textReceived)
#		outf.close()
		correctResult = ('Data exists! (9 records found)', 9)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
	def testFindingDataByCoords(self):
		"""Live search: Do we find data for NGC 936 using coords?"""
		self.theArchive.InsertTarget("")
		self.theArchive.InsertCoordinates(ngc936_coords)
		correctResult = ('Data exists! (9 records found)', 9)
		newText = self.theArchive.QueryServer()
		result = self.theArchive.AnalyzeHTML(newText)
		self.assertEqual(correctResult, result)
		
		
# 	def testCountingData(self):
# 		"""Live search: Do we find and count the (non-HST) missions and obs. for M83?"""
# 		correctMissionCount = "\n\t\tFUSE (1); IUE (19); UIT (7); HUT (4); WUPPE (2); GALEX (1)"
# 		missionCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
# 		self.assertEqual(correctMissionCount, missionCount)




if __name__	== "__main__":
	
	print("\n** Unit tests for hst_archive.py **\n")
	unittest.main()	  
