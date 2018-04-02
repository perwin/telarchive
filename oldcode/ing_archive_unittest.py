#! /usr/bin/env python

"""Unit test for ing_archive.py"""

import ing_archive
import unittest


#  Successful search (target was observed = NGC 4321 = 109 obs):
htmlFile = "html/ngc_4321_ing.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()


#testArchive = ing_archive.MakeArchive()


class INGArchiveTestCase(unittest.TestCase):
	def setUp(self):
		self.theArchive = ing_archive.MakeArchive()


class CheckAnalyzeHTML(INGArchiveTestCase):
	def testDataExistsHTML(self):
		"""Analyzing HTML text indicating data exists"""
		correctResult = ('Data exists! (109 observations found)', 109)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
# 	def testBadQueryHTML(self):
# 		"""Analyzing HTML text indicating improper query (e.g., object name instead of RA,dec)"""
# 		correctResult = ("Invalid reply from archive (possibly malformed coordinates?).", 0)
# 		result = self.theArchive.AnalyzeHTML( badQueryHTML )
# 		self.assertEqual(correctResult, result)


# 	def testNoDataHTML(self):
# 		"""Analyzing HTML text indicating no data exists"""
# 		correctResult = ("No data found.", 0)
# 		result = testArchive.AnalyzeHTML( foundNoDataHTML, textSearches )
# 		self.assertEqual(correctResult, result)


if __name__	== "__main__":
	
	print "\n** Unit tests for ing_archive.py **\n"
	unittest.main()	  
