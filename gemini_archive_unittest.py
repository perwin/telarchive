#! /usr/bin/env python

"""Unit test for gemini_archive.py"""

import gemini_archive
import unittest


#  Successful search (target was observed = M83 w/ 1.0 arcmin box = 77 obs):
htmlFile = "html/Gemini_M83_result.html"
foundDataHTML = open(htmlFile).read()

#  Unsuccessful search (target not observed):
noData_htmlFile = "html/Gemini_NoData.html"
foundNoDataHTML = open(noData_htmlFile).read()

goodSearchParams="""
action=Search&target=M83&resolver=SIMBAD&ra=&dec=&equinox=J2000&radius_acs=1.0&missions%5B%5D=FUSE&radius_fuse=1.0&radius_wfpc2=1.0&missions%5B%5D=IUE&radius_iue=1.0&radius_wfpc2_asn=1.0&missions%5B%5D=EUVE&radius_euve=1.0&radius_wfpc1=1.0&missions%5B%5D=COPERNICUS&radius_copernicus=1.0&radius_fos=1.0&missions%5B%5D=UIT&radius_uit=5.0&radius_ghrs=1.0&missions%5B%5D=HUT&radius_hut=1.0&radius_stis=1.0&missions%5B%5D=WUPPE&radius_wuppe=1.0&radius_nicmos=1.0&missions%5B%5D=BEFS&radius_befs=1.0&radius_foc=1.0&missions%5B%5D=IMAPS&radius_imaps=1.0&radius_fgs=1.0&missions%5B%5D=TUES&radius_tues=1.0&radius_hsp=1.0&missions%5B%5D=VLAFIRST&radius_vlafirst=1.0&missions%5B%5D=GALEX&radius_galex=1.0&outputformat=HTML_Table&max_records=1
"""

#  Bad object name:
#htmlFile = "ngc_bob_ing.html"
#badQueryHTML = open(htmlFile).read()



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
		"""Analyzing (old, locally stored) HTML text indicating data exists"""
		correctResult = ('Data exists! (74 observations found)', 74)
		result = self.theArchive.AnalyzeHTML( foundDataHTML )
		self.assertEqual(correctResult, result)
		
 	def testSpecialSearches1(self):
 		"""Checking HTML text to find and count types of observations"""
 		correctResult = "\n\t\t52 imaging, 22 long-slit"
 		result = self.theArchive.theSearches[0](foundDataHTML, 1)
 		self.assertEqual(correctResult, result)
		
 	def testSpecialSearches2(self):
 		"""Checking HTML text to find and count instruments"""
 		correctResult = "\n\t\tGMOS-S (31), NIRI (43)"
 		result = self.theArchive.theSearches[1](foundDataHTML, 1)
 		self.assertEqual(correctResult, result)
		

class MakeQuery(GeminiArchiveTestCase):
	def setUp(self):
		self.theArchive = gemini_archive.MakeArchive()	
		self.theArchive.InsertTarget("M83")
		self.theArchive.InsertBoxSize(1.0)
		self.textReceived = self.theArchive.QueryServer()
		
	def testFindingData(self):
		"""Live search: Do we sucessfully find data for M83?"""
		correctResult = ('Data exists! (77 observations found)', 77)
		result = self.theArchive.AnalyzeHTML(self.textReceived)
		self.assertEqual(correctResult, result)
		
 	def testCountingData(self):
 		"""Live search: Do we find and count modes & instruments for M83?"""
 		correctCount = "\n\t\t3 IFU, 52 imaging, 22 long-slit\n\t\tGMOS-S (34), NIRI (43)"
 		instCount = self.theArchive.DoSpecialSearches(self.textReceived, 1)
 		self.assertEqual(correctCount, instCount)




if __name__	== "__main__":
	
	print "\n** Unit tests for gemini_archive.py **\n"
	unittest.main()	  
