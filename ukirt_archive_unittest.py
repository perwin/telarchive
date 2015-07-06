#! /usr/bin/env python

"""Unit test for ukirt_archive.py"""

import ukirt_archive
import unittest


#  Successful search (target was observed = NGC 4321 = 109 obs):
#htmlFile = "ngc_4321_ing.html"
#foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
htmlFile = "html/ukirt_nodata.html"
foundNoDataHTML = open(htmlFile).read()

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



class UKIRTArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = ukirt_archive.MakeArchive()


class CheckAnalyzeHTML(UKIRTArchiveTestCase):
# 	def testDataExistsHTML(self):
# 		"""Analyzing HTML text indicating data exists"""
# 		correctResult = ('Data exists! ("A total of 109 were retrieved")', 109)
# 		result = self.theArchive.AnalyzeHTML( foundDataHTML )
# 		self.assertEqual(correctResult, result)
		
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


if __name__	== "__main__":
	
	print "\n** Unit tests for ukirt_archive.py **\n"
	unittest.main()	  
