#! /usr/bin/env python

"""Unit test for (user interface for) fetchsdss.py"""

# Some quasi-unit tests for aspects of the user interface for fetchsdss
# Tests fetchsdss.main() with various argv string-lists.

import fetchsdss
import unittest

badInput_filternames = ["fetchsdss", "ngc 936", "jkl"]
badInput_object_and_coords = ["fetchsdss", "ngc 1022", "--coords='00 00 00 +15 00 00'"]



class CheckFilterString(unittest.TestCase):
	def testGoodFilterStrings(self):
		"""Checking if FilterStringOK() recognizes good filter strings."""
		inputList = ["ugriz", "uz", "gri"]
		resultList = [ fetchsdss.FilterStringOK(input) for input in inputList ]
		self.assertEqual([True]*3, resultList)

	def testBadFilterStrings(self):
		"""Checking if FilterStringOK() recognizes bad filter strings."""
		inputList = ["y", "u g", "URI"]
		resultList = [ fetchsdss.FilterStringOK(input) for input in inputList ]
		self.assertEqual([False]*3, resultList)


class CheckJPEGSize(unittest.TestCase):
	def testGoodJPEGSizes(self):
		"""Checking if JPEGSizeOK() recognizes good size strings."""
		inputList = ["z00", "z10", "z25", "z30"]
		resultList = [ fetchsdss.JPEGSizeOK(input) for input in inputList ]
		self.assertEqual([True]*4, resultList)

	def testBadFilterStrings(self):
		"""Checking if JPEGSizeOK() recognizes bad filter strings."""
		inputList = ["gri", "z35", "z0"]
		resultList = [ fetchsdss.JPEGSizeOK(input) for input in inputList ]
		self.assertEqual([False]*3, resultList)


class CheckSDSSString(unittest.TestCase):
	def testGoodSDSSStrings(self):
		"""Checking if CheckSDSSString() recognizes good SDSS field-specification strings."""
		inputList = ["1034 40 6 304", "7734 41 1 72", "125 40 3 788", "1023,40,6,304",
					"1302 3 248", "1302,3,248"]
		resultList = [ fetchsdss.CheckSDSSString(input) for input in inputList ]
		self.assertEqual([True]*6, resultList)

	def testBadSDSSStrings(self):
		"""Checking if CheckSDSSString() recognizes bad SDSS field-specification strings."""
		inputList = ["1023,40,6,304,5", "7734 40 7 72", "125"]
		resultList = [ fetchsdss.CheckSDSSString(input) for input in inputList ]
		self.assertEqual([False]*3, resultList)


class CheckBadRequests(unittest.TestCase):
 	def testFindBadFilters1(self):
 		"""Checking that bad filters are noticed: coords supplied."""
 		inputList = ["fetchsdss", "--coords=00 00 00 +15 00 00", "jkl"]
 		correctResult = fetchsdss.kInputError
 		result = fetchsdss.main(inputList)
 		self.assertEqual(correctResult, result)

 	def testFindBadFilters2(self):
 		"""Checking that bad filters are noticed: field-ref supplied."""
 		inputList = ["fetchsdss", "--ref=1034 41 4 334", "jkl"]
 		correctResult = fetchsdss.kInputError
 		result = fetchsdss.main(inputList)
 		self.assertEqual(correctResult, result)
		
 	def testFindBadFilters3(self):
 		"""Checking that bad filters are noticed: online object search."""
 		inputList = ["fetchsdss", "ngc 1022", "jkl"]
 		correctResult = fetchsdss.kInputError
 		result = fetchsdss.main(inputList)
 		self.assertEqual(correctResult, result)
		

if __name__	== "__main__":
	
	print "\n** Unit tests for fetchsdss.py **\n"
	unittest.main()	  
